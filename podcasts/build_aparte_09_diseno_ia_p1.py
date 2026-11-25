#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 9 (Solo Fred):
"El diseño después de la IA — Parte 1: La transformación del diseño"
Narrated with Fred's Fish Audio drama-3 voice (96e5d63e023a4fd5b7926226ed8db011),
using the same custom Drive background music bed (generate_podcast_music.py)
used in the duo podcasts, with reflective pauses and clean natural intonation.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_09"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

# (id, gap_ms_before, text)
CHUNKS = [
    (
        "01_intro_vuelta", 0,
        "Hay algo bastante curioso que está ocurriendo en nuestra industria del diseño, y cuando uno se detiene un segundo a mirarlo, hasta da un poquito de risa. "
        "Hace algunos años estábamos todos enfocados en aprender a utilizar Figma. Después, aprendimos a construir sistemas de diseño. "
        "Más adelante, empezamos a incorporar inteligencia artificial a nuestros procesos. "
        "Y ahora resulta que estamos enseñándoles a las inteligencias artificiales a utilizar esos mismos sistemas de diseño que nosotros construimos."
    ),
    (
        "02_intro_pregunta", 1200,
        "Es como si la industria hubiera dado una vuelta completa. Pero hay algo que me deja todavía más pensativo. "
        "Mientras las herramientas se vuelven cada vez más inteligentes, mientras construir una aplicación toma minutos y cualquiera puede generar una interfaz aparentemente profesional, "
        "seguimos chocando con problemas que conocemos desde hace décadas: usuarios que no entienden los productos, procesos innecesariamente complejos, fallas de accesibilidad y empresas construyendo cosas que nadie pidió. "
        "Entonces… ¿estamos diseñando mejores experiencias o simplemente estamos produciendo más cosas en menos tiempo?"
    ),
    (
        "03_figma_agentes_contexto", 1500,
        "A ver, sentémonos con calma y pensemos en lo que nos dejó noviembre de dos mil veintiséis. "
        "Porque si uno conecta los puntos de lo que pasó este mes, se nota que diseñar dejó de ser solamente mover píxeles. "
        "El veintitrés de noviembre, Figma anunció que su agente de inteligencia artificial llegó a FigJam y a Figma Slides. "
        "A primera vista uno podría decir: bueno, otra actualización más con IA. Pero, si lo miras un poquito más de cerca, hay un movimiento estratégico enorme."
    ),
    (
        "04_figma_agentes_reflexion", 850,
        "Figma está entrando de lleno en espacios que antes vivían medio sueltos alrededor del diseño visual: la investigación, la ideación, las sesiones colaborativas, la documentación y la comunicación de decisiones. "
        "Piénsalo en un día normal de trabajo. Tienes una sesión de descubrimiento con producto, ingeniería y negocio. Durante una hora llueven ideas, hipótesis, restricciones y dudas. "
        "Terminas con un tablero de FigJam repleto de notas… y llega ese silencio incómodo donde todos se miran preguntándose quién va a organizar todo eso. "
        "Ahora el agente puede estructurar ese material, armar documentos editables y transformar hallazgos en presentaciones."
    ),
    (
        "05_figma_agentes_critica", 950,
        "Ojo: eso no significa que la máquina haya entendido mágicamente todo lo que pasó en la sala ni que sus conclusiones sean infalibles. "
        "Pero sí quita de encima una carga operativa pesadísima entre conversar y decidir. "
        "Y aquí viene lo importante: ¿qué vamos a hacer con ese tiempo recuperado? Porque automatizar la documentación solo para llenar la agenda con más reuniones no sería ningún avance. "
        "La verdadera oportunidad es usar ese aire para hablar más con los usuarios, cuestionar supuestos y participar de verdad en las decisiones de producto."
    ),
    (
        "06_figma_specs_problema", 1400,
        "Y fíjate cómo eso conecta directo con algo que la misma Figma publicó apenas tres días antes, el veinte de noviembre, sobre Figma Specs y su trabajo junto al agente para pasar de información dispersa a un plan de implementación. "
        "Quienes trabajamos en productos digitales conocemos de memoria ese dolor de cabeza: tienes las pantallas en Figma, los requerimientos en otra plataforma, las decisiones técnicas en un documento aparte, las conversaciones en Slack o Teams… "
        "y esa decisión crítica que alguien tomó hace tres semanas y que hoy nadie recuerda dónde quedó."
    ),
    (
        "07_figma_specs_comportamientos", 900,
        "Muchas veces lo difícil no es programar el producto; es reconstruir el porqué detrás de cada decisión. "
        "Con Specs, la idea es reunir requisitos, diagramas, componentes, reglas y prototipos en un mismo contexto que puedan leer tanto las personas como los agentes. "
        "Y eso me hace cuestionar algo de fondo: si una inteligencia artificial ya puede traducir una pantalla a código, ¿cuál debería ser realmente el entregable de un diseñador? "
        "Imagina una transferencia en una aplicación bancaria. Dibujar la pantalla es lo fácil. Lo verdaderamente complejo son las casuísticas: beneficiarios guardados, límites transaccionales, un corte de conexión justo al confirmar o un usuario novato que necesita contexto antes de mover su dinero. "
        "Eso es diseñar comportamientos, reglas y decisiones, no solamente interfaces bonitas."
    ),
    (
        "08_zalando_caso", 1500,
        "Ahora bien, una cosa es hablar de teoría y otra ver qué pasa cuando una empresa gigante intenta llevar esto a la práctica. "
        "El nueve de noviembre, en Into Design Systems, el equipo de Zalando compartió cómo construyó su propia herramienta de prototipado con inteligencia artificial, llamada ZDS Capsule, apoyándose en Claude Code y en su propio sistema de diseño. "
        "Lo fascinante no es que hayan hecho otra herramienta más; lo fascinante es por qué tuvieron que construirla."
    ),
    (
        "09_zalando_tokens", 850,
        "Según contaron, las herramientas genéricas de generación de interfaces simplemente no lograban respetar la identidad visual ni las reglas reales de su producto. "
        "A más de uno nos ha pasado: le entregas tu guía a una IA, le pides que use tus componentes… y te devuelve algo que interpretó tu marca con demasiada libertad creativa. "
        "¿Qué hizo Zalando? Volvió a los fundamentos. Preparó design tokens independientes, conectó componentes visuales con su código real y reescribió su documentación y reglas en archivos Markdown para que los agentes pudieran entenderlas sin adivinar."
    ),
    (
        "10_zalando_conocimiento", 900,
        "Esa lección me parece oro puro. Adoptar inteligencia artificial en diseño no empieza comprando la herramienta más ruidosa del mercado; empieza ordenando tu propio conocimiento. "
        "Un sistema de diseño que tiene botones pero no explica cuándo usarlos, o que solo documenta el camino feliz e ignora las excepciones, sigue incompleto. "
        "Cuando conviertes tu sistema de diseño en una verdadera infraestructura de conocimiento, no solo ayudas a una IA a generar mejor código: ayudas a cualquier diseñador humano que llegue nuevo al equipo."
    ),
    (
        "11_lukew_feedback", 1500,
        "Pero espera, porque si los agentes empiezan a usar nuestros sistemas de diseño todos los días, aparece un problema nuevo del que casi nadie estaba hablando. "
        "El tres de noviembre, Luke Wroblewski publicó una reflexión buenísimamente planteada sobre la retroalimentación entre los agentes de inteligencia artificial y los sistemas de diseño. "
        "La realidad es simple: ningún sistema de diseño puede prever todas las combinaciones que surgen al construir software real. Siempre aparecen excepciones y necesidades nuevas."
    ),
    (
        "12_lukew_preguntas", 900,
        "Cuando un diseñador humano encuentra que le falta una variante de un componente, habla con el equipo del sistema y propone una mejora. "
        "Pero, ¿qué pasa cuando quien encuentra ese vacío es un agente de IA? ¿Se inventa el componente? ¿Modifica uno existente por su cuenta? ¿Duplica algo parecido? ¿O le avisa al equipo responsable? "
        "Imagina cincuenta agentes construyendo funcionalidades en paralelo y resolviendo excepciones cada uno a su manera. En pocos meses tendrías cientos de patrones duplicados y un sistema de diseño que solo existe en el papel."
    ),
    (
        "13_lukew_sistema_vivo", 950,
        "Por eso me encanta la idea de pensar en sistemas de diseño vivos: sistemas que no solo reparten componentes, sino que escuchan cómo se usan, registran excepciones y le muestran al equipo humano dónde las reglas se están quedando cortas. "
        "La IA no tiene por qué cambiar las reglas sola, pero sí puede ayudarnos a ver qué necesita evolucionar. "
        "Y eso transforma el trabajo de quienes lideran sistemas de diseño: pasan de ser guardianes de una biblioteca estática a arquitectos de decisiones compartidas entre personas y máquinas."
    ),
    (
        "14_nng_datos_crudos", 1500,
        "Ahora demos un paso atrás y miremos el otro lado de la moneda: los usuarios. "
        "Porque con tanta velocidad para prototipar, corre una ilusión peligrosa en la industria: creer que basta con tirarle transcripciones y comentarios sin procesar a un modelo de IA para que diseñe la solución perfecta. "
        "El veinte de noviembre, Nielsen Norman Group publicó una investigación directa sobre este punto: compararon diseños generados con datos de usuarios sin procesar frente a diseños alimentados con hallazgos previamente sintetizados y recomendaciones."
    ),
    (
        "15_nng_sintesis", 900,
        "El resultado confirma algo que quienes hemos hecho investigación intuíamos: los resultados mejoran claramente cuando hay síntesis humana de por medio. "
        "Piénsalo con un ejemplo cotidiano. Entrevistas a veinte clientes que tuvieron problemas con una app. Uno dice que hay demasiados pasos, otro que no encuentra un botón, otro siente que es insegura y otro prefiere llamar por teléfono. "
        "Si tomas eso literal, terminas quitando pasos, agregando botones y poniendo letreros de seguridad por todas partes. "
        "Pero cuando analizas el patrón real, quizá el problema de fondo sea uno solo: incertidumbre. La gente no sabe qué está pasando ni qué ocurrirá al tocar el botón. "
        "Escuchar a los usuarios no es lo mismo que comprenderlos. Una transcripción no es un hallazgo, y un hallazgo no es automáticamente una solución."
    ),
    (
        "16_nng_research_loop", 1400,
        "Y justo una semana antes, el trece de noviembre, la misma Nielsen Norman Group publicó un concepto que encaja como anillo al dedo con esto: Research-in-the-loop, investigar mientras construimos. "
        "Antes trabajábamos, al menos en teoría, en una secuencia ordenada: investigar, definir, diseñar, probar y lanzar. "
        "Pero hoy, con inteligencia artificial, un equipo puede pasar de una idea a un prototipo funcional en cuestión de horas. A veces el producto sale a producción antes de que investigación termine de agendar entrevistas."
    ),
    (
        "17_nng_velocidad_direccion", 900,
        "Entonces, ¿renunciamos a investigar? Claro que no. La propuesta es integrar la investigación dentro del ciclo continuo: definir qué hipótesis queremos validar antes de construir, observar comportamientos reales mientras se usa y volcar ese aprendizaje en la siguiente iteración. "
        "Hay una diferencia gigante entre construir rápido para aprender y construir rápido simplemente porque la tecnología nos deja hacerlo. "
        "En el primer caso hay una pregunta clara; en el segundo, solo hay velocidad. Y correr muy rápido en la dirección equivocada es la forma más eficiente de desperdiciar tiempo y talento. "
        "Ahí es donde el diseñador recupera su lugar estratégico: ayudando a decidir qué vale la pena construir, no solo ejecutando pedidos."
    ),
    (
        "18_adobe_intenciones", 1500,
        "Y todo este cambio no ocurre solo en el mundo del producto digital; también está sacudiendo la creatividad visual. "
        "El diez de noviembre, Adobe presentó su nueva ola de avances alrededor de Firefly, agentes creativos y experiencias de diseño guiadas por lenguaje natural. "
        "Fíjate en el giro cultural que eso representa. Durante décadas, ser buen creativo implicaba dominar herramientas complejas: atajos de teclado, capas, máscaras, menús escondidos. "
        "Hoy estamos pasando de dominar herramientas a expresar intenciones creativas."
    ),
    (
        "19_adobe_criterio", 950,
        "Eso democratiza muchísimo la creación y baja barreras técnicas, lo cual es genial. Puedes explorar decenas de direcciones en una tarde. "
        "Pero aquí aparece una pregunta incómoda: ¿tener posibilidades casi ilimitadas nos convierte automáticamente en mejores creativos? "
        "Pedir cien propuestas de identidad visual no significa saber cuál representa de verdad a una marca. Generar un anuncio en segundos no significa entender a tu audiencia. "
        "Cuando producir una opción nueva es más fácil que evaluar las que ya tienes, es facilísimo caer en la trampa de confundir cantidad con creatividad. "
        "Más que nunca, lo que marca la diferencia es el criterio: la sensibilidad estética, la intención conceptual y la disciplina para saber cuándo parar y defender una buena decisión."
    ),
    (
        "20_cierre_reflexion", 1500,
        "Cuando juntamos todas estas piezas —desde los agentes en Figma y las especificaciones compartidas, hasta el sistema vivo de Zalando, las advertencias de Luke Wroblewski, los estudios de Nielsen Norman Group y los nuevos flujos de Adobe— aparece una imagen muy clara. "
        "No estamos ante el fin del diseño, ni tampoco ante una varita mágica que resuelve todo sola. "
        "Estamos ante una transformación profunda de nuestro oficio: estamos dejando de ser únicamente productores de pantallas para convertirnos en intérpretes de problemas, facilitadores de decisiones, estrategas y constructores de sistemas de conocimiento."
    ),
    (
        "21_cierre_pregunta", 1500,
        "Y con eso te dejo pensando hoy. "
        "Si producir una interfaz deja de ser la parte más difícil del diseño, ¿dónde estará realmente nuestro valor como diseñadores?"
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
                temperature=0.61,
                top_p=0.76,
            )
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

    lead_in_samples = int(2.6 * sr)
    # 10 seconds ambient music outro as requested
    tail_samples = int(10.0 * sr)

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

    voice_full = Path("/tmp/aparte_09_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 9: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_09_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 4.5)

    out_mp3 = OUT_DIR / "aparte_diseno_despues_ia_p1.mp3"
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
