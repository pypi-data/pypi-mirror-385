# -*- coding: utf-8 -*-

"""
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
"""

import requests
import hashlib
import hmac
import base64
import time
import uuid
import json
from cryptography.fernet import Fernet
import dolphin_voice.speech_syn as speech_syn
from dolphin_voice.speech_syn._log import _log
from dolphin_voice.speech_syn.parameters import Parameters


class Token:
    @staticmethod
    def get_token(app_id, app_secret, url):
        speech_syn.SpeechClient.set_log_level('INFO')

        headers = {'Content-Type': 'application/json'}
        t = time.time()
        timestamp = int(t)
        timestamp_str = str(timestamp)
        uuid1 = uuid.uuid1()
        signature_nonce = str(uuid1)
        string_to_sign = "app_id="+app_id+"&secret="+app_secret+"&timestamp="+timestamp_str
        def _hmac_sha1(secret, data):
            return str(base64.b64encode(hmac.new(bytes(secret, 'utf-8'), bytes(data, 'utf-8'),
                                                 hashlib.sha1).digest()), 'utf-8')
        signature = _hmac_sha1(app_secret, string_to_sign)
        payload = {Parameters.TOKEN_APP_ID: app_id,
                   Parameters.TOKEN_TIMESTAMP: timestamp,
                   Parameters.TOKEN_SIGNATURE_NONCE: signature_nonce,
                   Parameters.TOKEN_SIGNATURE: signature
                   }
        if not url:
            url = "https://api.voice.dolphin-ai.jp/platform/v1/auth/online/token"
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        res = r.json()
        if int(res.get(Parameters.TOKEN_STATUS)) < 400:
            data = res.get(Parameters.TOKEN_DATA)
            token = data.get(Parameters.TOKEN_APP_TOKEN)
            expire_time = data.get(Parameters.TOKEN_EXPIRE_TIME)
            if expire_time:
                print('Beijing time of token validity：%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time))))
            return token, expire_time
        _log.error(res.get(Parameters.TOKEN_MESSAGE))
        return None, None
