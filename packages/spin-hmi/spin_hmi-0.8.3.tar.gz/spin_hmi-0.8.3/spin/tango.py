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

"""Tango backend."""

import ast

import tango
from tango import DevFailed, DevState
from tango.asyncio import DeviceProxy as AsyncDeviceProxy

from .backend import State
from .device import PeriodicPollDevice

STATE_MAP = {
    DevState.ALARM: State.WARN,
    DevState.CLOSE: State.DISABLED,
    DevState.DISABLE: State.DISABLED,
    DevState.FAULT: State.ERROR,
    DevState.INIT: State.BUSY,
    DevState.MOVING: State.BUSY,
    DevState.OFF: State.DISABLED,
    DevState.ON: State.OK,
    DevState.OPEN: State.OK,
    DevState.RUNNING: State.BUSY,
    DevState.STANDBY: State.DISABLED,
}

NUMERIC_TYPES = {
    tango.DevUChar: ['int', 0, 255],
    tango.DevShort: ['int', -32768, 32767],
    tango.DevUShort: ['int', 0, 65535],
    tango.DevLong: ['int', -2**31, 2**31 - 1],
    tango.DevULong: ['int', 0, 2**32 - 1],
    tango.DevLong64: ['int', -2**63, 2**63 - 1],
    tango.DevULong64: ['int', 0, 2**64 - 1],
    tango.DevFloat: ['float', -3e38, 3e38],
    tango.DevDouble: ['float', -1e308, 1e308],
}


def format_fail(exc):
    """Return a *simple* one-line exception string from a convoluted tango exc.

    Takes the first line of the exception's string representation that looks
    like it could be the topmost "description" of the exception.
    """
    lines = str(exc).splitlines()
    firstline = ''
    desc = ''
    for line in lines:
        line = line.strip()
        if line.endswith(('DevError[', 'DevFailed[')):
            continue
        if not firstline:
            firstline = line
        if line.startswith('desc ='):
            desc = line[6:].strip()
        if line.startswith('reason =') and desc:
            desc = f'{line[8:].strip()}: {desc}'
            break
    return desc or firstline


def parse_int_mapping(mapping):
    """Parse the "mapping" property of digital devices."""
    labels = []
    val2label = {}
    label2val = {}
    mapping = ast.literal_eval(mapping)
    for entry in mapping:
        parts = entry.split(':')
        if len(parts) < 2:
            continue
        try:
            val = int(parts[0].strip())
        except ValueError:
            continue
        label = parts[1].strip()
        val2label[val] = label
        label2val[label] = val
        if len(parts) == 2 or 'ro' not in parts[2]:
            labels.append(label)
    return labels, val2label, label2val


class Device(PeriodicPollDevice):
    """Abstraction for Tango devices, using the PyTango asyncio integration.

    Device url should look like: 'tango://<host>:<port>/<x>/<y>/<z>',
    with x/y/z being the device name.
    """

    _dev = None
    _params = None

    async def init_poll(self):
        self._dev = await AsyncDeviceProxy(self._devconf.device)
        self._attrconf = {}
        self._props = {}
        self._mapping = None, None, None

        for elem in self._dev.attribute_list_query():
            self._attrconf[elem.name] = elem
        unit = self._attrconf['value'].unit

        try:
            proplist = await self._dev.command_inout('GetProperties')
        except DevFailed as e:
            self.log.warning('could not query properties: %s', format_fail(e))
        else:
            for i in range(0, len(proplist), 2):
                self._props[proplist[i]] = proplist[i + 1]

            if self._devconf.options.get('enum') and 'mapping' in self._props:
                self._mapping = parse_int_mapping(self._props['mapping'])

        self._unit = unit if unit != 'No unit' else ''
        self._params = {}
        for param in self._devconf.params or []:
            try:
                unit = self._attrconf[param].unit
            except DevFailed as e:
                self.log.error('could not find info for parameter %s, '
                               'ignoring it', param)
                await self.send_param(
                    param, None, '', f'Could not query unit: {format_fail(e)}')
            else:
                self._params[param] = unit if unit != 'No unit' else ''

    async def poll(self):
        try:
            state = await self._dev.State()
            status = await self._dev.Status()
        except DevFailed as e:
            await self.send(State.ERROR,
                            f'Error in status poll: {format_fail(e)}')
            return

        state = STATE_MAP.get(state, State.UNKNOWN)
        if state in (State.ERROR, State.UNKNOWN):
            await self.send(state, status)
            return

        try:
            val = (await self._dev.read_attribute('value')).value
        except DevFailed as e:
            await self.send(State.ERROR,
                            f'Error in value poll: {format_fail(e)}')
        else:
            if self._mapping[1]:
                val = self._mapping[1].get(val, str(val))
            await self.send(state, status, val)

        for param, unit in self._params.items():
            try:
                res = await self._dev.read_attribute(param)
            except DevFailed as e:
                await self.send_param(param, None, '',
                                      f'Error in param poll: {format_fail(e)}')
            else:
                await self.send_param(param, res.value, unit)

    def format_exception(self, exc):
        if isinstance(exc, DevFailed):
            return format_fail(exc)
        return str(exc)

    async def input_value_type(self, param):
        try:
            dtype = self._attrconf[param].data_type
        except KeyError:
            return ['float', -1e308, 1e308]

        absmin = absmax = 0
        if param == 'value':
            if self._mapping[0]:
                return ['choice', self._mapping[0]]
            absmin = self._props.get('absmin', 0)
            absmax = self._props.get('absmax', 0)

        if dtype in NUMERIC_TYPES:
            if absmin == absmax == 0:
                absmin = NUMERIC_TYPES[dtype][1]
                absmax = NUMERIC_TYPES[dtype][2]
            return [NUMERIC_TYPES[dtype][0], absmin, absmax]
        return ['str']

    async def action_state(self, param):
        if param == 'value':
            return STATE_MAP.get(await self._dev.State(), State.UNKNOWN)
        return State.OK

    async def action_stop(self):
        await self._dev.Stop()

    async def action_reset(self):
        await self._dev.Reset()

    async def action_get(self, param):
        return (await self._dev.read_attribute(param)).value

    async def action_set(self, param, value):
        if param == 'value' and self._mapping[2] and value in self._mapping[2]:
            value = self._mapping[2][value]
        await self._dev.write_attribute(param, value)

    async def action_upload(self, filename, file, target=None):
        pass
