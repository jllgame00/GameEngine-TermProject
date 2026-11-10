"""Run from the project root; rebuilds only RS004/5/6 twice to check reproducibility."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import wave
import numpy as np

ROOT = Path(__file__).resolve().parent


def check():
    source = ROOT / 'compose_expansion.py'
    assert source.exists(), 'Independent expansion generator is not implemented'
    originals = [ROOT / name for name in ('compose_music.py', 'RS001_Best.wav',
                 'RS002_Good.wav', 'RS003_Poor.wav')]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {p: digest(p) for p in originals}
    spec = importlib.util.spec_from_file_location('expansion', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for kind in ('synth', 'guitar', 'piano', 'strings', 'bass', 'wood'):
        x = module.tone(60, .8, kind, np.random.default_rng(1))
        assert x.shape == (38400,) and np.isfinite(x).all(), kind
        assert x[0] == 0 and abs(x[-1]) < .001, kind
        assert np.array_equal(x, module.tone(60, .8, kind, np.random.default_rng(1)))
    try:
        module.tone(60, .8, 'missing', np.random.default_rng(1))
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown instrument must fail')
    for iteration in range(2):
        subprocess.run([sys.executable, str(source)], check=True)
        report = json.loads((ROOT / 'expansion-audio-provenance.json').read_text(encoding='utf-8'))
        hashes = {}
        for item in report['tracks']:
            path = ROOT / item['file']
            hashes[path.name] = digest(path)
            with wave.open(str(path), 'rb') as w:
                assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (2, 2, 48000)
                x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2)
                assert 25 <= w.getnframes() / w.getframerate() <= 35
            assert np.max(np.abs(x.astype(int))) < 32767, path.name
            assert not x[0].any() and not x[-1].any(), path.name
            assert np.max(np.abs(x[:48].astype(int))) <= 2, path.name
            assert -20 <= item['integrated_lufs'] <= -17, path.name
            assert item['max_silent_run_seconds'] < .2, path.name
        if iteration == 0:
            first = hashes
        else:
            assert hashes == first, 'PCM generation is not reproducible'
    assert {p: digest(p) for p in originals} == before, 'Original sources changed'
    verification = {'status': 'PASS', 'generator_runs': 2,
        'reproducible_wav_sha256': first,
        'original_sources_unchanged_sha256': {p.name: value for p, value in before.items()},
        'test_sha256': digest(Path(__file__)),
        'checks': ['six instrument envelopes and seed repeatability', 'unknown instrument rejection',
                   'stereo 48000 Hz PCM16', '25-35 second duration', 'zero clipping',
                   'zero endpoints and quiet first millisecond', 'integrated LUFS -20 to -17',
                   'no silent run of 200 ms', 'two byte-identical generator rebuilds',
                   'four original source hashes unchanged'],
        'listening_review': 'MANUAL PENDING'}
    (ROOT / 'expansion-audio-verification.json').write_text(
        json.dumps(verification, indent=2)+'\n', encoding='utf-8')
    print('PASS: six instruments, invalid instrument, WAV format/levels/endpoints, '
          'two identical rebuilds, four original source hashes unchanged')
    print(json.dumps(first, indent=2))


if __name__ == '__main__':
    check()
