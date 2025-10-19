#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Author:        digua
Created at:    2021-10-30 17:03:31
Last modified: 2021-11-01 15:26:05
'''

import asyncio
import collections
import copy
import datetime
import decimal
import inspect
import json
import math
import os
import socket
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial, reduce
from itertools import chain, zip_longest
from pathlib import Path
from socket import inet_aton, inet_ntoa
from struct import pack, unpack

import requests
import yaml
from pymongo.cursor import Cursor
from rich.console import Console
from rich.table import Table
from tqdm import tqdm as _tqdm


def _include_yaml(loader, node):
    root = Path(loader.name).parent
    if isinstance(node, yaml.SequenceNode):
        return [yaml.load(open(root / x.value), Loader=yaml.FullLoader) for x in node.value]
    else:
        return yaml.load(open(root / node.value), Loader=yaml.FullLoader)


def yaml_load(stream, **kwargs):
    loader = yaml.FullLoader(stream)
    try:
        return DictWrapper(loader.get_single_data())
    finally:
        loader.dispose()


def yaml_dump(data, stream=None, default_flow_style=False, allow_unicode=True, sort_keys=False, **kwargs):
    return yaml.dump_all([DictUnwrapper(data)], stream, Dumper=yaml.Dumper,
                         default_flow_style=default_flow_style,
                         allow_unicode=allow_unicode, sort_keys=sort_keys, **kwargs)


yaml.add_constructor('!include', _include_yaml)


class tqdm(_tqdm):

    def __init__(self, iterable=None, colour='green', **kwargs):
        if not kwargs.get('total') and isinstance(iterable, Cursor):
            kwargs.setdefault('total', iterable.count())
        kwargs.setdefault('disable', not sys.stdout.isatty())
        super().__init__(iterable, colour=colour, **kwargs)

    def update(self, n=1, total=None):
        if total is not None:
            self.total = total
            super().update(max(0, n - self.n))
        else:
            super().update(n)


class JSONEncoder(json.encoder.JSONEncoder):
    '''针对某些不能序列化的类型如datetime，使用json.dumps(data, cls=JSONEncoder)
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'tolist') and callable(obj.tolist):
            return obj.tolist()
        try:
            return super().default(obj)
        except Exception:
            return str(obj)


class Singleton(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Cache:

    def __init__(self):
        self.lock = threading.RLock()
        self.data = {}

    def get(self, key):
        item = self.data.get(key)
        if item is not None:
            value, ttl = item
            if ttl is None:
                return value
            if ttl >= int(time.time()):
                return value

    def set(self, key, value, ttl=None):
        with self.lock:
            ttl = int(time.time()) + ttl if ttl is not None else None
            self.data[key] = value, ttl

    def incr(self, key, value=1):
        with self.lock:
            self.data.setdefault(key, 0)
            self.data[key] += value
            return self.data[key]

    def delete(self, key):
        with self.lock:
            return self.data.pop(key, None)

    def clear(self):
        with self.lock:
            data = copy.deepcopy(self.data)
            self.data.clear()
            return data

    def ttl(self, key, ttl):
        with self.lock:
            item = self.data[key]
            if item is not None:
                self.data[key] = item[0], int(time.time()) + ttl


class Dict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            self.__setitem__(key, value)

    def dict(self):
        return DictUnwrapper(self)

    def __delattr__(self, key):
        try:
            del self[key]
        except Exception:
            pass

    def __getattr__(self, key):
        try:
            return self[key]
        except Exception:
            pass

    def __setitem__(self, key, value):
        super().__setitem__(key, DictWrapper(value))

    __setattr__ = __setitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __or__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    # def __repr__(self):
    #     return 'Dict<%s>' % dict.__repr__(self)

    # def __str__(self):
    #     return json.dumps(self, cls=JSONEncoder, ensure_ascii=False)


class DefaultDict(collections.defaultdict):

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        return self[key]


def DictWrapper(*args, **kwargs):
    if args and len(args) == 1:
        if isinstance(args[0], collections.defaultdict):
            return DefaultDict(args[0].default_factory, args[0])
        elif isinstance(args[0], dict):
            return Dict(args[0])
        elif isinstance(args[0], (tuple, list)):
            return type(args[0])(map(DictWrapper, args[0]))
        else:
            return args[0]
    elif args:
        return type(args)(map(DictWrapper, args))
    else:
        return Dict(**kwargs)


def DictUnwrapper(doc):
    if isinstance(doc, DefaultDict):
        return collections.defaultdict(doc.default_factory, doc)
    if isinstance(doc, Dict):
        return dict(map(lambda x: (x[0], DictUnwrapper(x[1])), doc.items()))
    if isinstance(doc, (tuple, list)):
        return type(doc)(map(DictUnwrapper, doc))
    return doc


async def awaitable(ret):
    return await ret if inspect.isawaitable(ret) else ret


def multi_apply(func, *args, **kwargs):
    workers = kwargs.pop('workers', os.cpu_count())
    pool = kwargs.pop('pool', True)
    batch = kwargs.pop('batch', None)
    size = len(args[0])
    if batch:
        step = math.ceil(size / batch)
        iterables = [[x[i::step] for i in range(step)] for x in args]
    else:
        iterables = [[x[i::workers] for i in range(workers)] for x in args]
    func = partial(func, **kwargs) if kwargs else func
    Executor = ProcessPoolExecutor if pool else ThreadPoolExecutor
    with Executor(workers) as executor:
        results = executor.map(func, *iterables)
    results = list(results)
    if all([isinstance(x, (list, tuple)) for x in results]):
        results = list(chain(*zip_longest(*results)))
    return results[:size]


async def async_tasks(func, *args, **kwargs):
    workers = kwargs.pop('workers', os.cpu_count())
    semaphore = asyncio.Semaphore(workers)

    async def worker(func, *args):
        async with semaphore:
            return await func(*args)

    func = partial(func, **kwargs) if kwargs else func
    tasks = [worker(func, *x) for x in zip(*args)]
    results = await asyncio.gather(*tasks)
    return results


def floor(number, ndigits=0):
    '''当ndigits大于等于number的小数点位数时，直接返回
    '''
    if ndigits == 0:
        return math.floor(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_DOWN))


def ceil(number, ndigits=0):
    if ndigits == 0:
        return math.ceil(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_UP))


def to_str(*args):
    result = tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x if isinstance(x, str) else str(x), args))
    return result[0] if len(args) == 1 else result


def to_bytes(*args):
    result = tuple(map(lambda x: x.encode() if isinstance(x, str) else x if isinstance(x, bytes) else str(x).encode(), args))
    return result[0] if len(args) == 1 else result


def get_ip(local=True):
    if local:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
        finally:
            s.close()
    else:
        try:
            resp = requests.get('http://4.ipw.cn', timeout=1)
            return resp.text.split()[-1]
        except Exception:
            return get_ip()


def connect(ip, port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    result = s.connect_ex((ip, port))
    s.close()
    return result == 0


def ip2int(ip):
    return unpack("!I", inet_aton(ip))[0]


def int2ip(i):
    return inet_ntoa(pack("!I", i))


def str2int(str_time):
    return int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S")))


def int2str(int_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int_time))


def pprint(docs, header=None, auto=False, index=False):
    console = Console()
    if auto:
        stack = inspect.stack()
        if not [x for x in stack if x.function == 'Fire']:
            return

    if not isinstance(docs, (list, tuple)):
        return console.print(docs)

    if header is None and docs and isinstance(docs[0], dict):
        header = sorted(set(reduce(lambda x, y: x + y, [list(x.keys()) for x in docs])))
    if header is not None and index:
        header.insert(0, 'id')

    if header is not None:
        table = Table(show_header=True, header_style="bold magenta")
        for key in header:
            table.add_column(key)
    else:
        table = Table(show_header=False, header_style="bold magenta")

    for idx, doc in enumerate(docs):
        if isinstance(doc, dict):
            line = [str(doc.get(x, '')) for x in header]
        elif isinstance(doc, (list, tuple)):
            line = [str(x) for x in doc]
        else:
            line = [str(getattr(doc, x)) for x in header]
        if index:
            line.insert(0, str(idx))
        table.add_row(*line)
    console.print(table)
