import speech_recognition as sr
import argparse
import sounddevice
import torch
import io

from queue import Queue
from sys import platform
from time import sleep
from pprint import pprint
from tempfile import NamedTemporaryFile



def main():
    parser = argparse.ArgumentParser()
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    parser.add_argument("--record_timeout", default=30,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large",
                                 "tiny.en", "base.en", "small.en", "medium.en"])
    parser.add_argument("--language", default=None,
                            help="Language for transcription.", type=str)
    parser.add_argument("--energy_threshold", default=2000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--phrase_threshold", default=0.5,
                        help="minimum seconds of speaking audio"
                             "before we consider the speaking audio a phrase.", type=float)
    parser.add_argument("--microphone_calibrate", action='store_true',
                        help="Automatic calibration for microphone level.")  
    args = parser.parse_args()    
    
    SAMPLE_RATE = 16000
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=SAMPLE_RATE, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=SAMPLE_RATE)


    phrase_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False
    recorder.phrase_threshold = args.phrase_threshold
    if args.microphone_calibrate:
        with source:
            print("Please wait. Calibrating microphone...")
            recorder.adjust_for_ambient_noise(source, duration=1)
    
    torch.set_num_threads(1)
    USE_ONNX = False
    vad_model, vad_utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=False,
                              onnx=USE_ONNX)
    (get_speech_timestamps,
    save_audio,
    read_audio,
    VADIterator,
    collect_chunks) = vad_utils

    temp_file = NamedTemporaryFile().name
    def record_callback(_, audio:sr.AudioData) -> None:
        wav_data = io.BytesIO(audio.get_wav_data())
        with open(temp_file, 'w+b') as f:
            f.write(wav_data.read())
        vad_audio = read_audio(temp_file, sampling_rate=SAMPLE_RATE)
        speech_timestamps = get_speech_timestamps(vad_audio, vad_model, sampling_rate=SAMPLE_RATE)
        # save_audio('only_speech.wav',
        #    collect_chunks(speech_timestamps, vad_audio), sampling_rate=SAMPLE_RATE) 
        pprint(speech_timestamps)
        if speech_timestamps != []:
            phrase_queue.put(audio)
            print("New phrase added.")
    
    recorder.listen_in_background(source, record_callback, phrase_time_limit=args.record_timeout)

    print("You can start talking")
    while True:
        if not phrase_queue.empty():
            print('Processing...')
            audio_data = phrase_queue.get()
            transcript = recorder.recognize_whisper(audio_data, args.model, language=args.language)
            print(transcript)
            sleep(0.25)


if __name__ == '__main__':
    main()