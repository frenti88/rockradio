#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 8 (Solo Fred):
"¿El minimalismo nos volvió aburridos?"
Inspired by Dolly Borade Solanki's article:
"Beyond Minimalism: 9 Design Trends That Are Quietly Taking Over the UX Industry".

Narrated exclusively with Fred's cloned voice on ElevenLabs (eleven_v3,
voice_id=XTaJGjpMayd6Yf596zn2), with expressive audio tags ([sighs], [chuckles]),
reflective pauses, and the custom cinematic background music bed with sidechain ducking.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
import numpy as np

REPO = Path("/home/antigravity/frenti88/rockradio")
sys.path.insert(0, str(REPO / "podcasts"))

from build_aparte_podcast import probe_dur
from generate_podcast_music import render_bed_wav

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_08_elevenlabs"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

ELEVEN_VOICE_ID = "XTaJGjpMayd6Yf596zn2"
ELEVEN_MODEL_ID = "eleven_v3"

# (id, gap_ms_before, stability, text)
# In eleven_v3, stability supports 0.0 (Creative), 0.5 (Natural), 1.0 (Robust).
CHUNKS = [
    (
        "01_apertura_gancho", 0, 0.5,
        "Hay algo que me viene dando vueltas en la cabeza desde hace un tiempo… "
        "¿En qué momento todas las aplicaciones empezaron a parecerse tanto?"
    ),
    (
        "02_apertura_observacion", 650, 0.5,
        "Es que… uno abre una aplicación bancaria, después entra a una herramienta de productividad, "
        "luego abre una página de inteligencia artificial… y, bueno… [chuckles] parece que todas hubieran contratado al mismo diseñador. "
        "Las mismas tarjetas redondeadas, los mismos fondos blancos, las mismas tipografías limpias, los mismos botones flotando en el mismo lugar."
    ),
    (
        "03_apertura_pregunta", 700, 0.5,
        "Y no me malinterpreten. Muchas funcionan bastante bien. Cumplen. No te pierdes, encuentras lo que buscas, haces la tarea y sigues con tu vida. "
        "Pero entonces me surge una pregunta… ¿Será que, intentando hacer que todo fuera más fácil de usar, "
        "terminamos haciendo que todo fuera un poquito más aburrido?"
    ),
    (
        "04_articulo_intro", 1200, 0.5,
        "[sighs] A ver… hace poco me topé con un artículo que me puso a pensar bastante en esto. "
        "Lo escribió Dolly Borade Solanki y se titula Más allá del minimalismo: nueve tendencias de diseño que están transformando silenciosamente la industria UX. "
        "Y lo interesante, al menos para mí, no fue leerlo como una lista de modas para salir corriendo a copiar mañana, sino como un síntoma. "
        "Como una señal de que algo está cambiando por debajo de la superficie en cómo pensamos el diseño digital."
    ),
    (
        "05_historia_minimalismo", 650, 0.5,
        "Porque durante años —y llevo más de diez años en esto— nos repetimos una especie de mandamiento: "
        "quita todo lo que sobre, deja solo lo esencial, sé consistente, no inventes la rueda. "
        "Y tenía todo el sentido del mundo. Veníamos de interfaces saturadas, llenas de sombras innecesarias, botones que brillaban como si fueran de plástico "
        "y menús imposibles de descifrar. El minimalismo llegó como un respiro. Nos salvó del caos."
    ),
    (
        "06_consistencia_uniformidad", 900, 0.5,
        "Pero, un momento… ¿en qué punto la consistencia se confundió con la uniformidad? "
        "Es que no son lo mismo. Ser consistente significa que un producto tiene reglas claras, que no te obliga a reaprender cómo funciona cada vez que cambias de pantalla. "
        "La uniformidad, en cambio, es cuando todos los productos del planeta deciden hablar con exactamente el mismo tono de voz, "
        "vestirse con la misma camisa blanca y esconder cualquier rasgo de carácter por miedo a incomodar."
    ),
    (
        "07_expresivas", 750, 0.5,
        "Y aquí es donde la cosa se pone interesante. En su artículo, Dolly habla de cómo está regresando lo que llama interfaces expresivas: "
        "tipografías con carácter, contrastes más atrevidos, composiciones editoriales, ilustraciones propias, cosas que te hacen recordar con quién estás hablando. "
        "No es decorar por decorar; es devolverle identidad al producto."
    ),
    (
        "08_bento_ironia", 800, 0.5,
        "Ahora… seamos honestos también. Porque a uno como diseñador le encanta emocionarse con lo nuevo, y luego pasa lo de siempre. "
        "Piensen en las famosas cuadrículas tipo Bento, esas cajas modulares organizadas como si fueran una lonchera japonesa, que también menciona el artículo. "
        "Cuando aparecieron, fueron una maravilla. Te permiten mostrar métricas, notificaciones, estados y accesos rápidos en un mismo golpe de vista sin que todo parezca una lista interminable hacia abajo. "
        "[chuckles] ¿Y qué pasó después? Que todo el mundo empezó a meterlo todo en cajas Bento. Portafolios, dashboards, páginas de producto, hasta menús que no lo necesitaban. "
        "Es casi irónico, ¿no? Una tendencia que nace para darle estructura y frescura a las interfaces termina convirtiéndose en el nuevo uniforme de la industria."
    ),
    (
        "09_critica_minimalismo", 1100, 0.5,
        "Y ahí es donde yo me freno un poco. Porque tampoco creo que el minimalismo haya muerto, ni que ahora tengamos que llenar todas las pantallas de colores chillones y tipografías gigantes. "
        "¿Qué pasa si una interfaz expresiva termina generando sobrecarga visual justo cuando alguien solo quiere hacer una transferencia rápida o leer un dato importante? "
        "Tal vez el problema nunca fue el minimalismo. Tal vez el problema fue aplicarlo en piloto automático, sin preguntarnos qué necesitaba realmente el producto… "
        "ni qué quería sentir la persona del otro lado."
    ),
    (
        "10_ia_nativa", 1300, 0.5,
        "Bueno, pensándolo bien… hay un cambio todavía más profundo que lo visual. "
        "Porque podemos discutir horas sobre tipografías, bordes redondeados y cuadrículas, pero la conversación de fondo ya ni siquiera es sobre cómo se ven las pantallas. "
        "Es sobre cómo se comportan. En el artículo, Dolly describe un giro que a mí me parece clave en la manera en que diseñamos con inteligencia artificial. "
        "Tradicionalmente, el diseño de experiencias funcionaba como una cadena bastante predecible: el usuario hace clic en algo, el sistema responde, el usuario vuelve a actuar. Pantalla tras pantalla, paso tras paso."
    ),
    (
        "11_intencion_decisiones", 650, 0.5,
        "Con las interfaces nativas de inteligencia artificial, esa relación cambia. "
        "Ya no empiezas necesariamente con un formulario de veinte campos. Empiezas con una intención. "
        "Le dices al sistema qué quieres lograr, la inteligencia artificial interpreta esa intención, propone una acción o arma un borrador… y tú confirmas, ajustas o corriges. "
        "Fíjense en lo que eso implica para nuestro trabajo. Estamos pasando de diseñar botones y flujos rígidos a diseñar decisiones, intenciones y comportamientos del sistema."
    ),
    (
        "12_contextuales_intro", 950, 0.5,
        "[sighs] Y eso me conecta directo con algo que me obsesiona bastante: las interfaces contextuales y la personalización real. "
        "No esa personalización superficial de poner tu nombre en un saludo arriba a la derecha o mostrarte tres productos parecidos al último que compraste. "
        "Hablo de experiencias capaces de entender el momento en el que estás, tu nivel de conocimiento previo y lo que de verdad estás tratando de resolver."
    ),
    (
        "13_ejemplo_financiero", 700, 0.5,
        "Hagamos un ejercicio mental. Imaginen una aplicación de servicios financieros. "
        "Por un lado, entra una persona que va a hacer su primera inversión en la vida. "
        "Seguramente tiene dudas, miedo a equivocarse, no entiende la mitad de la jerga financiera y necesita claridad, contexto y acompañamiento paso a paso. "
        "Ahora imaginen, en esa misma aplicación, a alguien con años de experiencia invirtiendo. "
        "Esa persona entra con un objetivo concreto, sabe leer indicadores, quiere comparar rápido y si le pones un tutorial explicándole qué es la rentabilidad, probablemente va a cerrar la aplicación desesperada."
    ),
    (
        "14_pregunta_identicas", 1100, 0.5,
        "¿Por qué seguimos diseñando experiencias prácticamente idénticas para personas que tienen necesidades completamente diferentes? "
        "Es una pregunta incómoda, porque responderla implica aceptar que diseñar una sola pantalla perfecta ya no alcanza."
    ),
    (
        "15_riesgos_autonomia", 900, 0.5,
        "Ahora, ojo con esto… porque aquí también hay un lado oscuro que no podemos ignorar. "
        "Cuando una interfaz se vuelve demasiado inteligente o demasiado personalizada, aparece una línea muy delgada entre ayudar y decidir por ti. "
        "Si el sistema automatiza todo en silencio, sin explicarte por qué te está recomendando algo, sin dejarte editarlo o sin pedirte confirmación cuando la decisión es delicada… pierdes autonomía. "
        "Y en temas como tus finanzas o tus datos personales, perder control no se siente mágico; se siente invasivo."
    ),
    (
        "16_duda_ia", 750, 0.5,
        "Además, hay otra duda válida: ¿de verdad la inteligencia artificial siempre simplifica la experiencia, o a veces simplemente le agrega una capa nueva de incertidumbre? "
        "Porque si no sabes qué hizo el sistema por detrás ni cómo corregirlo cuando se equivoca, terminas trabajando el doble. "
        "Por eso, incluso en el diseño más inteligente, la transparencia y el control humano siguen siendo innegociables."
    ),
    (
        "17_movimiento_lenguaje", 1250, 0.5,
        "Y mientras pensaba en cómo se comunican los sistemas con nosotros, me llamó mucho la atención otro bloque de ideas del artículo: el movimiento y las interfaces espaciales. "
        "A ver… durante mucho tiempo, muchos equipos trataron las animaciones como si fueran el adorno del final. "
        "Cuando terminemos el desarrollo, si queda tiempo, le ponemos unas transiciones bonitas. [chuckles] "
        "Y claro, si la animación es solo un adorno, sobra. Peor aún: a veces estorba y te hace perder segundos valiosos esperando a que una tarjeta termine de rebotar."
    ),
    (
        "18_ejemplo_carrito", 650, 0.5,
        "Pero cuando el movimiento se diseña con intención, se convierte en un lenguaje. No necesitas estar viendo una pantalla ahora mismo para imaginarlo. "
        "Piensa en cuando borras un producto de un carrito de compras. Si simplemente desaparece de golpe en un parpadeo, tu cerebro duda un instante: ¿Se borró? ¿Le di bien? ¿Qué pasó? "
        "En cambio, si el elemento se desliza suavemente hacia afuera mientras el contador del carrito se actualiza en ese mismo instante, no hace falta ningún letrero explicándote nada. "
        "El movimiento te contó la historia completa en medio segundo. "
        "Lo mismo pasa con las microinteracciones: ese pequeño cambio de estado de un botón que te confirma que sí recibió tu toque, "
        "o esa transición que te muestra de dónde salió una pantalla para que no pierdas el sentido de orientación."
    ),
    (
        "19_espacial_3d", 850, 0.5,
        "Y si llevamos esa lógica un paso más allá, llegamos a las experiencias espaciales y en tres dimensiones. "
        "Durante décadas diseñamos atrapados en rectángulos planos. Hoy, con realidad aumentada o mixta, la interfaz empieza a convivir con el espacio físico. "
        "Imaginen querer comprar un sofá y poder proyectarlo a escala real en la sala de su casa antes de pagarlo, caminar alrededor, ver si bloquea el paso o si combina con la luz natural. "
        "Ahí el 3D no es un truco futurista para presumir en una presentación; es una herramienta práctica para tomar una mejor decisión. "
        "Claro, igual que con el resto, toca ser críticos. No todo necesita ser espacial ni todo necesita moverse. "
        "Si una animación no aclara una relación, no da retroalimentación o no orienta tu atención, entonces es ruido."
    ),
    (
        "20_accesibilidad", 1300, 0.5,
        "[sighs] Y esto me lleva a una parte del artículo que, honestamente, creo que debería estar siempre en el centro de cualquier conversación sobre diseño, "
        "aunque a veces sea la menos glamorosa en redes sociales: la accesibilidad, el data storytelling y el diseño sostenible. "
        "Es que hay algo muy curioso con esto. A veces celebramos productos que se ven espectaculares en un monitor enorme de última generación, con internet de alta velocidad y en una oficina con luz perfecta. "
        "Pero en el mundo real… no existe el usuario promedio."
    ),
    (
        "21_accesibilidad_real", 700, 0.5,
        "Dolly lo recuerda muy bien en su texto: las personas usan nuestros productos en condiciones completamente distintas. "
        "Hay quienes tienen discapacidades visuales, auditivas, motoras o cognitivas. "
        "Pero también está quien intenta leer una pantalla bajo el sol del mediodía, quien navega con una sola mano en el transporte público o quien tiene una conexión lenta y un teléfono de hace varios años. "
        "Si tu aplicación solo usa el color rojo para indicar un error, alguien con daltonismo puede quedarse completamente perdido. "
        "Si el contraste es demasiado suave porque se ve más elegante en gris clarito, estás excluyendo gente por pura vanidad estética. "
        "La accesibilidad no es una lista de verificación que se revisa el viernes antes de salir a producción; es la base de diseñar para seres humanos reales."
    ),
    (
        "22_data_y_sostenible", 850, 0.5,
        "Y pasa algo muy parecido con los datos. Nos encanta llenar pantallas de gráficos, números y porcentajes, como si mostrar información fuera lo mismo que hacerla comprensible. "
        "El data storytelling propone otra cosa: darle contexto a los números. Conectar puntos. "
        "Que si entras a ver tus hábitos de salud o tus gastos del mes, el producto no te suelte una tabla fría, sino que te ayude a entender qué cambió, por qué importa y qué podrías hacer al respecto. "
        "Y por último, algo en lo que casi nunca pensamos cuando estamos moviendo píxeles: la huella digital. El diseño sostenible. "
        "A veces olvidamos que cada video pesado que se reproduce automáticamente sin que nadie lo pida, cada imagen sin optimizar y cada script innecesario consume energía en servidores, redes y dispositivos. "
        "Diseñar de forma sostenible no significa pintar la página de verde ni poner un mensaje ecológico en el inicio. "
        "Significa diseñar con respeto por los recursos, por el planeta y también por la batería y el plan de datos de la persona que está usando tu producto."
    ),
    (
        "23_clasicos_norman_krug", 1100, 0.5,
        "En el fondo, me gusta que al final del artículo la autora vuelva a los clásicos: a Don Norman, recordándonos que lo comprensible y lo emocional van de la mano, "
        "y a Steve Krug, con esa idea tan simple y tan vigente de no hacer pensar innecesariamente al usuario. "
        "Porque las tendencias cambian cada dos años, pero la forma en que funcionamos los seres humanos cambia muchísimo más despacio."
    ),
    (
        "24_reflexion_valor", 1400, 0.5,
        "[sighs] Y todo esto me deja pensando en algo más grande. "
        "Hoy en día, generar una interfaz limpia, moderna y visualmente correcta es cada vez más rápido. "
        "Con librerías de componentes, sistemas de diseño e inteligencia artificial, armar una pantalla bonita ya no es el cuello de botella que era hace diez años. "
        "Entonces… ¿dónde queda realmente nuestro valor?"
    ),
    (
        "25_cierre", 1500, 0.5,
        "Tal vez el futuro del diseño no esté en aprender a hacer interfaces más bonitas… "
        "Porque eso, cada vez más, lo puede hacer una máquina. "
        "Tal vez esté en aprender a mirar mejor. En desarrollar criterio para saber cuándo una tendencia suma y cuándo solo distrae. "
        "En hacer mejores preguntas antes de abrir cualquier herramienta. "
        "En entender qué necesita realmente una persona, incluso cuando esa persona todavía no sabe cómo explicarlo. "
        "Y eso… eso cambia completamente lo que significa ser diseñador."
    ),
]


def elevenlabs_tts(text: str, out_mp3: Path, stability: float = 0.5) -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY no está configurada.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    payload = {
        "text": text,
        "model_id": ELEVEN_MODEL_ID,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": 0.80,
        },
    }

    for attempt in range(4):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                    "User-Agent": "curl/8.5.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                audio = resp.read()
            if not audio or len(audio) < 500:
                raise RuntimeError("Respuesta de audio vacía desde ElevenLabs.")
            out_mp3.write_bytes(audio)
            return
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            if attempt == 3:
                raise
            wait = 2.0 * (attempt + 1)
            print(f"[WARN] ElevenLabs intento {attempt + 1} falló ({e}). Reintentando en {wait}s...", flush=True)
            time.sleep(wait)


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

    total_words = sum(len(t.split()) for _, _, _, t in CHUNKS)
    print(f"[SCRIPT] Total spoken words (approx): {total_words}", flush=True)

    for tid, gap_ms, stability, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"

        if not (mp3.exists() and mp3.stat().st_size > 2000):
            print(f"[TTS-EL] {tid} (eleven_v3, stability={stability})...", flush=True)
            elevenlabs_tts(text, mp3, stability=stability)
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
    tail_samples = int(6.5 * sr)

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

    voice_full = Path("/tmp/aparte_08_el_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    voice_end_sec = max_end / sr
    print(f"[TIMELINE] Assembled Aparte Ep 8 (ElevenLabs eleven_v3): voice_end={voice_end_sec:.2f}s, total={total_dur:.2f}s", flush=True)

    bed_wav = Path("/tmp/aparte_08_el_bed.wav")
    print(f"[BED] Rendering cinematic music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_start = max(0.0, total_dur - 3.5)

    out_mp3 = OUT_DIR / "aparte_minimalismo_aburridos.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12,"
            f"afade=t=in:st=0:d=2.0,afade=t=out:st={fade_start:.2f}:d=3.5[b_raw];"
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
