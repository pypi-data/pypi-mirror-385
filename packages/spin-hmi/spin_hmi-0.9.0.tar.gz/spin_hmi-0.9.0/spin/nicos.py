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

"""Readonly NICOS backend."""

import re
from ast import (
    Add,
    BinOp,
    Call,
    Constant,
    Dict,
    List,
    Name,
    Set,
    Sub,
    Tuple,
    UnaryOp,
    USub,
    parse,
)

from .backend import State
from .device import AsyncUpdateDevice
from .utils import StreamConnection

DEFAULT_CACHE_PORT = 14869

OP_TELL = '='
OP_ASK = '?'
OP_WILDCARD = '*'
OP_SUBSCRIBE = ':'
OP_UNSUBSCRIBE = '|'
OP_TELLOLD = '!'
OP_LOCK = '$'
OP_REWRITE = '~'
END_MARKER = '###'

OPKEYS = OP_TELL + OP_ASK + OP_WILDCARD + OP_SUBSCRIBE + OP_UNSUBSCRIBE + \
    OP_TELLOLD + OP_LOCK + OP_REWRITE


# regular expression matching a cache protocol message
# pylint: disable=consider-using-f-string
msg_pattern = re.compile(fr'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?                   # timestamp
      \s* (?P<ttlop>[+-]?)                       # ttl operator
      \s* (?P<ttl>\d+\.?\d*(?:[eE][+-]?\d+)?)?   # ttl
      \s* (?P<tsop>@)                            # timestamp mark
    )?
    \s* (?P<key>[^{OPKEYS}]*?)                     # key
    \s* (?P<op>[{OPKEYS}])                        # operator
    \s* (?P<value>[^\r\n]*?)                     # value
    \s* $
    ''', re.VERBOSE)


STATE_MAP = {
    200: State.OK,
    210: State.WARN,
    220: State.BUSY,
    230: State.ERROR,  # NOTREACHED
    235: State.DISABLED,
    240: State.ERROR,
    999: State.UNKNOWN,
}


_safe_names = {'None': None, 'True': True, 'False': False,
               'inf': float('inf'), 'nan': float('nan')}


def ast_eval(node):
    # copied from Python 2.7 ast.py, but added support for float inf/-inf/nan
    def _convert(node):
        if isinstance(node, Constant):
            return node.value
        if isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        if isinstance(node, List):
            return list(map(_convert, node.elts))
        if isinstance(node, Dict):
            return {_convert(k): _convert(v) for k, v
                    in zip(node.keys, node.values)}
        if isinstance(node, Set):
            return frozenset(map(_convert, node.elts))
        if isinstance(node, Name) and node.id in _safe_names:
            return _safe_names[node.id]
        if isinstance(node, UnaryOp) and \
           isinstance(node.op, USub) and \
           isinstance(node.operand, Name) and \
           node.operand.id in _safe_names:
            return -_safe_names[node.operand.id]
        if isinstance(node, UnaryOp) and \
           isinstance(node.op, USub) and \
           isinstance(node.operand, Constant):
            return -node.operand.value
        if isinstance(node, BinOp) and \
           isinstance(node.op, (Add, Sub)) and \
           isinstance(node.right, Constant) and \
           isinstance(node.right.value, complex) and \
           isinstance(node.left, Constant) and \
           isinstance(node.left.value, (int, float)):
            left = node.left.value
            right = node.right.value
            if isinstance(node.op, Add):
                return left + right
            return left - right
        if isinstance(node, Call) and \
           isinstance(node.func, Name) and \
           node.func.id == 'cache_unpickle':
            return None  # we don't support pickled values
        raise ValueError(f'malformed literal string with {node}')
    return _convert(node)


def cache_load(entry):
    try:
        # parsing with 'eval' always gives an ast.Expression node
        expr = parse(entry, mode='eval').body
        return ast_eval(expr)
    except Exception as err:
        raise ValueError(
            f'corrupt cache entry: {entry!r} ({err})') from err


class NicosCache(StreamConnection):
    """Device representing a NICOS cache connection."""

    default_port = DEFAULT_CACHE_PORT

    async def _synchronize(self):
        self.log.info('connected to cache')
        await self._send(f'@{OP_WILDCARD}\n@{OP_SUBSCRIBE}\n'
                         f'{END_MARKER}{OP_ASK}'.encode())
        end = f'{END_MARKER}{OP_TELLOLD}\n'
        unseen = set(self.devices)
        updates = []
        devs = set()
        while True:
            line = await self._receive()
            if line == end:
                break
            msg = self._decode(line)
            if msg[4].endswith('/unit'):
                if (valuekey := msg[4][:-5] + '/value') in self.devices:
                    for dev in self.devices[valuekey]:
                        dev.set_unit(cache_load(msg[6]))
            elif msg[4] in self.devices:  # cache updates until units set
                updates.append(msg)
            unseen.discard(msg[4])
        for key in unseen:
            for dev in self.devices[key]:
                dev.log.error('key %s not present in cache', key)
                await dev.send(State.ERROR,
                               'Device not present in NICOS cache')
        for msg in updates:
            for dev in self.devices[msg[4]]:
                if dev not in devs:
                    devs.add(dev)
                    dev.log.info('device got initial update')
            await self._handle_message(msg)

    def _decode(self, line):
        return msg_pattern.match(line).groups()

    async def _handle_message(self, msg):
        *_, key, op, value = msg
        if key not in self.devices:
            return
        value = cache_load(value) if value else None
        for dev in self.devices[key]:
            await dev.update(key, op, value)

    def add_device(self, device):
        key = device.device
        self.devices[f'{key}/value'].append(device)
        # we always want the status
        self.devices[f'{key}/status'].append(device)
        for par in device.extra_params or []:
            self.devices[f'{key}/{par}'].append(device)


class Device(AsyncUpdateDevice):
    """Abstraction for NICOS devices.

    Device url should look like: 'nicos://<host>:[<port>]/<device>',
    with devicepath being the devices slash-separated name in the nicos cache.
    If host is not given, the default NICOS cache port is used.
    """

    _connclass = NicosCache

    def set_unit(self, unit):
        self._unit = unit

    async def update(self, key, op, value):
        _, _, param = key.rpartition('/')
        if op == OP_TELL:
            if param == 'status':
                nicos_state, state_str = value
                state = STATE_MAP.get(nicos_state, State.UNKNOWN)
                self.cache['status'] = (state, state_str)
                await self.send(state, state_str, self.cache['value'])
            elif param == 'value':
                self.cache['value'] = value
                state, state_str = self.cache['status']
                await self.send(state, state_str, value)
            else:
                self.cache[param] = value
                state, state_str = self.cache['status']
                await self.send_param(param, value, '')
        elif op == OP_TELLOLD and param == 'status':
            self.cache['status'] = (State.UNKNOWN, 'expired')
            await self.send(State.UNKNOWN, 'expired', self.cache['value'])

    async def handle(self, request):
        raise NotImplementedError('NICOS devices cannot be used interactively')
