# *****************************************************************************
# Nobody expects the Spanish Inquisition!
# Copyright (c) 2024- by the authors, see LICENSE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Alexander Zaft <a.zaft@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Base implementations for backend devices."""

import asyncio
from contextlib import asynccontextmanager
from typing import ClassVar

from .backend import Reply, Request, State, Update
from .utils import decode_base64_file


class BaseDevice:
    """Base abstraction for a single device."""

    def __init__(self, name, devconf, uri, backend, log):
        self.log = log
        self._uri = uri
        self._name = name
        self._devconf = devconf
        self._backend = backend
        self._unit = ''

    @property
    def is_initialized(self):
        """Can return False if the device is not yet initialized."""
        return True

    # Utility methods.

    def run_task(self, coro):
        self._backend.run_task(coro)

    async def send(self, state, state_str, value=None):
        """Call this to send a main value update to all frontends."""
        await self._backend.send_update(Update(
            self._name,
            self._unit,
            state,
            state_str,
            value,
        ))

    async def send_param(self, name, value, unit, error=None):
        """Call this to send a parameter update to all frontends."""
        await self._backend.send_update(Update(
            self._name + '.' + name,
            unit,
            State.OK if error is None else State.ERROR,
            error or '',
            value,
        ))

    async def send_reply(self, reply: Reply):
        await self._backend.send_reply(reply)

    async def send_progress(self, conn, progress, label=''):
        """Send a progress update to the given frontend.

        *progress* should be a float between 0 and 1. *label* is not required
        if progress is 1 (done).
        """
        await self.send_reply(Reply(conn, self._name, None, 'progress',
                                    [label, progress]))

    @asynccontextmanager
    async def error_guard(self, conn, msg=None, *, reset_progress=True):
        """Catch errors of long running tasks spawned for this device.

        The error message will be appended to 'msg'.
        """
        try:
            yield
        except Exception as err:
            if reset_progress:
                await self.send_progress(conn, 1)
            msg = (msg or 'Error in task: ') + str(err)
            self.log.exception(msg)
            await self.send_reply(Reply(conn, self._name, None, 'error', msg))

    # Overridable methods.

    def needed_assets(self):
        """Return a list of CSS/JS assets needed by this device."""
        return []

    def init(self):
        raise NotImplementedError

    def format_exception(self, exc):
        """Format exceptions for sending to the frontend.

        This can be overridden by subclasses to avoid overly complex
        information.
        """
        return str(exc)

    async def handle_request(self, request: Request):
        """Handle a Request from a frontend."""
        param = request.key.partition('.')[2] or 'value'

        if not self.is_initialized:
            raise RuntimeError('device not initialized')

        transform = None
        firstbit = None
        bitmask = None
        factor = 1.0
        if request.transform:
            if request.transform[0] == 'bits':
                transform = 'bits'
                firstbit = int(request.transform[1])
                bitmask = (1 << int(request.transform[2])) - 1
            elif request.transform[0] == 'scale':
                transform = 'scale'
                factor = float(request.transform[1])
            else:
                raise ValueError('unknown transform specified')

        # 'click' needs to be confirmed if the device is configured for that
        if request.action == 'click' and request.intent != 'input' and \
           self._devconf.confirm:
            return Reply(request.connection, request.key,
                         request.transform, 'confirm',
                         {'intent': request.intent,
                          'data': request.data,
                          'what': f'{request.intent} on {self._name}',
                          'prompt': self._devconf.confirm})

        # otherwise, 'confirm' and 'click' are the same
        if request.action in ('click', 'confirm'):
            cur_state = await self.action_state(param)

            if request.intent not in ('reset', 'stop', 'input',
                                      'toggle', 'set', 'run'):
                raise ValueError(f'Unknown intent {request.intent}')

            if request.intent == 'reset' or \
               (param == 'value' and cur_state == State.ERROR):
                await self.action_reset()
                return None

            if request.intent == 'stop' or \
               (param == 'value' and cur_state == State.BUSY):
                await self.action_stop()
                return None

            if request.intent == 'run':
                await self.action_run(request.data)
                return None

            if request.intent == 'input':
                valuetype = await self.input_value_type(param)
                return Reply(request.connection, request.key,
                             request.transform, 'input', valuetype)

            new_value = None

            if request.intent == 'toggle':
                cur_value = await self.action_get(param)
                if transform == 'bits':
                    field_value = (cur_value >> firstbit) & bitmask
                    new_value = cur_value & ~(bitmask << firstbit)
                    new_value |= int(not field_value) << firstbit
                else:
                    toggle_vals = request.data or [0, 1]
                    new_value = toggle_vals[1] if cur_value == toggle_vals[0] \
                        else toggle_vals[0]

            elif request.intent == 'set':
                if transform == 'bits':
                    cur_value = await self.action_get(param)
                    new_value = cur_value & ~(bitmask << firstbit)
                    new_value |= (request.data & bitmask) << firstbit
                elif transform == 'scale':
                    new_value = request.data / factor
                else:
                    new_value = request.data

            await self.action_set(param, new_value)

        elif request.action == 'input':
            # got a specific value to set, treat it like a click
            request.action = 'click'
            request.intent = 'set'
            return await self.handle_request(request)

        elif request.action == 'upload':
            decoded = decode_base64_file(request.data['contents'])
            await self.action_upload(request.data['filename'], decoded)
            return None

        else:
            raise ValueError(f'Unknown action {request.action}')

        # after an action, make sure we poll the new state directly
        if isinstance(self, PeriodicPollDevice):
            await self.poll(0)
        return None

    # The following methods are used by the default handle_request() and
    # can be ignored by subclasses that define their own.

    async def action_state(self, param):
        """Get the state of the device or a parameter, for actions."""
        raise NotImplementedError

    async def action_stop(self):
        """Stop the device, for actions."""
        raise NotImplementedError

    async def action_reset(self):
        """Reset the device, for actions."""
        raise NotImplementedError

    async def action_get(self, param):
        """Get the value of a parameter, for actions."""
        raise NotImplementedError

    async def action_set(self, param, value):
        """Set the value of a parameter, for actions."""
        raise NotImplementedError

    async def action_run(self, command):
        """Execute a backend-specific command."""
        raise NotImplementedError

    async def action_upload(self, filename, file, target=None):
        """Upload a file to the device.

        Select which action to do by specifying target.
        """
        raise NotImplementedError

    async def input_value_type(self, _param):
        """Return the type of a parameter, for querying input.

        Possible return values are:

        - ['int', min, max]
        - ['float', min, max]
        - ['str']
        - ['choice', ['value1', 'value2', ...]]
        """
        return ['float', -1e308, 1e308]


class PeriodicPollDevice(BaseDevice):
    """Base class for devices which periodically poll their endpoint."""

    _is_initialized = False

    def init(self):
        self.run_task(self.periodic_poll())

    @property
    def is_initialized(self):
        return self._is_initialized

    async def periodic_poll(self):
        sleep = 1
        while True:
            n = 0
            self._is_initialized = False
            try:
                await self.init_poll()
            except Exception as e:
                self.log.exception('error initializing poller')
                exc_str = self.format_exception(e)
                await self.send(State.ERROR, f'Could not init: {exc_str}')
                await asyncio.sleep(sleep)
                sleep = min(30, sleep * 1.53)
                continue
            self.log.info('poller initialized')
            self._is_initialized = True

            while True:
                try:
                    await self.poll(n)
                    n += 1
                except Exception as e:
                    self.log.exception('error in poll')
                    exc_str = self.format_exception(e)
                    await self.send(State.ERROR, f'Error in poll: {exc_str}')

                await asyncio.sleep(self._devconf.pollinterval)

    async def init_poll(self):
        raise NotImplementedError

    async def poll(self, n):
        raise NotImplementedError


class AsyncUpdateDevice(BaseDevice):
    # pylint: disable=abstract-method
    """Base class for devices that support async updates.

    This provides common functionality for devices that maintain
    a cache of status/value and handle parameter updates.
    """

    _cache: ClassVar = {}
    # must be something that has an `add_device` method, possibly
    # a spin.utils.StreamConnection
    _connclass = object

    def __init__(self, name, devconf, uri, backend, log):
        super().__init__(name, devconf, uri, backend, log)
        self.cache = {
            'status': (State.UNKNOWN, ''),
            'value': None,
        }
        self.extra_params = [par.name for par in devconf.params]
        self._addr, self.device = uri.netloc, uri.path.lstrip('/')

    def init(self):
        if self._addr not in self._cache:
            self._cache[self._addr] = self._connclass(
                self._addr, self.log.parent.getChild(self._addr))
            self.run_task(self._cache[self._addr].run())
        self._conn = self._cache[self._addr]
        self._conn.add_device(self)

    @property
    def is_initialized(self):
        return self._conn.is_initialized

    async def action_state(self, param):
        if param == 'value':
            return self.cache['status'][0]
        return State.OK

    async def action_get(self, param):
        return self.cache[param]
