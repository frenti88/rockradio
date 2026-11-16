#!/usr/bin/env python3
"""
ROCK RADIO — Generador de Bases Musicales Instrumentales por Género (100% Libres de Derechos)
=============================================================================================
Genera pistas instrumentales originales estéreo de 60 segundos por subgénero rock/80s/90s
para ambientar las historias de DJ Fredd con ducking cinematográfico, cumpliendo al 100%
con políticas de Spotify y derechos de autor (cero muestreo de fonogramas comerciales).
"""

import os
import subprocess
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BEDS_DIR = os.path.join(PROJECT_ROOT, 'audio', 'beds')
FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"

SR = 44100
DURATION_SEC = 64.0  # >60s para permitir distintos bed_seek_sec sin truncar los 45s


def midi_to_hz(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))


def note_name_to_hz(name):
    notes = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    if len(name) >= 2 and name[1] in ('#', 'b'):
        pitch, octave = name[:2], int(name[2:])
    else:
        pitch, octave = name[:1], int(name[1:])
    return midi_to_hz((octave + 1) * 12 + notes[pitch])


def place_mono_into_stereo(buf, start_idx, sig, pan=0.0, gain=1.0):
    """Mezcla un array mono en un buffer estéreo [N, 2] con paneo constante (-1 izq .. +1 der)."""
    if start_idx >= buf.shape[0] or len(sig) == 0:
        return
    end_idx = min(buf.shape[0], start_idx + len(sig))
    n = end_idx - start_idx
    if n <= 0:
        return
    theta = (pan + 1.0) * 0.25 * np.pi
    lg = np.cos(theta) * gain
    rg = np.sin(theta) * gain
    seg = sig[:n]
    buf[start_idx:end_idx, 0] += seg * lg
    buf[start_idx:end_idx, 1] += seg * rg


def synth_kick(dur=0.28, f_start=145.0, f_end=46.0, punch=1.0, rng=None):
    t = np.arange(int(SR * dur)) / SR
    freq = f_end + (f_start - f_end) * np.exp(-t * 38.0)
    phase = 2.0 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 11.5)
    click = np.sin(2.0 * np.pi * 1650.0 * t) * np.exp(-t * 140.0) * 0.28 * punch
    if rng is not None:
        click += rng.standard_normal(len(t)) * np.exp(-t * 180.0) * 0.12 * punch
    sig = np.tanh((body + click) * 1.45) * 0.92
    return sig


def synth_snare(dur=0.26, gated=False, tone_hz=195.0, rng=None):
    rng = rng or np.random.default_rng(42)
    t = np.arange(int(SR * dur)) / SR
    tone = (np.sin(2.0 * np.pi * tone_hz * t) + 0.45 * np.sin(2.0 * np.pi * (tone_hz * 1.68) * t)) * np.exp(-t * 24.0)
    noise = rng.standard_normal(len(t))
    # Simple 1-pole high-pass + low-pass noise shaping
    hp = np.zeros_like(noise)
    lp = np.zeros_like(noise)
    for k in (1, 2):
        noise = noise - 0.85 * np.roll(noise, k)
    hp = noise * 0.32
    if gated:
        gate_dur = 0.165
        env = np.where(t < gate_dur, np.exp(-t * 5.2), np.exp(-(t - gate_dur) * 65.0) * np.exp(-gate_dur * 5.2))
        sig = tone * 0.60 + hp * env * 0.95
    else:
        env = np.exp(-t * 16.0)
        sig = tone * 0.55 + hp * env * 0.80
    return np.tanh(sig * 1.3) * 0.72


def synth_hat(dur=0.07, open_hat=False, rng=None):
    rng = rng or np.random.default_rng(7)
    t = np.arange(int(SR * dur)) / SR
    noise = rng.standard_normal(len(t))
    metallic = (
        np.sin(2.0 * np.pi * 6240.0 * t)
        + 0.8 * np.sin(2.0 * np.pi * 7910.0 * t)
        + 0.6 * np.sin(2.0 * np.pi * 9840.0 * t)
    )
    hp_noise = noise - 0.92 * np.roll(noise, 1)
    decay = 14.0 if open_hat else 68.0
    env = np.exp(-t * decay)
    return (hp_noise * 0.35 + metallic * 0.12) * env * 0.45


def synth_crash(dur=1.4, rng=None):
    rng = rng or np.random.default_rng(9)
    t = np.arange(int(SR * dur)) / SR
    noise = rng.standard_normal(len(t))
    hp = noise - 0.90 * np.roll(noise, 1)
    shimmer = np.sin(2.0 * np.pi * 5320.0 * t) + 0.7 * np.sin(2.0 * np.pi * 7480.0 * t)
    env = (1.0 - np.exp(-t * 180.0)) * np.exp(-t * 3.1)
    return (hp * 0.38 + shimmer * 0.10) * env * 0.50


def synth_bass_note(hz, dur, drive=1.15, bright=0.35):
    t = np.arange(int(SR * dur)) / SR
    if len(t) == 0:
        return t
    attack = 1.0 - np.exp(-t * 95.0)
    decay = np.exp(-t * 2.4)
    fade_out = np.minimum(1.0, np.arange(len(t))[::-1] / max(1, int(SR * 0.015)))
    # Fundamental + 2nd + 3rd harmonic pick-bass character
    wave = (
        np.sin(2.0 * np.pi * hz * t)
        + bright * 0.55 * np.sin(2.0 * np.pi * 2.0 * hz * t) * np.exp(-t * 5.0)
        + bright * 0.25 * np.sin(2.0 * np.pi * 3.0 * hz * t) * np.exp(-t * 8.0)
    )
    return np.tanh(wave * drive) * attack * decay * fade_out * 0.55


def synth_power_chord(root_hz, dur, palm_mute=False, drive=3.2):
    t = np.arange(int(SR * dur)) / SR
    if len(t) == 0:
        return t
    freqs = [root_hz, root_hz * 1.498, root_hz * 2.0]
    raw = np.zeros_like(t)
    for idx, f in enumerate(freqs):
        w = 1.0 if idx < 2 else 0.75
        raw += w * (
            np.sin(2.0 * np.pi * f * t)
            + 0.45 * np.sin(2.0 * np.pi * 2.0 * f * t)
            + 0.20 * np.sin(2.0 * np.pi * 3.0 * f * t)
        )
    overdriven = np.tanh(raw * drive)
    if palm_mute:
        env = (1.0 - np.exp(-t * 140.0)) * np.exp(-t * 13.5)
    else:
        env = (1.0 - np.exp(-t * 80.0)) * np.exp(-t * 1.7)
    fade = np.minimum(1.0, np.arange(len(t))[::-1] / max(1, int(SR * 0.02)))
    return overdriven * env * fade * 0.36


def synth_clean_pluck(hz, dur, shimmer=True):
    t = np.arange(int(SR * dur)) / SR
    if len(t) == 0:
        return t
    wave = np.zeros_like(t)
    harmonics = [(1.0, 1.0, 2.1), (2.0, 0.52, 3.8), (3.0, 0.28, 6.0), (4.0, 0.14, 9.5)]
    for mult, amp, dec in harmonics:
        wave += amp * np.sin(2.0 * np.pi * hz * mult * t) * np.exp(-t * dec)
        if shimmer:
            wave += (amp * 0.35) * np.sin(2.0 * np.pi * (hz * mult * 1.004) * t) * np.exp(-t * dec)
    attack = 1.0 - np.exp(-t * 160.0)
    fade = np.minimum(1.0, np.arange(len(t))[::-1] / max(1, int(SR * 0.02)))
    return wave * attack * fade * 0.34


def synth_analog_pad_chord(freqs, dur, detune_cents=8.0, bright=0.45):
    t = np.arange(int(SR * dur)) / SR
    if len(t) == 0:
        return np.zeros((0, 2))
    det = 2.0 ** (detune_cents / 1200.0)
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    for f in freqs:
        for mult, amp in [(1.0, 1.0), (2.0, 0.42 * bright), (3.0, 0.20 * bright), (4.0, 0.10 * bright)]:
            left += amp * np.sin(2.0 * np.pi * (f * mult / det) * t)
            right += amp * np.sin(2.0 * np.pi * (f * mult * det) * t)
    att = 1.0 - np.exp(-t * 6.0)
    rel = np.minimum(1.0, np.arange(len(t))[::-1] / max(1, int(SR * 0.08)))
    env = att * rel
    stereo = np.stack([left * env, right * env], axis=1)
    return np.tanh(stereo * 0.55) * 0.28


def synth_analog_bass_pulse(hz, dur, resonance=0.6):
    t = np.arange(int(SR * dur)) / SR
    if len(t) == 0:
        return t
    # Rich saw-like stack with exponential filter-closing envelope
    saw = np.zeros_like(t)
    for h in range(1, 7):
        filt = np.exp(-t * (1.8 + h * 1.9))
        saw += (1.0 / h) * np.sin(2.0 * np.pi * hz * h * t) * (1.0 + resonance * filt)
    att = 1.0 - np.exp(-t * 110.0)
    fade = np.minimum(1.0, np.arange(len(t))[::-1] / max(1, int(SR * 0.012)))
    return np.tanh(saw * 0.9) * att * fade * 0.48


def render_hard_rock_bed():
    """Hard Rock Clásico (116 BPM) — Em - D - A - G (estilo AC/DC, KISS, Led Zeppelin)."""
    rng = np.random.default_rng(101)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 116.0
    eighth = beat_sec / 2.0

    kick = synth_kick(punch=1.1, rng=rng)
    snare = synth_snare(gated=False, rng=rng)
    hat_c = synth_hat(open_hat=False, rng=rng)
    hat_o = synth_hat(dur=0.18, open_hat=True, rng=rng)
    crash = synth_crash(rng=rng)

    prog = [('E2', 'E3'), ('D2', 'D3'), ('A1', 'A2'), ('G1', 'G2')]
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        chord_idx = bar % len(prog)
        bass_n, gtr_n = prog[chord_idx]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_mid = int((t0 + eighth) * SR)

        # Drums
        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.95)
        if beat_in_bar == 2 and (bar % 2 == 1):
            place_mono_into_stereo(buf, s_mid, kick, pan=0.0, gain=0.72)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.92)
        if beat_in_bar == 0 and (bar % 4 == 0):
            place_mono_into_stereo(buf, s0, crash, pan=-0.22, gain=0.45)

        place_mono_into_stereo(buf, s0, hat_c, pan=0.25, gain=0.48)
        place_mono_into_stereo(buf, s_mid, hat_o if beat_in_bar == 3 else hat_c, pan=0.25, gain=0.40)

        # Bass & Crunchy Power Guitar
        b_hz = note_name_to_hz(bass_n)
        g_hz = note_name_to_hz(gtr_n)
        if beat_in_bar == 0:
            place_mono_into_stereo(buf, s0, synth_power_chord(g_hz, beat_sec * 1.4, palm_mute=False, drive=3.4), pan=-0.35, gain=0.75)
            place_mono_into_stereo(buf, s0, synth_power_chord(g_hz, beat_sec * 1.4, palm_mute=False, drive=3.1), pan=0.35, gain=0.70)
            place_mono_into_stereo(buf, s0, synth_bass_note(b_hz, beat_sec * 0.9), pan=0.0, gain=0.88)
            place_mono_into_stereo(buf, s_mid, synth_bass_note(b_hz, eighth * 0.9), pan=0.0, gain=0.68)
        else:
            place_mono_into_stereo(buf, s0, synth_power_chord(g_hz, eighth * 0.95, palm_mute=True, drive=3.0), pan=-0.35, gain=0.58)
            place_mono_into_stereo(buf, s_mid, synth_power_chord(g_hz, eighth * 0.95, palm_mute=True, drive=3.0), pan=0.35, gain=0.58)
            place_mono_into_stereo(buf, s0, synth_bass_note(b_hz, eighth * 0.95), pan=0.0, gain=0.78)
            place_mono_into_stereo(buf, s_mid, synth_bass_note(b_hz, eighth * 0.95), pan=0.0, gain=0.72)

        # Subtle pentatonic rock guitar turnaround lick every 4th bar
        if bar % 4 == 3 and beat_in_bar >= 2:
            lick_notes = ['E4', 'G4', 'A4', 'B4'] if beat_in_bar == 2 else ['D5', 'B4', 'A4', 'G4']
            step = eighth / 2.0
            for k, ln in enumerate(lick_notes):
                sk = int((t0 + k * step) * SR)
                place_mono_into_stereo(buf, sk, synth_power_chord(note_name_to_hz(ln), step * 1.3, palm_mute=False, drive=2.6), pan=0.18, gain=0.45)

    return buf, "highpass=f=45,equalizer=f=900:width_type=o:width=1.2:g=1.5,lowpass=f=11000,aecho=0.8:0.88:35:0.18"


def render_prog_rock_bed():
    """Rock Progresivo (106 BPM) — Dm - C - Bb - A (estilo Rush, Pink Floyd, Yes)."""
    rng = np.random.default_rng(202)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 106.0
    eighth = beat_sec / 2.0

    kick = synth_kick(punch=1.0, rng=rng)
    snare = synth_snare(gated=False, tone_hz=210.0, rng=rng)
    hat_c = synth_hat(rng=rng)
    crash = synth_crash(rng=rng)

    prog = [
        ('D2', ['D4', 'F4', 'A4', 'E5'], ['D3', 'A3', 'D4', 'F4']),
        ('C2', ['C4', 'E4', 'G4', 'D5'], ['C3', 'G3', 'C4', 'E4']),
        ('Bb1', ['Bb3', 'D4', 'F4', 'C5'], ['Bb2', 'F3', 'Bb3', 'D4']),
        ('A1', ['A3', 'C#4', 'E4', 'G4'], ['A2', 'E3', 'A3', 'C#4']),
    ]
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        bass_n, pad_notes, arp_notes = prog[bar % len(prog)]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_mid = int((t0 + eighth) * SR)

        # Pad on downbeat of each bar
        if beat_in_bar == 0:
            pad_sig = synth_analog_pad_chord([note_name_to_hz(x) for x in pad_notes], beat_sec * 4.0, detune_cents=10.0, bright=0.65)
            end_s = min(n_samples, s0 + pad_sig.shape[0])
            buf[s0:end_s] += pad_sig[:end_s - s0] * 0.85
            if bar % 4 == 0:
                place_mono_into_stereo(buf, s0, crash, pan=-0.25, gain=0.40)

        # Prog drums with syncopation on beat 2.5
        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.90)
        if beat_in_bar == 2:
            place_mono_into_stereo(buf, s_mid, kick, pan=0.0, gain=0.75)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.88)
        place_mono_into_stereo(buf, s0, hat_c, pan=0.22, gain=0.44)
        place_mono_into_stereo(buf, s_mid, hat_c, pan=0.22, gain=0.35)

        # Oberheim-style analog bass + clean prog guitar arpeggio
        b_hz = note_name_to_hz(bass_n)
        place_mono_into_stereo(buf, s0, synth_analog_bass_pulse(b_hz, eighth * 0.92, resonance=0.8), pan=0.0, gain=0.85)
        place_mono_into_stereo(buf, s_mid, synth_analog_bass_pulse(b_hz * (2.0 if beat_in_bar == 3 else 1.0), eighth * 0.92, resonance=0.7), pan=0.0, gain=0.65)

        arp_a = note_name_to_hz(arp_notes[beat_in_bar % len(arp_notes)])
        arp_b = note_name_to_hz(arp_notes[(beat_in_bar + 1) % len(arp_notes)])
        place_mono_into_stereo(buf, s0, synth_clean_pluck(arp_a, beat_sec * 0.9, shimmer=True), pan=-0.30, gain=0.62)
        place_mono_into_stereo(buf, s_mid, synth_clean_pluck(arp_b, beat_sec * 0.9, shimmer=True), pan=0.30, gain=0.58)

    return buf, "highpass=f=45,lowpass=f=12500,aecho=0.8:0.88:55|85:0.22|0.16"


def render_synth_pop_80s_bed():
    """Synth-Pop / New Wave 80s Shuffle (114 BPM) — D - G - Bm - A (Tears for Fears, The Cars, Alphaville)."""
    rng = np.random.default_rng(303)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 114.0
    shuffle_off = beat_sec * 0.66  # Classic 80s shuffle pocket

    kick = synth_kick(f_start=135.0, f_end=48.0, punch=0.95, rng=rng)
    snare = synth_snare(gated=True, tone_hz=200.0, rng=rng)
    hat_c = synth_hat(rng=rng)
    hat_o = synth_hat(dur=0.14, open_hat=True, rng=rng)
    crash = synth_crash(rng=rng)

    prog = [
        ('D2', ['D4', 'F#4', 'A4', 'E5'], ['D4', 'A4', 'F#4', 'A4']),
        ('G2', ['G3', 'B3', 'D4', 'A4'], ['G4', 'D4', 'B4', 'D4']),
        ('B1', ['B3', 'D4', 'F#4', 'A4'], ['B3', 'F#4', 'D4', 'F#4']),
        ('A1', ['A3', 'C#4', 'E4', 'B4'], ['A3', 'E4', 'C#4', 'E4']),
    ]
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        bass_n, pad_notes, pluck_notes = prog[bar % len(prog)]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_shuf = int((t0 + shuffle_off) * SR)

        if beat_in_bar == 0:
            pad_sig = synth_analog_pad_chord([note_name_to_hz(x) for x in pad_notes], beat_sec * 4.0, detune_cents=9.0, bright=0.55)
            end_s = min(n_samples, s0 + pad_sig.shape[0])
            buf[s0:end_s] += pad_sig[:end_s - s0] * 0.78
            if bar % 4 == 0:
                place_mono_into_stereo(buf, s0, crash, pan=-0.20, gain=0.35)

        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.90)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.86)
        place_mono_into_stereo(buf, s0, hat_c, pan=0.25, gain=0.45)
        place_mono_into_stereo(buf, s_shuf, hat_o if beat_in_bar == 3 else hat_c, pan=0.25, gain=0.34)

        b_hz = note_name_to_hz(bass_n)
        place_mono_into_stereo(buf, s0, synth_analog_bass_pulse(b_hz, beat_sec * 0.55, resonance=0.5), pan=0.0, gain=0.78)
        place_mono_into_stereo(buf, s_shuf, synth_analog_bass_pulse(b_hz * 2.0, beat_sec * 0.32, resonance=0.5), pan=0.0, gain=0.56)

        p1 = note_name_to_hz(pluck_notes[beat_in_bar % len(pluck_notes)])
        p2 = note_name_to_hz(pluck_notes[(beat_in_bar + 1) % len(pluck_notes)])
        place_mono_into_stereo(buf, s0, synth_clean_pluck(p1, beat_sec * 0.85, shimmer=True), pan=-0.35, gain=0.68)
        place_mono_into_stereo(buf, s_shuf, synth_clean_pluck(p2, beat_sec * 0.65, shimmer=True), pan=0.35, gain=0.58)

    return buf, "highpass=f=45,lowpass=f=13000,aecho=0.8:0.88:45|75:0.20|0.14"


def render_arena_rock_80s_bed():
    """Arena / Stadium / Glam Rock 80s (106 BPM) — C - G - Am - F (Queen, Def Leppard, Bon Jovi)."""
    rng = np.random.default_rng(404)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 106.0
    eighth = beat_sec / 2.0

    kick = synth_kick(f_start=150.0, f_end=45.0, punch=1.15, rng=rng)
    snare = synth_snare(gated=True, tone_hz=185.0, rng=rng)
    hat_c = synth_hat(rng=rng)
    crash = synth_crash(rng=rng)

    prog = [
        ('C2', 'C3', ['C4', 'E4', 'G4', 'D5'], ['C4', 'G4', 'E4', 'G4']),
        ('G1', 'G2', ['G3', 'B3', 'D4', 'A4'], ['G4', 'D4', 'B4', 'D4']),
        ('A1', 'A2', ['A3', 'C4', 'E4', 'G4'], ['A3', 'E4', 'C4', 'E4']),
        ('F1', 'F2', ['F3', 'A3', 'C4', 'G4'], ['F4', 'C4', 'A4', 'C4']),
    ]
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        bass_n, gtr_n, pad_notes, chime_notes = prog[bar % len(prog)]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_mid = int((t0 + eighth) * SR)

        if beat_in_bar == 0:
            pad_sig = synth_analog_pad_chord([note_name_to_hz(x) for x in pad_notes], beat_sec * 4.0, detune_cents=12.0, bright=0.65)
            end_s = min(n_samples, s0 + pad_sig.shape[0])
            buf[s0:end_s] += pad_sig[:end_s - s0] * 0.85
            if bar % 2 == 0:
                place_mono_into_stereo(buf, s0, crash, pan=0.22, gain=0.42)
            # Anthemic guitar chord swell on bar start
            place_mono_into_stereo(buf, s0, synth_power_chord(note_name_to_hz(gtr_n), beat_sec * 2.2, palm_mute=False, drive=2.5), pan=-0.38, gain=0.58)

        # Stadium stomp beat (boom-boom-clap/snare feel)
        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.98)
        if beat_in_bar == 0:
            place_mono_into_stereo(buf, s_mid, kick, pan=0.0, gain=0.72)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.95)
        place_mono_into_stereo(buf, s0, hat_c, pan=0.20, gain=0.42)
        place_mono_into_stereo(buf, s_mid, hat_c, pan=0.20, gain=0.36)

        b_hz = note_name_to_hz(bass_n)
        place_mono_into_stereo(buf, s0, synth_bass_note(b_hz, eighth * 0.92, drive=1.2, bright=0.4), pan=0.0, gain=0.84)
        place_mono_into_stereo(buf, s_mid, synth_bass_note(b_hz, eighth * 0.92, drive=1.2, bright=0.4), pan=0.0, gain=0.76)

        c1 = note_name_to_hz(chime_notes[beat_in_bar % len(chime_notes)])
        c2 = note_name_to_hz(chime_notes[(beat_in_bar + 1) % len(chime_notes)])
        place_mono_into_stereo(buf, s0, synth_clean_pluck(c1, beat_sec * 0.85, shimmer=True), pan=0.35, gain=0.60)
        place_mono_into_stereo(buf, s_mid, synth_clean_pluck(c2, beat_sec * 0.70, shimmer=True), pan=-0.25, gain=0.52)

    return buf, "highpass=f=45,lowpass=f=12500,aecho=0.8:0.88:50|80:0.22|0.15"


def render_heavy_metal_bed():
    """Heavy Metal 80s (130 BPM) — Em - C - D - Bm (Dokken, Iron Maiden, Metallica, Black Sabbath)."""
    rng = np.random.default_rng(505)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 130.0
    eighth = beat_sec / 2.0
    sixteenth = beat_sec / 4.0

    kick = synth_kick(f_start=155.0, f_end=48.0, punch=1.25, rng=rng)
    snare = synth_snare(gated=True, tone_hz=205.0, rng=rng)
    hat_c = synth_hat(rng=rng)
    crash = synth_crash(rng=rng)

    prog = [('E2', 'E3'), ('C2', 'C3'), ('D2', 'D3'), ('B1', 'B2')]
    riff_melody = ['E4', 'G4', 'F#4', 'E4', 'B4', 'A4', 'G4', 'F#4']
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        bass_n, gtr_n = prog[bar % len(prog)]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_mid = int((t0 + eighth) * SR)
        s_gal = int((t0 + eighth + sixteenth) * SR)

        # Tight metal kick gallop + snappy snare
        place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.92 if beat_in_bar in (0, 2) else 0.65)
        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s_gal, kick, pan=0.0, gain=0.72)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.92)
        if beat_in_bar == 0 and (bar % 4 == 0):
            place_mono_into_stereo(buf, s0, crash, pan=-0.25, gain=0.45)
        place_mono_into_stereo(buf, s0, hat_c, pan=0.28, gain=0.45)
        place_mono_into_stereo(buf, s_mid, hat_c, pan=0.28, gain=0.38)

        b_hz = note_name_to_hz(bass_n)
        g_hz = note_name_to_hz(gtr_n)
        # Gallop bass & twin-panned palm-muted rhythm guitars
        place_mono_into_stereo(buf, s0, synth_bass_note(b_hz, eighth * 0.9, drive=1.4, bright=0.55), pan=0.0, gain=0.86)
        place_mono_into_stereo(buf, s_mid, synth_bass_note(b_hz, sixteenth * 0.95, drive=1.4, bright=0.55), pan=0.0, gain=0.74)
        place_mono_into_stereo(buf, s_gal, synth_bass_note(b_hz, sixteenth * 0.95, drive=1.4, bright=0.55), pan=0.0, gain=0.78)

        mute = beat_in_bar != 0
        place_mono_into_stereo(buf, s0, synth_power_chord(g_hz, beat_sec * (0.95 if not mute else 0.45), palm_mute=mute, drive=3.8), pan=-0.42, gain=0.68)
        place_mono_into_stereo(buf, s0, synth_power_chord(g_hz, beat_sec * (0.95 if not mute else 0.45), palm_mute=mute, drive=3.6), pan=0.42, gain=0.68)
        place_mono_into_stereo(buf, s_mid, synth_power_chord(g_hz, sixteenth * 0.9, palm_mute=True, drive=3.5), pan=-0.40, gain=0.55)
        place_mono_into_stereo(buf, s_gal, synth_power_chord(g_hz, sixteenth * 0.9, palm_mute=True, drive=3.5), pan=0.40, gain=0.55)

        # Harmonized 80s twin-lead motif on alternating bars
        if bar % 2 == 1:
            ln = riff_melody[(beat_in_bar * 2) % len(riff_melody)]
            l_hz = note_name_to_hz(ln)
            place_mono_into_stereo(buf, s0, synth_power_chord(l_hz, beat_sec * 0.85, palm_mute=False, drive=2.6), pan=-0.20, gain=0.38)
            place_mono_into_stereo(buf, s0, synth_power_chord(l_hz * 1.189, beat_sec * 0.85, palm_mute=False, drive=2.4), pan=0.20, gain=0.30)

    return buf, "highpass=f=50,equalizer=f=1200:width_type=o:width=1.2:g=1.6,lowpass=f=11500,aecho=0.8:0.88:32:0.16"


def render_pop_rock_90s_bed():
    """New Wave / Pop-Rock Atmosférico (96 BPM) — Bm - G - D - A (Duran Duran, U2, The Police)."""
    rng = np.random.default_rng(606)
    n_samples = int(SR * DURATION_SEC)
    buf = np.zeros((n_samples, 2), dtype=np.float64)
    beat_sec = 60.0 / 96.0
    eighth = beat_sec / 2.0

    kick = synth_kick(f_start=125.0, f_end=46.0, punch=0.85, rng=rng)
    snare = synth_snare(gated=False, tone_hz=185.0, rng=rng)
    hat_c = synth_hat(rng=rng)
    crash = synth_crash(rng=rng)

    prog = [
        ('B1', ['B3', 'D4', 'F#4', 'A4'], ['B3', 'F#4', 'D4', 'A4']),
        ('G1', ['G3', 'B3', 'D4', 'F#4'], ['G3', 'D4', 'B3', 'F#4']),
        ('D2', ['D4', 'F#4', 'A4', 'E5'], ['D4', 'A4', 'F#4', 'E5']),
        ('A1', ['A3', 'C#4', 'E4', 'B4'], ['A3', 'E4', 'C#4', 'B4']),
    ]
    total_beats = int(DURATION_SEC / beat_sec)

    for b in range(total_beats):
        bar = b // 4
        beat_in_bar = b % 4
        bass_n, pad_notes, arp_notes = prog[bar % len(prog)]
        t0 = b * beat_sec
        s0 = int(t0 * SR)
        s_mid = int((t0 + eighth) * SR)

        if beat_in_bar == 0:
            pad_sig = synth_analog_pad_chord([note_name_to_hz(x) for x in pad_notes], beat_sec * 4.0, detune_cents=11.0, bright=0.45)
            end_s = min(n_samples, s0 + pad_sig.shape[0])
            buf[s0:end_s] += pad_sig[:end_s - s0] * 0.88
            if bar % 4 == 0:
                place_mono_into_stereo(buf, s0, crash, pan=0.20, gain=0.32)

        if beat_in_bar == 0:
            place_mono_into_stereo(buf, s0, kick, pan=0.0, gain=0.88)
        elif beat_in_bar == 2:
            place_mono_into_stereo(buf, s_mid, kick, pan=0.0, gain=0.76)
        if beat_in_bar in (1, 3):
            place_mono_into_stereo(buf, s0, snare, pan=0.0, gain=0.80)
        place_mono_into_stereo(buf, s0, hat_c, pan=0.22, gain=0.38)
        place_mono_into_stereo(buf, s_mid, hat_c, pan=0.22, gain=0.30)

        b_hz = note_name_to_hz(bass_n)
        if beat_in_bar in (0, 2):
            place_mono_into_stereo(buf, s0, synth_bass_note(b_hz, beat_sec * 1.4, drive=1.05, bright=0.25), pan=0.0, gain=0.82)

        a1 = note_name_to_hz(arp_notes[beat_in_bar % len(arp_notes)])
        a2 = note_name_to_hz(arp_notes[(beat_in_bar + 1) % len(arp_notes)])
        place_mono_into_stereo(buf, s0, synth_clean_pluck(a1, beat_sec * 1.1, shimmer=True), pan=-0.34, gain=0.72)
        place_mono_into_stereo(buf, s_mid, synth_clean_pluck(a2, beat_sec * 0.9, shimmer=True), pan=0.34, gain=0.64)

    return buf, "highpass=f=45,lowpass=f=12500,aecho=0.8:0.88:55|90:0.24|0.18"


GENRE_RENDERERS = {
    "hard_rock": render_hard_rock_bed,
    "prog_rock": render_prog_rock_bed,
    "synth_pop_80s": render_synth_pop_80s_bed,
    "arena_rock_80s": render_arena_rock_80s_bed,
    "heavy_metal": render_heavy_metal_bed,
    "pop_rock_90s": render_pop_rock_90s_bed,
}


def build_bed_file(genre_key, force=False):
    os.makedirs(BEDS_DIR, exist_ok=True)
    out_mp3 = os.path.join(BEDS_DIR, f"bed_{genre_key}.mp3")
    if not force and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 50000:
        return out_mp3

    renderer = GENRE_RENDERERS[genre_key]
    buf, post_fx = renderer()
    peak = float(np.max(np.abs(buf))) or 1.0
    buf = (buf / peak) * 0.88
    pcm = np.clip(buf * 32767.0, -32768, 32767).astype(np.int16)

    tmp_wav = os.path.join(BEDS_DIR, f".tmp_bed_{genre_key}.wav")
    tmp_mp3 = os.path.join(BEDS_DIR, f".tmp_bed_{genre_key}.mp3")
    import wave
    with wave.open(tmp_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    af = f"{post_fx},loudnorm=I=-11.5:TP=-1.5:LRA=5"
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", tmp_wav,
        "-af", af,
        "-codec:a", "libmp3lame", "-b:a", "192k",
        tmp_mp3
    ], capture_output=True, check=True)
    os.replace(tmp_mp3, out_mp3)
    if os.path.exists(tmp_wav):
        os.remove(tmp_wav)
    return out_mp3


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for gk in GENRE_RENDERERS:
        p = build_bed_file(gk, force=args.force)
        print(f"✅ Base instrumental [{gk}] -> {os.path.relpath(p, PROJECT_ROOT)} ({os.path.getsize(p)} bytes)")
