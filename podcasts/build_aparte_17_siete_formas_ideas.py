#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 17 (Solo Fred):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 6/6: Las 7 formas de convertir cualquier idea corriente en ideas originales"
Inspired by Álvaro García's series (27 de noviembre de 2026).

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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_17"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

CHUNKS = [
    (
        "01_apertura", 0,
        "Mucha gente descarta buenas ideas en cuestión de segundos porque, a primera vista, parecen demasiado corrientes. "
        "Pero casi ninguna idea brillante nace brillante. Nace normalita… y se vuelve extraordinaria cuando sabes cómo pulirla."
    ),
    (
        "02_intro_cap6", 1100,
        "Llegamos al capítulo seis y cierre de nuestra serie inspirada en la guía de Álvaro García, Cómo crear tu sistema infinito de ideas: "
        "Las siete formas de convertir cualquier idea corriente en una idea original. "
        "A lo largo de esta serie desmontamos el mito del genio solitario, vimos cómo funciona la inspiración en el cerebro, "
        "probamos la supresión conceptual, el trabajo creativo en grupo y cómo construir una obra desde su conclusión. "
        "Hoy cerramos con la caja de herramientas para potenciar cualquier idea que ya tengas en tu cuaderno."
    ),
    (
        "03_formas_1_a_4", 1100,
        "Veamos las primeras cuatro formas de transformar una idea común en algo memorable. "
        "Primera: cambia el contexto o el público. Una idea que parece gastada en una industria puede ser revolucionaria en otra. "
        "Segunda: invierte la premisa. Si todo el mundo dice cómo hacer algo más rápido, pregúntate qué pasa si lo haces deliberadamente más lento. "
        "Tercera: llévala al extremo, haciéndola diez veces más grande o diez veces más pequeña. "
        "Y cuarta: crúzala con una disciplina que no tenga nada que ver, como mezclar finanzas con storytelling o diseño con gastronomía."
    ),
    (
        "04_formas_5_a_7", 1100,
        "Y aquí van las últimas tres, que son igual de poderosas. "
        "Quinta: cambia el formato. Lo que suena aburrido en un informe de veinte páginas puede cobrar vida en un audio de tres minutos o en una experiencia interactiva. "
        "Sexta: ponle una restricción creativa. Limitar el tiempo, el presupuesto o las herramientas te obliga a encontrar soluciones mucho más ingeniosas. "
        "Y séptima: aterriza la idea en una historia humana concreta. Una teoría abstracta se olvida rápido; una escena real con personas de carne y hueso se queda para siempre."
    ),
    (
        "05_cierre_serie", 1300,
        "Si te das cuenta, el secreto de todo este sistema infinito de ideas nunca fue tener una mente sobrehumana. "
        "Fue dejar de esperar la inspiración perfecta y empezar a jugar con método, curiosidad y constancia. "
        "Gracias por acompañarme en estos seis capítulos. Ahora te toca a ti abrir tu cuaderno, elegir una idea corriente… y ver hasta dónde la puedes llevar. "
        "Esto fue Aparte. Nos escuchamos en la próxima."
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
    tail_samples = int(8.0 * sr)

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

    voice_full = Path("/tmp/aparte_17_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 17: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_17_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.5)

    out_mp3 = OUT_DIR / "aparte_siete_formas_ideas.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12,"
            f"afade=t=in:st=0:d=2.0,afade=t=out:st={fade_start:.2f}:d=4.5[b_raw];"
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
