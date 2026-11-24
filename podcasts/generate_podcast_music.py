#!/usr/bin/env python3
"""
Generates a studio-quality Morning-Show / Editorial Jazz-Pop instrumental
music bed for Aparte podcasts (110 BPM, F Major):
  - Stereo Fender Rhodes electric piano (FM tine + warm body + tremolo)
  - Syncopated warm electric bass groove
  - Soft muted guitar off-beat comping
  - Studio light drums (soft kick, cross-stick rimshot, swung shaker/hi-hat)
  - Subtle marimba/vibraphone motif alternating across A/B sections

Outputs:
  - podcasts/aparte_morning_bed.mp3 (standalone 2-minute instrumental master)
  - Helper function render_bed_wav(out_wav, duration_sec) for full-episode mixing
"""
import subprocess
import wave
from pathlib import Path
import numpy as np

REPO = Path("/home/antigravity/frenti88/rockradio")
OUT_DIR = REPO / "podcasts"


def midi_to_hz(m: float) -> float:
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))


def rhodes_note(freq: float, dur_s: float, sr: int, vel: float = 0.7) -> np.ndarray:
    """Warm FM Fender Rhodes electric piano tone (body + soft bell tine)."""
    n = int(dur_s * sr)
    t = np.arange(n, dtype=np.float32) / sr
    # Attack + natural decay
    env_body = (1.0 - np.exp(-t * 90.0)) * np.exp(-t * 1.45)
    env_tine = (1.0 - np.exp(-t * 180.0)) * np.exp(-t * 8.5)
    # FM tine modulation
    mod = np.sin(2.0 * np.pi * (freq * 7.0) * t) * env_tine * 0.35
    body = (
        np.sin(2.0 * np.pi * freq * t + mod)
        + 0.25 * np.sin(2.0 * np.pi * (freq * 2.0) * t) * np.exp(-t * 2.5)
        + 0.08 * np.sin(2.0 * np.pi * (freq * 3.0) * t) * np.exp(-t * 4.5)
    )
    return (body * env_body * vel).astype(np.float32)


def bass_note(freq: float, dur_s: float, sr: int, vel: float = 0.8) -> np.ndarray:
    """Warm round electric bass with gentle pluck."""
    n = int(dur_s * sr)
    t = np.arange(n, dtype=np.float32) / sr
    env = (1.0 - np.exp(-t * 110.0)) * np.exp(-t * 2.8)
    sig = (
        0.78 * np.sin(2.0 * np.pi * freq * t)
        + 0.28 * np.sin(2.0 * np.pi * (freq * 2.0) * t) * np.exp(-t * 5.0)
        + 0.10 * np.sin(2.0 * np.pi * (freq * 3.0) * t) * np.exp(-t * 9.0)
    )
    return (sig * env * vel).astype(np.float32)


def marimba_note(freq: float, dur_s: float, sr: int, vel: float = 0.5) -> np.ndarray:
    """Soft woody marimba / vibraphone mallet hit."""
    n = int(dur_s * sr)
    t = np.arange(n, dtype=np.float32) / sr
    env = (1.0 - np.exp(-t * 260.0)) * np.exp(-t * 6.5)
    sig = (
        0.85 * np.sin(2.0 * np.pi * freq * t)
        + 0.22 * np.sin(2.0 * np.pi * (freq * 4.0) * t) * np.exp(-t * 18.0)
    )
    return (sig * env * vel).astype(np.float32)


def muted_guitar_strum(freqs: list, sr: int, vel: float = 0.35) -> np.ndarray:
    """Short percussive muted guitar comping chord."""
    dur_s = 0.14
    n = int(dur_s * sr)
    t = np.arange(n, dtype=np.float32) / sr
    env = (1.0 - np.exp(-t * 300.0)) * np.exp(-t * 26.0)
    sig = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        delay = int(i * 0.004 * sr)
        if delay < n:
            tt = t[: n - delay]
            tone = np.sin(2.0 * np.pi * f * tt) + 0.4 * np.sin(2.0 * np.pi * f * 2.0 * tt)
            sig[delay:] += tone * env[: n - delay]
    return (sig / max(1, len(freqs)) * vel).astype(np.float32)


def synth_kick(sr: int) -> np.ndarray:
    n = int(0.18 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    pitch = 48.0 + 75.0 * np.exp(-t * 36.0)
    phase = 2.0 * np.pi * np.cumsum(pitch) / sr
    env = (1.0 - np.exp(-t * 400.0)) * np.exp(-t * 16.0)
    return (np.sin(phase) * env * 0.65).astype(np.float32)


def synth_rimshot(sr: int, rng: np.random.Generator) -> np.ndarray:
    n = int(0.08 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    click = np.sin(2.0 * np.pi * 1650.0 * t) * np.exp(-t * 65.0)
    body = np.sin(2.0 * np.pi * 420.0 * t) * np.exp(-t * 42.0)
    noise = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 70.0) * 0.25
    return ((0.45 * click + 0.35 * body + noise) * 0.42).astype(np.float32)


def synth_shaker(sr: int, rng: np.random.Generator, accent: float = 1.0) -> np.ndarray:
    n = int(0.055 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    noise = rng.standard_normal(n).astype(np.float32)
    # Simple high-pass via first difference
    hp = np.diff(noise, prepend=0.0)
    env = (1.0 - np.exp(-t * 200.0)) * np.exp(-t * 48.0)
    return (hp * env * 0.14 * accent).astype(np.float32)


def add_stereo(buf: np.ndarray, start: int, mono: np.ndarray, pan: float = 0.0):
    """Add mono clip into stereo buffer with equal-power pan (-1..+1)."""
    if start >= len(buf) or start < 0:
        return
    end = min(len(buf), start + len(mono))
    seg = mono[: end - start]
    angle = (pan + 1.0) * (np.pi / 4.0)
    buf[start:end, 0] += seg * np.cos(angle)
    buf[start:end, 1] += seg * np.sin(angle)


def render_bed_wav(out_wav: Path, duration_sec: float, sr: int = 48000):
    custom_mp3 = OUT_DIR / "aparte_custom_bed.mp3"
    if custom_mp3.exists() and custom_mp3.stat().st_size > 10000:
        tmp_src = Path("/tmp/aparte_custom_bed_48k.wav")
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(custom_mp3),
                "-ar", str(sr), "-ac", "2",
                str(tmp_src),
            ],
            check=True,
        )
        with wave.open(str(tmp_src), "rb") as wf:
            raw = wf.readframes(wf.getnframes())
            src = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)

        total_samples = int(duration_sec * sr)
        xfade = min(int(3.0 * sr), len(src) // 4)
        step = len(src) - xfade
        out = np.zeros((total_samples, 2), dtype=np.float32)

        pos = 0
        first = True
        while pos < total_samples:
            chunk = src.copy()
            if not first and xfade > 0:
                ramp_in = np.linspace(0.0, 1.0, xfade, dtype=np.float32)[:, None]
                chunk[:xfade] *= ramp_in
            if pos + len(chunk) < total_samples and xfade > 0:
                ramp_out = np.linspace(1.0, 0.0, xfade, dtype=np.float32)[:, None]
                chunk[-xfade:] *= ramp_out
            end = min(total_samples, pos + len(chunk))
            out[pos:end] += chunk[: end - pos]
            pos += step
            first = False

        t_all = np.arange(total_samples, dtype=np.float32) / sr
        fade_in = np.minimum(1.0, t_all / 1.8)
        fade_out = np.minimum(1.0, np.maximum(0.0, (duration_sec - t_all) / 3.0))
        out *= (fade_in * fade_out)[:, None]

        peak = np.max(np.abs(out)) + 1e-9
        if peak > 0.95:
            out *= 0.95 / peak
        pcm = (np.clip(out, -1.0, 1.0) * 32767.0).astype(np.int16)
        with wave.open(str(out_wav), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())
        return

    rng = np.random.default_rng(2027)
    bpm = 110.0
    beat_s = 60.0 / bpm
    bar_s = beat_s * 4.0
    total_samples = int(duration_sec * sr)
    stereo = np.zeros((total_samples, 2), dtype=np.float32)

    # 8-bar uplifting Morning-Show Jazz-Pop progression in F Major:
    # (bass_midi, chord_midis, motif_midis)
    PROG = [
        (41, [53, 57, 60, 64, 67], [72, 74, 76, 72]),  # Fmaj9
        (38, [50, 57, 60, 64, 65], [69, 72, 74, 69]),  # Dm9
        (43, [55, 58, 62, 65, 69], [70, 72, 74, 77]),  # Gm9
        (48, [52, 58, 62, 67, 69], [76, 74, 72, 70]),  # C13
        (45, [55, 60, 64, 67, 72], [72, 76, 79, 76]),  # Am7
        (38, [54, 57, 60, 64, 69], [74, 72, 69, 66]),  # D9
        (43, [55, 58, 62, 65, 69], [70, 74, 77, 74]),  # Gm9
        (48, [53, 58, 62, 65, 67], [72, 70, 69, 67]),  # C9sus4
    ]

    kick = synth_kick(sr)
    rim = synth_rimshot(sr, rng)

    num_bars = int(np.ceil(duration_sec / bar_s))
    for bar in range(num_bars):
        bar_t = bar * bar_s
        bass_m, chord_ms, motif_ms = PROG[bar % len(PROG)]
        section_b = (bar // 8) % 2 == 1  # Alternate richer B-section every 8 bars

        # 1. Rhodes electric piano: beat 1 + syncopated beat 2.5
        for b_off, vel, dur_mult in [(0.0, 0.22, 2.2), (2.5, 0.16, 1.5)]:
            t_start = int((bar_t + b_off * beat_s) * sr)
            for idx, m in enumerate(chord_ms):
                note = rhodes_note(midi_to_hz(m), dur_mult * beat_s, sr, vel=vel / len(chord_ms) * 2.2)
                pan = -0.35 + (idx / max(1, len(chord_ms) - 1)) * 0.70
                add_stereo(stereo, t_start + int(idx * 0.008 * sr), note, pan=pan)

        # 2. Warm electric bass groove (beats 1, 2.5, 3.5)
        bass_pattern = [
            (0.0, bass_m, 0.42, 1.3),
            (2.5, bass_m + 7, 0.32, 0.7),
            (3.5, bass_m + 12 if bar % 2 == 0 else bass_m + 5, 0.30, 0.45),
        ]
        for b_off, bm, vel, d_b in bass_pattern:
            bn = bass_note(midi_to_hz(bm), d_b * beat_s, sr, vel=vel)
            add_stereo(stereo, int((bar_t + b_off * beat_s) * sr), bn, pan=-0.05)

        # 3. Soft muted guitar off-beats (1.5, 3.5)
        g_freqs = [midi_to_hz(m) for m in chord_ms[1:4]]
        for b_off in (1.5, 3.5):
            strum = muted_guitar_strum(g_freqs, sr, vel=0.18)
            add_stereo(stereo, int((bar_t + b_off * beat_s) * sr), strum, pan=0.35)

        # 4. Studio drums: kick (1, 3, and light 2.75), rimshot (2, 4), swung shaker
        for b_off, g_k in [(0.0, 0.55), (2.0, 0.48), (2.75, 0.28)]:
            add_stereo(stereo, int((bar_t + b_off * beat_s) * sr), kick * g_k, pan=0.0)
        for b_off in (1.0, 3.0):
            add_stereo(stereo, int((bar_t + b_off * beat_s) * sr), rim, pan=-0.12)
        for step in range(8):
            swing = 0.03 * beat_s if step % 2 == 1 else 0.0
            acc = 1.0 if step % 2 == 0 else 0.55
            sh = synth_shaker(sr, rng, accent=acc)
            add_stereo(stereo, int((bar_t + step * 0.5 * beat_s + swing) * sr), sh, pan=0.22)

        # 5. Subtle marimba motif on B-sections (and first 2 bars intro)
        if section_b or bar < 2:
            for i, b_off in enumerate((0.5, 1.5, 2.5, 3.25)):
                mn = marimba_note(midi_to_hz(motif_ms[i]), 0.45 * beat_s, sr, vel=0.14)
                add_stereo(stereo, int((bar_t + b_off * beat_s) * sr), mn, pan=-0.28 if i % 2 == 0 else 0.28)

    # Gentle stereo tremolo on overall pad feel + fade in/out
    t_all = np.arange(total_samples, dtype=np.float32) / sr
    fade_in = np.minimum(1.0, t_all / 1.8)
    fade_out = np.minimum(1.0, np.maximum(0.0, (duration_sec - t_all) / 3.0))
    env = (fade_in * fade_out)[:, None]
    stereo *= env

    peak = np.max(np.abs(stereo)) + 1e-9
    stereo = stereo * (0.88 / peak)

    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def main():
    tmp_wav = Path("/tmp/aparte_morning_bed_master.wav")
    out_mp3 = OUT_DIR / "aparte_morning_bed.mp3"
    print("[MUSIC] Rendering 2-minute Morning-Show Jazz-Pop instrumental bed...", flush=True)
    render_bed_wav(tmp_wav, 120.0)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_wav),
            "-af", "aecho=0.8:0.88:28|42:0.18|0.12,loudnorm=I=-16:TP=-1.0:LRA=9",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(out_mp3),
        ],
        check=True,
    )
    print(f"DONE! {out_mp3} ({out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
