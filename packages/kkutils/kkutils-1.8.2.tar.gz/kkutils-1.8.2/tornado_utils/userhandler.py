#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Last modified: 2018-06-03 00:38:17
'''

import hashlib
import random
import re
import uuid
from datetime import datetime

import pymongo
import tornado.web
from bson import ObjectId
from utils import Dict

from .application import Blueprint
from .basehandler import BaseHandler

bp = Blueprint(__name__)


class BaseHandler(BaseHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, HEAD, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Max-Age', '3600')

    def options(self):
        self.set_status(204)
        self.finish()

    def encrypt(self, password):
        return hashlib.md5(f'digua_{password}'.encode()).hexdigest()

    async def gen_code(self, email):
        code = ''.join(random.sample('0123456789', 4))
        key = f'{self.prefix}_code_{email}'
        await self.rd.setex(key, 3600, code)
        return code

    async def get_user(self, email):
        if email.find('@') >= 0:
            return await self.db.users.find_one({'email': email})
        else:
            return await self.db.users.find_one({'username': email})

    async def check_code(self):
        email, code = self.args.email, self.args.code
        if email and code:
            key = f'{self.prefix}_code_{email}'
            if code == await self.rd.get(key):
                return Dict({'err': 0})
        return Dict({'err': 1, 'msg': '验证码无效'})

    async def check_username(self):
        username = self.args.username
        if not username:
            return Dict({'err': 1, 'msg': '请输入用户名'})
        if not 5 <= len(username) <= 20:
            return Dict({'err': 1, 'msg': '用户名长度请限制在5到20个字符之间'})
        if await self.db.users.find_one({'username': username}):
            return Dict({'err': 1, 'msg': '用户名重复'})
        return Dict({'err': 0})

    async def check_password(self):
        password = self.args.password
        if not password:
            return Dict({'err': 1, 'msg': '请输入密码'})
        if not 5 <= len(password) <= 20:
            return Dict({'err': 1, 'msg': '密码长度请限制在5到20个字符之间'})
        return Dict({'err': 0})

    async def check_email(self):
        email = self.args.email
        if not email:
            return Dict({'err': 1, 'msg': '请输入邮箱'})
        if len(email) > 64:
            return Dict({'err': 1, 'msg': '邮箱地址太长'})
        if email.find(' ') >= 0:
            return Dict({'err': 1, 'msg': '邮箱地址不能包含空格'})
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Dict({'err': 1, 'msg': '请填写正确的邮箱格式'})
        if not re.search(r'@(qq.com|gmail.com|163.com|126.com|yeah.net|outlook.com|live.com|foxmail.com|hotmail.com|sina.com|vip.qq.com|139.com|icloud.com|aliyun.com|88.com|sina.cn|tom.com|live.cn|yahoo.com|189.cn|msn.com|sohu.com|yandex.com|.edu.cn|vip.163.com|msn.cn)$', email.lower()):
            return Dict({'err': 1, 'msg': '请使用常用邮箱注册'})
        if await self.db.users.find_one({'email': email}):
            return Dict({'err': 1, 'msg': '邮箱地址重复'})
        return Dict({'err': 0})

    async def check_scene(self):
        scene = self.args.scene
        if not scene:
            return Dict({'err': 1, 'msg': f'scene is not defined: {scene}'})

        resp = await self.http.get(scene)
        if not resp.code == 200:
            return Dict({'err': 1, 'msg': f'get scene failed: {scene}'})

        ret = resp.json()
        if ret.err:
            return ret

        user = await self.db.users.find_one({'openId': ret.openId})
        if not user and ret.unionId:
            user = await self.db.users.find_one({'unionId': ret.unionId})
        if not user:
            if self.current_user:
                keys = ['openId', 'unionId', 'avatarUrl', 'nickName']
                update = {k: v for k, v in ret.items() if k in keys if v}
                user = await self.db.users.find_one_and_update({'_id': self.current_user._id}, {'$set': update}, return_document=True)
            else:
                ret.token = uuid.uuid4().hex
                ret.id = await self.db.users.seq_id
                ret.code = self.encode(ret.id)
                ret.created_at = datetime.now().replace(microsecond=0)
                user = await self.db.users.find_one_and_update({'unionId': ret.unionId}, {'$set': ret}, upsert=True, return_document=True)
        elif ret.unionId and not user.unionId:
            await self.db.users.update_one({'_id': user._id}, {'$set': {'unionId': ret.unionId}})

        user.err = 0
        self.set_cookie('token', user.token, expires_days=365)
        return user


@bp.route("/check")
class CheckHandler(BaseHandler):

    async def get(self):
        for key, value in self.args.items():
            if hasattr(self, f'check_{key}'):
                ret = await getattr(self, f'check_{key}')()
                break
        else:
            ret = Dict({'err': 1, 'msg': 'not authorized'})
        self.finish(ret)


@bp.route("/logout")
class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_all_cookies()
        self.redirect('/')


@bp.route("/signup")
class SignupHandler(BaseHandler):

    def get(self):
        self.render('signup.html')

    async def post(self):
        ret = await self.check_username()
        if ret.err:
            return self.finish(ret)
        ret = await self.check_password()
        if ret.err:
            return self.finish(ret)
        ret = await self.check_email()
        if ret.err:
            return self.finish(ret)
        ret = await self.check_code()
        if ret.err:
            return self.finish(ret)
        self.args.pop('code', None)
        self.args.pop('confirmPassword', None)

        if from_id := self.args.pop('from_id', None):
            if from_id.isdigit():
                self.args.link = int(from_id)

        if link := self.args.pop('link', None):
            try:
                if len(link) == 5:
                    self.args.link = self.decode_old(link)
                elif uid := self.decode(link):
                    self.args.link = uid
            except Exception as e:
                self.logger.warning(f"decode {link} failed: {e}")

        keys = ['username', 'email', 'link']
        doc = Dict({k: v for k, v in self.args.items() if k in keys})
        seq_id = await self.db.users.seq_id
        doc.update({
            'id': seq_id,
            'ip': self.ip,
            'code': self.encode(seq_id),
            'token': uuid.uuid4().hex,
            'password': self.encrypt(self.args.password),
            'created_at': datetime.now().replace(microsecond=0),
        })
        try:
            user = await self.db.users.find_one_and_update({'username': doc.username},
                                                           {'$set': doc},
                                                           upsert=True,
                                                           return_document=True)
        except pymongo.errors.DuplicateKeyError as e:
            detail = e.details.get('keyValue', {})
            if detail.get('username'):
                return self.finish({'err': 1, 'msg': '用户名重复'})

            if not detail.get('id'):
                self.logger.exception(e)
                return self.finish({'err': 1, 'msg': '未知错误'})

            cursor = self.db.users.find({}, {'_id': 0, 'id': 1}).sort('id', -1).limit(1)
            exists = await cursor.to_list()
            doc.id = exists[0].id + 1 if exists else await self.db.users.seq_id
            await self.db.ids.update_one({'_id': 'users'}, {'$set': {'seq': doc.id}})
            doc.code = self.encode(doc.id)
            user = await self.db.users.find_one_and_update({'username': doc.username},
                                                           {'$set': doc},
                                                           upsert=True,
                                                           return_document=True)

        self.set_cookie('token', user.token, expires_days=365)
        self.finish({'err': 0, 'user': user})


@bp.route("/v1/login")
@bp.route("/signin")
class SigninHandler(BaseHandler):

    def get(self):
        self.render('signin.html')

    async def post(self):
        username = self.args.username
        password = self.args.password
        remember = self.args.remember
        if not (username and password):
            return self.finish({'err': 1, 'msg': '请输入用户名和密码'})

        if username.find('@') >= 0:
            query = {'email': username, 'password': self.encrypt(password)}
        else:
            query = {'username': username, 'password': self.encrypt(password)}
        user = await self.db.users.find_one(query)
        if not user:
            return self.finish({'err': 1, 'msg': '用户名或密码错误'})

        expires_days = 365 if remember == 'on' else None
        self.set_cookie('token', user.token, expires_days=expires_days)
        self.finish({'err': 0, 'user': user})


@bp.route("/v1/user")
@bp.route("/user")
class UserHandler(BaseHandler):

    async def get(self):
        if self.current_user:
            user = {k: v for k, v in self.current_user.items() if k not in ['password']}
            self.finish(user)
        else:
            self.finish({'err': 1, 'msg': '用户未登录'})

    async def put(self):
        self.logger.info(f'new user: {self.args}')
        if not self.args.unionId:
            return self.finish({'err': 1, 'msg': '未获取到用户'})

        doc = Dict({k: v for k, v in self.args.items() if k in ['openId', 'unionId', 'nickName']})
        user = None
        if self.args.openId:
            user = await self.db.users.find_one({'openId': self.args.openId})
        if not user and self.args.unionId:
            user = await self.db.users.find_one({'unionId': self.args.unionId})
        if user:
            await self.db.users.update_one({'_id': user._id}, {'$set': doc})
        else:
            doc.setdefault('token', uuid.uuid4().hex)
            doc.id = await self.db.users.seq_id
            doc.code = self.encode(doc.id)
            doc.created_at = datetime.now().replace(microsecond=0)
            try:
                user = await self.db.users.find_one_and_update({'unionId': doc.unionId},
                                                               {'$set': doc},
                                                               upsert=True,
                                                               return_document=True)
            except pymongo.errors.DuplicateKeyError as e:
                detail = e.details.get('keyValue', {})
                if not detail.get('id'):
                    self.logger.exception(e)
                    return self.finish({'err': 1, 'msg': '未知错误'})

                cursor = self.db.users.find({}, {'_id': 0, 'id': 1}).sort('id', -1).limit(1)
                exists = await cursor.to_list()
                doc.id = exists[0].id + 1 if exists else await self.db.users.seq_id
                await self.db.ids.update_one({'_id': 'users'}, {'$set': {'seq': doc.id}})
                doc.code = self.encode(doc.id)
                user = await self.db.users.find_one_and_update({'unionId': doc.unionId},
                                                               {'$set': doc},
                                                               upsert=True,
                                                               return_document=True)

        self.finish({'err': 0, 'user': user})

    @tornado.web.authenticated
    async def post(self):
        old_password = self.args.old_password
        password = self.args.password
        if self.current_user.password and not (old_password and self.encrypt(old_password) == self.current_user.password):
            return self.finish({'err': 1, 'msg': '原密码错误'})
        if not password:
            return self.finish({'err': 1, 'msg': '请输入新密码'})

        await self.db.users.update_one({'_id': self.current_user._id}, {'$set': {'password': self.encrypt(password)}})
        self.finish({'err': 0})

    @tornado.web.authenticated
    async def delete(self):
        if not self.current_user.admin:
            return self.finish({'err': 1, 'msg': 'unauthorized'})

        await self.db.users.delete_one({'_id': ObjectId(self.args._id)})
        self.finish({'err': 0})


@bp.route("/reset")
class ResetHandler(BaseHandler):

    def get(self):
        self.render('reset.html')

    async def post(self):
        ret = await self.check_code()
        if ret.err:
            return self.finish(ret)

        if not (self.args.email and self.args.password):
            return self.finish({'err': 1, 'msg': '请输入邮箱和密码'})

        user = await self.get_user(self.args.email)
        if not user:
            return self.finish({'err': 1, 'msg': '用户不存在'})

        await self.db.users.update_one({'_id': user._id}, {'$set': {'password': self.encrypt(self.args.password)}})
        self.finish({'err': 0})


@bp.route(r'/active/(\w+)')
class ActiveHandler(BaseHandler):

    async def get(self, code):
        value = await self.rd.get(f'{self.prefix}_active_{code}')
        if value:
            token, email = value.split('_', 1)
            await self.db.users.update_one({'token': token}, {'$set': {'email': email}})
            if not self.get_cookie('token'):
                self.set_cookie('token', token, expires_days=30)
        self.redirect('/admin')

    async def post(self, _id):
        await self.db.users.update_one({'_id': ObjectId(_id)}, {'$set': {'active': True}})
        self.finish({'err': 0})


@bp.route(r'/email/(\w+)')
class EmailHandler(BaseHandler):

    async def get(self, action):
        if not re.match(r'.*@(.*)\.(\w+)$', self.args.email or ''):
            return self.finish({'err': 1, 'msg': '请填写正确的邮箱格式'})

        if action == 'reset':
            user = await self.get_user(self.args.email)
            if not user:
                return self.finish({'err': 1, 'msg': '用户不存在'})
            title = f'{self.host} 重设密码邮件'
            code = await self.gen_code(self.args.email)
            content = f'您本次操作的验证码为: {code}'
        elif action == 'check':
            title = f'{self.host} 验证邮件'
            code = await self.gen_code(self.args.email)
            content = f'您本次操作的验证码为: {code}'
        elif action == 'active':
            user = await self.get_user(self.args.email)
            if user:
                return self.finish({'err': 1, 'msg': '当前邮箱已被使用，请更换其他邮箱'})
            if not self.current_user:
                return self.finish({'err': 1, 'msg': '用户未登录'})
            title = f'{self.host} 激活邮件'
            code = uuid.uuid4().hex
            key = f'{self.prefix}_active_{code}'
            value = f'{self.current_user.token}_{self.args.email}'
            await self.rd.setex(key, 3600, value)
            url = f'{self.scheme}://{self.host}/active/{code}'
            content = f'请点击链接或将其复制到浏览器地址栏打开: <br><a href="{url}">{url}</a>'
        else:
            return self.finish({'err': 1, 'msg': '未定义操作'})

        key = f'{self.prefix}_wait_{self.args.email}'
        if not await self.rd.exists(key):
            await self.rd.setex(key, 60, 1)
            await self.email.send(self.args.email, title, content)
            self.finish({'err': 0})
        else:
            self.finish({'err': 1, 'msg': '邮件已发送，再次尝试请等候1分钟'})

    post = get
