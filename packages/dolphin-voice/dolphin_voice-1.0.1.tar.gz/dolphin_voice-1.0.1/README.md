

## Installation

Install the Dolphin Voice Python SDK using pip:

```bash
pip install dolphin_voice
```

## Usage

### Quick Start

#### Short Speech Recognition

```python

from dolphin_voice.speech_rec.callbacks import SpeechRecognizerCallback
from dolphin_voice import speech_rec
import time

class Callback(SpeechRecognizerCallback):
    def started(self, message):
        print('RecognitionStarted: %s' % message)

    def result_changed(self, message):
        print('RecognitionResultChanged: %s' % message)

    def completed(self, message):
        print('RecognitionCompleted: %s' % message)

    def task_failed(self, message):
        print('TaskFailed: %s' % message)

    def warning_info(self, message):
        print('Warning: %s' % message)

    def channel_closed(self):
        print('RecognitionChannelClosed')

audio_path = 'demo.mp3'
client = speech_rec.SpeechClient(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET')

with client.create_recognizer(Callback()) as recognizer:
    recognizer.set_parameter({
        "lang_type": "zh-cmn-Hans-CN",
        "format": "mp3",
        "sample_rate": 16000,
    })
    recognizer.start()
    with open(audio_path, 'rb') as f:
        audio = f.read(7680)
        while audio:
            recognizer.send(audio)
            time.sleep(0.24)
            audio = f.read(7680)
    recognizer.stop()

```

#### Real-time Speech Recognition

```python

from dolphin_voice.speech_rec.callbacks import SpeechTranscriberCallback
from dolphin_voice import speech_rec
import time

class Callback(SpeechTranscriberCallback):
    def started(self, message):
        print('TranscriptionStarted: %s' % message)

    def result_changed(self, message):
        print('TranscriptionResultChanged: %s' % message)

    def sentence_begin(self, message):
        print('SentenceBegin: %s' % message)

    def sentence_end(self, message):
        print('SentenceEnd: %s' % message)

    def completed(self, message):
        print('TranscriptionCompleted: %s' % message)

    def task_failed(self, message):
        print('TaskFailed: %s' % message)

    def warning_info(self, message):
        print('Warning: %s' % message)

    def channel_closed(self):
        print('TranslationChannelClosed')

audio_path = 'demo.mp3'
client = speech_rec.SpeechClient(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET')

with client.create_transcriber(Callback()) as transcriber:
    transcriber.set_parameter({
        "lang_type": "zh-cmn-Hans-CN",
        "format": "mp3",
        "sample_rate": 16000,
    })
    transcriber.start()
    with open(audio_path, 'rb') as f:
        audio = f.read(7680)
        while audio:
            transcriber.send(audio)
            time.sleep(0.24)
            audio = f.read(7680)
    transcriber.stop()

```

#### Audio File Transcription

```python

from dolphin_voice import speech_rec

client = speech_rec.SpeechClient(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET')

asrfile = client.create_asrfile()

audio = 'demo.mp3'
data = {
    "lang_type": "ja-JP",
    "format": "mp3",
    "sample_rate": 16000
}
result = asrfile.transcribe_file(audio, data)
print(result)

```

#### Text-to-Speech

```python

from dolphin_voice.speech_syn.callbacks import SpeechSynthesizerCallback
from dolphin_voice import speech_syn

class MyCallback(SpeechSynthesizerCallback):
    def __init__(self, name):
        self._name = name
        self._fout = open(name, 'wb')

    def binary_data_received(self, raw):
        self._fout.write(raw)

    def on_message(self, message):
        print('Received : %s' % message)

audio_name = 'syAudio.mp3'
client = speech_syn.SpeechClient(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET')
callback = MyCallback(audio_name)

with client.create_synthesizer(callback) as synthesizer:
    synthesizer.set_parameter({
        "text": "今天是个晴天，您吃过了吗？",
        "lang_type": "zh-cmn-Hans-CN",
        "format": "mp3"
    })
    synthesizer.start()
    synthesizer.wait_completed()

```