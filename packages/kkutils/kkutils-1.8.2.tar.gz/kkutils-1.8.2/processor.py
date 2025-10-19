#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Last modified: 2020-06-29 10:18:14
'''

import asyncio
import inspect
import sys
import time
from concurrent.futures._base import CancelledError
from datetime import timedelta
from functools import partial
from importlib import import_module
from inspect import isclass
from signal import SIGINT, SIGTERM

import uvloop
from utils import Config, Dict, Logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Processor:

    def __init__(self, **kwargs):
        self.opt = Dict(kwargs)
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.result = asyncio.Queue()
        self.logger = Logger()
        self.start_time = None
        self.time_anchor = None
        if hasattr(self, 'init'):
            ret = self.init()
            if inspect.isawaitable(ret):
                self.loop.run_until_complete(ret)

    async def producer(self):
        raise NotImplementedError

    async def consumer(self, args):
        raise NotImplementedError

    async def collector(self):
        raise NotImplementedError

    def _log_stats(self):
        qsize = self.queue.qsize()
        if self.time_anchor is None:
            self.start_time = time.time()
            self.time_anchor = qsize, time.time()
        else:
            total_consumed = int(time.time() - self.start_time)
            time_consumed = int(time.time() - self.time_anchor[1])
            data_consumed = self.time_anchor[0] - qsize
            if time_consumed != 0 and data_consumed != 0:
                speed = data_consumed / time_consumed
                eta = int(qsize / speed)
                if time_consumed >= 60:
                    self.time_anchor = qsize, time.time()
                self.logger.info(f'queue size: {qsize}, speed: {speed:.2f} it/s, '
                                 f'consumed: {timedelta(seconds=total_consumed)}, '
                                 f'eta: {timedelta(seconds=eta)}')

    async def _consumer(self):
        while True:
            try:
                args = await self.queue.get()
                self._log_stats()
                if isinstance(args, (tuple, list)):
                    ret = await self.consumer(*args)
                else:
                    ret = await self.consumer(args)
                if ret is not None:
                    await self.result.put(ret)
                self.queue.task_done()
            except CancelledError:
                return self.logger.error('Cancelled consumer')
            except Exception as e:
                self.logger.exception(e)
                self.queue.task_done()

    async def finish(self):
        if self.result.qsize() > 0:
            await self.collector()

    async def shutdown(self, sig):
        self.logger.warning(f'received signal {sig.name}')
        self.loop.stop()

    def start(self):
        for sig in (SIGINT, SIGTERM):
            self.loop.add_signal_handler(sig, partial(self.loop.create_task, self.shutdown(sig)))

        for _ in range(self.opt.workers):
            self.loop.create_task(self._consumer())

        if self.opt.forever:
            self.loop.create_task(self.producer())
            self.loop.run_forever()
        else:
            self.loop.run_until_complete(self.producer())
            self.loop.run_until_complete(self.queue.join())
            self.loop.run_until_complete(self.finish())


def main():
    kwargs = Config(dict(workers=10, forever=False))
    arr = sys.argv[1].split('.')
    module = import_module(arr[0])
    if len(arr) == 1:
        items = list(module.__dict__.items())
        for k, v in items:
            if isclass(v) and any([x.__module__ == 'processor' and x.__name__ == 'Processor' for x in v.__bases__]):
                app = v(**kwargs)
                app.start()
    else:
        app = getattr(module, arr[1])(**kwargs)
        app.start()


if __name__ == '__main__':
    main()
