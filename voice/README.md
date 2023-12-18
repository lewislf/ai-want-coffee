# Whisper Transcription with VAD

This application is based on [whisper_real_time](https://github.com/davabase/whisper_real_time) repository. In order to make the use more reliable, it was used [Silero Voice Activity Detector](https://github.com/snakers4/silero-vad). Whenever voice activity is detected, the audio recorded is transcribed by whisper. We wish to use that to facilitate communication with the GPT Assistant we developed.

The transcription can be used by calling
```
python3 transcribe.py --language portuguese --microphone_calibrate
```

# Real Time Whisper Transcription

This is a demo of real time speech to text with OpenAI's Whisper model. It works by constantly recording audio in a thread and concatenating the raw bytes over multiple recordings.

To install dependencies simply run
```
pip install -r requirements.txt
```
in an environment of your choosing.

Whisper also requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) to be installed on your system, which is available from most package managers:

```
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

For more information on Whisper please see https://github.com/openai/whisper