#!/usr/bin/env python3
"""
Synthesizes the Aparte podcast episode in natural human-paced chunks using
Fish Audio (drama-3) with the user's official voice, stitches with natural
pauses, and masters to -16 LUFS / -1 dBTP.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/antigravity/frenti88/rockradio")
sys.path.insert(0, str(REPO / "scripts"))
import generate_dj_fred_track as g

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_01"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS = [
    (
        "01_intro",
        0.7,
        "¿Y si la época dorada del diseño no estuviera terminando, sino apenas comenzando? "
        "Últimamente escuchamos mucho que el diseño UX y UI está en crisis. Y, seamos sinceros, hay razones para pensar así. "
        "Diseñadores con años de experiencia tienen dificultades para encontrar trabajo. Las oportunidades para quienes apenas comienzan son cada vez más competitivas. "
        "Algunas empresas están reduciendo sus equipos de diseño, mientras herramientas de inteligencia artificial como Claude pueden construir sitios web e interfaces funcionales en cuestión de minutos."
    ),
    (
        "02_preguntas",
        0.7,
        "Entonces, es inevitable preguntarse: ¿Qué va a pasar con nosotros, los diseñadores? "
        "¿Tiene sentido seguir aprendiendo diseño? ¿Cuánto tiempo pasará antes de que una inteligencia artificial pueda hacer gran parte de nuestro trabajo? "
        "Son preguntas válidas. Pero creo que estamos mirando esta transformación desde una perspectiva incompleta. "
        "Porque quizás lo que está llegando a su fin no es el diseño, sino la manera en la que hemos entendido nuestra profesión durante los últimos años. Y esa diferencia lo cambia todo."
    ),
    (
        "03_distancia",
        0.65,
        "Durante mucho tiempo, los diseñadores hemos tenido una limitación importante: la distancia entre lo que imaginamos y lo que realmente podemos construir. "
        "Podíamos dedicar días enteros a diseñar una experiencia en Figma, perfeccionar una interacción, pensar en una animación y cuidar hasta el más mínimo detalle. "
        "Y después llegaba esa conversación que muchos conocemos. Eso es muy complejo de desarrollar. No tenemos tiempo. No está dentro del alcance. Dejémoslo para una segunda fase. "
        "Y esa segunda fase, muchas veces, nunca llegaba."
    ),
    (
        "04_ia_puente",
        0.65,
        "Hoy, la inteligencia artificial está reduciendo esa distancia. "
        "Si tienes una idea, puedes construir un prototipo funcional. Si quieres experimentar con una interacción, puedes probarla. "
        "Si quieres explorar diferentes maneras de resolver un problema, puedes hacerlo sin depender de semanas de desarrollo. "
        "Eso no significa que los desarrolladores hayan dejado de ser necesarios. Significa que los diseñadores tenemos una capacidad de experimentación que antes era mucho más difícil de alcanzar."
    ),
    (
        "05_criterio",
        0.7,
        "Y aquí aparece una pregunta interesante. Si cualquier persona puede construir una interfaz utilizando inteligencia artificial, ¿por qué seguiríamos necesitando diseñadores? "
        "Imagina que le entregamos exactamente la misma herramienta a dos personas. Una sin experiencia en diseño y otra con años de experiencia comprendiendo usuarios, productos y negocios. "
        "Ambas pueden construir una aplicación. Pero eso no significa que ambas puedan construir una buena experiencia. "
        "Un diseñador experimentado puede identificar problemas que otras personas ni siquiera perciben. Sabe cuándo una interacción genera incertidumbre, cuándo una jerarquía visual no funciona, "
        "cuándo estamos pidiendo información innecesaria o cuándo una decisión aparentemente pequeña puede generar una fricción enorme. "
        "La diferencia ya no está únicamente en la capacidad de ejecutar. Está en el criterio."
    ),
    (
        "06_proposito",
        0.65,
        "Y ese criterio se vuelve especialmente importante cuando producir interfaces es cada vez más fácil. "
        "Porque construir una pantalla es una cosa. Comprender por qué esa pantalla necesita existir es otra completamente diferente. "
        "¿De qué sirve crear un proceso de registro visualmente espectacular si las personas lo abandonan antes de terminarlo? "
        "¿De qué sirve implementar una animación maravillosa si el usuario no entiende qué debe hacer después? "
        "¿De qué sirve construir una aplicación en diez minutos si estamos resolviendo el problema equivocado?"
    ),
    (
        "07_oportunidad",
        0.65,
        "Creo que ahí está una de las mayores oportunidades para nuestra profesión. "
        "Durante años hemos dedicado una cantidad considerable de tiempo a aprender herramientas. A dominar Figma, construir componentes, organizar sistemas de diseño y perfeccionar interfaces. "
        "Todo eso sigue teniendo valor. Pero dominar una herramienta nunca debió ser el objetivo final del diseño. "
        "Lo verdaderamente importante es comprender cómo piensan las personas, cómo toman decisiones, qué les genera confianza, qué les produce incertidumbre y qué necesitan realmente. "
        "También debemos comprender el negocio. Entender cómo nuestras decisiones afectan la conversión, la retención, la eficiencia y los resultados de un producto. "
        "Necesitamos fortalecer nuestro criterio visual. Aprender a reconocer cuándo algo funciona, cuándo no funciona y, sobre todo, por qué. "
        "Y, por supuesto, aprender a trabajar con inteligencia artificial. No solamente para generar pantallas, sino para investigar, contrastar información, explorar hipótesis, construir soluciones y validar ideas."
    ),
    (
        "08_portafolio",
        0.65,
        "Pensemos también en cómo estamos construyendo nuestros portafolios. "
        "Durante mucho tiempo, un portafolio atractivo era una de las principales formas de demostrar nuestras capacidades. "
        "Pero en un mundo donde una inteligencia artificial puede generar interfaces atractivas en segundos, mostrar únicamente el resultado visual empieza a ser insuficiente. "
        "Lo interesante está detrás. ¿Qué problema identificaste? ¿Cómo descubriste que realmente era un problema? ¿Qué alternativas consideraste? "
        "¿Por qué descartaste algunas? ¿Cómo comprobarías que tu solución mejora la experiencia? "
        "Esas preguntas revelan algo que una colección de pantallas difícilmente puede mostrar: tu capacidad de pensar."
    ),
    (
        "09_aprender",
        0.65,
        "Y si queremos prepararnos para esta nueva etapa, también necesitamos cambiar la forma en la que aprendemos diseño. "
        "Menos obsesión por dominar herramientas y más interés por comprender problemas. "
        "Menos preocupación por producir interfaces perfectas y más curiosidad por descubrir si realmente estamos construyendo algo valioso. "
        "Menos tiempo dedicado a demostrar que sabemos diseñar pantallas y más tiempo demostrando que sabemos tomar decisiones. "
        "La inteligencia artificial no elimina la incertidumbre del mercado laboral. Tampoco garantiza que todos los diseñadores tengan las mismas oportunidades. "
        "Hay cambios reales que debemos reconocer y habilidades que necesitamos transformar. Pero también tenemos delante una oportunidad extraordinaria."
    ),
    (
        "10_cierre",
        0.8,
        "Por primera vez, muchos diseñadores podemos investigar, imaginar, construir, experimentar y validar nuestras propias ideas con una autonomía que hace unos años parecía difícil de alcanzar. "
        "Quizás el futuro del diseño consista precisamente en recuperar aquello que siempre debió estar en el centro de nuestra profesión. "
        "Comprender antes de construir. Preguntar antes de responder. Pensar antes de ejecutar. "
        "Porque cuando construir cualquier cosa se vuelve más fácil, decidir qué vale la pena construir se vuelve mucho más importante. "
        "Y quizás, dentro de unos años, cuando miremos hacia atrás, descubramos que este no fue el momento en el que el diseño perdió su valor. "
        "Fue el momento en el que finalmente pudimos demostrar todo su potencial. "
        "La época dorada del diseño no ha terminado. Acaba de empezar. "
        "Esto es Aparte. Ideas que merecen ser escuchadas."
    ),
]


import wave
import numpy as np


def probe_dur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        text=True,
    ).strip()
    return round(float(out), 2)


def generate_editorial_bed(out_wav: Path, duration_sec: float, sr: int = 48000):
    """Warm, minimalist editorial podcast music bed (Rhodes-like maj7/min9 pads + gentle pulse)."""
    n = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float32)

    # 4-chord warm modern editorial progression (Am9 -> Fmaj7 -> Cmaj7 -> G6), 4 seconds per chord
    chords = [
        [110.0, 220.0, 261.63, 329.63, 392.0],   # Am7/9
        [87.31, 174.61, 220.0, 261.63, 329.63],  # Fmaj7
        [130.81, 196.0, 246.94, 329.63, 392.0],  # Cmaj7
        [98.0, 196.0, 246.94, 293.66, 329.63],   # G6
    ]
    chord_dur = 4.0
    chord_idx = (t / chord_dur).astype(np.int32) % len(chords)
    local_t = t % chord_dur
    # Smooth crossfade envelope on each chord change
    chord_env = np.minimum(1.0, local_t / 0.35) * np.minimum(1.0, (chord_dur - local_t) / 0.35)
    chord_env = (0.75 + 0.25 * chord_env).astype(np.float32)

    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    for voice_i in range(5):
        freqs = np.array([chords[c][voice_i] for c in chord_idx], dtype=np.float32)
        phase_l = 2 * np.pi * np.cumsum(freqs) / sr
        phase_r = 2 * np.pi * np.cumsum(freqs * (1.0018 if voice_i % 2 == 0 else 0.9982)) / sr
        weight = 0.32 if voice_i == 0 else (0.18 if voice_i < 3 else 0.11)
        lfo = 0.78 + 0.22 * np.sin(2 * np.pi * (0.11 + 0.03 * voice_i) * t)
        # Soft electric-piano-like overtone
        sig_l = (np.sin(phase_l) + 0.12 * np.sin(phase_l * 2.0)) * weight * lfo * chord_env
        sig_r = (np.sin(phase_r) + 0.12 * np.sin(phase_r * 2.0)) * weight * lfo * chord_env
        left += sig_l
        right += sig_r

    # Soft intro/outro fade
    fade_in = min(int(sr * 2.5), n // 6)
    fade_out = min(int(sr * 4.5), n // 5)
    env = np.ones(n, dtype=np.float32)
    env[:fade_in] = np.linspace(0, 1, fade_in, dtype=np.float32)
    env[-fade_out:] = np.linspace(1, 0, fade_out, dtype=np.float32)
    left = np.tanh(left * env * 0.85) * 0.48
    right = np.tanh(right * env * 0.85) * 0.48

    stereo = np.stack([left, right], axis=1)
    pcm = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def main():
    concat_entries = []
    for name, pause_sec, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{name}.mp3"
        if not (mp3.exists() and mp3.stat().st_size > 5000):
            print(f"[TTS] Synthesizing {name}...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), model="drama-3")
        else:
            print(f"[REUSE] {name}.mp3", flush=True)
        padded = CHUNKS_DIR / f"{name}_pad.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(mp3),
                "-af", f"aresample=48000,apad=pad_dur={pause_sec}",
                str(padded),
            ],
            check=True,
        )
        concat_entries.append(f"file '{padded}'")

    list_file = Path("/tmp/aparte_concat.txt")
    list_file.write_text("\n".join(concat_entries) + "\n", encoding="utf-8")

    voice_full = Path("/tmp/aparte_voice_full.wav")
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-af", "aresample=48000,adelay=2000|2000,apad=pad_dur=4.0",
            str(voice_full),
        ],
        check=True,
    )
    total_dur = probe_dur(voice_full)

    bed_wav = Path("/tmp/aparte_editorial_bed.wav")
    print(f"[BED] Generating warm editorial music bed ({total_dur}s)...", flush=True)
    generate_editorial_bed(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_epoca_dorada_diseno.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            "[0:a]asplit=2[v_mix][v_sc];"
            "[1:a]aresample=48000,lowpass=f=2200,volume=0.055[b_raw];"
            "[b_raw][v_sc]sidechaincompress=threshold=0.01:ratio=5:attack=60:release=500:makeup=1[b_duck];"
            "[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            "loudnorm=I=-16:TP=-1.0:LRA=11[out]",
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
