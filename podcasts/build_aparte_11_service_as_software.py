#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 11 (Solo Fred) — Expressive & Unhurried Edition:
"Service as Software: por qué los diseñadores deberían empezar a pensar más allá de las pantallas"
Based on the Bootcamp article by Balogun Ayanfe Olamide.

Directed for Fish Audio drama-3 (voice 96e5d63e023a4fd5b7926226ed8db011) with:
- 24 shorter, breathing-paced chunks with generous reflective pauses (700–1800 ms)
- Scene-by-scene temperature, top_p, subtle pacing (atempo 0.94–1.00), and gentle gain contour
- Standalone question phrases for crisp Spanish interrogative intonation
- Natural mid-sentence (chuckle) and (sigh) cues (never at word 1 to avoid timbre drift)
- Same Drive ambient background music bed with soft sidechain ducking
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_11_v2"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

# (id, gap_ms_before, temp, top_p, tempo, gain_db, text)
CHUNKS = [
    (
        "01_pregunta_inicial", 0, 0.68, 0.79, 0.95, 0.0,
        "¿Y si dejáramos de diseñar herramientas?"
    ),
    (
        "02_apertura_reflexion", 1200, 0.60, 0.76, 0.95, -0.5,
        "Suena un poco raro decirlo en voz alta… sobre todo para quienes llevamos años diseñando pantallas, botones y flujos. "
        "Pero piénsalo un segundo. Hemos pasado décadas diseñando herramientas para ayudar a las personas a hacer su trabajo. "
        "¿Qué pasa ahora que el software empieza a hacer ese trabajo por ellas?"
    ),
    (
        "03_escena_reclutamiento", 1300, 0.65, 0.78, 0.97, 0.0,
        "Imagina esta escena. Una empresa te contrata para diseñar una plataforma de reclutamiento. "
        "Como buen diseñador de producto, te pones manos a la obra: diseñas el dashboard, los perfiles de candidatos, los formularios, los filtros avanzados y cada detalle para que todo sea facilísimo de usar. "
        "Pasas semanas enteras puliendo la experiencia."
    ),
    (
        "04_giro_reclutamiento", 950, 0.72, 0.81, 0.96, 0.8,
        "Pero, un momento… ¿qué pasa si la empresa en realidad no quería otro dashboard? "
        "¿Y si lo único que necesita es recibir una lista de candidatos cualificados cada viernes? "
        "A veces uno se enamora tanto de la interfaz (chuckle) que se le olvida preguntar si el cliente siquiera quiere abrirla. "
        "Tal vez no le interesa gestionar cien postulaciones. Simplemente quiere el trabajo hecho."
    ),
    (
        "05_intro_autor", 1300, 0.62, 0.77, 0.96, 0.0,
        "Hace poco leí un artículo muy bueno de Balogun Ayanfe Olamide, publicado en Bootcamp, que pone el dedo justo en esa llaga con un concepto que cada vez suena más fuerte: Service as Software, o servicio como software. "
        "Y la verdad… si eres diseñador, y más aún si alguna vez has pensado en construir tu propio producto, vale muchísimo la pena detenerse a entender qué está cambiando aquí."
    ),
    (
        "06_saas_clasico", 1100, 0.64, 0.78, 0.97, 0.0,
        "Todos conocemos el modelo clásico de Software as a Service, el famoso SaaS. Piensa en Notion, en Canva o en cualquier CRM tradicional. "
        "Tú pagas una suscripción para acceder a un software que te ayuda a hacer una tarea. La plataforma te entrega las herramientas… pero el trabajo sigue siendo completamente tuyo."
    ),
    (
        "07_sas_contraste", 900, 0.70, 0.80, 0.98, 0.8,
        "Service as Software le da la vuelta a esa lógica! "
        "En lugar de venderte acceso a una herramienta, la empresa te vende la realización de un servicio concreto, usando software e inteligencia artificial detrás de escena para ejecutar gran parte del trabajo. "
        "En el ejemplo del reclutamiento, el sistema hace el filtrado inicial, evalúa los perfiles según criterios acordados y te entrega una lista corta de finalistas lista para revisión humana. "
        "Tú pagas por el servicio recibido, no por la licencia de un software."
    ),
    (
        "08_sequoia_foundation", 1200, 0.62, 0.77, 0.96, 0.0,
        "Y no es solo una idea bonita de blog. En marzo de dos mil veintiséis, Julien Bek, socio de Sequoia Capital, publicó un ensayo titulado Services: The New Software, argumentando que algunas de las mayores oportunidades de la inteligencia artificial podrían venir de empresas que venden trabajo realizado en lugar de simples herramientas. "
        "Ya en dos mil veinticuatro, Foundation Capital había explorado una tesis parecida, estimando una oportunidad de mercado de cuatro coma seis billones de dólares en trabajo y servicios externalizados. "
        "Claro… siempre hay que leer esas cifras con cabeza fría: son estimaciones de inversionistas, no garantías. Pero dejan clarísimo por qué tanta gente está mirando hacia allá."
    ),
    (
        "09_por_que_importa", 1400, 0.66, 0.78, 0.96, 0.4,
        "Ahora, bajemos esto a nuestro terreno. ¿Por qué debería importarnos tanto como diseñadores? "
        "Porque durante años nuestro reflejo automático frente a un problema ha sido diseñar una interfaz para que el usuario lo resuelva. "
        "Investigamos, mapeamos viajes, encontramos fricciones… y casi siempre terminamos construyendo un dashboard más bonito."
    ),
    (
        "10_nng_agentes", 1000, 0.59, 0.75, 0.95, -0.5,
        "Pero, pensémoslo un segundo… ¿qué pasaría si empezáramos a preguntar si el usuario realmente necesita ejecutar ese proceso por sí mismo? "
        "En un artículo de Nielsen Norman Group de dos mil veinticinco, Sarah Gibbons y Pablo Fernández Vallejo explicaban cómo los agentes de inteligencia artificial están pasando a ser participantes activos en la prestación de servicios. "
        "Y eso abre preguntas enormes de diseño: qué responsabilidades asume la IA, cuándo interviene un humano, cómo fluye la información y qué pasa cuando algo falla. Todo eso es diseño de servicios puro."
    ),
    (
        "11_ejemplo_auditoria", 1400, 0.65, 0.78, 0.97, 0.2,
        "Veámoslo con un ejemplo súper concreto. Imagina que eres un diseñador que suele hacer auditorías de usabilidad para empresas que quieren mejorar sus sitios web. "
        "Normalmente un cliente te escribe, entras a su página, revisas pantallas, anotas hallazgos y armas un documento con recomendaciones. "
        "Varias partes de ese proceso son bastante repetitivas. "
        "¿Qué pasaría si convirtieras ese servicio en un pequeño producto?"
    ),
    (
        "12_auditoria_flujo", 850, 0.68, 0.79, 0.98, 0.5,
        "El dueño de la empresa entra a tu plataforma, pega la dirección de su sitio, te cuenta su objetivo y solicita la auditoría. "
        "Por debajo, el sistema recorre las páginas clave, corre chequeos técnicos y de accesibilidad, detecta fricciones evidentes y te arma un borrador estructurado para que tú lo revises antes de enviarlo."
    ),
    (
        "13_criterio_humano", 1000, 0.58, 0.75, 0.95, -0.6,
        "Ahora, ojo con esto… tú sigues revisando el resultado, corrigiendo errores y aportando tu criterio profesional. "
        "Ninguna verificación automática garantiza por sí sola que un sitio sea realmente claro o accesible para todo el mundo. "
        "Pero reduciste muchísimo el esfuerzo manual repetitivo. "
        "Y fíjate en lo que ahora estás diseñando: ya no es solo un formulario bonito. Estás diseñando cómo entender el problema del cliente, qué datos recolectar, cómo manejar análisis incompletos y cómo entregar un informe que realmente sirva. "
        "Y lo mejor: no hace falta automatizarlo todo el primer día. Puedes empezar con un flujo sencillo asistido manualmente e ir refinándolo con tus clientes."
    ),
    (
        "14_modelo_negocio", 1400, 0.67, 0.79, 0.97, 0.4,
        "Y aquí hay otro cambio fascinante que a los diseñadores nos conviene entender: el modelo de negocio. "
        "En el SaaS tradicional, cobras una mensualidad por acceso a la herramienta, la use mucho el cliente o casi nada. "
        "Con Service as Software, el precio puede atarse directamente al trabajo entregado! "
        "En el caso de la auditoría web, podrías cobrar por cada auditoría terminada en lugar de vender una suscripción mensual. "
        "Un caso real de precios basados en resultados es Fin AI Agent, de Intercom, que cobra por resultados específicos como resoluciones de soporte o ciertas transferencias completadas."
    ),
    (
        "15_matiz_resultados", 950, 0.62, 0.77, 0.96, 0.0,
        "Claro, cobrar por resultados tiene su ciencia… hay que definir muy bien qué cuenta como un resultado exitoso. "
        "Transferir un ticket a otra persona (chuckle) no significa automáticamente que el problema original del cliente quedó resuelto. "
        "Y tampoco es el único camino: siguen funcionando las suscripciones, los contratos recurrentes y los modelos híbridos. "
        "Lo clave, sobre todo si quieres emprender como diseñador, es entender cuánto vale el trabajo real que estás entregando."
    ),
    (
        "16_cautela_automatizar", 1400, 0.57, 0.74, 0.94, -0.8,
        "Ahora… pongamos los pies en la tierra. Porque con la inteligencia artificial es facilísimo dejarse llevar por el entusiasmo. "
        "Automatizar un proceso no lo convierte mágicamente en un buen negocio. "
        "¿Qué pasa cuando el agente entrega información equivocada? ¿Quién responde frente al cliente? ¿Qué ocurre cuando alguien pide algo que se sale del molde del sistema? "
        "Cuando un cliente paga por un trabajo hecho, el margen de tolerancia frente a los errores es muchísimo menor."
    ),
    (
        "17_debate_bahr", 1000, 0.59, 0.75, 0.95, -0.5,
        "De hecho, en febrero de dos mil veintiséis, JC Bahr-de Stefano publicó un artículo muy lúcido llamado Services Won't Become Software. "
        "Su punto es muy sensato: la inteligencia artificial puede volver muchísimo más eficientes a las empresas de servicios, sin que por eso dejen de ser empresas de servicios ni se conviertan en compañías de software puro. "
        "Los clientes siguen pagando por criterio experto, por confianza, por responsabilidad y por saber que hay alguien real dando la cara cuando algo sale mal. "
        "Y lejos de restarle valor al diseño, esa realidad lo vuelve todavía más interesante, porque nos obliga a diseñar más allá del camino feliz."
    ),
    (
        "18_por_donde_empezar", 1400, 0.66, 0.78, 0.97, 0.3,
        "Entonces… si esto te dejó picando la curiosidad, ¿por dónde empezar? "
        "Yo no le diría a nadie que renuncie mañana a su trabajo para montar una startup de inteligencia artificial (chuckle). "
        "Empezaría mucho más pequeño. Mira a tu alrededor: ¿por qué servicios ya están pagando las empresas hoy? "
        "Busca procesos repetitivos, que consuman bastante tiempo y donde el cliente pueda describir claramente qué resultado espera."
    ),
    (
        "19_cuatro_preguntas", 900, 0.64, 0.78, 0.96, 0.2,
        "Y ahí hazte cuatro preguntas sencillas. "
        "¿Qué parte de esto se puede automatizar? "
        "¿Qué parte exige sí o sí criterio humano? "
        "¿Por qué resultado concreto pagaría un cliente? "
        "¿Y cómo puedo probar una versión pequeña combinando herramientas existentes y trabajo manual? "
        "La primera versión no tiene que ser cien por ciento autónoma; tiene que resolver un problema real de forma confiable."
    ),
    (
        "20_mas_alla_interfaz", 1400, 0.62, 0.77, 0.96, 0.0,
        "A mí me sigue encantando diseñar interfaces, cuidar la tipografía, armar sistemas de diseño y pulir el detalle visual. No creo que esas habilidades vayan a desaparecer de la noche a la mañana. "
        "Pero sí creo que tenemos una oportunidad enorme para ampliar nuestra mirada. "
        "Porque la próxima gran idea de producto tal vez no sea otra aplicación con un dashboard espectacular… sino un servicio tan bien pensado que resuelva el problema sin obligarte a vivir dentro de una aplicación."
    ),
    (
        "21_cierre_reflexion", 1500, 0.56, 0.74, 0.94, -1.0,
        "Al final, todo esto nos invita a ver la evolución de nuestro oficio con otros ojos. "
        "Hay una diferencia profunda entre diseñar una interacción… diseñar una decisión… y diseñar un resultado. "
        "A veces la mejor experiencia digital no es una pantalla más bonita ni un flujo con menos clics. "
        "A veces, en el contexto adecuado, la mejor experiencia consiste precisamente en eliminar la necesidad de interactuar con la interfaz."
    ),
    (
        "22_cierre_pregunta", 1800, 0.55, 0.74, 0.93, -1.0,
        "Y te dejo con esta pregunta rondando en la cabeza… "
        "¿Estamos dedicando demasiado tiempo a diseñar las herramientas que las personas utilizan… y demasiado poco a comprender el trabajo que realmente necesitan resolver?"
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

    total_words = sum(len(t.split()) for *_, t in CHUNKS)
    print(f"[SCRIPT] Total spoken words (approx): {total_words}", flush=True)

    for tid, gap_ms, temp, top_p, tempo, gain_db, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"

        if not (mp3.exists() and mp3.stat().st_size > 2000):
            print(f"[TTS] {tid} (T={temp}, top_p={top_p}, tempo={tempo}, gain={gain_db:+.1f}dB)...", flush=True)
            g._fish_audio_tts_sync(
                text,
                str(mp3),
                reference_id=FISH_VOICE_ID,
                model=FISH_MODEL_ID,
                temperature=temp,
                top_p=top_p,
            )
        else:
            print(f"[REUSE] {tid}.mp3", flush=True)

        gain_lin = 10.0 ** (gain_db / 20.0)
        af = f"aresample=48000,silenceremove=start_periods=1:start_silence=0.04:start_threshold=-45dB,atempo={tempo},volume={gain_lin:.4f}"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(mp3),
                "-af", af,
                "-ac", "1", "-ar", str(sr),
                str(wav),
            ],
            check=True,
        )
        clips.append((gap_ms, load_wav_mono(wav)))

    lead_in_samples = int(2.8 * sr)
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

    voice_full = Path("/tmp/aparte_11_v2_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 11 v2: voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_11_v2_bed.wav")
    print(f"[BED] Rendering duo-style Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 5.0)

    out_mp3 = OUT_DIR / "aparte_service_as_software.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12,"
            f"afade=t=in:st=0:d=2.2,afade=t=out:st={fade_start:.2f}:d=5.0[b_raw];"
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
