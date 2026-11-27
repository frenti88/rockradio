#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 13 (Solo Fred):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 2/6: Cómo estar siempre inspirado (según la ciencia)"
Inspired by Álvaro García's series (24 de octubre de 2026).

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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_13"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

CHUNKS = [
    (
        "01_apertura", 0,
        "¿Por qué las mejores ideas casi nunca llegan cuando estás sentado frente al computador mirando la pantalla con cara de concentración… "
        "y en cambio aparecen justo cuando te estás bañando, caminando sin prisa o a punto de quedarte dormido?"
    ),
    (
        "02_contexto_cap2", 1100,
        "Seguimos con el segundo capítulo de esta serie inspirada en la guía de Álvaro García, Cómo crear tu sistema infinito de ideas: "
        "Cómo estar siempre inspirado según la ciencia, y cómo organizar tus ideas para que no se evaporen en cinco minutos. "
        "En el capítulo anterior desmontamos el mito del genio solitario. Hoy vamos a la pregunta práctica: "
        "si la creatividad no es magia, ¿cómo funciona de verdad la inspiración en nuestro cerebro?"
    ),
    (
        "03_red_neuronal_defecto", 1200,
        "Aquí la neurociencia tiene una respuesta fascinante. Cuando estás hiperconcentrado en una tarea concreta, "
        "tu cerebro opera en modo ejecutivo: enfocado, lineal, buscando una respuesta rápida. "
        "Pero cuando sueltas el control —al caminar, lavar los platos o mirar por la ventana sin el celular en la mano—, "
        "se activa lo que la ciencia llama la red neuronal por defecto. "
        "En ese estado aparentemente distraído, tu cerebro empieza a conectar recuerdos lejanos, lecturas viejas y problemas abiertos. "
        "Eso es la incubación. No es perder el tiempo; es dejar que la cocina trabaje a fuego lento."
    ),
    (
        "04_combustible_inputs", 1100,
        "Claro, hay una condición indispensable: el cerebro no puede conectar puntos que nunca le diste. "
        "Si todos los días consumes exactamente las mismas noticias, las mismas cuentas y las mismas conversaciones, "
        "tus combinaciones van a ser siempre previsibles. "
        "Estar siempre inspirado empieza por cuidar tu dieta de curiosidad: leer temas fuera de tu profesión, escuchar música distinta, "
        "observar cómo resuelven problemas en otras industrias y hacerte preguntas simples sobre lo cotidiano."
    ),
    (
        "05_captura_inmediata", 1100,
        "Ahora, de nada sirve tener una gran idea caminando por la calle si confías en que te vas a acordar de ella al llegar a casa. "
        "Todos hemos caído en esa trampa (chuckle): 'esta idea es buenísima, imposible que se me olvide'. "
        "Media hora después, desapareció por completo. "
        "Tu memoria de trabajo no está diseñada para almacenar ideas; está diseñada para procesarlas. "
        "Por eso el segundo pilar de un sistema infinito de ideas es la captura sin fricción: una nota rápida en el teléfono, una nota de voz o una app sencilla donde anotes el pensamiento en menos de diez segundos."
    ),
    (
        "06_organizar_app", 1100,
        "Y aquí viene un detalle clave sobre las aplicaciones para organizar ideas. "
        "Mucha gente pasa más tiempo diseñando carpetas perfectas, etiquetas de colores y tableros complejos que generando ideas reales. "
        "La mejor app para organizar tus ideas no es la más sofisticada; es la que realmente abres todos los días. "
        "Basta con tres cosas: una bandeja de entrada rápida para capturar al vuelo, un espacio para agrupar por temas o proyectos, "
        "y un hábito semanal de diez minutos para releer lo que anotaste y conectar piezas entre sí."
    ),
    (
        "07_cierre_puente", 1200,
        "Al final, estar siempre inspirado no significa vivir en un estado permanente de genialidad. "
        "Significa alternar entre alimentar tu mente, darle espacio para respirar y tener un lugar confiable donde atrapar cada chispa antes de que se apague. "
        "En el próximo capítulo vamos a ver algo buenísimo: cómo transformar una sola idea en mil ideas con la técnica de supresión conceptual. "
        "Nos escuchamos en el capítulo tres."
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

    voice_full = Path("/tmp/aparte_13_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 13: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_13_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.0)

    out_mp3 = OUT_DIR / "aparte_siempre_inspirado.mp3"
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
