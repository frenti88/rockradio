#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 12 (Solo Fred):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 1/6: El mito del genio solitario"
Inspired by Álvaro García's series (10 de septiembre de 2026).

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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_12"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

# (id, gap_ms_before, text) — uniform voice volume, natural punctuation & pauses
CHUNKS = [
    (
        "01_apertura", 0,
        "¿Alguna vez te has quedado mirando una hoja en blanco esperando a que te caiga un rayo de inspiración desde el cielo? "
        "Nos vendieron durante siglos una imagen muy romántica de la creatividad: el genio solitario, encerrado en un cuarto oscuro, "
        "mirando por la ventana hasta que, de repente, grita eureka y cambia el mundo."
    ),
    (
        "02_intro_serie", 1100,
        "Hoy arrancamos una serie especial inspirada en la guía de Álvaro García, publicada en septiembre de dos mil veintiséis: "
        "Cómo crear tu sistema infinito de ideas. Son seis capítulos donde vamos a recorrer cómo generar ideas según la ciencia, "
        "cómo transformar una sola idea en mil mediante la supresión conceptual, cuál es la mejor técnica de creatividad en grupo "
        "y cómo levantar una obra entera a partir de una simple conclusión. "
        "Pero antes de hablar de técnicas, hay que desmontar el primer gran obstáculo: el mito del genio solitario."
    ),
    (
        "03_por_que_atrapa_el_mito", 1200,
        "A ver… ¿por qué nos gusta tanto creer en el genio solitario? "
        "Primero, porque es una gran historia. Es mucho más cinematográfico contar que alguien tuvo una iluminación mágica en una tarde "
        "que contar meses de borradores mediocres, conversaciones en un café, libros subrayados y pruebas que salieron mal. "
        "Y segundo, seamos honestos (chuckle), porque ese mito también es una excusa comodísima. "
        "Si las grandes ideas solo le llegan a unos pocos elegidos, entonces cuando a mí no se me ocurre nada… bueno, simplemente hoy no bajó la musa."
    ),
    (
        "04_realidad_creatividad", 1100,
        "Pero cuando miras de cerca cómo nacen de verdad las ideas memorables —en la ciencia, en la música, en el diseño o en los negocios—, "
        "el patrón casi nunca es un destello aislado en el vacío. "
        "Una idea nueva casi siempre es una recombinación inesperada de piezas que ya existían en tu cabeza: "
        "una frase que leíste hace dos años, un problema que viste ayer en la calle, una conversación casual con un amigo y una pregunta que no te dejaba dormir."
    ),
    (
        "05_red_y_entorno", 1100,
        "Nadie crea desde la nada absoluta. Incluso las mentes que la historia recuerda como solitarias vivían conectadas a una red gigante de influencias, "
        "cartas, cuadernos, debates, rivales y maestros. "
        "Cuando trabajas completamente aislado, tu cerebro solo puede reciclar los mismos tres pensamientos de siempre. "
        "En cambio, cuando expones tu mente a disciplinas distintas, a otras personas y a puntos de vista que te incomodan un poco, "
        "las conexiones nuevas empiezan a aparecer casi solas."
    ),
    (
        "06_sistema_vs_inspiracion", 1200,
        "Y aquí está el verdadero cambio de mentalidad que propone esta guía: dejar de depender de la inspiración y empezar a construir un sistema. "
        "La inspiración es caprichosa; aparece cuando quiere y desaparece justo el día que tienes una entrega. "
        "Un sistema, en cambio, es una fábrica tranquila y constante. "
        "Significa capturar observaciones todos los días, guardar preguntas que te llamen la atención, conectar referencias de mundos distintos "
        "y darte permiso de producir diez ideas normales para que, entre ellas, aparezca una brillante."
    ),
    (
        "07_cantidad_y_calidad", 1000,
        "El perfeccionismo del genio solitario te paraliza porque te exige que la primera idea sea genial. "
        "Un sistema infinito de ideas funciona exactamente al revés: separa el momento de generar del momento de juzgar. "
        "Primero llenas la mesa de materia prima sin censurarte, y después, con calma y criterio, eliges, pules y descartas."
    ),
    (
        "08_cierre_puente", 1300,
        "Así que si alguna vez sentiste que no eras lo suficientemente creativo, quizás nunca te faltó talento… "
        "quizás solo estabas esperando una chispa mágica en lugar de encender un sistema. "
        "Este fue el primer capítulo: El mito del genio solitario. "
        "En el próximo episodio entraremos de lleno en cómo generar infinitas ideas según la ciencia. "
        "Nos escuchamos pronto."
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

    voice_full = Path("/tmp/aparte_12_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 12: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_12_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.0)

    out_mp3 = OUT_DIR / "aparte_mito_genio_solitario.mp3"
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
