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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""PILS backend via Zapf."""

import asyncio
from typing import ClassVar

import zapf.io
from zapf.scan import Scanner
from zapf.spec import DevStatus, ReasonMap, decode_bitfield

from .backend import Reply, Request, State
from .device import PeriodicPollDevice

STATE_MAP = {
    DevStatus.RESET:    State.UNKNOWN,
    DevStatus.IDLE:     State.OK,
    DevStatus.DISABLED: State.DISABLED,
    DevStatus.WARN:     State.WARN,
    DevStatus.START:    State.BUSY,
    DevStatus.BUSY:     State.BUSY,
    DevStatus.STOP:     State.BUSY,
    DevStatus.ERROR:    State.ERROR,
    DevStatus.DIAGNOSTIC_ERROR: State.ERROR,
}


class Device(PeriodicPollDevice):
    """Abstraction for PILS devices, using the Zapf library.

    The library is not async, but has an internal polling thread, so that
    most requests should be "non-blocking enough".

    Device uri can have different forms, depending on the IO protocol.
    To the Zapf connection URI, add `#devname`.
    """

    _cache: ClassVar = {}
    _table = None

    def needed_assets(self):
        if self._devconf.options.get('table'):
            yield 'pils-table.js'

    async def init_poll(self):
        devname = self._uri.fragment
        scheme = self._uri.scheme
        zapfuri = self._uri._replace(scheme=scheme.removeprefix('pils+'),
                                     fragment='').geturl()
        if zapfuri.startswith('sim:/'):
            # fix side effect of urllib.parse without a "hostname"
            zapfuri = 'sim:///' + zapfuri[5:]

        # Scanning can block for a long time, so we run it on a side thread
        # for the first Zapf device.  All other devices reuse the same PlcIO,
        # so they must wait for the "scan done" event to be set.
        if zapfuri not in self._cache:
            def scan():
                return list(Scanner(io, log).get_devices())
            entry = self._cache[zapfuri] = [asyncio.Event(), None]
            log = self.log.getChild('zapf')
            io = zapf.io.PlcIO(zapfuri, log)
            entry[1] = await asyncio.to_thread(scan)
            # This starts the polling thread.
            io.start_cache()
            entry[0].set()
        else:
            await self._cache[zapfuri][0].wait()

        for dev in self._cache[zapfuri][1]:
            if dev.name == devname:
                self._dev = dev
                break
        else:
            raise RuntimeError(f'device {devname} not present in PLC')

        if tblname := self._devconf.options.get('table'):
            try:
                self._table = self._dev.tables[tblname]
            except KeyError:
                raise RuntimeError(f'table {tblname!r} not found in device '
                                   f'{devname!r}') from None

        self._useenum = self._devconf.options.get('enum', False)
        self._auxdef = self._dev.info.get('aux', {})
        self._unit = self._dev.info['unit']
        self._params = {}
        for i, param in enumerate(self._devconf.params):
            if param.name == 'target':
                self._params['target'] = (self._unit, param.poll_every,
                                          i % param.poll_every)
                continue

            try:
                unit = self._dev.get_param_valueinfo(param.name).unit
            except zapf.Error as e:
                self.log.error('could not find info for parameter %s, '
                               'ignoring it', param.name)
                await self.send_param(
                    param.name, None, '', f'Could not query unit: {e}')
            else:
                self._params[param.name] = (unit, param.poll_every,
                                            i % param.poll_every)

    async def poll(self, n):
        try:
            state, reason, aux, _ = self._dev.read_status()
        except zapf.Error as e:
            await self.send(State.ERROR, f'Error in status poll: {e}')
            return

        state = STATE_MAP.get(state, State.UNKNOWN)
        string_list = []
        reason = ReasonMap[reason]
        if reason:
            string_list.append(reason)
        if aux:
            string_list.append(decode_bitfield(aux, self._auxdef))
        status = ', '.join(string_list)

        try:
            if self._useenum:
                val = self._dev.read_value()
            else:
                val = self._dev.read_value_raw()
        except zapf.Error as e:
            await self.send(State.ERROR, f'Error in value poll: {e}')
        else:
            await self.send(state, status, val)

        for param, (unit, every, stagger) in self._params.items():
            if n == 0 or n % every == stagger:
                try:
                    if param == 'target':
                        if self._useenum:
                            res = self._dev.read_target()
                        else:
                            res = self._dev.read_target_raw()
                    else:
                        # get_param() can block for a long time due to
                        # manipulation of the paramctrl interface
                        # TODO: avoid for FlatParam devices
                        res = await asyncio.to_thread(
                            lambda p=param: self._dev.get_param(p))
                except zapf.Error as e:
                    await self.send_param(param, None, '',
                                          f'Error in param poll: {e}')
                else:
                    await self.send_param(param, res, unit)

    def _value_type_from_info(self, info):
        if info.basetype == 'float':
            return ['float', info.min_value, info.max_value]
        if info.basetype in ('int', 'uint'):
            return ['int', info.min_value, info.max_value]
        if info.basetype == 'enum':
            return ['choice', list(info.enum_w)]
        return ['float', -1e308, 1e308]

    async def input_value_type(self, param):
        try:
            if param == 'value':
                info = self._dev.value_info
            else:
                info = self._dev.get_param_valueinfo(param)
        except zapf.Error:
            return ['float', -1e308, 1e308]
        return self._value_type_from_info(info)

    async def handle_request(self, request: Request):
        if request.action == 'read-table':
            return await self._read_table(request)
        if request.action == 'write-cell':
            return await self._write_table_cell(request)
        return await super().handle_request(request)

    async def action_state(self, param):
        if param == 'value':
            return STATE_MAP.get(self._dev.read_status()[0], State.UNKNOWN)
        return State.OK

    async def action_stop(self):
        self._dev.change_status((DevStatus.BUSY,), DevStatus.STOP)

    async def action_reset(self):
        self._dev.reset()

    async def action_get(self, param):
        if param == 'value':
            return self._dev.read_value_raw()
        return self._dev.get_param(param)

    async def action_set(self, param, value):
        if param in {'value', 'target'}:
            if self._useenum:
                self._dev.change_target(value)
            else:
                self._dev.change_target_raw(value)
        else:
            self._dev.set_param(param, value)

    async def action_run(self, command):
        await asyncio.to_thread(lambda: self._dev.exec_func(command))

    async def action_upload(self, filename, file, target=None):
        pass

    async def _read_table(self, request):
        """Read the current table data."""
        if not self._table:
            raise RuntimeError('no table configured for this device')
        rows = self._table.get_size()[0]
        colnames = self._table.list_columns()
        cols = []
        for name in colnames:
            value_info = self._table.get_column_valueinfo(name)
            if value_info.readonly:
                cols.append((name, None))
            else:
                cols.append((name, self._value_type_from_info(value_info)))
        data = []
        for i in range(rows):
            await self.send_progress(request.connection, i/rows,
                                     'Reading table...')
            row_data = []
            for col in colnames:
                try:
                    value = self._table.get_cell(i, col)
                except zapf.Error as e:
                    raise RuntimeError('Error reading table cell '
                                       f'{i}, {col}: {e}') from None
                row_data.append(value)
            data.append(row_data)
        await self.send_progress(request.connection, 1)
        return Reply(request.connection, request.key, None,
                     'pilstable', {
                         'rows': rows,
                         'cols': cols,
                         'data': data,
                     })

    async def _write_table_cell(self, request):
        """Write a single cell in the table."""
        row, col = request.data['row'], request.data['col']
        self._table.set_cell(row, col, request.data['value'])
        new_value = self._table.get_cell(row, col)
        return Reply(request.connection, request.key, None,
                     'pilscell', {
                         'row': row,
                         'col': col,
                         'value': new_value,
                     })
