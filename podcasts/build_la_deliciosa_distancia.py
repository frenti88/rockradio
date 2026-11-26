#!/usr/bin/env python3
"""
Builds intimate audio piece: "La deliciosa distancia"
Narrated with Fred's Fish Audio drama-3 voice (96e5d63e023a4fd5b7926226ed8db011),
with warm, unhurried pacing, a reflective pause, and soft instrumental background music.
"""
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

REPO = Path("/home/antigravity/frenti88/rockradio")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "podcasts"))

import generate_dj_fred_track as g
from build_aparte_podcast import probe_dur
from generate_podcast_music import render_bed_wav

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_deliciosa_distancia"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

CHUNKS = [
    (
        "01_parte1", 0,
        "Hay algo profundamente seductor en una mujer que no necesita intentar seducirte. "
        "En esa manera de mirarte mientras habla, de acomodarse el cabello distraídamente, "
        "de sonreír como si guardara un secreto que todavía no estás preparado para descubrir. "
        "Y tú, inevitablemente, comienzas a prestar atención a los pequeños detalles. "
        "A la cadencia de su voz. A su perfume, que permanece unos segundos después de que se aleja. "
        "A esa forma tan suya de pronunciar tu nombre."
    ),
    (
        "02_parte2", 1300,
        "Siempre he pensado que el verdadero erotismo habita en la insinuación. "
        "En aquello que podría suceder, pero que todavía no sucede."
    ),
]


def load_wav_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            arr = arr.reshape(-1, 2).mean(axis=1)
        return arr


def main():
    sr = 48000
    clips = []

    for tid, gap_ms, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"
        print(f"[TTS] {tid} (drama-3, voice={FISH_VOICE_ID[:8]})...", flush=True)
        g._fish_audio_tts_sync(
            text,
            str(mp3),
            reference_id=FISH_VOICE_ID,
            model=FISH_MODEL_ID,
            temperature=0.56,
            top_p=0.74,
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(mp3),
                "-af", "aresample=48000,silenceremove=start_periods=1:start_silence=0.04:start_threshold=-45dB",
                "-ac", "1", "-ar", str(sr),
                str(wav),
            ],
            check=True,
        )
        clips.append((gap_ms, load_wav_mono(wav)))

    lead_in = int(2.8 * sr)
    tail = int(5.5 * sr)

    cursor = lead_in
    placements = []
    for gap_ms, audio in clips:
        cursor += int(gap_ms * sr / 1000.0)
        placements.append((cursor, audio))
        cursor += len(audio)

    total_samples = cursor + tail
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for start, audio in placements:
        end = start + len(audio)
        stereo[start:end, 0] += audio
        stereo[start:end, 1] += audio

    peak = np.max(np.abs(stereo)) + 1e-9
    if peak > 0.95:
        stereo *= 0.95 / peak

    voice_full = Path("/tmp/deliciosa_distancia_voice.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    bed_wav = Path("/tmp/deliciosa_distancia_bed.wav")
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.0)
    out_mp3 = OUT_DIR / "la_deliciosa_distancia.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=3200,volume=0.10,"
            f"afade=t=in:st=0:d=2.2,afade=t=out:st={fade_start:.2f}:d=4.0[b_raw];"
            f"[b_raw][v_sc]sidechaincompress=threshold=0.012:ratio=4.5:attack=50:release=500:makeup=1[b_duck];"
            f"[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            f"loudnorm=I=-16:TP=-1.0:LRA=11[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(out_mp3),
        ],
        check=True,
    )
    dur = probe_dur(out_mp3)
    print(f"DONE! {out_mp3} -> {dur:.2f}s ({out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
