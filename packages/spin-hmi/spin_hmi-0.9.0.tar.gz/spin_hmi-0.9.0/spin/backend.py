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

"""Backend code for reading values and sending the updates to the frontend."""

import asyncio
import enum
import importlib
import json
import socket
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import mlzlog

from . import __version__
from .config import Config, Param


class State(str, enum.Enum):  # later: use StrEnum
    """Device states."""

    OK = 'ok'
    WARN = 'warn'
    BUSY = 'busy'
    DISABLED = 'disabled'
    ERROR = 'error'
    UNKNOWN = 'unknown'


@dataclass
class Update:
    """Poll event sent to all connected frontends."""

    key: str
    unit: str
    state: State
    state_str: str
    value: object

    def serialize(self):
        return json.dumps({
            'key': self.key,
            'unit': self.unit,
            'state': self.state.value,
            'state_str': self.state_str,
            'value': self.value,
        })


@dataclass
class Request:
    """Request from a frontend."""

    connection: object = field(repr=False)
    key: str
    transform: object
    action: str
    intent: str
    data: object

    @staticmethod
    def unserialize(connection, data):
        data = json.loads(data)
        return Request(connection,
                       data['key'],
                       data['transform'],
                       data['action'],
                       data['intent'],
                       data['data'])


@dataclass
class Reply:
    """Reply to a Request sent to a specific frontend."""

    connection: object
    key: str
    transform: object
    action: str
    data: object = None

    def serialize(self):
        return json.dumps({
            'key': self.key,
            'transform': self.transform,
            'action': self.action,
            'data': self.data,
        })


# maps Device URI schemes to the module that implements the device
BUILTIN_PROTOS = {
    'tango': 'spin.tango',
    'secop': 'spin.secop',
    'nicos': 'spin.nicos',
    'pils+ads': 'spin.pils',
    'pils+modbus': 'spin.pils',
    'pils+tango': 'spin.pils',
    'pils+sim': 'spin.pils',
}


class Backend:
    """Collection of polling tasks for the devices."""

    def __init__(self, loop, connections, log):
        self.log = log
        self._loop = loop
        self._connections = connections
        self._tasks = set()
        self._devices = {}
        self._last_updates = {}  # last update for each key
        self.protos = BUILTIN_PROTOS.copy()  # this can be extended by plugins

    def start(self, conf: Config, asset_list: list[Path]):
        for name, device in conf.devices.items():
            parsed = urlparse(device.device)
            if parsed.scheme not in self.protos:
                raise ValueError(f'{device.device}: unknown protocol')
            fixup_params(device)
            devcls = self.protos[parsed.scheme]
            if isinstance(devcls, str):
                # import the module if it's a string
                devcls = importlib.import_module(devcls).Device
            log = mlzlog.getLogger(parsed.scheme).getChild(name)
            dev = self._devices[name] = devcls(name, device, parsed, self, log)
            for asset in map(Path, dev.needed_assets()):
                if asset not in asset_list:
                    asset_list.append(asset)
            try:
                dev.init()
            except Exception as err:
                dev.log.exception('while initializing device: %r', err)

        self.run_task(self.periodic())

    def run_task(self, coro):
        task = self._loop.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def handle_request(self, request):
        devname = request.key.partition('.')[0]
        if not (dev := self._devices.get(devname)):
            self.log.warning('unknown device in request: %r', devname)
            return
        dev.log.debug('handling request: %r', request)
        try:
            reply = await dev.handle_request(request)
        except Exception as err:
            dev.log.exception('error handling request')
            exc_str = dev.format_exception(err)
            await self.send_reply(Reply(
                request.connection,
                request.key,
                request.transform,
                'error',
                f'Could not execute action: {exc_str}',
            ))
        else:
            if reply is not None:
                await self.send_reply(reply)

    async def send_reply(self, reply):
        """Send data to one connected websocket."""
        data = reply.serialize()
        try:
            await reply.connection.send_str(data)
        except ConnectionResetError:
            self.log.warning('error sending reply to %s', reply.connection)

    async def send_all_updates(self, conn):
        """Send all cached data to a new websocket."""
        for data in self._last_updates.values():
            await conn.send_str(data)

    async def send_update(self, update: Update):
        """Send data to all connected websockets."""
        data = update.serialize()
        self._last_updates[update.key] = data
        for conn in self._connections:
            try:
                await conn.send_str(data)
            except ConnectionResetError:
                pass  # socket is being closed down

    async def update_common_info(self):
        fqdn = socket.getfqdn()
        state = State.OK
        if fqdn.startswith('localhost'):
            state = State.WARN
        common = {
            'hostinfo': fqdn,
            'version': f'Connected to Spin {__version__}',
        }
        await self.send_update(Update('__common__', '', state, '', common))

    async def periodic(self):
        while True:
            await self.update_common_info()
            await asyncio.sleep(10)

    async def notify_restart(self):
        """Best-effort notification that the server is restarting."""
        for conn in self._connections:
            with suppress(Exception):
                await conn.send_str(Reply(None, '__common__',
                                          None, 'restart').serialize())


def fixup_params(devconf):
    new_list = []
    for param in devconf.params or []:
        paramcfg = Param(name=param) if not isinstance(param, Param) else param
        poll_every = max(paramcfg.pollinterval // devconf.pollinterval, 1) \
            if paramcfg.pollinterval else 1
        paramcfg.poll_every = poll_every
        new_list.append(paramcfg)
    devconf.params = new_list
