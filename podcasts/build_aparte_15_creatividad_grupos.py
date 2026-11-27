#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 15 (Solo Fred):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 4/6: La mejor técnica de creatividad para grupos"
Inspired by Álvaro García's series.

Narrated with Fred's Fish Audio drama-3 voice (96e5d63e023a4fd5b7926226ed8db011),
strictly keeping UNIFORM voice volume across every chunk (no per-chunk gain changes),
natural reflective pauses, and the Drive ambient background music bed.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_15"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

CHUNKS = [
    (
        "01_apertura_brainstorming", 0,
        "Seamos sinceros un segundo. ¿Cuántas veces has salido de una sesión tradicional de lluvia de ideas "
        "sintiendo que hablaron siempre las mismas dos personas… y que terminaron eligiendo la primera idea medio decente que dijo el jefe? (chuckle) "
        "La ciencia lleva décadas demostrando que el brainstorming clásico en voz alta suele bloquear más ideas de las que genera."
    ),
    (
        "02_intro_cap4", 1100,
        "Bienvenidos al capítulo cuatro de nuestra serie inspirada en la guía de Álvaro García, Cómo crear un sistema infinito de ideas: "
        "la mejor técnica de creatividad para grupos que existe según la ciencia. "
        "Cuando hablamos todos al mismo tiempo, ocurren tres problemas: mientras alguien habla los demás se frenan, "
        "las voces más tímidas se quedan calladas por miedo al juicio y todo el grupo se queda anclado en la primera idea que salió."
    ),
    (
        "03_rotacion_rondas", 1100,
        "¿Cuál es la alternativa que sí funciona? Escribir en silencio y rotar las ideas. "
        "Primero cada persona escribe sus primeras propuestas en una hoja durante unos minutos, sin interrupciones ni críticas. "
        "Y aquí viene la magia de la rotación: cada hoja pasa a la siguiente persona, que dispone de otros cinco minutos "
        "para desarrollar una idea que ya está escrita… o, si no le resuena, añadir una idea nueva. "
        "Después se repiten nuevas rondas hasta que vuelve a tus manos la hoja inicial. "
        "Cuantas más rondas pasan, más manos han tocado cada idea y mayor es la divergencia."
    ),
    (
        "04_agrupar_y_cribar", 1100,
        "Fíjate en lo que pasa al terminar esa fase de generación silenciosa: en lugar de tener cinco ideas sueltas en un tablero, "
        "tienes una montaña de variaciones ricas construidas entre todo el equipo. "
        "Entonces llega el momento de agrupar y cribar. "
        "Cada persona toma una hoja y tiene unos minutos en calma para detectar patrones, agrupar las ideas parecidas "
        "y subrayar lo verdaderamente interesante para compartirlo con el resto."
    ),
    (
        "05_debate_final", 1100,
        "Y solo entonces —al final, no al principio— empieza el debate. "
        "Ahora sí se habla sobre los resultados y se discute con criterio sobre una base amplia de material ya producido y filtrado. "
        "Nada que ver con el caos habitual del brainstorming donde se juzga cada frase antes de que termine de nacer. "
        "Aquí todas las voces participan en igualdad de condiciones y las ideas crecen antes de pasar por el filtro crítico."
    ),
    (
        "06_cierre_puente", 1200,
        "La próxima vez que te toque liderar una sesión creativa con tu equipo, prueba a cambiar el micrófono por papel, silencio y rotación. "
        "Te vas a sorprender con la calidad de lo que aparece sobre la mesa. "
        "En el próximo capítulo veremos cómo escribir una obra entera a partir de una simple conclusión. "
        "Nos escuchamos en el capítulo cinco."
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

    total_words = sum(len(t.split()) for _, _, t in CHUNKS)
    print(f"[SCRIPT] Total spoken words (approx): {total_words}", flush=True)

    for tid, gap_ms, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"

        if not (mp3.exists() and mp3.stat().st_size > 2000):
            print(f"[TTS] {tid} (drama-3, voice={FISH_VOICE_ID[:8]})...", flush=True)
            g._fish_audio_tts_sync(
                text,
                str(mp3),
                reference_id=FISH_VOICE_ID,
                model=FISH_MODEL_ID,
                temperature=0.62,
                top_p=0.77,
            )
        else:
            print(f"[REUSE] {tid}.mp3", flush=True)

        # Strictly uniform voice volume (no gain changes)
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

    lead_in_samples = int(2.6 * sr)
    tail_samples = int(7.0 * sr)

    cursor = lead_in_samples
    placements = []
    max_end = lead_in_samples
    for gap_ms, audio in clips:
        start = max(lead_in_samples, cursor + int(gap_ms * sr / 1000.0))
        end = start + len(audio)
        placements.append((start, audio))
        cursor = end
        if end > max_end:
            max_end = end

    total_samples = max_end + tail_samples
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for start, audio in placements:
        end = start + len(audio)
        stereo[start:end, 0] += audio
        stereo[start:end, 1] += audio

    peak = np.max(np.abs(stereo)) + 1e-9
    if peak > 0.95:
        stereo *= 0.95 / peak

    voice_full = Path("/tmp/aparte_15_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 15: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_15_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.0)

    out_mp3 = OUT_DIR / "aparte_creatividad_grupos.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12,"
            f"afade=t=in:st=0:d=2.0,afade=t=out:st={fade_start:.2f}:d=4.0[b_raw];"
            f"[b_raw][v_sc]sidechaincompress=threshold=0.012:ratio=4.5:attack=50:release=480:makeup=1[b_duck];"
            f"[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            f"loudnorm=I=-16:TP=-1.0:LRA=11[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(out_mp3),
        ],
        check=True,
    )
    dur = probe_dur(out_mp3)
    print(f"DONE! {out_mp3} -> {dur}s ({out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
