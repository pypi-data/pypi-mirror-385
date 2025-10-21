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

"""Backend server."""

import argparse
import asyncio
import html
import signal
import socket
import sys
from hashlib import sha256
from pathlib import Path

import mlzlog
from aiohttp import BasicAuth, WSMsgType, hdrs, web

from .backend import Backend, Request
from .config import config_watcher, get_config
from .utils import error_fallback, extract_addr

ASSET_DIR = Path(__file__).parent / 'assets'

# Add provisions for development usage
rootdir = Path(__file__).parent.parent.resolve()
if (rootdir / '.git').exists():  # noqa: SIM108
    default_cfgdir = rootdir / 'demo'
else:  # pragma: no cover
    default_cfgdir = Path('/etc/spin')


def sanitize_path(path):
    """Make sure that the given path is a safe relative path."""
    path = Path(path)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f'invalid path {path}')
    return path


class SiteHandler:
    """Handlers for Http and Websocket connections."""

    def __init__(self, conf, conf_root, log):
        self.log = log
        self.connections = set()
        self._asset_root = ASSET_DIR
        self._conf_root = conf_root
        self._conf = conf
        self._backend = None
        self.builtin_assets = [  # can be extended by backends
            Path('pico.min.css'),
            Path('keyboard.css'),
            Path('spin.css'),
            Path('sprintf.js'),
            Path('keyboard.js'),
            Path('filesaver.js'),
            Path('luxon.js'),
            Path('hammer.js'),
            Path('chart.js'),
            Path('chart-luxon.js'),
            Path('chart-timestack.js'),
            Path('chart-zoom.js'),
            # spin.js is implicit and must be last
        ]
        self.plugin_assets = []  # filled by load_plugins() below

    def set_backend(self, backend):
        self._backend = backend

    def handle_auth(self, request, creds):
        if hdr := request.headers.get(hdrs.AUTHORIZATION):
            try:
                auth = BasicAuth.decode(hdr)
            except ValueError:
                pass
            else:
                cred = (auth.login, sha256(auth.password.encode()).hexdigest())
                if cred in creds:
                    return
        raise web.HTTPUnauthorized(headers={'WWW-Authenticate': 'Basic'})

    def generate_nav(self, cur_page):
        cur_parent = self._conf.pages[cur_page].parent
        nav = ['<nav><ul>']
        # if the current page has a parent, add a "back" link
        if cur_parent:
            parent_conf = self._conf.pages.get(cur_parent)
            if parent_conf and not parent_conf.hidden:
                title = html.escape(parent_conf.title or cur_parent)
                nav.append('<li class="item">'
                           f'<a href="{cur_parent}">&larr; {title}</a></li>')
        children = []
        for page, pageconf in self._conf.pages.items():
            if pageconf.hidden:
                continue
            icon = '<img src="s/locked.svg">' if pageconf.auth else ''
            title = html.escape(pageconf.title or page)
            if page == cur_page:
                nav.append(f'<li class="active item">{icon}{title}</li>')
            else:
                navitem = ('<li class="item">'
                           f'<a href="{page}">{icon}{title}</a></li>')
                # only show pages on the same level
                if pageconf.parent == cur_parent:
                    nav.append(navitem)
                # or children of the current page
                elif pageconf.parent == cur_page:
                    children.append(navitem)
        if children:
            nav.append('<li class="sep">|</li>')
            nav.extend(children)
        nav.append('</ul><ul>'
                   '<li class="clock"><span id="nav-clock"></span></li>'
                   '<li class="logo"><img src="s/mlz.svg"></li>'
                   '</ul></nav>')
        return ''.join(nav)

    async def page(self, request):
        page = request.match_info.get('page', 'default')
        pageconf = self._conf.pages.get(page)
        if not pageconf:
            raise web.HTTPNotFound
        if pageconf.auth:
            self.handle_auth(request, pageconf.auth)
        self.log.info('[%s] serving page %r', request.remote, page)

        # master template
        template = (self._asset_root / 'page.html').read_text()

        # assets
        js = ''.join(f'    <script src="s/{fn}"></script>\n'
                     for fn in self.builtin_assets if fn.suffix == '.js')
        # plugin assets get a numbered "subdirectory" to avoid name clashes
        js += ''.join(f'    <script src="p/{i}/{fn.name}"></script>\n'
                      for i, fn in enumerate(self.plugin_assets)
                      if fn.suffix == '.js')
        jsname = Path(pageconf.file).with_suffix('.js')
        if (self._conf_root / jsname).is_file():
            js += f'    <script src="c/{jsname}"></script>\n'

        cs = ''.join(f'    <link rel="stylesheet" href="s/{fn}">\n'
                     for fn in self.builtin_assets if fn.suffix == '.css')
        cs += ''.join(f'    <link rel="stylesheet" href="p/{i}/{fn.name}">\n'
                      for i, fn in enumerate(self.plugin_assets)
                      if fn.suffix == '.css')
        cssname = Path(pageconf.file).with_suffix('.css')
        if (self._conf_root / cssname).is_file():
            cs += f'<link rel="stylesheet" href="c/{cssname}">'
        template = template.replace('{{JS}}', js).replace('{{CSS}}', cs)

        # main page content
        content = (self._conf_root / pageconf.file).read_text()
        template = template.replace('{{CONTENT}}', content)

        # navigation bar
        show_nav = pageconf.nav_bar
        if show_nav is None:
            show_nav = self._conf.nav_bar and not pageconf.hidden
        if show_nav:
            template = template.replace('{{NAVBAR}}', self.generate_nav(page))
        else:
            template = template.replace('{{NAVBAR}}', '')

        # quick bar
        show_quick = pageconf.quick_icons
        if show_quick is None:
            show_quick = self._conf.quick_icons
        if show_quick:
            template = template.replace('{{QUICKSTYLE}}', '')
        else:
            template = template.replace('{{QUICKSTYLE}}', 'display: none')

        # further template replacements
        if url := self._conf.control_url:
            template = template.replace('{{CONTROL}}', url)
            template = template.replace('{{CONTROL_DISPLAY}}', 'inline')
        else:
            template = template.replace('{{CONTROL}}', '')
            template = template.replace('{{CONTROL_DISPLAY}}', 'none')
        template = template.replace('{{THEME}}', 'dark'
                                    if self._conf.dark_theme else 'light')
        template = template.replace('{{READONLY}}',
                                    str(pageconf.readonly).lower())
        template = template.replace('{{WITHAUTH}}',
                                    str(bool(pageconf.auth)).lower())
        hostname = socket.getfqdn().split('.')[0]
        title = f'{hostname}: {pageconf.title or page}'
        template = template.replace('{{TITLE}}', html.escape(title))

        return web.Response(text=template, content_type='text/html')

    async def static(self, request):
        subpath = sanitize_path(request.match_info['file'])
        if request.match_info['path'] == 's':
            filepath = self._asset_root / subpath
        elif request.match_info['path'] == 'p':
            try:
                filepath = self.plugin_assets[int(subpath.parts[0])]
            except (ValueError, IndexError):
                self.log.warning('[%s] invalid plugin asset name %s',
                                 request.remote, subpath)
                raise web.HTTPNotFound from None
        elif request.match_info['path'] == 'c':
            filepath = self._conf_root / subpath
        else:
            raise web.HTTPNotFound
        self.log.info('[%s] serving %s', request.remote, filepath)
        if filepath.is_file():
            return web.FileResponse(filepath)
        self.log.warning('[%s] %s not found', request.remote, filepath)
        raise web.HTTPNotFound

    async def ws(self, request):
        ws = web.WebSocketResponse()
        self.log.info('[%s] [ws] connection accepted', request.remote)
        await ws.prepare(request)

        try:
            await self._backend.send_all_updates(ws)
        except OSError as err:
            self.log.warning('[%s] [ws] connection error during initial '
                             'update: %s', request.remote, err)
            return

        self.connections.add(ws)
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    req_msg = Request.unserialize(ws, msg.data)
                    self.log.info('got request: %r', req_msg)
                    await self._backend.handle_request(req_msg)
                except Exception:
                    self.log.exception('[%s] [ws] error handling data %r',
                                       request.remote, msg.data)
            elif msg.type == WSMsgType.ERROR:
                self.log.warning('[%s] [ws] connection closed with error %s',
                                 request.remote, ws.exception())

        self.log.info('[%s] [ws] connection closed', request.remote)
        self.connections.discard(ws)
        return ws


def init_app(handler):
    """Set up the aiohttp application and routes."""
    app = web.Application()
    app.router.add_get('/', handler.page, name='default_page')
    app.router.add_get('/ws', handler.ws, name='websocket')
    app.router.add_get(r'/{page:\w+}', handler.page, name='page')
    app.router.add_get(r'/{path:[spc]}/{file:[/\w.-]+}', handler.static,
                       name='static')
    return app


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Start Spin daemon.')
    parser.add_argument('-c', dest='confdir', action='store',
                        type=Path, default=default_cfgdir,
                        help='configuration directory (default '
                        f'{default_cfgdir})')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='enable debug logging')
    return parser.parse_args(argv)


def load_plugins(args, conf, loop, handler, backend):
    for path in conf.plugins:
        pluginpath = Path(path)
        try:
            if pluginpath.suffix == '':
                # builtin plugin
                mod = __import__(f'spin.plugins.{path}', None, None, ['*'])
                namespace = mod.__dict__
                pluginpath = Path(__file__).parent / 'plugins' / f'{path}'
            else:
                pluginpath = args.confdir / pluginpath
                namespace = {'__file__': str(pluginpath)}
                # pylint: disable=exec-used
                exec(pluginpath.read_bytes(), namespace)  # noqa: S102
        except Exception as err:  # noqa: BLE001
            mlzlog.log.error('could not load plugin %s: %s', path, err)
            continue
        try:
            res = namespace['init_plugin'](conf, loop)
        except Exception as err:  # noqa: BLE001
            mlzlog.log.error('could not initialize plugin %s: %s', path, err)
            continue
        if 'protos' in res:
            backend.protos.update(res['protos'])
        if 'assets' in res:
            plugindir = pluginpath if pluginpath.is_dir() else pluginpath.parent
            handler.plugin_assets.extend(
                plugindir / a for a in res.get('assets', []))


def main():
    """Run the spin service (backend and HTTP) until interrupted."""
    args = parse_args(sys.argv[1:])
    rootlevel = 'debug' if args.verbose else 'info'
    # log to stdout, as a daemon it goes to journal anyway
    mlzlog.initLogging('spin', rootlevel, logdir=None,
                       tracebacks_on_console=args.verbose)

    conf = get_config(args)
    loop = asyncio.get_event_loop()
    exitstatus = [0]

    handler = SiteHandler(conf, args.confdir, mlzlog.getLogger('handler'))
    backend = Backend(loop, handler.connections, mlzlog.getLogger('backend'))
    handler.set_backend(backend)

    load_plugins(args, conf, loop, handler, backend)

    # handle signals to stop completely
    def stop_everything(sig):
        mlzlog.log.info('stopping due to %s', sig)
        for task in asyncio.all_tasks(loop):
            task.cancel()
    loop.add_signal_handler(signal.SIGINT, stop_everything, 'SIGINT')
    loop.add_signal_handler(signal.SIGTERM, stop_everything, 'SIGTERM')
    loop.set_exception_handler(error_fallback)

    # handle configuration change by a graceful reload on the frontends
    async def stop_and_restart():
        await backend.notify_restart()
        stop_everything('config change')
        exitstatus[0] = 3
    loop.create_task(config_watcher(args, stop_and_restart))  # noqa: RUF006

    def print_to_log(s):
        # in the initial "Running on ..." message, cut the "Ctrl-C" second line
        mlzlog.log.info(s.splitlines()[0])

    backend.start(conf, handler.builtin_assets)
    app = init_app(handler)
    host, port = extract_addr(conf.server, 8000)
    try:
        web.run_app(app, host=host, port=port, loop=loop, handle_signals=False,
                    print=print_to_log)
    except asyncio.CancelledError:
        mlzlog.log.info('server stopped')
    sys.exit(exitstatus[0])
