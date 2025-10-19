#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings

from .base_utils import (Cache, DefaultDict, Dict, DictUnwrapper, DictWrapper,
                         JSONEncoder, Singleton, async_tasks, awaitable, ceil,
                         connect, floor, get_ip, int2ip, int2str, ip2int,
                         multi_apply, pprint, str2int, to_bytes, to_str, tqdm,
                         yaml)
from .config_utils import Config
from .crypto import (aes_decrypt, aes_encrypt, des_decrypt, des_encrypt,
                     gen_rsa_key, rsa_decrypt, rsa_encrypt, xor_decrypt,
                     xor_encrypt)
from .db_utils import (AioMysql, AioRedis, Mongo, MongoClient, Motor,
                       MotorClient, Mysql, Redis, parse_uri)
from .decorator import aioretry, retry, smart_decorator, synchronize, timeit
from .email_utils import AioEmail, Email
from .fire import Fire
from .generate_machine_id import get_machine_id
from .http_utils import Response, patch_connection_pool
from .log_utils import Logger, WatchedFileHandler
from .rabbitmq import AioPika, Pika
from .stopwatch import Stopwatch
from .xdb_searcher import XdbSearcher
from .xor_file import xor_file_multiprocess

try:
    import pycurl  # noqa

    from .curl_utils import Request
except:
    from .http_utils import Request

warnings.filterwarnings("ignore")

__all__ = [
    'awaitable', 'floor', 'ceil', 'to_str', 'to_bytes', 'tqdm', 'yaml', 'pprint', 'timeit',
    'retry', 'aioretry', 'smart_decorator', 'synchronize', 'multi_apply', 'async_tasks',
    'get_ip', 'connect', 'ip2int', 'int2ip', 'int2str', 'str2int', 'patch_connection_pool', 'parse_uri',
    'des_encrypt', 'des_decrypt', 'aes_encrypt', 'aes_decrypt', 'gen_rsa_key', 'rsa_encrypt', 'rsa_decrypt',
    'xor_encrypt', 'xor_decrypt',
    'Fire', 'Singleton', 'JSONEncoder', 'Dict', 'DefaultDict', 'DictWrapper', 'DictUnwrapper',
    'Email', 'AioEmail', 'Config', 'Logger', 'WatchedFileHandler', 'Cache', 'XdbSearcher',
    'Mongo', 'MongoClient', 'Redis', 'AioRedis', 'Motor', 'MotorClient', 'Mysql', 'AioMysql', 'Pika', 'AioPika',
    'get_machine_id', 'xor_file_multiprocess',
    'Request', 'Response', 'Stopwatch'
]
