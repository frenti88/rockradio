#!/usr/bin/env python3
"""
Humanized Podcast Narration Engine for Fish Audio (Drama 3 / S2 family).

Designed to transform written scripts into natural, unhurried, conversational
spoken podcasts while preserving the exact vocal identity, timbre, accent,
and register of the cloned voice model.

Key capabilities:
- Uses Fish Audio native prosody (speed, volume, normalize_loudness=False),
  contextual continuity (condition_on_previous_chunks=True, chunk_length=300),
  BCP-47 language hinting ("es"), lossless WAV retrieval, and Drama 3 inline
  expressive markers.
- Processes text in coherent multi-sentence narrative units (never arbitrary
  single-sentence splits) with per-unit caching for selective regeneration.
- Intent-driven pacing, moderate dynamic volume shifts, and post-production
  pause calibration (gentling rushed internal silences + exact semantic pauses
  between units).
- Wide-dynamic-range mastering (LRA=15, -16 LUFS) that preserves intimate
  reflections and emphatic conclusions without flattening them.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

SR = 48000
DEFAULT_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
DEFAULT_MODEL_ID = "drama-3"


@dataclass(frozen=True)
class IntentProfile:
    """Prosody & sampling configuration for a communicative intent."""
    speed: float          # Fish Audio prosody.speed (0.5 - 2.0)
    volume_db: float      # Moderate dynamic intensity shift in dB
    temperature: float    # Expressiveness (0.0 - 1.0)
    top_p: float          # Nucleus sampling diversity
    min_internal_gap_ms: int   # Target minimum pause when Fish rushes punctuation
    extra_internal_ms: int     # Gentle breathing room added to detected sentence pauses


# Subtle, human prosody profiles — never theatrical or commercial announcer style.
# All variations act on pacing, intensity and intention, never altering vocal identity.
INTENT_PROFILES: Dict[str, IntentProfile] = {
    "conversational": IntentProfile(
        speed=0.93, volume_db=0.0, temperature=0.68, top_p=0.79,
        min_internal_gap_ms=260, extra_internal_ms=110,
    ),
    "reflective": IntentProfile(
        speed=0.88, volume_db=-1.2, temperature=0.66, top_p=0.78,
        min_internal_gap_ms=300, extra_internal_ms=180,
    ),
    "intimate": IntentProfile(
        speed=0.87, volume_db=-1.6, temperature=0.65, top_p=0.77,
        min_internal_gap_ms=320, extra_internal_ms=200,
    ),
    "question": IntentProfile(
        speed=0.91, volume_db=-0.3, temperature=0.72, top_p=0.81,
        min_internal_gap_ms=280, extra_internal_ms=160,
    ),
    "discovery": IntentProfile(
        speed=0.95, volume_db=0.9, temperature=0.73, top_p=0.82,
        min_internal_gap_ms=240, extra_internal_ms=95,
    ),
    "revelation": IntentProfile(
        speed=0.91, volume_db=1.4, temperature=0.71, top_p=0.80,
        min_internal_gap_ms=270, extra_internal_ms=140,
    ),
    "conclusion": IntentProfile(
        speed=0.90, volume_db=1.3, temperature=0.67, top_p=0.78,
        min_internal_gap_ms=290, extra_internal_ms=170,
    ),
    "transition": IntentProfile(
        speed=0.92, volume_db=-0.2, temperature=0.68, top_p=0.79,
        min_internal_gap_ms=260, extra_internal_ms=120,
    ),
}


@dataclass(frozen=True)
class NarrativeUnit:
    """A coherent multi-sentence narrative unit for synthesis."""
    unit_id: str
    text: str
    intent: str = "conversational"
    pause_before_ms: int = 900    # Semantic silence before this unit
    pause_after_ms: int = 0       # Optional extra silence after (e.g. reflective question)
    speed: Optional[float] = None
    volume_db: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return round(float(out), 2)


def synthesize_fish_unit(
    text: str,
    out_wav_path: Path,
    *,
    voice_id: str = DEFAULT_VOICE_ID,
    model: str = DEFAULT_MODEL_ID,
    speed: float = 0.92,
    volume_db: float = 0.0,
    temperature: float = 0.68,
    top_p: float = 0.79,
    language: str = "es",
    chunk_length: int = 300,
) -> Path:
    """Call Fish Audio /v1/tts with full prosody and continuity controls."""
    api_key = os.environ.get("FISH_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FISH_API_KEY no está configurada en el entorno.")

    payload = {
        "text": text,
        "reference_id": voice_id,
        "format": "wav",
        "sample_rate": 44100,
        "normalize": True,
        "language": language,
        "latency": "normal",
        "chunk_length": int(chunk_length),
        "min_chunk_length": 60,
        "condition_on_previous_chunks": True,
        "temperature": float(temperature),
        "top_p": float(top_p),
        "prosody": {
            "speed": round(float(speed), 3),
            "volume": round(float(volume_db), 2),
            "normalize_loudness": False,
        },
    }

    raw_tmp = out_wav_path.with_suffix(".raw.wav")
    max_retries = 4
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                "https://api.fish.audio/v1/tts",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "model": model,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                audio_bytes = resp.read()
            if not audio_bytes or len(audio_bytes) < 2000:
                raise RuntimeError("Respuesta de audio vacía o demasiado corta desde Fish Audio.")
            raw_tmp.write_bytes(audio_bytes)
            break
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as exc:
            if attempt == max_retries - 1:
                raise
            wait_s = 2.0 * (attempt + 1)
            print(f"  [RETRY {attempt + 1}] {out_wav_path.name}: {exc} (esperando {wait_s:.0f}s)...", flush=True)
            time.sleep(wait_s)

    # Resample cleanly to 48 kHz mono 16-bit WAV without altering dynamics
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(raw_tmp),
            "-ac", "1", "-ar", str(SR),
            "-c:a", "pcm_s16le",
            str(out_wav_path),
        ],
        check=True,
    )
    try:
        raw_tmp.unlink()
    except OSError:
        pass
    return out_wav_path


def load_wav_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            arr = arr.reshape(-1, 2).mean(axis=1)
        return arr


def trim_outer_silence(
    audio: np.ndarray,
    threshold_db: float = -44.0,
    keep_head_ms: int = 45,
    keep_tail_ms: int = 85,
) -> np.ndarray:
    """Trim dead air at clip edges while preserving natural breath attack/release."""
    if len(audio) == 0:
        return audio
    thresh = 10.0 ** (threshold_db / 20.0)
    win = int(0.015 * SR)  # 15 ms RMS frames
    n_frames = len(audio) // win
    if n_frames < 2:
        return audio
    rms = np.sqrt(np.mean(audio[: n_frames * win].reshape(n_frames, win) ** 2, axis=1))
    voiced = np.where(rms > thresh)[0]
    if len(voiced) == 0:
        return audio
    start = max(0, int(voiced[0] * win) - int(keep_head_ms * SR / 1000))
    end = min(len(audio), int((voiced[-1] + 1) * win) + int(keep_tail_ms * SR / 1000))
    clipped = audio[start:end].copy()
    # Micro 12ms fade at edges to prevent clicks
    fade_n = min(len(clipped) // 4, int(0.012 * SR))
    if fade_n > 0:
        clipped[:fade_n] *= np.linspace(0.0, 1.0, fade_n, dtype=np.float32)
        clipped[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)
    return clipped


def calibrate_internal_pauses(
    audio: np.ndarray,
    min_detect_ms: int = 230,
    extra_ms: int = 120,
    max_pause_ms: int = 900,
    threshold_db: float = -42.0,
) -> np.ndarray:
    """
    Post-production pause calibration:
    When Fish Audio rushes through periods, ellipses, or question marks,
    this detects genuine inter-sentence silence valleys (>= min_detect_ms)
    and smoothly inserts controlled breathing silence (extra_ms) at the
    quietest midpoint — without ever cutting mid-word or sounding robotic.
    """
    if extra_ms <= 0 or len(audio) < SR:
        return audio

    thresh = 10.0 ** (threshold_db / 20.0)
    frame_ms = 10
    frame_n = int(frame_ms * SR / 1000)
    n_frames = len(audio) // frame_n
    if n_frames < 10:
        return audio

    rms = np.sqrt(np.mean(audio[: n_frames * frame_n].reshape(n_frames, frame_n) ** 2, axis=1))
    silent = rms < thresh

    # Find contiguous silent runs strictly inside the clip (not leading/trailing)
    runs: List[tuple[int, int]] = []
    in_run = False
    run_start = 0
    for i, is_sil in enumerate(silent):
        if is_sil and not in_run:
            in_run = True
            run_start = i
        elif not is_sil and in_run:
            in_run = False
            if run_start > 5 and i < n_frames - 5:
                runs.append((run_start, i))

    min_frames = max(1, min_detect_ms // frame_ms)
    max_frames = max(min_frames + 1, max_pause_ms // frame_ms)
    insert_samples = int(extra_ms * SR / 1000)
    xfade_n = int(0.015 * SR)  # 15 ms crossfade into silence

    out_parts: List[np.ndarray] = []
    prev_sample = 0
    expanded_count = 0

    for rs, re in runs:
        dur_frames = re - rs
        if min_frames <= dur_frames < max_frames:
            # Find the quietest frame near the middle of the silence valley
            mid_frame = rs + int(np.argmin(rms[rs:re]))
            cut = mid_frame * frame_n
            if cut > prev_sample + xfade_n and cut < len(audio) - xfade_n:
                seg = audio[prev_sample:cut].copy()
                seg[-xfade_n:] *= np.linspace(1.0, 0.0, xfade_n, dtype=np.float32)
                out_parts.append(seg)
                out_parts.append(np.zeros(insert_samples, dtype=np.float32))
                prev_sample = cut
                expanded_count += 1

    if expanded_count == 0:
        return audio

    tail = audio[prev_sample:].copy()
    if len(tail) > xfade_n:
        tail[:xfade_n] *= np.linspace(0.0, 1.0, xfade_n, dtype=np.float32)
    out_parts.append(tail)
    return np.concatenate(out_parts)


def apply_moderate_dynamics(audio: np.ndarray, target_rms_db: float, delta_db: float) -> np.ndarray:
    """
    Align each unit to a consistent baseline speech loudness, then apply the
    moderate intentional dynamic shift (delta_db) so intimate reflections sit
    gently lower and key conclusions stand out naturally.
    """
    # Measure active speech RMS (ignoring silent frames)
    frame_n = int(0.02 * SR)
    n_frames = len(audio) // frame_n
    if n_frames < 2:
        return audio
    rms_frames = np.sqrt(np.mean(audio[: n_frames * frame_n].reshape(n_frames, frame_n) ** 2, axis=1))
    active = rms_frames[rms_frames > 0.012]
    if len(active) == 0:
        return audio
    cur_rms = float(np.sqrt(np.mean(active ** 2)))
    cur_db = 20.0 * np.log10(max(cur_rms, 1e-6))

    # Clamp intentional delta to a tasteful, natural range [-2.0, +2.0] dB
    clamped_delta = max(-2.0, min(2.0, float(delta_db)))
    gain_db = (target_rms_db + clamped_delta) - cur_db
    # Avoid extreme gain swings
    gain_db = max(-6.0, min(6.0, gain_db))
    gain = 10.0 ** (gain_db / 20.0)
    return np.clip(audio * gain, -0.96, 0.96).astype(np.float32)


def render_humanized_podcast(
    units: Sequence[NarrativeUnit],
    *,
    chunks_dir: Path,
    out_mp3: Path,
    bed_renderer,
    voice_id: str = DEFAULT_VOICE_ID,
    model: str = DEFAULT_MODEL_ID,
    lead_in_sec: float = 2.8,
    tail_sec: float = 7.5,
    bed_volume: float = 0.115,
    force_regen_ids: Optional[Sequence[str]] = None,
) -> float:
    """
    Synthesize, calibrate pauses, apply natural dynamics, mix with the ambient
    music bed (with smooth sidechain ducking), and master to -16 LUFS while
    preserving natural loudness range (LRA=15).
    """
    chunks_dir.mkdir(parents=True, exist_ok=True)
    regen_set = set(force_regen_ids or [])

    total_words = sum(len(u.text.split()) for u in units)
    print(f"[ENGINE] {len(units)} narrative units | ~{total_words} words | model={model} | voice={voice_id[:8]}", flush=True)

    rendered_clips: List[tuple[NarrativeUnit, np.ndarray]] = []
    for unit in units:
        profile = INTENT_PROFILES.get(unit.intent, INTENT_PROFILES["conversational"])
        speed = unit.speed if unit.speed is not None else profile.speed
        vol_db = unit.volume_db if unit.volume_db is not None else profile.volume_db
        temp = unit.temperature if unit.temperature is not None else profile.temperature
        top_p = unit.top_p if unit.top_p is not None else profile.top_p

        wav_path = chunks_dir / f"{unit.unit_id}.wav"
        need_gen = (unit.unit_id in regen_set) or not (wav_path.exists() and wav_path.stat().st_size > 4000)

        if need_gen:
            print(
                f"[TTS] {unit.unit_id} | intent={unit.intent} | speed={speed:.2f} | vol={vol_db:+.1f}dB | temp={temp:.2f}",
                flush=True,
            )
            synthesize_fish_unit(
                unit.text,
                wav_path,
                voice_id=voice_id,
                model=model,
                speed=speed,
                volume_db=vol_db,
                temperature=temp,
                top_p=top_p,
            )
        else:
            print(f"[REUSE] {unit.unit_id}.wav", flush=True)

        audio = load_wav_mono(wav_path)
        audio = trim_outer_silence(audio)
        audio = calibrate_internal_pauses(
            audio,
            min_detect_ms=profile.min_internal_gap_ms,
            extra_ms=profile.extra_internal_ms,
        )
        audio = apply_moderate_dynamics(audio, target_rms_db=-19.0, delta_db=vol_db)
        rendered_clips.append((unit, audio))

    # Assemble stereo voice timeline with exact semantic pauses
    lead_in_samples = int(lead_in_sec * SR)
    tail_samples = int(tail_sec * SR)
    cursor = lead_in_samples
    placements: List[tuple[int, np.ndarray]] = []

    for idx, (unit, audio) in enumerate(rendered_clips):
        if idx > 0:
            cursor += int(unit.pause_before_ms * SR / 1000.0)
        start = cursor
        end = start + len(audio)
        placements.append((start, audio))
        cursor = end + int(unit.pause_after_ms * SR / 1000.0)

    total_samples = cursor + tail_samples
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for start, audio in placements:
        end = start + len(audio)
        stereo[start:end, 0] += audio
        stereo[start:end, 1] += audio

    peak = float(np.max(np.abs(stereo)) + 1e-9)
    if peak > 0.94:
        stereo *= 0.94 / peak

    voice_full = Path(f"/tmp/{out_mp3.stem}_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_duration(voice_full)
    print(f"[TIMELINE] Voice assembled: {total_dur:.2f}s", flush=True)

    bed_wav = Path(f"/tmp/{out_mp3.stem}_bed.wav")
    print(f"[BED] Rendering ambient music bed ({total_dur + 1.0:.2f}s)...", flush=True)
    bed_renderer(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.5)

    # Master with gentle high-pass (clean rumble), soft bed ducking, and wide LRA=15
    # so natural vocal dynamics (intimate drops vs. emphatic rises) remain intact.
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]highpass=f=65,asplit=2[v_mix][v_sc];"
            f"[1:a]aresample={SR},aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4000,volume={bed_volume:.3f},"
            f"afade=t=in:st=0:d=2.2,afade=t=out:st={fade_start:.2f}:d=4.5[b_raw];"
            f"[b_raw][v_sc]sidechaincompress=threshold=0.010:ratio=4.2:attack=60:release=540:makeup=1[b_duck];"
            f"[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            f"loudnorm=I=-16:TP=-1.0:LRA=15[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR),
            str(out_mp3),
        ],
        check=True,
    )

    final_dur = probe_duration(out_mp3)
    mins = int(final_dur // 60)
    secs = int(round(final_dur % 60))
    print(f"[DONE] {out_mp3} -> {final_dur:.2f}s ({mins}:{secs:02d}, {out_mp3.stat().st_size} B)", flush=True)
    return final_dur
