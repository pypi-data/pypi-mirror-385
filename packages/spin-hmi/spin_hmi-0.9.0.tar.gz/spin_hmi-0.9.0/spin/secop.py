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

"""SECoP backend."""

import json
from collections import defaultdict

from .backend import State
from .device import AsyncUpdateDevice
from .utils import StreamConnection


def to_state(status):
    status, statustext = status
    if status < 0:
        return State.UNKNOWN, ''
    if status < 100:
        return State.DISABLED, statustext
    if status < 200:
        return State.OK, statustext
    if status < 300:
        return State.WARN, statustext
    if status < 400:
        return State.BUSY, statustext
    if status < 500:
        return State.ERROR, statustext
    return State.UNKNOWN, ''


# We want to open only one connection per node, so save them here
NODES = {}


class SECNode(StreamConnection):
    """Device representing a SEC node connection."""

    async def _synchronize(self):
        self.log.info('connected to node')
        await self._send(b'*IDN?')
        proto = await self._receive()
        if ',SECoP,' not in proto:
            raise RuntimeError('not a SECoP node, IDN = {proto!r}')
        await self._send(b'describe')
        description_msg = await self._receive()
        _, _, description = self._decode(description_msg)
        # check if identifiers are in description and set all units
        await self._set_units(description)
        self.log.info('waiting for initial updates')
        await self._send(b'activate')
        unseen = set(self.devices)
        while True:
            msg = self._decode(await self._receive())
            if msg[0] == 'active':
                break
            await self._handle_message(msg)
            unseen.discard(msg[1])
        if unseen:
            self.log.warning('not all initial updates from SEC node '
                             'received (missing %s)', unseen)

    async def _set_units(self, descr):
        for name, devs in self.devices.items():
            for dev in devs:
                mod, _, param = name.partition(':')
                if param == 'status':
                    continue
                try:
                    modules = descr['modules']
                except KeyError as e:
                    raise RuntimeError('Malformed description message!') from e

                try:
                    datainfo = modules[mod]['accessibles'][param]['datainfo']
                    dev.set_datainfo(param, datainfo)
                except KeyError:
                    # pylint: disable=raise-missing-from
                    dev.log.error('accessible %s not present on SEC node', name)
                    await dev.send(State.ERROR,
                                   'Module/param not present on SEC node')

    def _decode(self, line):
        action, ident, data = [*line.strip().split(' ', 2), '', ''][:3]
        data = {} if data == '' else json.loads(data)
        return action, ident, data

    async def _handle_message(self, msg):
        action, ident, data = msg
        if ident not in self.devices:
            return
        for dev in self.devices[ident]:
            await dev.update(action, ident, data)

    def add_device(self, device):
        mod = device.device
        self.devices[f'{mod}:value'].append(device)
        # we always want the status
        self.devices[f'{mod}:status'].append(device)
        for par in device.extra_params or []:
            self.devices[f'{mod}:{par}'].append(device)

    async def run_cmd(self, dev, cmd):
        await self._send(f'do {dev}:{cmd}'.encode())

    async def write(self, dev, param, value):
        await self._send(f'change {dev}:{param} {value}'.encode())


class Device(AsyncUpdateDevice):
    """A device representing a polled secop module.

    The polling happens in the SEC node, this is kept for callbacks on actions.
    Device url should look like: 'secop://<host>:<port>/<module>'
    """

    _connclass = SECNode

    def __init__(self, name, devconf, uri, backend, log):
        super().__init__(name, devconf, uri, backend, log)
        self._input_value_type = {}
        self._useenum = devconf.options.get('enum', False)
        self._enums = {}
        self._units = defaultdict(str)

    def set_datainfo(self, param, info):
        self.log.info('datainfo is set')
        self._units[param] = info.get('unit', '')
        if param == 'value':
            self._unit = self._units[param]
        if info.get('type') == 'double':
            mini = info.get('min', -1e308)
            maxi = info.get('max', 1e308)
            self._input_value_type[param] = ['float', mini, maxi]
        elif info.get('type') == 'int':
            mini = info.get('min', -2147483648)
            maxi = info.get('max', 2147483647)
            self._input_value_type[param] = ['int', mini, maxi]
        elif info.get('type') == 'bool':
            self._input_value_type[param] = ['int', 0, 1]
        elif info.get('type') == 'enum':
            members = info.get('members', {})
            if self._useenum:
                rev_members = {v: k for k, v in members.items()}
                self._enums[param] = members, rev_members
                self._input_value_type[param] = ['choice', list(members)]
            else:
                self._input_value_type[param] = ['int', 0, len(members) - 1]
        elif info.get('type') == 'string':
            self._input_value_type[param] = ['str']

    async def update(self, action, ident, data):
        _, _, param = ident.partition(':')
        value = data[0]
        if action == 'update':
            if param == 'status':
                self.cache['status'] = to_state(value)
                state, state_str = self.cache['status']
                await self.send(state, state_str, self.cache['value'])
            elif param == 'value':
                if 'value' in self._enums and value in self._enums['value'][1]:
                    value = self._enums[param][1][value]
                self.cache['value'] = value
                state, state_str = self.cache['status']
                await self.send(state, state_str, value)
            else:
                if param in self._enums and value in self._enums[param][1]:
                    value = self._enums[param][1][value]
                self.cache[param] = value
                state, state_str = self.cache['status']
                await self.send_param(param, value, self._units[param])

    async def input_value_type(self, param):
        return self._input_value_type.get(param, ['float', -1e308, 1e308])

    async def action_stop(self):
        await self._conn.run_cmd(self.device, 'stop')

    async def action_reset(self):
        # TODO: check if reset exists
        await self._conn.run_cmd(self.device, 'reset')

    async def action_set(self, param, value):
        if param == 'value':
            param = 'target'
        if (members := self._enums.get(param)) and \
           (value in members[0]):
            value = members[0][value]
        await self._conn.write(self.device, param, json.dumps(value))

    async def action_run(self, command):
        await self._conn.run_cmd(self.device, command)

    async def action_upload(self, filename, file, target=None):
        pass
