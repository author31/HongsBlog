#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: oauthmanager.py
@time: 2016/11/26 下午5:09
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from oauth.models import OAuthUser, OAuthConfig
from django.conf import settings
import requests
import json
import logging
import urllib.parse
from DjangoBlog.utils import parse_dict_to_url, cache_decorator

logger = logging.getLogger(__name__)


class OAuthAccessTokenException(Exception):
    '''
    oauth授权失败异常
    '''


class BaseOauthManager(metaclass=ABCMeta):
    """获取用户授权"""
    AUTH_URL = None
    """获取token"""
    TOKEN_URL = None
    """获取用户信息"""
    API_URL = None
    '''icon图标名'''
    ICON_NAME = None

    def __init__(self, access_token=None, openid=None):
        self.access_token = access_token
        self.openid = openid

    @property
    def is_access_token_set(self):
        return self.access_token is not None

    @property
    def is_authorized(self):
        return self.is_access_token_set and self.access_token is not None and self.openid is not None

    @abstractmethod
    def get_authorization_url(self, nexturl='/'):
        pass

    @abstractmethod
    def get_access_token_by_code(self, code):
        pass

    @abstractmethod
    def get_oauth_userinfo(self):
        pass

    def do_get(self, url, params, headers=None):
        rsp = requests.get(url=url, params=params, headers=headers)
        logger.info(rsp.text)
        return rsp.text

    def do_post(self, url, params, headers=None):
        rsp = requests.post(url, params, headers=headers)
        logger.info(rsp.text)
        return rsp.text

    def get_config(self):
        value = OAuthConfig.objects.filter(type=self.ICON_NAME)
        return value[0] if value else None


class GoogleOauthManager(BaseOauthManager):
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    API_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
    ICON_NAME = 'google'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            GoogleOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'scope': 'openid email',
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,

            'redirect_uri': self.callback_url
        }
        rsp = self.do_post(self.TOKEN_URL, params)

        obj = json.loads(rsp)

        if 'access_token' in obj:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['id_token'])
            logger.info(self.ICON_NAME + ' oauth ' + rsp)
            return self.access_token
        else:
            raise OAuthAccessTokenException(rsp)

    def get_oauth_userinfo(self):
        if not self.is_authorized:
            return None
        params = {
            'access_token': self.access_token
        }
        rsp = self.do_get(self.API_URL, params)
        try:

            datas = json.loads(rsp)
            user = OAuthUser()
            user.matedata = rsp
            user.openid = datas['sub']
            user.token = self.access_token
            user.type = 'google'
            if datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('google oauth error.rsp:' + rsp)
            return None


@cache_decorator(expiration=100 * 60)
def get_oauth_apps():
    configs = OAuthConfig.objects.filter(is_enable=True).all()
    if not configs:
        return []
    configtypes = [x.type for x in configs]
    applications = BaseOauthManager.__subclasses__()
    apps = [x() for x in applications if x().ICON_NAME.lower() in configtypes]
    return apps


def get_manager_by_type(type):
    applications = get_oauth_apps()
    if applications:
        finds = list(
            filter(
                lambda x: x.ICON_NAME.lower() == type.lower(),
                applications))
        if finds:
            return finds[0]
    return None
