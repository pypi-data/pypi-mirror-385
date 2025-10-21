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
import time
import websocket
import os
from cryptography.fernet import Fernet

try:
    import thread
except ImportError:
    import _thread as thread
from dolphin_voice.speech_rec._log import _log
from dolphin_voice.speech_rec._token import Token
from dolphin_voice.speech_rec._speech_recognizer import SpeechRecognizer
from dolphin_voice.speech_rec._speech_transcriber import SpeechTranscriber
from dolphin_voice.speech_rec._utils import utils
from dolphin_voice.speech_rec._speech_asrfile import SpeechASRFile
__all__ = ["SpeechClient"]


class SpeechClient(utils):

    def __init__(self, app_id=None, app_secret=None, url=None, url_token=None):
        super().__init__()
        websocket.enableTrace(False)

        self.donation = 'wss://api.voice.dolphin-ai.jp/v1/asr/ws' if not url else url
        self.url_token = url_token

        self.app_id = app_id
        self.app_secret = app_secret
        assert self.app_id and self.app_secret, "Please check app_id, app_secret"
        self.token = self.update_token()
        assert self.token, "Please check app_id, app_secret"

    @staticmethod
    def set_log_level(level):
        _log.setLevel(level)

    def update_token(self):
        token = None
        token_file = ".token"
        extime = 7
        new_time = time.time()
        if not os.path.exists(token_file):
            token = self.get_token(self.app_id, self.app_secret, token_file)
        with open(token_file, "r", encoding="utf-8") as fr:
            token_info = eval(fr.read())
        old_time = token_info['time']
        token = token_info['token']

        if not token or new_time - old_time > 60 * 60 * 24 * (extime - 1):
            token = self.get_token(self.app_id, self.app_secret, token_file)

        return token

    def get_token(self, app_id, app_secret, token_file):
        token = Token.get_token(app_id, app_secret, self.url_token)
        with open(token_file, "w", encoding="utf-8") as fd:
            fd.write(str({"token": token[0], "time": time.time()}))
        return token

    def create_recognizer(self, callback, url=None):
        if url:
            recognizer = SpeechRecognizer(callback, url)
        else:
            recognizer = SpeechRecognizer(callback, self.donation)
        self.token = self.update_token()
        recognizer.set_app_id(self.app_id)
        recognizer.set_token(self.token)
        return recognizer

    def create_transcriber(self, callback, url=None):
        if url:
            transcriber = SpeechTranscriber(callback, url)
        else:
            transcriber = SpeechTranscriber(callback, self.donation)
        self.token = self.update_token()
        transcriber.set_app_id(self.app_id)
        transcriber.set_token(self.token)
        return transcriber

    def create_asrfile(self, asr_file_upload_url=None, asr_file_result_url=None):
        self.token = self.update_token()
        asrfile = SpeechASRFile(self.token, asr_file_upload_url=asr_file_upload_url, asr_file_result_url=asr_file_result_url)
        return asrfile
