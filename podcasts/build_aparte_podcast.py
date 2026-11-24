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
    """Upbeat 112 BPM morning-news / modern tech-podcast music bed (marimba pulse, light groove, clean bass)."""
    n = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float32)

    bpm = 112.0
    beat_sec = 60.0 / bpm
    sixteenth_sec = beat_sec / 4.0
    bar_sec = beat_sec * 4.0

    # Upbeat modern news progression (Dm7 -> Bbmaj7 -> Fmaj7 -> C), 2 bars per chord
    chords = [
        [146.83, 293.66, 349.23, 440.0, 523.25],   # Dm7
        [116.54, 233.08, 293.66, 349.23, 440.0],   # Bbmaj7
        [174.61, 261.63, 349.23, 440.0, 523.25],   # Fmaj7
        [130.81, 261.63, 329.63, 392.0, 523.25],   # C
    ]
    chord_idx = (t / (bar_sec * 2.0)).astype(np.int32) % len(chords)

    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    # 1. Crisp 16th-note marimba / plucked news-magazine arpeggio pattern
    arp_pattern = [1, 2, 3, 2, 4, 2, 3, 1, 2, 3, 4, 3, 2, 1, 3, 2]
    step_idx = (t / sixteenth_sec).astype(np.int32)
    step_in_bar = step_idx % 16
    local_16 = (t % sixteenth_sec) / sixteenth_sec
    pluck_env = np.exp(-9.0 * local_16).astype(np.float32)

    note_slots = np.array([arp_pattern[s] for s in step_in_bar], dtype=np.int32)
    arp_freqs = np.array([chords[c][ns] for c, ns in zip(chord_idx, note_slots)], dtype=np.float32)
    arp_phase = 2 * np.pi * np.cumsum(arp_freqs) / sr
    # Marimba-like fundamental + woody 4th harmonic transient
    marimba = (np.sin(arp_phase) * 0.8 + np.sin(arp_phase * 4.0) * 0.15 * np.exp(-24.0 * local_16)) * pluck_env * 0.24
    pan_l = np.where((step_idx % 2) == 0, 1.05, 0.80).astype(np.float32)
    pan_r = np.where((step_idx % 2) == 0, 0.80, 1.05).astype(np.float32)
    left += marimba * pan_l
    right += marimba * pan_r

    # 2. Clean bouncing bassline on 8th-note groove
    bass_f = np.array([chords[c][0] * 0.5 for c in chord_idx], dtype=np.float32)
    eighth_local = (t % (beat_sec * 0.5)) / (beat_sec * 0.5)
    bass_env = (0.35 + 0.65 * np.exp(-5.0 * eighth_local)).astype(np.float32)
    bass = np.sin(2 * np.pi * np.cumsum(bass_f) / sr) * bass_env * 0.28
    left += bass
    right += bass

    # 3. Light, crisp morning-news percussion (soft kick, rimshot on 2 & 4, ticking 8th shaker)
    rng = np.random.default_rng(19)
    kick_n = int(sr * 0.14)
    kt = np.linspace(0, 0.14, kick_n, endpoint=False, dtype=np.float32)
    kick = np.sin(2 * np.pi * np.cumsum(125.0 * np.exp(-28.0 * kt) + 48.0) / sr) * np.exp(-15.0 * kt) * 0.36

    rim_n = int(sr * 0.045)
    rt = np.linspace(0, 0.045, rim_n, endpoint=False, dtype=np.float32)
    rim = (np.sin(2 * np.pi * 880.0 * rt) * 0.5 + rng.standard_normal(rim_n).astype(np.float32) * 0.25) * np.exp(-65.0 * rt) * 0.22

    hat_n = int(sr * 0.035)
    ht = np.linspace(0, 0.035, hat_n, endpoint=False, dtype=np.float32)
    hat = np.diff(rng.standard_normal(hat_n).astype(np.float32), prepend=0.0) * np.exp(-75.0 * ht) * 0.09

    total_beats = int(duration_sec / beat_sec)
    for b in range(total_beats):
        pos = int(b * beat_sec * sr)
        bi = b % 4
        if bi in (0, 2):
            end = min(n, pos + kick_n)
            left[pos:end] += kick[:end - pos]
            right[pos:end] += kick[:end - pos]
        if bi in (1, 3):
            end = min(n, pos + rim_n)
            left[pos:end] += rim[:end - pos] * 0.9
            right[pos:end] += rim[:end - pos] * 1.1
        for sub_i in (0, 1):
            hp = pos + int(sub_i * beat_sec * 0.5 * sr)
            if hp < n:
                end = min(n, hp + hat_n)
                left[hp:end] += hat[:end - hp] * 1.1
                right[hp:end] += hat[:end - hp] * 0.9

    # Soft intro/outro fade
    fade_in = min(int(sr * 1.8), n // 6)
    fade_out = min(int(sr * 4.0), n // 5)
    env = np.ones(n, dtype=np.float32)
    env[:fade_in] = np.linspace(0, 1, fade_in, dtype=np.float32)
    env[-fade_out:] = np.linspace(1, 0, fade_out, dtype=np.float32)
    left = np.tanh(left * env * 0.9) * 0.52
    right = np.tanh(right * env * 0.9) * 0.52

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
