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

"""Plugin for handling Lakeshore calibration curves."""

from typing import NamedTuple

from spin.backend import Reply, Request
from spin.device import BaseDevice
from spin.utils import decode_base64_file

try:
    import tango
    import tango.asyncio
except ImportError:
    tango = None

# Lakeshore curve lists (set 0 to not use one on the sensor)
# Lakeshore,    fixed,  user,   unused
# LS 211,       1-20,   21-21,  -
# LS 218,       1-9,    21-28,  10-20
# LS 224,       1-20,   21-59,  -
# LS 332,       1-20,   21-41,  -
# LS 335,       1-20,   21-59,  -
# LS 336,       1-20,   21-59,  -
# LS 340,       1-20,   21-60,  -
# LS 350,       1-20,   21-59,  -
# LS 372,       1-20,   21-59,  -

# Model -> (Max idx predef curve, Max idx user curve)
CURVES = {
    'MODEL211': (20, 21),
    'MODEL218': (9, 28),
    'MODEL218S': (9, 28),
    'MODEL224': (20, 59),
    'MODEL332': (20, 41),
    'MODEL335': (20, 59),
    'MODEL336': (20, 59),
    'MODEL340': (20, 60),
    'MODEL350': (20, 59),
    'MODEL372': (20, 59),
}

FORMAT = {
    1: 'mV/K',
    2: 'V/K',
    3: 'Ohm/K (linear)',
    4: 'log(Ohm)/K',
    5: 'log(Ohm)/log(K)',
    7: 'Ohm/K (cubic spline)',
}

COEFFICIENT = {
    1: 'negative',
    2: 'positive',
}

HEADER_FIELDS = {
    'sensor model': 'name',
    'serial number': 'serial',
    'data format': 'fmt',
    'setpoint limit': 'limit',
    'temperature coefficient': 'coeff',
    # number of breakpoints
}

# TODO: only wait 0.05s or longer to be safe for the polling?
WAIT_TIME = 0.05


def to_340_file(curve, points):
    # TODO: Sensor Model is name?, spacing
    out = f'Sensor Model: {curve.name}\n'
    out += f'Serial Number: {curve.serial}\n'
    out += f'Data Format: {curve.fmt}\n'
    out += f'SetPoint Limit: {curve.limit}\n'
    out += f'Temperature coefficient: {curve.coeff}\n'
    out += f'Number Of Breakpoints: {len(points)}\n'
    out += '\n No.  Units    Temperature (K)\n\n'
    for i, point in enumerate(points):
        unit, temp = point.split(',')
        out += f'{i+1:>3} {unit:>6}    {temp:>6}\n'
    return out


def from_340_file(idx, file):
    points = []
    fields = {'idx': idx}
    for line in file.splitlines():
        if not line:
            continue
        if ':' in line:
            key, value = line.split(':')
            key = key.strip().lower()
            if key in HEADER_FIELDS:
                fields[HEADER_FIELDS[key]] = value.strip()
        else:
            if line.strip().lower().startswith('no.'):
                continue
            i, x, y = line.split()
            points.append((int(i), x, y))
    try:
        curve = Curve(**fields)
    except TypeError as e:
        raise ValueError('.340 file header does not contain all expected '
                         'fields') from e
    return curve, points


class Curve(NamedTuple):
    """Represents a Lakeshore curve header."""

    idx: int
    name: str
    serial: str
    fmt: int
    limit: float
    coeff: float

    def to_dict(self):
        res = self._asdict()
        coeff = res['coeff']
        res['coeff'] = COEFFICIENT.get(coeff, coeff)
        fmt = res['fmt']
        res['fmt'] = FORMAT.get(fmt, fmt)
        return res

    def to_str(self):
        return (f'{self.idx},{self.name},{self.serial},'
                f'{self.fmt},{self.limit},{self.coeff}')


def parse_curve(idx, curve):
    curve = curve.removeprefix('CRVHDR ')
    name, serial, fmt, limit, coeff = curve.split(',')  # TODO: comma in name?
    return Curve(idx, name.strip(), serial.strip(),
                 int(fmt), float(limit), int(coeff))


class LakeshoreCurveDeviceTango(BaseDevice):
    # pylint: disable=abstract-method
    """Lakeshore Curve Up- and Download."""

    # TODO: DOCUMENT!

    _comm = None

    def init(self):
        if not tango:
            raise RuntimeError('PyTango is required to use this plugin')
        self.run_task(self._setup())

    async def _setup(self):
        self.log.info('setting up connection for lakeshore plugin')
        self._comm = await tango.asyncio.DeviceProxy(
                self._devconf.device.replace('lsfile+tango', 'tango'))

    async def _communicate(self, msg):
        return (await self._comm.command_inout('MultiCommunicate',
                                               [[-WAIT_TIME], [msg]]))[0]

    async def _tell(self, msg):
        await self._comm.command_inout('MultiCommunicate',
                                       [[WAIT_TIME], [msg]])

    async def handle_request(self, request: Request):
        if request.action == 'scan':
            self.run_task(self._read_headers(request.connection))
        elif request.action == 'download':
            self.run_task(self._download_curve(request.connection,
                                               request.data))
        elif request.action == 'upload':
            self.run_task(
                self._update_curve(request.connection,
                                   request.data['idx'],
                                   request.data['contents']),
            )
        else:
            self.log.warning('got unknown request %r', request)

    async def _read_headers(self, conn):
        async with self.error_guard(
                conn, msg='Error during curve scanning:', reset_progress=True):
            self.log.info('scanning headers')
            await self.send_progress(conn, 0, 'Scanning curves...')
            await self.send_reply(Reply(conn, self._name, None,
                                        'plugin-lakeshore',
                                        {'reason': 'reset'}))
            model = (await self._communicate('*IDN?')).split(',')[1]
            # TODO: error when unknown device
            max_predef, max_user = CURVES.get(model, (0, 0))
            curves_to_scan = [*range(1, max_predef+1), *range(21, max_user+1)]
            for i, curve_idx in enumerate(curves_to_scan):
                response = await self._communicate(f'CRVHDR? {curve_idx}')
                curve = parse_curve(curve_idx, response)
                data = {
                    'reason': 'curve-found',
                    'curve': curve.to_dict(),
                }
                await self.send_reply(Reply(conn, self._name, None,
                                            'plugin-lakeshore', data))
                await self.send_progress(conn, (i+1) / len(curves_to_scan),
                                         'Scanning curves...')
            self.log.info('scanning headers done')

    async def _download_curve(self, conn, curveidx):
        async with self.error_guard(conn, msg='Error downloading curve:'):
            points = []
            self.log.info('downloading curve %d', curveidx)
            await self.send_progress(conn, 0, 'Reading curves from lakeshore')
            curve = parse_curve(curveidx,
                                await self._communicate(f'CRVHDR? {curveidx}'))
            for i in range(1, 201):
                response = await self._communicate(f'CRVPT? {curveidx},{i}')
                await self.send_progress(conn, i/200,
                                         f'Reading point {i} from lakeshore')
                point = (*map(float, response.split(',')[:2]),)
                if point == (0.0, 0.0):
                    await self.send_progress(conn, 1)
                    break
                points.append(response)
            file = to_340_file(curve, points)
            data = {
                'reason': 'curve-ready',
                'curve': curveidx,
                'curvename': curve.name,
                'file': file,
            }
            await self.send_reply(Reply(conn, self._name, None,
                                        'plugin-lakeshore', data))
            self.log.info('downloading curve done')

    async def _update_curve(self, conn, idx, file):
        async with self.error_guard(
                conn, msg='Error while uploading curve:', reset_progress=True):
            decoded = decode_base64_file(file).decode('utf-8')
            curve, points = from_340_file(idx, decoded)
            self.log.info('updating curve %d', idx)
            total = len(points) + 1
            await self.send_progress(conn, 0, f'Uploading curve: 0/{total}')
            await self._tell(f'CRVHDR {curve.to_str()}')
            for (i, x, y) in points:
                await self._tell(f'CRVPT {idx},{i},{x},{y}')
                await self.send_progress(conn, i/total,
                                         f'Uploading curve: {i}/{total}')
            await self._tell(f'CRVPT {idx},{total},0.0,0.0')
            await self.send_progress(conn, 1)
            self.log.info('updating curve done')


def init_plugin(_conf, _loop):
    return {
        'protos': {
            'lsfile+tango': LakeshoreCurveDeviceTango,
        },
        'assets': ['lakeshore.js', 'lakeshore.css'],
    }
