"""A little testing config."""

import hashlib
import os

from spin.config import Config, Device, Page, Param

config = Config()
config.server = '0.0.0.0:8000'
config.control_url = 'http://{host}:8080/'
config.plugins = ['plugin.py']
config.nav_bar = True

tg = 'tango://localhost:10000/test/sim'
sec = 'secop://localhost:10767'
nic = 'nicos://localhost/nicos'
plc = f'pils+sim://{os.path.dirname(__file__)}/plc.py'  # noqa: PTH120
config.devices = {
    'field': Device(device=f'{tg}/motor',
                    params=[Param('ramp', 5.0), 'target']),
    'coil_a': Device(device=f'{tg}/sensor'),
    'coil_b': Device(device=f'{tg}/sensor'),
    'coldhead_stage1': Device(device=f'{tg}/sensor'),
    'coldhead_stage2': Device(device=f'{tg}/sensor'),
    'fsm': Device(device=f'{tg}/digitaloutput'),
    'valve': Device(device=f'{tg}/discreteoutput',
                    confirm='Do not open the valve without proper training!'),
    'valvetext': Device(device=f'{tg}/discreteoutput', options={'enum': True}),
    'cryo_label': Device(device=f'{sec}/label'),
    'cryo_tc': Device(device=f'{sec}/tc1'),
    'cryo_ts': Device(device=f'{sec}/ts'),
    'cryo_switch': Device(device=f'{sec}/heatswitch', options={'enum': True}),
    'net_rx': Device(device=f'{nic}/net_rx'),
    'net_tx': Device(device=f'{nic}/net_tx'),
    'reactor': Device(device=f'{nic}/reactorpower'),
    'plc_mot': Device(device=f'{plc}#po32', params=['Speed', 'target'],
                      options={'table': 'table2'}),
    'plc_inp': Device(device=f'{plc}#di32', options={'enum': True}),
    'plugin': Device(device='demoplugin://some/device'),
}
config.pages = {
    'default': Page('default.html', title='Spin demo page'),
    'subpage': Page('default.html', title='Subpage', parent='default'),
    'locked':  Page('default.html', title='Locked subpage', parent='default',
                    auth=[('admin', hashlib.sha256(b'admin').hexdigest())]),
    'view':    Page('default.html', readonly=True, title='Spin demo (r/o)',
                    quick_icons=False),
    'table':   Page('table.html', title='PILS table'),
    'secret':  Page('secret.html', title='Very secret', hidden=True,
                    auth=[('admin', hashlib.sha256(b'admin').hexdigest()),
                          ('heiner', hashlib.sha256(b'heiner').hexdigest())]),
}
