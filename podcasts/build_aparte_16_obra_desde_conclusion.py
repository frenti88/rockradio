#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 16 (Solo Fred):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 5/6: Cómo escribir una obra entera desde una simple conclusión"
Inspired by Álvaro García's series (21 de noviembre de 2026).

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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_16"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

CHUNKS = [
    (
        "01_apertura", 0,
        "Cuando nos sentamos a escribir un artículo, un guion o un libro, casi todos cometemos el mismo error: "
        "intentamos empezar por el principio. "
        "Nos quedamos mirando la primera línea, pensando en una introducción brillante… sin tener del todo claro a dónde diablos queremos llegar."
    ),
    (
        "02_intro_cap5", 1100,
        "Bienvenidos al capítulo cinco de esta serie inspirada en la guía de Álvaro García, Cómo crear tu sistema infinito de ideas: "
        "Cómo escribir una obra entera desde una simple conclusión. "
        "Y la idea de fondo es tan sencilla como liberadora: en lugar de caminar a ciegas desde la página uno, "
        "empiezas por el destino final. Tomas una sola frase —esa conclusión clara que quieres dejar en la cabeza del lector o del oyente— "
        "y construyes el camino hacia atrás."
    ),
    (
        "03_ingenieria_inversa", 1100,
        "Piénsalo como ingeniería inversa de una historia. "
        "Si ya sabes exactamente cuál es tu conclusión, de inmediato aparecen las preguntas correctas: "
        "¿qué tendría que dudar mi lector al principio para que esta conclusión lo sorprenda? "
        "¿Qué objeciones razonables tendría alguien inteligente frente a esta idea? "
        "¿Qué ejemplo cotidiano la vuelve imposible de ignorar? "
        "¿Y qué error común hace que la gente piense exactamente lo contrario?"
    ),
    (
        "04_expandir_ideas", 1100,
        "Ahí es donde una simple frase se expande y se convierte en una obra completa. "
        "Usando herramientas prácticas para expandir ideas —como contrastar opuestos, contar un caso real, explicar la causa y el efecto, "
        "desmontar un mito o responder a la crítica más fuerte—, cada pregunta se transforma en una sección o un capítulo entero. "
        "Ya no estás rellenando palabras para llegar a una extensión; cada párrafo tiene una razón de ser porque empuja hacia la misma conclusión."
    ),
    (
        "05_claridad_y_ritmo", 1100,
        "Y fíjate en lo que eso hace por quien te lee o te escucha: se nota al instante cuando un creador sabe a dónde va. "
        "No hay rodeos innecesarios ni finales improvisados (chuckle). "
        "Todo encaja como un puente donde el primer ladrillo ya estaba pensado para sostener el último paso."
    ),
    (
        "06_cierre_puente", 1200,
        "Así que la próxima vez que te bloquees frente a una hoja en blanco, no busques la primera frase perfecta. "
        "Escribe la última. Escribe tu conclusión en una sola línea… y déjala que ella te muestre todo lo que falta por contar. "
        "Este fue el capítulo cinco. Y ya nos queda solo el gran cierre: las siete formas de convertir cualquier idea en una idea brillante. "
        "Nos escuchamos en el capítulo seis."
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

    voice_full = Path("/tmp/aparte_16_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 16: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_16_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.0)

    out_mp3 = OUT_DIR / "aparte_obra_desde_conclusion.mp3"
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
