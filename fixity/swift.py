# Copyright (c) 2015 Christopher MacGown. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib

from swift.common import swob
from swift.common import utils
from swift.common import wsgi


def fixity_factory(conf, **kwargs):
    utils.register_swift_info('fixity')
    conf = conf.copy()
    conf.update(**kwargs)
    def fixity_filter(app, conf):
        return FixityCheckMiddleware(app, conf)
    return fixity_filter


class FixityCheckMiddleware(object):
    def __init__(self, app, conf):
        self.app       = app
        self.path      = conf.get('get_fixity_path', 'fixity-check')
        self.swift_dir = conf.get('swift_dir', '/etc/swift')

    @swob.wsgify
    def __call__(self, request):
        try:
            (version, account, container, obj, fix) = request.split_path(2, 4, True)
        except ValueError:
            pass

        if obj and fix == self.path:
            if not request.method == 'HEAD':
                return swob.HTTPBadRequest()

            nonce = request.headers.get('x-fixity-nonce')
            if not nonce:
                return swob.HTTPNotModified()

            if len(nonce) > 128:
                return swob.HTTPBadRequest('x-fixity-nonce is too long')

            path = str.join('/', (version, account, container, obj))

            subrequest = wsgi.get_subrequest(self.app.env,
                                             method='GET',
                                             headers=request.headers,
                                             path=path)

            response = subrequest.get_response(self.app)
            fixity_tag = hashlib.md5()
            fixity_tag.update(nonce)
            for chunk in response.app_iter():
                fixity_tag.update(chunk)

            response.body = None  # HEAD Request
            response.headers['x-fixity-tag'] = fixity_tag.hexdigest()
            return response
        return request.get_response(self.app)
