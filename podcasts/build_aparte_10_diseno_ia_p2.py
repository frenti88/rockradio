#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 10 (Solo Fred):
"El diseño después de la IA — Parte 2: El futuro de las experiencias digitales"
Narrated with Fred's Fish Audio drama-3 voice (96e5d63e023a4fd5b7926226ed8db011),
using the same custom Drive background music bed (generate_podcast_music.py)
used in the duo podcasts, with reflective pauses, a 3s final pause, and 10s ambient outro.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_10"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

# (id, gap_ms_before, text)
CHUNKS = [
    (
        "01_intro_contradiccion", 0,
        "Hay una contradicción enorme en el momento que estamos viviendo como industria. "
        "Nunca habíamos tenido tanta capacidad técnica para construir productos digitales… y, sin embargo, seguimos creando experiencias que las personas no comprenden, no necesitan o simplemente no pueden utilizar."
    ),
    (
        "02_intro_puente", 1100,
        "En el episodio anterior conversamos sobre cómo Figma, los sistemas de diseño, la investigación con usuarios y las herramientas creativas están evolucionando gracias a la inteligencia artificial. "
        "Hoy quiero que vayamos un paso más allá. Quiero que hablemos de qué pasa cuando la tecnología empieza a tomar decisiones, ejecutar tareas y construir productos a una velocidad que supera nuestra capacidad para evaluarlos. "
        "¿Qué pasa cuando construir deja de ser el problema… y decidir qué construir se convierte en nuestro mayor desafío?"
    ),
    (
        "03_openai_gpt62", 1400,
        "Arranquemos por lo que pasó el diecisiete de noviembre de dos mil veintiséis. "
        "OpenAI presentó su nueva familia de modelos GPT seis punto dos, enfocada en razonamiento avanzado, programación, ejecución de tareas profesionales y uso directo de herramientas digitales. "
        "Cada vez que sale un modelo nuevo, el ruido en redes se va directo a las tablas comparativas y los porcentajes. "
        "Pero a mí me interesa mirarlo desde otro ángulo: el de la experiencia de usuario."
    ),
    (
        "04_experiencia_delegar", 900,
        "Porque la diferencia real entre un asistente que te responde una pregunta y un agente que ejecuta acciones por ti está en las consecuencias. "
        "Si le pides a una IA que te sugiera cómo organizar un presupuesto y se equivoca, lo corriges y no pasa nada. "
        "Pero si autorizas a un agente financiero o a una plataforma empresarial a ejecutar transferencias, aprobar compras o reprogramar entregas, el diseño cambia por completo. "
        "Aquí nace una categoría nueva: la experiencia de delegar. "
        "Como diseñadores, ya no diseñamos solo flujos donde la persona hace cada clic; ahora diseñamos patrones de autorización, supervisión, transparencia, confirmación y recuperación ante errores. "
        "El usuario necesita saber qué está haciendo el agente, qué permisos tiene y en qué momento exacto debe intervenir."
    ),
    (
        "05_google_gemini_neon", 1500,
        "Y al día siguiente, el dieciocho de noviembre, Google dio otro golpe sobre la mesa con el anuncio de Gemini cuatro Neon y su integración con herramientas como Google AI Studio y Antigravity. "
        "Lo que más me llama la atención de este avance es cómo cambia la forma en que los diseñadores exploramos y comunicamos ideas. "
        "Durante años vivimos atrapados en prototipos estáticos: pantallas conectadas con flechitas donde todo funcionaba perfecto mientras nadie se saliera del guion."
    ),
    (
        "06_interfaces_contextuales", 900,
        "Ahora podemos construir prototipos funcionales con variables, condiciones, reglas de negocio y datos simulados en cuestión de horas. "
        "Piensa en una aplicación financiera diseñada bajo el enfoque de interfaces contextuales. "
        "No le muestra lo mismo a alguien que acaba de abrir su primera cuenta de ahorros que a una persona que lleva años invirtiendo y necesita ver rendimientos detallados al instante. "
        "La experiencia se adapta al momento, al historial y a la intención real de quien está al frente. "
        "Claro, hay que tener los pies en la tierra: un prototipo convincente no es lo mismo que un producto listo para producción, con toda su seguridad y escalabilidad detrás. "
        "Pero sí le devuelve al diseñador una autonomía brutal para experimentar, validar hipótesis y sentarse a la mesa estratégica con evidencia tangible."
    ),
    (
        "07_shopify_caso", 1500,
        "Y si alguien todavía duda de qué tan rápido se está moviendo el desarrollo de software, basta mirar lo que compartió el equipo de ingeniería de Shopify el diez de noviembre. "
        "Publicaron el caso de cómo reconstruyeron su aplicación móvil en apenas doce semanas apoyándose intensamente en agentes de inteligencia artificial, junto a sus ingenieros. "
        "Ahora, ojo: esos son los resultados reportados por Shopify en su propio contexto y con su infraestructura; eso no significa que cualquier empresa vaya a replicar lo mismo mágicamente."
    ),
    (
        "08_shopify_cuello_botella", 900,
        "Pero lo más revelador del caso no es la velocidad en sí, sino dónde apareció el verdadero cuello de botella. "
        "Cuando programar y generar pantallas se vuelve muchísimo más rápido, el problema deja de ser producir… y pasa a ser coordinar, probar, documentar y mantener la coherencia. "
        "Imagina un escenario muy real: tu equipo de diseño genera cien pantallas funcionales en una sola semana. "
        "Suena impresionante, ¿no? Pero, ¿quién garantiza que esas cien pantallas mantienen consistencia, accesibilidad, calidad y una conexión real con el problema del usuario? "
        "Sin sistemas de diseño sólidos, reglas claras y gobernanza, la velocidad solo multiplica el desorden."
    ),
    (
        "09_smashing_necesitamos_ia", 1500,
        "Y justo ahí entra una pregunta que me parece un respiro de aire fresco, planteada el doce de noviembre en Smashing Magazine: ¿realmente necesitamos inteligencia artificial en todos los productos? "
        "Seamos sinceros… últimamente parece que hay una obsesión colectiva por meterle un chat inteligente a cualquier cosa. "
        "¿Quieres cambiar tu contraseña? Habla con nuestro asistente. ¿Quieres filtrar un catálogo por talla y color? Escríbele un párrafo a la IA. "
        "A veces un simple botón, un filtro claro o un buen formulario resuelven el problema en dos segundos, sin hacerte adivinar qué prompt escribir."
    ),
    (
        "10_smashing_metricas", 900,
        "Lo curioso es que muchas funciones que prometen ahorrar tiempo terminan creándote un trabajo nuevo: revisar, verificar y corregir lo que la IA entendió mal. "
        "Eso aumenta la carga cognitiva y erosiona la confianza. "
        "Por eso, antes de sumar IA por moda, vale la pena medir con cabeza fría: ¿reduce de verdad el tiempo de tarea? ¿Mejora la tasa de finalización? ¿Baja los errores? ¿Aumenta la confianza del usuario? "
        "A veces, tomar una gran decisión de diseño significa decir con total seguridad: esta experiencia es mejor sin inteligencia artificial."
    ),
    (
        "11_accesibilidad_velocidad", 1500,
        "Y hay otro costo oculto de esta obsesión por correr, que Smashing Magazine volvió a poner sobre la mesa el diecisiete de noviembre: la accesibilidad. "
        "Cuando la inteligencia artificial acelera la creación de interfaces sin controles rigurosos, es facilísimo producir pantallas que se ven impecables a simple vista… pero que dejan por fuera a millones de personas. "
        "Contraste insuficiente, navegación rota por teclado, jerarquía semántica inexistente o componentes que un lector de pantalla simplemente no logra interpretar."
    ),
    (
        "12_accesibilidad_agentes", 900,
        "Además, las interfaces conversacionales y dinámicas traen retos completamente nuevos. "
        "¿Cómo debería anunciar un lector de pantalla una respuesta que aparece palabra por palabra en tiempo real? "
        "¿Cómo navega una persona entre mensajes, archivos adjuntos y acciones sugeridas cuando la interfaz cambia sola según lo que decide un agente? "
        "La solución no puede ser revisar la accesibilidad al final del proyecto. Tiene que vivir dentro del sistema de diseño, en las instrucciones de los agentes y en pruebas automatizadas… siempre complementadas con pruebas manuales y personas reales. "
        "Porque construir más rápido nunca significa construir mejor si estamos dejando gente afuera."
    ),
    (
        "13_signal_privacidad", 1500,
        "Y llegamos al último gran tema de noviembre, que toca una fibra muy sensible: la privacidad. "
        "El veinte de noviembre, Signal anunció medidas concretas para proteger la privacidad de las conversaciones frente al acceso de ciertos agentes de inteligencia artificial que operan a nivel de sistema o capturan contenido en pantalla. "
        "Y aquí aparece una tensión fascinante y muy real para quienes diseñamos experiencias digitales."
    ),
    (
        "14_signal_limites", 900,
        "Por un lado, para que un asistente contextual sea verdaderamente útil, necesita contexto: saber qué estás haciendo, qué documentos manejas o qué necesitas resolver. "
        "Pero cuando un sistema puede leer tus pantallas, tus mensajes privados o tu información bancaria, el riesgo crece al mismo ritmo que la comodidad. "
        "Ahí es donde la privacidad desde el diseño deja de ser un discurso legal y se vuelve responsabilidad directa del UX: diseñar permisos claros, autorización contextual, transparencia total y una forma sencilla de revocar accesos. "
        "No toda la información disponible debería usarse solo porque la tecnología lo permite. "
        "La pregunta que deberíamos hacernos es directa: ¿estamos diseñando para que la inteligencia artificial tenga acceso a toda la información posible… o únicamente a la información necesaria?"
    ),
    (
        "15_reflexion_final", 1600,
        "Si miramos en conjunto todo lo que recorrimos entre la primera parte y este episodio, queda una sensación muy clara. "
        "No estamos viendo un futuro donde todo se convierta en un chat infinito, ni tampoco un futuro donde el diseñador desaparezca. "
        "Estamos entrando en una etapa donde convivirán interfaces tradicionales, experiencias contextuales adaptativas y agentes capaces de actuar por nosotros. "
        "Un futuro donde la buena tecnología sabrá cuándo ayudar, cuándo mostrar información, cuándo aceptar una tarea delegada… y también cuándo hacerse a un lado y no interrumpir."
    ),
    (
        "16_cierre_uno", 1400,
        "La inteligencia artificial está reduciendo las dificultades que teníamos para construir productos, pero no está eliminando nuestra responsabilidad de decidir qué productos vale la pena construir."
    ),
    (
        "17_cierre_dos", 3000,
        "Antes de preguntarte qué puedes construir con inteligencia artificial, pregúntate qué problema puedes comprender mejor gracias a ella. Quizás ahí esté la verdadera transformación."
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
    # 10 seconds ambient music outro fading out gradually
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

    voice_full = Path("/tmp/aparte_10_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 10: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_10_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 5.0)

    out_mp3 = OUT_DIR / "aparte_diseno_despues_ia_p2.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12,"
            f"afade=t=in:st=0:d=2.0,afade=t=out:st={fade_start:.2f}:d=5.0[b_raw];"
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
