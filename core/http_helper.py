#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import requests
from requests import RequestException


class ErrorTimeout(Exception):
    """self define exception: requests page time out"""
    def __init__(self):
        self.value = 'Can not reach destination'

    def __str__(self):
        return repr(self.value)


class ErrorPassword(Exception):
    """self define exception: wrong password"""
    def __init__(self):
        self.value = 'Wrong password'

    def __str__(self):
        return repr(self.value)


class HttpHelper(object):

    @staticmethod
    def connect(session, url, times):
        for x in xrange(times):
            try:
                if session:
                    r = session.get(url, timeout=3, allow_redirects=True)
                else:
                    r = requests.get(url, timeout=3, allow_redirects=True)
                return r
            except RequestException:
                pass
        raise ErrorTimeout

    @staticmethod
    def connect_with_headers(session, url, times, headers):
        for x in xrange(times):
            try:
                if session:
                    r = session.get(url, timeout=3, allow_redirects=True, headers=headers)
                else:
                    r = requests.get(url, timeout=3, allow_redirects=True, headers=headers)
                return r
            except RequestException:
                pass
        raise ErrorTimeout

    @staticmethod
    def connect_auth_with_headers(session, url, times, auth, headers):
        for x in xrange(times):
            try:
                if session:
                    r = session.get(url, auth=auth, timeout=3, allow_redirects=True, headers=headers)
                else:
                    r = requests.get(url, auth=auth, timeout=3, allow_redirects=True, headers=headers)
                return r
            except RequestException:
                pass
        raise ErrorTimeout

    @staticmethod
    def post_auth_with_headers(session, url, times, auth, headers, data):
        for x in xrange(times):
            try:
                if session:
                    r = session.post(url, auth=auth, timeout=2, allow_redirects=True, headers=headers, data=data)
                else:
                    r = requests.post(url, auth=auth, timeout=2, allow_redirects=True, headers=headers, data=data)
                return r
            except RequestException:
                pass
        raise ErrorTimeout
