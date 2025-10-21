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

"""Config handling logic."""

import asyncio
from dataclasses import dataclass, field


@dataclass
class Param:
    """Configuration for one parameter to be polled."""

    name: str
    # None means to use the device's default
    pollinterval: float = None
    # set internally
    poll_every: int = 1


@dataclass
class Device:
    """Configuration for one device to be polled."""

    device: str
    pollinterval: float = 1.0
    params: list = None
    confirm: str = None
    options: dict = field(default_factory=dict)


@dataclass
class Page:
    """Configuration for a page served by the frontend."""

    file: str
    title: str = None
    auth: list[tuple] = None
    hidden: bool = False
    readonly: bool = False
    nav_bar: bool = None
    quick_icons: bool = True
    parent: str = None


@dataclass
class Config:
    """The main configuration."""

    server: str = 'localhost:8000'
    plugins: list[str] = field(default_factory=list)
    control_url: str = None
    devices: dict[str, Device] = None
    pages: dict[str, Page] = None
    dark_theme: bool = False
    nav_bar: bool = False
    quick_icons: bool = True


def get_config(args):
    conffile = args.confdir / 'conf.py'
    namespace = {'__file__': str(conffile)}
    code = conffile.read_bytes()
    exec(code, namespace)  # pylint: disable=exec-used  # noqa: S102
    return namespace['config']


async def config_watcher(args, callback):
    """Watch the configuration file for changes."""
    conffile = args.confdir / 'conf.py'
    last_mtime = conffile.stat().st_mtime
    while True:
        await asyncio.sleep(1)
        try:
            mtime = conffile.stat().st_mtime
        except OSError:
            pass
        else:
            if mtime != last_mtime:
                return await callback()
