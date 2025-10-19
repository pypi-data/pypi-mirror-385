#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tornado Blueprint蓝图的实现。"""

import asyncio
import collections
import inspect
import os
from concurrent.futures import ThreadPoolExecutor

import tornado.netutil
import tornado.process
import tornado.web
from tornado.options import define, options
from utils import Cache, Dict, Logger, get_ip

__all__ = ['Blueprint', 'Application']

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except Exception:
    pass


class BlueprintMeta(type):
    derived_class = []

    def __new__(cls, name, bases, attr):
        _class = super(BlueprintMeta, cls).__new__(cls, name, bases, attr)
        cls.derived_class.append(_class)
        return _class

    @classmethod
    def register(cls, app):
        for _class in cls.derived_class:
            for blueprint in _class.blueprints:
                app.register(blueprint)


class Blueprint(metaclass=BlueprintMeta):
    blueprints = []

    def __init__(self, name=None, url_prefix='/', host='.*', strict_slashes=False):
        self.name = name
        self.host = host
        self.rules = []
        self.url_prefix = url_prefix
        self.strict_slashes = strict_slashes
        self._events = collections.defaultdict(list)
        self.blueprints.append(self)

    def route(self, uri, params=None, name=None):
        def decorator(handler):
            assert uri[0] == '/'
            rule_name = name or handler.__name__
            if self.name:
                rule_name = f'{self.name}.{rule_name}'
            if rule_name in [x[-1] for x in self.rules]:
                rule_name = None
            rule_uri = self.url_prefix.rstrip('/') + uri
            self.rules.append((rule_uri, handler, params, rule_name))
            if not self.strict_slashes and rule_uri.endswith('/'):
                self.rules.append(
                    (rule_uri.rstrip('/'), handler, params, None))
            return handler
        return decorator

    def listen(self, event):
        def decorater(func):
            self._events[event].append(func)
        return decorater


class Application(Blueprint):

    define('debug', default=True, type=bool)
    define('port', default=8000, type=int)
    define('workers', default=10, type=int)

    def __init__(self, name=None, url_prefix='/', host='.*', strict_slashes=False, **kwargs):
        super().__init__(name, url_prefix, host, strict_slashes)
        self.prefix = 'web'
        self.logger = Logger()
        self.executor = ThreadPoolExecutor(options.workers)
        self._cache = Cache()
        self._kwargs = Dict(kwargs)
        self._handlers = []
        self._events = collections.defaultdict(list)

        options.parse_command_line()
        self.opt = Dict(options.items())

    async def watch_users(self, keys):
        ret = await self.db.client.admin.command('ismaster')
        if not ret.get('setName'):
            return self.logger.warning('not replica set')

        while True:
            try:
                pipeline = [
                    {
                        "$match": {
                            "operationType": "update",
                            "$or": [{f"updateDescription.updatedFields.{x}": {"$exists": True}} for x in keys],
                        }
                    },
                    {"$project": {"fullDocument.token": 1}},
                ]
                async with self.db.users.watch(pipeline, full_document='updateLookup') as stream:
                    async for change in stream:
                        doc = change['fullDocument']
                        self.logger.info(f'watch users: {doc}')
                await self._cache.set(f'{self.prefix}_user_{doc["token"]}', doc)
            except Exception as e:
                self.logger.exception(f"watch stream error: {e}")

    def register(self, *blueprints, url_prefix='/'):
        assert url_prefix[0] == '/'
        url_prefix = url_prefix.rstrip('/')
        for blueprint in blueprints:
            rules = [(url_prefix + x[0], *x[1:]) for x in blueprint.rules]
            self._handlers.append((blueprint.host, rules))
            for rule in rules:
                setattr(rule[1], 'app', self)
            if blueprint != self:
                for k, v in blueprint._events.items():
                    self._events[k].extend(v)

    def url_for(self, endpoint, *args, **kwargs):
        return self.app.reverse_url(endpoint, *args, **kwargs)

    async def shutdown(self):
        self.logger.info('shutting down')
        for func in self._events['shutdown']:
            ret = func(self)
            if inspect.isawaitable(ret):
                await ret
        self.server.stop()
        self.loop.stop()

    async def main(self, **kwargs):
        self.loop = asyncio.get_event_loop()

        if hasattr(self, 'init'):
            self._events['startup'].insert(0, self.init.__func__)
        for func in self._events['startup']:
            ret = func(self)
            if inspect.isawaitable(ret):
                await ret

        self.register(self)
        app = tornado.web.Application(**self._kwargs)
        for host, rules in self._handlers:
            app.add_handlers(host, rules)

        self.logger.info(f"Address: http://{get_ip()}:{kwargs.get('port')}")
        self.server = app.listen(**kwargs)
        await asyncio.Event().wait()

    async def start(self, **kwargs):
        try:
            await self.main(**kwargs)
        except asyncio.CancelledError:
            await self.shutdown()
            os._exit(0)
        except Exception as e:
            self.logger.exception(e)
            os._exit(1)

    def run(self, **kwargs):
        self._kwargs.setdefault('static_path', 'static')
        self._kwargs.setdefault('template_path', 'templates')
        self._kwargs.setdefault('cookie_secret', 'YWpzYWhkaDgyMTgzYWpzZGphc2RhbDEwMjBkYWph')
        self._kwargs.setdefault('xsrf_cookie', True)
        self._kwargs.setdefault('login_url', '/signin')
        self._kwargs.setdefault('debug', options.debug)

        kwargs.setdefault('xheaders', True)
        kwargs.setdefault('port', options.port)
        asyncio.run(self.start(**kwargs))
