#!/usr/bin/env python3
"""
Combines all 6 chapters of 'Sistema infinito de ideas' into a single
continuous podcast episode, inserting a 5-second musical interlude between
each chapter where the Drive ambient background music swells louder.
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

OUT_DIR = Path("/home/antigravity/frenti88/rockradio/podcasts")
sys.path.insert(0, str(OUT_DIR))
from generate_podcast_music import render_bed_wav  # noqa: E402

SR = 48000
GAP_SEC = 5.0
CROSSFADE_SEC = 1.0  # smooth overlap between chapter edge and louder music bridge

CHAPTERS = [
    OUT_DIR / "aparte_mito_genio_solitario.mp3",
    OUT_DIR / "aparte_siempre_inspirado.mp3",
    OUT_DIR / "aparte_supresion_conceptual.mp3",
    OUT_DIR / "aparte_creatividad_grupos.mp3",
    OUT_DIR / "aparte_obra_desde_conclusion.mp3",
    OUT_DIR / "aparte_siete_formas_ideas.mp3",
]


def probe_dur(path: Path) -> float:
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


def decode_stereo_48k(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        [
            "ffmpeg", "-v", "error",
            "-i", str(path),
            "-f", "f32le", "-acodec", "pcm_f32le",
            "-ac", "2", "-ar", str(SR),
            "pipe:1",
        ]
    )
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def apply_fade_in(audio: np.ndarray, sec: float) -> np.ndarray:
    n = min(len(audio), int(sec * SR))
    if n > 0:
        ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)[:, None]
        audio[:n] *= ramp
    return audio


def apply_fade_out(audio: np.ndarray, sec: float) -> np.ndarray:
    n = min(len(audio), int(sec * SR))
    if n > 0:
        ramp = np.linspace(1.0, 0.0, n, dtype=np.float32)[:, None]
        audio[-n:] *= ramp
    return audio


def build_processed_bed(total_needed_sec: float) -> np.ndarray:
    raw_bed = Path("/tmp/aparte_18_bed_raw.wav")
    proc_bed = Path("/tmp/aparte_18_bed_proc.wav")
    print(f"[BED] Rendering Drive ambient music bed ({total_needed_sec:.1f}s)...", flush=True)
    render_bed_wav(raw_bed, total_needed_sec)
    # Same warm Drive character as individual episodes, boosted louder for the 5s bridges
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(raw_bed),
            "-af", "aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4800,volume=0.38",
            "-c:a", "pcm_f32le", "-ac", "2", "-ar", str(SR),
            str(proc_bed),
        ],
        check=True,
    )
    return decode_stereo_48k(proc_bed)


def main() -> None:
    for ch in CHAPTERS:
        if not ch.exists():
            raise FileNotFoundError(f"Missing chapter audio: {ch}")

    # Trim inner music tails/intros so the gap between chapters is a clean 5.0s
    # (Each individual chapter has ~3s intro music and ~8s outro music.)
    INNER_TRIM_HEAD_SEC = 2.0
    INNER_TRIM_TAIL_SEC = 6.5

    clips = []
    for idx, ch in enumerate(CHAPTERS):
        audio = decode_stereo_48k(ch)
        is_first = idx == 0
        is_last = idx == len(CHAPTERS) - 1

        start_idx = 0 if is_first else int(INNER_TRIM_HEAD_SEC * SR)
        end_idx = len(audio) if is_last else max(start_idx + SR, len(audio) - int(INNER_TRIM_TAIL_SEC * SR))
        trimmed = audio[start_idx:end_idx].copy()

        if not is_first:
            apply_fade_in(trimmed, 0.7)
        if not is_last:
            apply_fade_out(trimmed, 0.9)

        clips.append(trimmed)
        print(f"[CH {idx + 1}/6] {ch.name}: {len(trimmed) / SR:.2f}s", flush=True)

    # Render a 60s Drive bed and slice a fresh segment for each of the 5 transitions
    bed_audio = build_processed_bed(65.0)
    gap_samples = int(GAP_SEC * SR)
    xfade_samples = int(CROSSFADE_SEC * SR)
    bridge_len = gap_samples + 2 * xfade_samples

    # Compute total output length
    total_samples = sum(len(c) for c in clips) + (len(clips) - 1) * gap_samples
    out = np.zeros((total_samples, 2), dtype=np.float32)

    cursor = 0
    for idx, clip in enumerate(clips):
        end = cursor + len(clip)
        out[cursor:end] += clip

        if idx < len(clips) - 1:
            # Place a 5s louder musical bridge centered in the 5s gap,
            # overlapping CROSSFADE_SEC into the outgoing tail and incoming head.
            bed_offset = int((idx * 10.5 + 3.0) * SR)
            bridge = bed_audio[bed_offset:bed_offset + bridge_len].copy()
            # Smooth swell up into the 5s gap and smooth duck down into the next chapter
            apply_fade_in(bridge, CROSSFADE_SEC + 0.4)
            apply_fade_out(bridge, CROSSFADE_SEC + 0.4)

            b_start = end - xfade_samples
            b_end = b_start + len(bridge)
            out[b_start:b_end] += bridge

            cursor = end + gap_samples
        else:
            cursor = end

    peak = float(np.max(np.abs(out)) + 1e-9)
    if peak > 0.98:
        out *= 0.98 / peak

    tmp_wav = Path("/tmp/aparte_18_combined.wav")
    pcm = (np.clip(out, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(tmp_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    out_mp3 = OUT_DIR / "aparte_sistema_infinito_ideas_completo.mp3"
    print(f"[MASTER] Encoding & normalizing {out_mp3.name} (-16 LUFS)...", flush=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_wav),
            "-af", "loudnorm=I=-16:TP=-1.0:LRA=11",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR),
            str(out_mp3),
        ],
        check=True,
    )

    dur = probe_dur(out_mp3)
    mins = int(dur // 60)
    secs = int(round(dur % 60))
    print(f"DONE! {out_mp3} -> {dur}s ({mins}:{secs:02d}, {out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
