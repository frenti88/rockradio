#!/usr/bin/env python3
"""
Builds Solo Podcast:
"INQUIETO: Retrato de una mente que nunca deja de explorar"
Narrated exclusively with Fred's voice model (g.DEFAULT_FISH_VOICE) in Fish Audio drama-3,
with reflective pauses, subtle breaths/sighs, spontaneous warm laughs, cinematic background
music bed with sidechain ducking, and a 3-second final pause + musical swell.
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
CHUNKS_DIR = OUT_DIR / "chunks_inquieto"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE

# (id, gap_ms_before, text)
CHUNKS = [
    (
        "01_apertura", 0,
        "Hay personas que pasan la vida buscando respuestas. Y hay otras que, cuando finalmente encuentran una, "
        "terminan formulando cinco preguntas más. Fred pertenece a ese segundo grupo."
    ),
    (
        "02_presentacion", 1600,
        "Nació el diecisiete de diciembre de mil novecientos ochenta y ocho, y su historia no es una pieza terminada "
        "ni un archivo cerrado. Es un cuaderno abierto en pleno movimiento. "
        "A veces la curiosidad es un motor extraordinario… y otras veces, bueno… puede convertirse en el mayor de tus desafíos."
    ),
    (
        "03_identidad", 1200,
        "En el papel, Fredy es un diseñador de experiencias digitales con más de diez años de trayectoria profesional. "
        "Pero quedarse en el cargo sería entender apenas la superficie. "
        "Su mente es inquieta, analítica, inconformista y profundamente creativa. "
        "Cuando mira algo, no se conforma con saber que funciona; necesita desarmarlo en su cabeza para entender cómo funciona… "
        "y, sobre todo, cómo podría funcionar mejor."
    ),
    (
        "04_filosofia", 1100,
        "Antes de proponer una solución, se obsesiona con descubrir el problema real. "
        "Cuestiona las convenciones, la complejidad innecesaria, las decisiones superficiales y esos procesos "
        "que sobreviven únicamente porque siempre se han hecho así. "
        "Y aquí hay algo curioso… en una industria que repite como mantra eso de equivocarse rápido, "
        "Fred no termina de comprarlo. Cree que detenerse a pensar, observar con calma y cuestionar a tiempo "
        "suele ser mucho más valioso que correr a ciegas."
    ),
    (
        "05_zoom_y_principio", 1300,
        "Su brújula profesional vive en un movimiento constante: hacer zoom in y zoom out. "
        "Alejarse para comprender el panorama completo, y acercarse sin perder de vista el detalle mínimo. "
        "Porque carga consigo un principio silencioso que lo define: Dios lo ve. "
        "Esa convicción íntima de hacer las cosas bien… incluso cuando absolutamente nadie está mirando."
    ),
    (
        "06_constructor", 1500,
        "Pero esa inquietud no se apaga cuando termina la jornada laboral. "
        "Durante el día puede estar diseñando experiencias financieras complejas, y al caer la tarde su cabeza ya está "
        "construyendo plataformas digitales, videojuegos, productos editoriales, podcasts o modelos de negocio "
        "potenciados por inteligencia artificial. No como trofeos en una vitrina, sino como la consecuencia natural "
        "de una mente que necesita convertir ideas en algo tangible."
    ),
    (
        "07_proyectos", 1000,
        "De ahí nacen exploraciones como Bajo Radar, una plataforma dedicada a visibilizar esos pequeños acontecimientos "
        "culturales que pasan inadvertidos frente a los grandes espectáculos, bajo una premisa clara: no todo pasa donde todos miran. "
        "O Track Stories, una experiencia que rescata las anécdotas y los acontecimientos detrás de las canciones, "
        "porque para él la música tiene memoria. "
        "También investiga interfaces contextuales, imaginando una tecnología capaz de entender mejor lo que una persona necesita "
        "en el momento justo. Y, claro, su propio podcast: un espacio para cruzar cultura, tecnología, pensamiento crítico "
        "e historias que merecen ser contadas."
    ),
    (
        "08_pasiones_rock", 1600,
        "(sigh) Y cuando bajas el volumen del trabajo y te asomas a lo que realmente lo mueve, aparece la música. "
        "El rock, sobre todo. La precisión de Rush, el espectáculo de Kiss, la épica de Iron Maiden, "
        "la teatralidad de Queen, la energía eléctrica de Van Halen y el pulso inconfundible de INXS. "
        "En él conviven la cultura de los ochenta y los noventa, las portadas de los discos, Nintendo, Zelda, "
        "el cine, la fotografía, la tipografía, el teatro y el humor."
    ),
    (
        "09_rituales_humano", 1100,
        "Es alguien que disfruta los pequeños rituales cotidianos: preparar con calma una buena taza de café de especialidad, "
        "poner música, descubrir una historia fascinante detrás de una obra… y, casi sin darse cuenta, imaginar un proyecto nuevo. "
        "También está su lado más cercano y afectivo: su pasión por Atlético Nacional y su vida compartida con Melissa, "
        "anclas humanas que le recuerdan que no todo en la vida se diseña en una pantalla."
    ),
    (
        "10_contradicciones", 1600,
        "Bueno… pensémoslo un momento, porque aquí aparece lo más fascinante de su retrato: sus contradicciones. "
        "Fredy utiliza tecnologías artificiales para construir experiencias que se sientan profundamente humanas. "
        "Quiere que una voz generada por inteligencia artificial tenga respiraciones, pausas, dudas, emoción y humor. "
        "Quiere que las interfaces comprendan a las personas y que la automatización jamás nos robe la sensibilidad. "
        "Mira hacia el futuro con entusiasmo, pero guarda una devoción genuina por la riqueza del pasado."
    ),
    (
        "11_humor_ideas", 1000,
        "(chuckle) Y tiene una facilidad casi peligrosa para imaginar posibilidades. "
        "Le das una observación mínima, un detalle cualquiera de la vida diaria… y a los diez minutos ya está buscando "
        "el nombre perfecto, la tipografía y el concepto para una nueva iniciativa digital. "
        "(laughing) El único problema, claro, es decidir cuál de todas esas ideas merece realmente toda su atención."
    ),
    (
        "12_incomodidad", 1500,
        "Esa misma sensibilidad explica lo que le incomoda. "
        "Le cuesta tolerar la mediocridad, la superficialidad, las decisiones sin fundamento y esa costumbre tan extendida "
        "de normalizar procesos que claramente están rotos. "
        "En su camino profesional, además, le preocupa quedar atrapado en lo meramente táctico, en lo operativo y lo urgente, "
        "lejos de los espacios estratégicos donde puede entender problemas de fondo y generar impacto real. "
        "No es una derrota; es más bien una etapa de transformación, de afinar la brújula."
    ),
    (
        "13_libertad", 1100,
        "Lo mismo ocurre con su deseo de construir estabilidad económica, patrimonio e independencia. "
        "No busca acumular por acumular. Lo que persigue es algo mucho más valioso: libertad. "
        "Libertad para elegir, para crear sin prisa y para dedicar su energía a lo que verdaderamente importa."
    ),
    (
        "14_conflicto_tiempo", 1800,
        "Porque en esta historia, el verdadero antagonista no es una empresa, ni una persona, ni siquiera la tecnología. "
        "Es el tiempo. "
        "Demasiadas ideas, demasiados mundos por explorar… y horas limitadas para darles forma. "
        "Quizás ahí esté la verdadera pregunta: ¿qué sucede cuando tu imaginación avanza más rápido de lo que tu vida te permite construir?"
    ),
    (
        "15_tension_abierta", 1600,
        "El reto que tiene frente a sí es claro, aunque nunca sencillo: transformar la curiosidad en dirección, "
        "la dirección en disciplina… y la disciplina en algo que permanezca. "
        "Y esa tensión no está resuelta. Sigue abierta, latiendo."
    ),
    (
        "16_cierre", 2000,
        "Tal vez el mayor logro de Fredy todavía no exista. Tal vez aún no tenga nombre, ni fecha, "
        "y quizás ni siquiera haya sido imaginado todavía. "
        "Su historia no es la de un hombre que llegó a la cima. "
        "Es la de alguien que todavía está descubriendo cuál es la montaña que realmente quiere conquistar. "
        "Hay personas que envejecen acumulando respuestas. Otras envejecen acumulando preguntas. "
        "Fred eligió las preguntas. Porque no quiere limitarse a consumir el mundo. Quiere participar en su creación. "
        "Esto es Inquieto. La historia de alguien que todavía no ha terminado de descubrir quién puede llegar a ser."
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
            print(f"[TTS] {tid} (fred)...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), reference_id=VOICE_FRED, model="drama-3")
        else:
            print(f"[REUSE] {tid}.mp3", flush=True)

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

    lead_in_samples = int(3.0 * sr)
    # 3s reflective pause + ~6s musical swell & slow fade-out
    tail_samples = int(9.0 * sr)

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

    voice_full = Path("/tmp/inquieto_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled INQUIETO solo Fred: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/inquieto_bed.wav")
    print(f"[BED] Rendering cinematic music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    # Smooth fade-out at the very end of the bed (last 3.5s)
    fade_start = max(0.0, total_dur - 3.5)

    out_mp3 = OUT_DIR / "inquieto_retrato_mente.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.14,"
            f"afade=t=in:st=0:d=2.2,afade=t=out:st={fade_start:.2f}:d=3.5[b_raw];"
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
    print(f"DONE! {out_mp3} -> {dur}s ({out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
