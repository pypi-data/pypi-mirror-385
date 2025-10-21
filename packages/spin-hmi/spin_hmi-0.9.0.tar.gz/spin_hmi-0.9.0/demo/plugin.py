# pylint: skip-file

import asyncio
import random

from spin.backend import Reply, Request, State
from spin.device import BaseDevice


class PluginDevice(BaseDevice):
    """A demo plugin device for testing purposes."""

    def init(self):
        self.run_task(self._poll())

    async def _poll(self):
        self.log.info('plugin device polling')
        while True:
            await self.send(State.OK, 'ok', random.random())
            await asyncio.sleep(1)

    async def handle_request(self, request: Request):
        if request.action == 'click' and request.intent == 'set':
            self.run_task(self._update(request.connection))
            return Reply(request.connection, request.key, request.transform,
                         'demoplugin-notify', 'working...')
        return None

    async def _update(self, conn):
        self.log.info('starting update')
        for i in range(101):
            label = 'Herding llamas...'
            if i > 30:
                label = 'Reticulating splines...'
            if i > 70:
                label = 'Almost there...'
            await self.send_progress(conn, i/100, label)
            await asyncio.sleep(random.random() / 10)  # Simulate some work
        self.log.info('update done')
        await self.send_reply(Reply(conn, self._name, None,
                                    'demoplugin-notify', 'success!'))


def init_plugin(_conf, _loop):
    return {
        'protos': {'demoplugin': PluginDevice},
        'assets': ['plugin-notify.js', 'plugin.css'],
    }
