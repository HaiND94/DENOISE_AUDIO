from pathlib import Path

import os
import subprocess
import soundfile as sf
import pyloudnorm as pyln
import sys
import gc

src = '/home/haind/Documents/rnnoise/original'

print(src)
rnn = "/home/haind/Documents/rnnoise/examples/rnnoise_demo"

paths = Path(src).glob("*.wav")
print(paths)


for filepath in paths:
    target_filepath=Path(str(filepath).replace("original", "converted"))
    target_dir=os.path.dirname(target_filepath)

    if (str(filepath) == str(target_filepath)):
        raise ValueError("Source and target path are identical: " + str(target_filepath))

    print("From: " + str(filepath))
    print("To: " + str(target_filepath))

    # Stereo to Mono; upsample to 48000Hz
    # subprocess.run(["sox", filepath, "48k.wav", "remix", "-", "rate", "48000"])
    subprocess.run(["sox", filepath, "48k.wav", "remix", "-", "rate", "44100"])
    # subprocess.run(["sox", "48k.wav", "-c", "1", "-r", "48000", "-b", "16", "-e", "signed-integer", "-t", "raw", "temp.raw"]) # convert wav to raw
    subprocess.run(["sox", "48k.wav", "-c", "1", "-r", "44100", "-b", "16", "-e", "signed-integer", "-t", "raw", "temp.raw"])
    subprocess.run([rnn, "temp.raw", "rnn.raw"]) # apply rnnoise
    # subprocess.run(["sox", "-r", "48k", "-b", "16", "-e", "signed-integer", "rnn.raw", "-t", "wav", "rnn.wav"]) # convert raw back to wav
    subprocess.run(["sox", "-r", "44100", "-b", "16", "-e", "signed-integer", "rnn.raw", "-t", "wav", "rnn.wav"])

    subprocess.run(["mkdir", "-p", str(target_dir)])
    # subprocess.run(["sox", "rnn.wav", str(target_filepath), "remix", "-", "highpass", "100", "lowpass", "6000", "rate", "22050"]) # apply high/low pass filter and change sr to 22050Hz
    subprocess.run(["sox", "rnn.wav", str(target_filepath), "remix", "-", "highpass", "100", "lowpass", "6000"])
    data, rate = sf.read(target_filepath)

    # peak normalize audio to -1 dB
    peak_normalized_audio = pyln.normalize.peak(data, -1.0)

    # measure the loudness first
    try:
        meter = pyln.Meter(rate) # create BS.1770 meter
        loudness = meter.integrated_loudness(data)
    except:
        # print(f"Can not create file {target_filepath}")
        continue

    # loudness normalize audio to -25 dB LUFS
    loudness_normalized_audio = pyln.normalize.loudness(data, loudness, -25.0)

    # sf.write(target_filepath, data=loudness_normalized_audio, samplerate=22050)
    sf.write(target_filepath, data=loudness_normalized_audio, samplerate=44100)

    print("")
    gc.collect()