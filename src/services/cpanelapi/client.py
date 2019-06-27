# Copyright (c) 2014 VEXXHOST, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import requests
from requests.auth import AuthBase

from services.cpanelapi import exceptions


class AccessHashAuth(AuthBase):
    """ Access hash authentication for requests """

    def __init__(self, username, access_hash):
        self.access_hash = access_hash.replace('\n', '')
        self.username = username

    def __call__(self, r):
        r.headers['Authorization'] = 'WHM %s:%s' % (self.username, self.access_hash)
        return r


class Client(object):

    def __init__(self, username, host, password=None, access_hash=None,
                 ssl=True, cpanel=False):
        """
        Constructs a new instance of the whmclient.Client class.  It can only
        accept a `password` or `access_hash`, but not both.

        The `cpanel` flag will send requests to cPanel ports instead of WHM.
        If that option is used, access_hash authentication is not supported.
        """
        self.username = username
        self.host = host

        if not password and not access_hash:
            raise exceptions.MissingCredentials()
        elif (password and access_hash) or (cpanel and access_hash):
            raise exceptions.InvalidCredentials()
        elif access_hash:
            self.auth = AccessHashAuth(username, access_hash)
        elif password:
            self.auth = (username, password)

        self.protocol = 'https' if ssl else 'http'
        self.port = 2082 if cpanel else 2086
        if ssl:
            self.port = 2083 if cpanel else 2087

    def call(self, command, **kwargs):
        """
        Calls the `command` WHM API function with keyword arguments as
        parameters.
        """
        url = self._build_url(command)

        if kwargs:
            r = requests.get(url, params=kwargs, auth=self.auth)
        else:
            r = requests.get(url, auth=self.auth)

        return r.json()

    def call_v1(self, command, **kwargs):
        """
        Calls the `command` v1 API function with keyword arguments as
        parameters.
        """
        kwargs['api.version'] = 1
        return self.call(command, **kwargs)

    def api1(self, module, function, *args, **kwargs):
        """
        Calls the `module`::`function` API1 function under the `user` cPanel
        account.  The `user` field is required if authenticated to WHM.
        """
        call_args = {'cpanel_jsonapi_apiversion': 1,
                     'cpanel_jsonapi_module': module,
                     'cpanel_jsonapi_func': function}

        if 'user' in kwargs:
            call_args['cpanel_jsonapi_user'] = kwargs['user']

        for idx, arg in enumerate(args):
            call_args['arg-%d' % idx] = arg
        return self._cpapi_call(**call_args)

    def api2(self, module, function, user=None, **kwargs):
        """
        Calls the `module`::`function` API2 function under the `user` cPanel
        account.  The `user` field is required if authenticated to WHM.
        """
        kwargs.update({'cpanel_jsonapi_apiversion': 2,
                       'cpanel_jsonapi_module': module,
                       'cpanel_jsonapi_func': function})

        if user:
            kwargs['cpanel_jsonapi_user'] = user
        return self._cpapi_call(**kwargs)

    def uapi(self, module, function, user=None, **kwargs):
        """
        Calls the `module`::`function` UAPI function under the `user` cPanel
        account.  The `user` field is required if authenticated to WHM.
        """
        kwargs.update({'cpanel_jsonapi_apiversion': 3,
                       'cpanel_jsonapi_module': module,
                       'cpanel_jsonapi_func': function})

        if user:
            kwargs['cpanel_jsonapi_user'] = user
        return self._cpapi_call(**kwargs)

    def _cpapi_call(self, **kwargs):
        if self.port in (2086, 2087) and 'cpanel_jsonapi_user' not in kwargs:
            raise exceptions.InvalidParameters('User parameter required.')
        elif 'cpanel_jsonapi_module' not in kwargs:
            raise exceptions.InvalidParameters('Module parameter required.')
        elif 'cpanel_jsonapi_func' not in kwargs:
            raise exceptions.InvalidParameters('Function parameter required.')
        return self.call('cpanel', **kwargs)

    def _build_url(self, call_name):
        return '%s://%s:%d/json-api/%s' % (self.protocol, self.host, self.port,
                                           call_name)
