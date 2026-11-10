"""Original RS004/5/6 procedural miniatures; no samples or borrowed melodies.
Run: python ArtSource/Audio/Music/compose_expansion.py
Only the three expansion WAVs and their provenance are written. Never imports
compose_music.py, whose top-level code rebuilds the original recordings.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import wave

import numpy as np
import scipy
from scipy.signal import butter, sosfilt

SR = 48000
OUT = Path(__file__).resolve().parent
TRACKS = (
    (4, 'RS004_QuietCircuit.wav', '빛의 잔결', '느린 회로', 72, 8, -19.0),
    (5, 'RS005_SmallTable.wav', '마주 놓은 의자', '나무결 셋', 88, 10, -18.5),
    (6, 'RS006_OpenMeasure.wav', '남겨 둔 쉼표', '작은 방 실내악', 60, 7, -19.0),
)


def filt(x, frequency, kind='lowpass'):
    return sosfilt(butter(2, frequency, kind, fs=SR, output='sos'), x)


def tone(note, duration, kind, rng):
    t = np.arange(round(duration * SR)) / SR
    f = 440 * 2 ** ((note - 69) / 12)
    attack, release = .012, .12
    if kind == 'synth':
        x = (np.sin(2*np.pi*f*t + .30*np.sin(2*np.pi*f*2*t)*np.exp(-t*1.1))
             + .13*np.sin(2*np.pi*f*2*t) + .045*np.sin(2*np.pi*f*3.003*t))
        x *= np.exp(-t*.85)
        attack, release = .07, .3
    elif kind == 'guitar':
        x = np.zeros_like(t)
        for k in range(1, 13):
            # Pluck position and frequency-dependent decay give a rounded string attack.
            x += (np.sin(np.pi*k*.24) / k**1.4 *
                  np.sin(2*np.pi*f*k*t) * np.exp(-t*(.9+k*.42)))
        x += filt(rng.normal(size=len(t)), 1800) * .008 * np.exp(-t*70)
        attack = .004
    elif kind == 'piano':
        x = np.zeros_like(t)
        for k in range(1, 10):
            fk = f*k*math.sqrt(1+.000045*k*k)
            x += (np.sin(2*np.pi*fk*t)+.3*np.sin(2*np.pi*fk*1.0007*t)) / k**1.75 * np.exp(-t*(.65+k*.35))
        x += filt(rng.normal(size=len(t)), 2100) * .009 * np.exp(-t*35)
    elif kind == 'strings':
        vibrato = .002*np.sin(2*np.pi*4.1*t) * np.minimum(t/1.8, 1)
        x = sum(np.sin(2*np.pi*f*k*t + vibrato*k)/k**1.9 for k in range(1, 7))
        x += .17*np.sin(2*np.pi*f*1.0014*t)
        attack, release = .8, .9
    elif kind == 'bass':
        x = (np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*f*2*t))*np.exp(-t*1.4)
        attack = .02
    elif kind == 'wood':
        x = (.7*np.sin(2*np.pi*710*t)+.25*np.sin(2*np.pi*1137*t)) * np.exp(-t*55)
        x += filt(rng.normal(size=len(t)), 2600)*.06*np.exp(-t*80)
        attack, release = .003, .03
    else:
        raise ValueError(kind)
    envelope = np.minimum(1, t/attack)*np.minimum(1, np.maximum(0, (duration-t)/release))
    return x*envelope


def arrange(number, bpm, bars):
    rng = np.random.default_rng(20261110 + number)
    beat = 60/bpm
    duration = bars*4*beat + (3 if number == 6 else 2)
    mix = np.zeros((round(duration*SR), 2))

    def note(pitch, start, length, gain, kind, pan=0):
        x = tone(pitch, length, kind, rng)
        i = round(start*SR)
        count = min(len(x), len(mix)-i)
        angle = (pan+1)*np.pi/4
        mix[i:i+count, 0] += x[:count]*gain*np.cos(angle)
        mix[i:i+count, 1] += x[:count]*gain*np.sin(angle)

    electronic = [(45,[57,60,64,71]), (41,[57,60,64,67]),
                  (48,[55,60,64,69]), (43,[55,59,62,69]),
                  (45,[57,60,64,71]), (50,[57,62,65,69]),
                  (43,[55,59,64,69]), (48,[55,60,64,67])]
    folk = [(48,[55,60,64,69]), (43,[55,59,62,67]),
            (41,[53,57,60,65]), (48,[55,60,64,67]),
            (50,[57,62,65,69]), (43,[55,59,62,69]),
            (48,[55,60,64,67]), (41,[57,60,65,69]),
            (43,[55,59,62,67]), (48,[55,60,64,67])]
    classical = [(48,[55,60,64]), (45,[57,60,64]), (53,[57,60,65]),
                 (50,[57,62,65]), (43,[55,59,62]), (48,[55,60,64]),
                 (48,[55,60,64])]
    for bar in range(bars):
        start = .08 + bar*4*beat
        root, chord = (electronic if number == 4 else folk if number == 5 else classical)[bar]
        closing = bar == bars-1
        tail = duration-start-.04 if closing else 4.5*beat
        if number == 4:
            # Sparse 3+3+2 accents suggest exploration without an urgent dance beat.
            note(root, start, tail, .15, 'synth', -.08)
            for k, pitch in enumerate(chord[:3]):
                note(pitch, start+.025*k, tail-.025*k, .075, 'synth', -.3+.3*k)
            if not closing:
                for off, pitch in zip([.5, 2, 3.5], [chord[3], chord[1]+12, chord[2]+12]):
                    note(pitch, start+off*beat, 1.3*beat, .065, 'synth', .25)
                for off in [0, 1.5, 3]:
                    note(root-12, start+off*beat, .25, .045, 'bass')
                if bar in (1, 3, 5):
                    note(chord[-1]+12, start+2.6*beat, 1.1*beat, .019, 'synth', -.55)
        elif number == 5:
            note(root-12, start, tail if closing else 2.6*beat, .18, 'bass', -.08)
            for off, k in zip([0, .5, 1.5, 2, 2.75, 3.5], [0, 2, 1, 3, 2, 1]):
                if closing and off > 2:
                    continue
                note(chord[k], start+off*beat+.009*k,
                     tail-off*beat-.009*k if closing else 1.75*beat,
                     .23 if off in (0, 2) else .17, 'guitar', -.3)
            if not closing:
                for off in [1, 3]:
                    note(60, start+off*beat, .16, .045, 'wood', .35)
            # The second player answers briefly, leaving room between gestures.
            if bar in (1, 3, 5, 7):
                for off, pitch in zip([.75, 2.5], [chord[2]+12, chord[1]+12]):
                    note(pitch, start+off*beat, 1.1*beat, .09, 'guitar', .34)
            if closing:
                for k, pitch in enumerate(chord):
                    note(pitch, start+2*beat+.018*k, tail-2*beat-.018*k, .1, 'guitar', .25)
        else:
            note(root, start, tail, .15, 'piano', -.22)
            for k, pitch in enumerate(chord):
                note(pitch, start+.035*k, tail-.035*k, .105, 'piano', -.2+.2*k)
            if bar in (1, 2, 4, 5, 6):
                for k, pitch in enumerate(chord[:2]):
                    note(pitch, start+.45, tail-.45, .028, 'strings', .2+k*.15)
            if not closing:
                for off, pitch in zip([1.25, 2.75], [chord[-1]+12, chord[1]+12]):
                    note(pitch, start+off*beat, 2.6*beat, .075, 'piano', .18)
    dry = mix.copy()
    reflection = np.column_stack([filt(dry[:,1], 3300), filt(dry[:,0], 3300)])
    for delay, gain in [(.031,.11),(.053,.09),(.097,.065),(.173,.04),(.283,.025)]:
        n = round(delay*SR)
        mix[n:] += reflection[:-n]*gain
    mix = np.column_stack([filt(mix[:,i], 28, 'highpass') for i in range(2)])
    n = round(.12*SR)
    mix[:n] *= np.linspace(0, 1, n)[:,None]
    n = round(1.3*SR)
    mix[-n:] *= (np.cos(np.linspace(0, np.pi/2, n))**2)[:,None]
    return mix * (.7 / np.max(np.abs(mix)))


def write(path, x):
    assert np.isfinite(x).all() and np.max(np.abs(x)) < 1, 'Invalid or clipping mix'
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x*32767).astype('<i2').tobytes())


def measure(path, target=-18):
    result = subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af',
        f'loudnorm=I={target}:TP=-3:LRA=9:print_format=json','-f','null','-'],
        capture_output=True, text=True, check=True)
    return json.loads(re.search(r'\{[^{}]+\}', result.stderr).group())


def stats(path):
    with wave.open(str(path), 'rb') as w:
        channels, bits, rate, frames = w.getnchannels(), w.getsampwidth()*8, w.getframerate(), w.getnframes()
        pcm = np.frombuffer(w.readframes(frames), dtype='<i2').reshape(-1, channels)
    x = pcm.astype(float)/32768
    silent = np.max(np.abs(pcm.astype(int)), axis=1) <= 1
    edges = np.flatnonzero(np.diff(np.r_[False, silent, False].astype(int)))
    loudness = measure(path)
    return {'file':path.name, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'duration_seconds':frames/rate, 'sample_rate':rate, 'channels':channels, 'bits':bits,
        'peak_dbfs':float(20*np.log10(np.max(np.abs(x)))),
        'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x)))),
        'integrated_lufs':float(loudness['input_i']), 'true_peak_dbtp':float(loudness['input_tp']),
        'loudness_range_lu':float(loudness['input_lra']),
        'clipped_samples':int(np.sum(np.abs(pcm.astype(int))>=32767)),
        'first_frame':pcm[0].tolist(), 'last_frame':pcm[-1].tolist(),
        'first_10ms_peak_pcm':int(np.max(np.abs(pcm[:480].astype(int)))),
        'last_10ms_peak_pcm':int(np.max(np.abs(pcm[-480:].astype(int)))),
        'max_silent_run_seconds':float(np.max(edges[1::2]-edges[::2])/rate) if len(edges) else 0,
        'max_adjacent_sample_delta':float(np.max(np.abs(np.diff(x, axis=0))))}


def main():
    references = [stats(OUT/name) for name in ('RS001_Best.wav','RS002_Good.wav','RS003_Poor.wav')]
    reports = []
    for number, filename, title, artist, bpm, bars, target in TRACKS:
        raw = OUT/'.expansion-mix.wav'
        try:
            write(raw, arrange(number, bpm, bars))
            measured = measure(raw, target)
            normalizer = (f'loudnorm=I={target}:TP=-3:LRA=9:linear=true:'
                f'measured_I={measured["input_i"]}:measured_TP={measured["input_tp"]}:'
                f'measured_LRA={measured["input_lra"]}:measured_thresh={measured["input_thresh"]}:'
                f'offset={measured["target_offset"]}')
            dest = OUT/filename
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),
                '-af',normalizer,'-ar',str(SR),'-ac','2','-c:a','pcm_s16le',str(dest)], check=True)
        finally:
            raw.unlink(missing_ok=True)
        item = stats(dest)
        assert item['clipped_samples'] == 0 and item['true_peak_dbtp'] <= -2.9, filename
        assert 25 <= item['duration_seconds'] <= 35 and item['max_silent_run_seconds'] < .2, filename
        item.update(record=f'RS{number:03}', title=title, artist=artist, bpm=bpm, bars=bars,
            seed=20261110+number, target_lufs=target, original=True,
            recommended_rpm=33, listening_review='MANUAL PENDING')
        reports.append(item)
    report = {'generator':'compose_expansion.py',
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'provenance':'All notes, rhythms and timbres synthesized locally; no downloaded audio, samples, or song references.',
        'synthesis_reference':'Existing compose_music.py envelope, additive synthesis, stereo room taps and FFmpeg loudnorm approach; never imported or modified.',
        'versions':{'numpy':np.__version__,'scipy':scipy.__version__,
                    'ffmpeg':subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]},
        'commands':['python ArtSource/Audio/Music/compose_expansion.py',
                    'python ArtSource/Audio/Music/test_compose_expansion.py'],
        'listening_review':'MANUAL PENDING: verify musical character and timbre in headphones and in-game; signal checks cannot establish subjective quality.',
        'reference_tracks':references, 'tracks':reports}
    (OUT/'expansion-audio-provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{k:item[k] for k in ('record','file','duration_seconds','peak_dbfs','rms_dbfs','integrated_lufs')} for item in reports], indent=2))


if __name__ == '__main__':
    main()

