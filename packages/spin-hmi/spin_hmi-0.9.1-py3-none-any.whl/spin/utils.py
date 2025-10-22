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

"""Various utils."""

import asyncio
import base64
import socket
from collections import defaultdict

import mlzlog

from spin.backend import State


def error_fallback(_loop, context):
    """Fallback exception handler."""
    msg = 'Uncaught exception in Task'
    if (f := context.get('future')) is not None:
        funcname = f.get_coro().__qualname__
        msg += f' "{f.get_name()}" running function {funcname}()'
    mlzlog.log.error(msg, exc_info=context.get('exception'))


def decode_base64_file(b64):
    contents = b64.removeprefix('data:application/octet-stream;base64,')
    return base64.b64decode(contents)


def extract_addr(addr, defaultport=None):
    """Extract host and port from a host:port string."""
    if ':' in addr:
        host, port = addr.split(':', 1)
        if not port.isdigit():
            raise ValueError(f'Invalid port number: {port}')
        return host, int(port)
    if defaultport is None:
        raise ValueError('No port specified and no default port provided')
    return addr, defaultport


class StreamConnection:
    """Base class for line-based protocol connections."""

    default_port = None

    def __init__(self, addr, log):
        self.log = log
        self.addr = addr
        self.devices = defaultdict(list)
        self.conn_write = None
        self.conn_read = None
        self.is_initialized = False

    async def _send(self, msg):
        self.conn_write.write(msg + b'\n')
        await self.conn_write.drain()

    async def _receive(self):
        msg = await self.conn_read.readuntil(b'\n')
        return msg.decode('utf-8')

    async def _open_connection(self):
        """Open the socket connection."""
        host, port = extract_addr(self.addr, self.default_port)
        reader, writer = await asyncio.open_connection(host, port,
                                                       family=socket.AF_INET)
        self.conn_read = reader
        self.conn_write = writer

    async def _synchronize(self):
        raise NotImplementedError

    async def _handle_message(self, msg):
        """Handle incoming messages - protocol specific."""
        raise NotImplementedError

    def add_device(self, device):
        """Add a device to be managed by this connection."""
        raise NotImplementedError

    def _decode(self, line):
        """Protocol-specific line handling."""
        raise NotImplementedError

    async def run(self):
        """Run the main connection loop with retry logic."""
        sleep = 1
        while True:
            self.is_initialized = False
            try:
                await self._open_connection()
                await self._synchronize()
            except Exception as e:
                self.log.exception('initializing connection')
                for devs in self.devices.values():
                    for dev in devs:
                        await dev.send(State.ERROR, f'Error in init: {e}')
                await asyncio.sleep(sleep)
                sleep = min(30, sleep * 1.53)
                continue
            self.is_initialized = True

            self.log.info('handling regular updates')
            while True:
                try:
                    line = await self._receive()
                    await self._handle_message(self._decode(line))
                except Exception as e:
                    self.log.exception('handling message')
                    for devs in self.devices.values():
                        for dev in devs:
                            await dev.send(State.ERROR,
                                           f'Error in connection: {e}')
                    sleep = 1
                    break
