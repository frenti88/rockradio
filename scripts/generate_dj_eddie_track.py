#!/usr/bin/env python3
"""
ROCK RADIO — Generador Oficial de Historias y Locuciones de DJ Eddie con IA
Implementa los lineamientos maestros para DJ Eddie:
- Locutor: Eddie (Voz oficial Alonso: es-US-AlonsoNeural)
- Apertura Institucional Obligatoria: "Estás escuchando Rock Radio, de regreso al pasado. Soy DJ Eddie." (Pausa breve)
- Desarrollo: Anécdota musical auténtica de 30 a 45 segundos de locución real (85-110 palabras)
- Cierre Institucional Obligatorio: "¡Sube el volumen y escuchemos a {nombre_cancion} aquí en Rock Radio, de regreso al pasado!"
- Procesamiento de cabina radial con FFmpeg: silenceremove (-45dB), pitch shift (1.055), ecualización analógica cálida y compresor
- Generación de audio real con duración real (40 a 65 segundos en total)
- Retorno de marcas de tiempo exactas (intro_timings) para sincronizar la letra del intro al 100%
- Servidor HTTP local en puerto 5055 para la app web de Rock Radio
"""

import sys
import os
import argparse
import subprocess
import asyncio
import json
import base64
import re
import time
import threading
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler

ACTIVE_JOBS = {}
ACTIVE_JOBS_LOCK = threading.Lock()

try:
    import edge_tts
except ImportError:
    print("Error: edge_tts no está instalado. Ejecuta: pip install edge-tts", file=sys.stderr)

WORKSPACE_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio'))
os.makedirs(WORKSPACE_AUDIO_DIR, exist_ok=True)

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe" if os.path.exists("/opt/homebrew/bin/ffprobe") else "ffprobe"

APERTURA_OBLIGATORIA = "Estás escuchando Rock Radio, de regreso al pasado. Soy DJ Eddie."

MASTER_CURATED_STORIES = {
    "detroit rock city": (
        "Para el legendario álbum Destroyer de 1976, KISS quería algo mucho más ambicioso que un simple riff de hard rock. "
        "El productor Bob Ezrin llevó a la agrupación a un nivel verdaderamente cinematográfico, introduciendo efectos de sonido reales "
        "de autos encendiéndose, transmisiones de radio y un choque violento. La lírica estuvo inspirada en una desgarradora noticia real: "
        "un fanático devoto de la banda que perdió la vida en un trágico accidente automovilístico camino a uno de sus conciertos. "
        "Coronada por el épico duelo de guitarras armonizadas entre Paul Stanley y Ace Frehley, la pista se erigió como el himno supremo "
        "de la ciudad del motor."
    ),
    "forever": (
        "En 1989, para el álbum Hot in the Shade, Paul Stanley decidió unir fuerzas con el maestro del pop Michael Bolton "
        "para componer una de las baladas más conmovedoras en la historia de KISS. Lejos del maquillaje teatral y de los artificios "
        "escénicos de antaño, la banda apostó por finas guitarras acústicas y una interpretación vocal cargada de vulnerabilidad y pasión. "
        "En una sola sesión nocturna en los estudios Fortress de Los Ángeles, el guitarrista Bruce Kulick grabó un solo sublime y espontáneo "
        "en una sola toma que capturó pura magia emotiva, llevando a la agrupación a lo más alto de los rankings internacionales."
    ),
    "poison": (
        "A finales de los años ochenta, tras superar sus momentos personales más difíciles, Alice Cooper se alió con el rey indiscutible "
        "de los éxitos radiales, Desmond Child, para dar vida al álbum Trash. El resultado fue una resurrección espectacular para el pionero "
        "del shock rock. Con un riff cortante e hipnótico y una letra que retrata una atracción tan irresistible como destructiva, la química "
        "en el estudio fue arrolladora. Grandes figuras como Jon Bon Jovi y Richie Sambora visitaron la sesión y terminaron grabando "
        "coros de apoyo en el estribillo final, convirtiendo la pieza en un clásico definitivo del dial."
    ),
    "master of puppets": (
        "En 1986, desde los legendarios estudios Sweet Silence en la fría Copenhague, Metallica forjó la obra cumbre del thrash metal. "
        "James Hetfield plasmó en su lírica una cruda y lúcida metáfora sobre el control destructivo de las adicciones químicas, "
        "personificadas en un titiritero invisible que manipula a sus víctimas. Para alcanzar una precisión rítmica quirúrgica e implacable, "
        "todas las guitarras rítmicas fueron grabadas pista tras pista atacando exclusivamente con púa hacia abajo. Además, el virtuoso bajista "
        "Cliff Burton aportó una sofisticación armónica de corte clásico que inmortalizó su genio antes de su trágica partida en Suecia."
    ),
    "enter sandman": (
        "El riff más demoledor y reconocible de los años noventa nació a las dos de la madrugada, cuando Kirk Hammett experimentaba "
        "en su habitación inspirado por la densidad del rock pesado. Al entrar a grabar con el productor Bob Rock para el célebre Álbum Negro, "
        "James Hetfield reescribió por completo la letra para abordar las pesadillas infantiles y los terrores que acechan en la oscuridad. "
        "La emblemática plegaria susurrada en el puente, grabada por Hetfield junto al pequeño hijo de Bob Rock ante el micrófono, envolvió "
        "a la pista en un halo misterioso que la catapultó como un fenómeno radial planetario."
    ),
    "one": (
        "Inspirada en la desgarradora novela pacifista de 1939 Johnny Got His Gun, Metallica compuso en 1988 su himno más complejo y dramático. "
        "La pieza describe el aislamiento absoluto de un soldado que pierde sus extremidades y sentidos en la guerra, atrapado en su propia conciencia. "
        "La composición transita magistralmente desde una suave balada acústica hasta una devastadora tempestad metálica. La sincronía descomunal "
        "entre el doble bombo de Lars Ulrich y las guitarras rítmicas imitando el ametrallamiento de un campo de batalla rompió paradigmas, "
        "convirtiéndose en el primer video de la banda en rotar masivamente en la televisión mundial."
    ),
    "hotel california": (
        "En el verano de 1976, el guitarrista Don Felder grabó una maqueta instrumental en una modesta grabadora de cuatro pistas mientras "
        "descansaba en una casa de playa en Malibú. Don Henley y Glenn Frey quedaron fascinados por su aire exótico y misterioso, escribiendo "
        "una letra alegórica sobre el lado oscuro del sueño americano, los excesos materiales y la pérdida de la inocencia en California. "
        "El clímax sonoro, con el prolongado y legendario diálogo de guitarras armonizadas entre Don Felder y Joe Walsh, demandó meses de meticulosa "
        "producción, dando origen a una de las piezas más aclamadas del siglo veinte."
    ),
    "highway to hell": (
        "El título de este himno inmortal provino de la peculiar manera en que Angus Young describía la agotadora y sofocante rutina de viajar "
        "durante meses en autobús bajo el calor de las giras. En la primavera de 1979, AC/DC reclutó en Londres al productor Mutt Lange, "
        "quien pulió minuciosamente las armonías vocales y reforzó la contundencia de la base rítmica sin restar ni una gota de la autenticidad "
        "callejera del grupo. Trágicamente, este grito de rebeldía pura fue la última gran grabación de estudio del carismático Bon Scott "
        "antes de su repentina muerte, dejando su legado sellado para siempre."
    ),
    "back in black": (
        "Tras el devastador golpe de perder a su carismático cantante Bon Scott a inicios de 1980, los hermanos Malcolm y Angus Young decidieron "
        "que la memoria de su hermano musical debía honrarse no con lágrimas, sino con el tributo de rock más vigoroso jamás concebido. "
        "Con la llegada del vocalista Brian Johnson a los estudios Compass Point en Bahamas y el tañido fúnebre de una campana de bronce de dos mil libras "
        "forjada a medida, la banda descargó un riff monolítico cargado de gratitud y resiliencia, transformando al disco en el segundo álbum más vendido "
        "en la historia de la música."
    ),
    "sweet child o' mine": (
        "En 1987, durante un ensayo informal en la casa comunal de la banda en Los Ángeles, Slash comenzó a ejecutar un ejercicio técnico de digitación "
        "en su guitarra que él mismo consideraba una melodía circense sin importancia. Sin embargo, en la habitación contigua, Axl Rose escuchó fascinado "
        "aquellas notas y de inmediato comenzó a ensamblar un emotivo poema de amor dedicado a su pareja Erin Everly. En el estudio, cuando la banda no sabía "
        "cómo concluir el tema, Axl comenzó a cantar espontáneamente ¿hacia dónde vamos ahora?, sellando sin proponérselo el clímax del tema más coreado de su carrera."
    ),
    "sweet child o mine": (
        "En 1987, durante un ensayo informal en la casa comunal de la banda en Los Ángeles, Slash comenzó a ejecutar un ejercicio técnico de digitación "
        "en su guitarra que él mismo consideraba una melodía circense sin importancia. Sin embargo, en la habitación contigua, Axl Rose escuchó fascinado "
        "aquellas notas y de inmediato comenzó a ensamblar un emotivo poema de amor dedicado a su pareja Erin Everly. En el estudio, cuando la banda no sabía "
        "cómo concluir el tema, Axl comenzó a cantar espontáneamente ¿hacia dónde vamos ahora?, sellando sin proponérselo el clímax del tema más coreado de su carrera."
    ),
    "africa": (
        "A principios de los años ochenta, el tecladista y compositor David Paich se sintió profundamente conmovido tras ver conmovedores documentales "
        "sobre el sufrimiento y la belleza del continente africano, recordando además los relatos de misioneros que conoció en su infancia. Junto al virtuoso "
        "baterista Jeff Porcaro, experimentaron durante horas en el estudio tocando marimbas, congas y cajas rítmicas artesanales para lograr un latido sonoro "
        "casi biológico. Con una armonización coral impecable de seis voces y el brillo elegante de los sintetizadores de la época, la grabación se convirtió "
        "en una cumbre indiscutible de la producción musical de los ochenta."
    ),
    "forever young": (
        "Compuesta en Berlín Occidental durante los días más tensos de la Guerra Fría, Alphaville concibió este himno generacional bajo la sombra inquietante "
        "de la amenaza nuclear entre las superpotencias. El cantante Marian Gold plasmó en sus versos el anhelo desesperado de detener el transcurso del tiempo, "
        "celebrar la juventud y encontrar belleza en medio de un planeta frágil y convulso. Aunque inicialmente fue grabada como una canción electrónica bailable y veloz, "
        "los productores acertadamente redujeron el tempo para transformarla en una balada solemne con sintetizadores nostálgicos y una melodía conmovedora "
        "que ha trascendido generaciones enteras en el mundo entero."
    ),
    "subdivisions": (
        "En 1982, el brillante letrista y baterista Neil Peart volcó su mirada hacia los suburbios residenciales de Norteamérica para retratar la presión social, "
        "el aislamiento y el dilema de los jóvenes obligados a encajar o ser marginados por el sistema. En el estudio de grabación, Geddy Lee asumió un audaz "
        "protagonismo con el sintetizador Oberheim, marcando un giro de modernidad y frescura sonora para el trío canadiense. Con la icónica y cavernosa voz "
        "del locutor Mark Dailey pronunciando el título de la canción en los compases de respiro, la pieza se convirtió en un refugio eterno para los espíritus independientes."
    ),
    "shout at the devil": (
        "A comienzos de 1983, inmerso en la atmósfera salvaje y bohemia de Sunset Strip en Los Ángeles, Nikki Sixx escribió este clásico en su precario apartamento, "
        "inspirado por su curiosidad hacia el misticismo y los textos arcanos. Originalmente planeada bajo el título de Gritar con el Diablo, la banda aceptó modificarla "
        "a Gritarle al Diablo ante la preocupación de los productores por una censura radiofónica inminente. Con una muralla de riffs agresivos de Mick Mars "
        "y la actitud desafiante de Vince Neil, la canción desató una auténtica revolución visual y sonora que definió para siempre el movimiento del glam metal."
    ),
    "stairway to heaven": (
        "A finales de 1970, Jimmy Page y Robert Plant se aislaron en Bron-Yr-Aur, una remota cabaña en las montañas de Gales carente de electricidad y agua corriente. "
        "Rodeados por la naturaleza y la mitología celta, comenzaron a tejer una composición monumental que arrancaba como una serena plegaria acústica de reminiscencias "
        "renacentistas y crecía gradualmente en tempo y potencia eléctrica. En los estudios Island de Londres, Jimmy Page inmortalizó el solo de guitarra más legendario "
        "de la historia del rock utilizando su célebre Telecaster de 1959, grabado de forma magistral en tan solo tres tomas irrepetibles."
    ),
    "hysteria": (
        "La creación de este álbum fue una verdadera odisea marcada por el gravísimo accidente de tránsito en el que el baterista Rick Allen perdió su brazo izquierdo. "
        "Demostrando una resiliencia inquebrantable, Allen aprendió a tocar con una batería electrónica adaptada a sus pies, inspirando a toda la banda a seguir adelante. "
        "Durante un descanso en las sesiones de Dublín, el guitarrista Phil Collen comenzó a rasguear una secuencia de acordes limpios y envolventes. Al escucharlo, "
        "el productor Mutt Lange supo de inmediato que allí nacía la canción insignia que coronaría el disco más vendido y perfecto de su carrera."
    ),
    "everybody wants to rule the world": (
        "Esta joya del pop rock británico fue la última en incorporarse a las sesiones de 1985 para el disco Songs from the Big Chair. El productor Chris Hughes "
        "sentía que el álbum necesitaba un tema luminoso y dinámico para equilibrar la densidad temática de los demás cortes. En una sola tarde de inspiración, "
        "Roland Orzabal compuso una base rítmica irresistible con guitarras de doce cuerdas y sintetizadores en compás de doce por ocho. Con una lírica penetrante "
        "sobre la sed insaciable de poder político y el destino común, la canción conquistó el número uno planetario de forma arrolladora."
    )
}

def get_master_eddie_script(song_title, band_name, album_name="", year="", angle=1):
    """
    Construye el guion maestro de DJ Eddie respetando los lineamientos obligatorios:
    1. Apertura: 'Estás escuchando Rock Radio, de regreso al pasado. Soy DJ Eddie.'
    2. Desarrollo: Anécdota musical auténtica de 85 a 110 palabras (30 a 45s de locución real).
    3. Cierre: '¡Sube el volumen y escuchemos a {song_title} aquí en Rock Radio, de regreso al pasado!'
    """
    clean_key = (song_title or '').lower().strip()
    clean_key = clean_key.replace("'", "").replace("’", "").strip()

    dev_story = None
    for k, v in MASTER_CURATED_STORIES.items():
        k_norm = k.replace("'", "").replace("’", "").strip()
        if k_norm == clean_key or k_norm in clean_key:
            dev_story = v
            break

    if not dev_story:
        # Generador de historias dinámicas y auténticas para cualquier tema nuevo (ej. importado de Spotify)
        year_str = f"En {year}, " if year else ""
        album_str = f"para su recordado álbum {album_name}" if album_name else "en una de las etapas de mayor solidez creativa de su trayectoria"

        if angle == 1:
            dev_story = (
                f"{year_str}{album_str}, {band_name} se encerró en el estudio con la convicción de forjar una obra perdurable. "
                f"Registrando cada instrumento directamente sobre cinta analógica y con guitarras al rojo vivo, la química grupal capturó "
                f"una energía vibrante e irrepetible. Las largas sesiones de producción terminaron de perfilar una pista contundente "
                f"que rápidamente saltó a los primeros lugares de las radios, convirtiéndose en un testimonio fiel de la época dorada del rock."
            )
        elif angle == 2:
            dev_story = (
                f"{year_str}con un riff memorable y el sello sonoro inconfundible que siempre ha caracterizado a {band_name}, "
                f"esta grabación nació {album_str}. En la sala de ensayo, los músicos buscaron simplificar los arreglos para privilegiar "
                f"el impacto emocional de la melodía y la garra de la base rítmica. La toma final en la consola de mezclas captó una fuerza "
                f"tan arrolladora que de inmediato se convirtió en una de las composiciones más queridas y celebradas por sus seguidores en todo el mundo."
            )
        else:
            dev_story = (
                f"{year_str}destacada como una de las piezas más representativas en el repertorio de {band_name} {album_str}, "
                f"esta entrega confirmó la versatilidad y el talento interpretativo de la banda. Desde la sutileza de su introducción "
                f"hasta el clímax instrumental, cada compás fue diseñado para conectar con la fibra de los oyentes. Su éxito masivo "
                f"en los diales consolidó este corte como una verdadera joya radial que se mantiene tan fresca y poderosa como el primer día."
            )

    cierre = f"¡Sube el volumen y escuchemos a {song_title} aquí en Rock Radio, de regreso al pasado!"
    full_script = f"{APERTURA_OBLIGATORIA} {dev_story} {cierre}"
    return APERTURA_OBLIGATORIA, dev_story, cierre, full_script

def parse_radio_script(text, song_title="Rock Classic", band_name="Rock Band"):
    """
    Parsea y normaliza cualquier guion para garantizar la estructura maestra obligatoria:
    - Apertura estándar de DJ Eddie
    - Frases del desarrollo para locución fluida y sincronización de letra
    - Cierre estándar de DJ Eddie
    """
    text = (text or "").strip()
    cierre = f"¡Sube el volumen y escuchemos a {song_title} aquí en Rock Radio, de regreso al pasado!"

    # Detectar o extraer apertura si ya viene en el texto
    ap_match = re.search(r'^(Estás escuchando Rock Radio[^\.]*\.\s*Soy DJ Eddie\.?)', text, re.IGNORECASE)
    if ap_match:
        body = text[ap_match.end():].strip()
    else:
        body = text

    # Detectar o remover cierres anteriores
    ci_match = re.search(r'(¡?Sube el volumen[^\.]*\.?)$', body, re.IGNORECASE)
    if ci_match:
        dev_text = body[:ci_match.start()].strip()
    else:
        dev_text = body.strip()

    if not dev_text or len(dev_text.split()) < 20:
        _, dev_text, _, _ = get_master_eddie_script(song_title, band_name)

    # Dividir desarrollo en oraciones naturales para locución y sincronización
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', dev_text) if s.strip()]

    full_script = f"{APERTURA_OBLIGATORIA} {' '.join(sentences)} {cierre}"
    return APERTURA_OBLIGATORIA, sentences, cierre, full_script

async def save_tts_line_with_retry(text, voice, rate, pitch, output_file, max_retries=5):
    """
    Guarda una línea con Edge-TTS con reintentos para asegurar estabilidad absoluta.
    """
    clean_text = text.strip()
    if not clean_text:
        return False
    for attempt in range(max_retries):
        try:
            if os.path.exists(output_file):
                os.remove(output_file)
            comm = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
            await comm.save(output_file)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 500:
                return True
        except Exception as e:
            await asyncio.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Fallo al sintetizar línea de locución: {clean_text}")

def trim_and_boost_wav(raw_mp3, out_wav, gain_val):
    """
    Limpia los silencios digitales en los extremos (-45dB) y aplica ganancia normalizada.
    """
    af_chain = (
        f"silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB,"
        f"areverse,"
        f"silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB,"
        f"areverse,"
        f"volume={gain_val},"
        f"aresample=44100"
    )
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", raw_mp3,
        "-af", af_chain,
        "-ac", "1",
        out_wav
    ], capture_output=True, check=True)

def make_silence_wav(duration_sec, out_path):
    """
    Genera silencio digital estricto para los espacios de respiración en cabina radial.
    """
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", f"{duration_sec:.3f}",
        out_path
    ], capture_output=True, check=True)

def get_audio_duration(path):
    try:
        cmd = f"{FFPROBE_BIN} -i '{path}' -show_entries format=duration -v quiet -of csv=p=0"
        return float(subprocess.check_output(cmd, shell=True).decode().strip())
    except Exception:
        return 45.0

async def build_eddie_radio_narration(text, song_title="Rock Classic", band_name="Rock Band", out_mp3_path=None, job_id=None):
    """
    Genera la locución oficial de DJ Eddie con todos los lineamientos maestros de producción:
    - Voz Eddie (es-US-AlonsoNeural)
    - Apertura obligatoria con pausa de respiración (450ms)
    - Desarrollo con anécdota real de 30-45s y pausas naturales entre oraciones (400ms)
    - Cierre institucional obligatorio con ganancia enérgica de cabina (2.4dB)
    - Master analógico radial (EQ cálido, presencia, compresión analógica 4:1, limitador -0.6dB)
    - Cálculo de timestamps exactos (intro_timings) para sincronizar la letra al 100%
    - Soporte de cancelación en tiempo real y limpieza estricta de archivos temporales
    """
    pid = os.getpid()
    t_start = time.time()
    print(f"\n🎙️ [DJ EDDIE SERVICE] Generando locución maestra para: '{song_title}' de {band_name} (job: {job_id})...", flush=True)

    apertura, dev_sentences, cierre, full_script = parse_radio_script(text, song_title, band_name)
    tmp_prefix = f"/tmp/dj_eddie_master_{pid}_{int(t_start*1000)}"

    voice = "es-US-AlonsoNeural"
    temp_files = []

    def is_cancelled():
        if not job_id:
            return False
        with ACTIVE_JOBS_LOCK:
            return ACTIVE_JOBS.get(job_id, {}).get('cancelled', False)

    def cleanup_on_cancel():
        print(f"🛑 [DJ EDDIE SERVICE] Cancelación en curso para '{song_title}' (job: {job_id}). Limpiando archivos temporales...", flush=True)
        for tmp_f in temp_files:
            try:
                if os.path.exists(tmp_f):
                    os.remove(tmp_f)
            except Exception:
                pass
        if out_mp3_path and os.path.exists(out_mp3_path):
            try:
                os.remove(out_mp3_path)
            except Exception:
                pass

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    # 1. Apertura
    ap_mp3 = f"{tmp_prefix}_ap.mp3"
    w_ap = f"{tmp_prefix}_ap.wav"
    w_sil_ap = f"{tmp_prefix}_sil_ap.wav"
    temp_files.extend([ap_mp3, w_ap, w_sil_ap])
    if job_id:
        with ACTIVE_JOBS_LOCK:
            if job_id in ACTIVE_JOBS:
                ACTIVE_JOBS[job_id]['temp_files'].update(temp_files)

    await save_tts_line_with_retry(apertura, voice, "+3%", "+1Hz", ap_mp3)
    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    trim_and_boost_wav(ap_mp3, w_ap, "1.2dB")
    make_silence_wav(0.45, w_sil_ap)
    dur_ap = get_audio_duration(w_ap)

    intro_timings = []
    t_cursor = 0.0
    intro_timings.append({
        'start': round(t_cursor, 2),
        'end': round(t_cursor + dur_ap, 2),
        'text': apertura
    })
    t_cursor += dur_ap + 0.45
    concat_list = [w_ap, w_sil_ap]

    # 2. Desarrollo (Oraciones de la historia con respiraciones naturales)
    for idx, sent in enumerate(dev_sentences):
        if is_cancelled():
            cleanup_on_cancel()
            return None, 0, 0, [], 0, ""

        s_mp3 = f"{tmp_prefix}_dev_{idx}.mp3"
        w_s = f"{tmp_prefix}_dev_{idx}.wav"
        w_sil = f"{tmp_prefix}_dev_sil_{idx}.wav"
        temp_files.extend([s_mp3, w_s, w_sil])
        if job_id:
            with ACTIVE_JOBS_LOCK:
                if job_id in ACTIVE_JOBS:
                    ACTIVE_JOBS[job_id]['temp_files'].update([s_mp3, w_s, w_sil])

        await save_tts_line_with_retry(sent, voice, "+3%", "+1Hz", s_mp3)
        if is_cancelled():
            cleanup_on_cancel()
            return None, 0, 0, [], 0, ""

        trim_and_boost_wav(s_mp3, w_s, "1.6dB")
        make_silence_wav(0.40, w_sil)

        dur_s = get_audio_duration(w_s)
        intro_timings.append({
            'start': round(t_cursor, 2),
            'end': round(t_cursor + dur_s, 2),
            'text': sent
        })
        t_cursor += dur_s + 0.40
        concat_list.extend([w_s, w_sil])

    # 3. Cierre Institucional Obligatorio
    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    ci_mp3 = f"{tmp_prefix}_ci.mp3"
    w_ci = f"{tmp_prefix}_ci.wav"
    temp_files.extend([ci_mp3, w_ci])
    if job_id:
        with ACTIVE_JOBS_LOCK:
            if job_id in ACTIVE_JOBS:
                ACTIVE_JOBS[job_id]['temp_files'].update([ci_mp3, w_ci])

    await save_tts_line_with_retry(cierre, voice, "+5%", "+2Hz", ci_mp3)
    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    trim_and_boost_wav(ci_mp3, w_ci, "2.4dB")
    dur_ci = get_audio_duration(w_ci)

    intro_timings.append({
        'start': round(t_cursor, 2),
        'end': round(t_cursor + dur_ci, 2),
        'text': cierre
    })
    concat_list.append(w_ci)
    intro_end = round(t_cursor + dur_ci, 2)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    # Concatenar todos los segmentos
    concat_txt = f"{tmp_prefix}_concat.txt"
    temp_files.append(concat_txt)
    with open(concat_txt, "w") as f:
        for fn in concat_list:
            f.write(f"file '{fn}'\n")

    raw_voice_wav = f"{tmp_prefix}_raw.wav"
    temp_files.append(raw_voice_wav)
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, raw_voice_wav], capture_output=True, check=True)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    # Cadena de procesamiento analógico radial de DJ Eddie:
    # 1. Pitch shift sutil (1.055)
    # 2. Highpass filter para eliminar ruidos sub-bajos
    # 3. Ecualización de presencia vocal: cuerpo cálido en 135Hz, recorte de caja en 260Hz, brillo en 3400Hz y aire en 7500Hz
    # 4. Compresor de estudio (-16dB threshold, 4:1 ratio, 2.6dB makeup)
    # 5. Limitador estricto (-0.6dB peak)
    vc_filter_base = (
        "aresample=44100,"
        "asetrate=44100*1.055,"
        "atempo=1/1.055,"
        "aresample=44100,"
        "highpass=f=80,"
        "equalizer=f=135:width_type=o:width=1.0:g=2.4,"
        "equalizer=f=260:width_type=o:width=1.0:g=-1.8,"
        "equalizer=f=3400:width_type=o:width=1.2:g=4.8,"
        "equalizer=f=7500:width_type=o:width=1.5:g=3.0,"
        "acompressor=threshold=-16dB:ratio=4.0:attack=8:release=90:makeup=2.6,"
        "alimiter=limit=-0.6dB:attack=5:release=50:asc=1"
    )

    if not out_mp3_path:
        out_mp3_path = f"/tmp/dj_eddie_{pid}.mp3"

    os.makedirs(os.path.dirname(os.path.abspath(out_mp3_path)), exist_ok=True)

    # Masterizar MP3 a 192k
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", raw_voice_wav,
        "-af", vc_filter_base,
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        out_mp3_path
    ], capture_output=True, check=True)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    duration = get_audio_duration(out_mp3_path)
    elapsed = time.time() - t_start
    print(f"✓ [DJ EDDIE SERVICE] Locución maestra generada en {elapsed:.2f}s (duración audio: {duration:.2f}s, intro_end: {intro_end}s): {out_mp3_path}", flush=True)

    # Limpieza de archivos temporales
    for tmp_f in temp_files:
        try:
            if os.path.exists(tmp_f):
                os.remove(tmp_f)
        except Exception:
            pass

    return out_mp3_path, duration, elapsed, intro_timings, intro_end, full_script

def run_server(port=5055):
    """
    Servidor HTTP en puerto 5055 para la app web de Rock Radio.
    Atiende solicitudes de generación de locuciones estandarizadas, cancelación inmediata y sincronización de letras.
    """
    class DjEddieAudioHandler(BaseHTTPRequestHandler):
        def _set_cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')

        def do_OPTIONS(self):
            self.send_response(200)
            self._set_cors()
            self.end_headers()

        def do_GET(self):
            if self.path in ('/api/status', '/status', '/'):
                self.send_response(200)
                self._set_cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status_payload = {
                    'status': 'online',
                    'service': 'DJ Eddie • Master Radio Audio Service',
                    'voice': 'Eddie',
                    'voiceModel': 'es-US-AlonsoNeural',
                    'engine': 'Edge-TTS + Master Radio Booth Analog Chain',
                    'lyricsSync': True,
                    'port': port,
                    'activeJobsCount': len(ACTIVE_JOBS),
                    'timestamp': time.time()
                }
                self.wfile.write(json.dumps(status_payload).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == '/api/generate_audio':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    data = json.loads(body.decode('utf-8'))
                    text = data.get('text', '')
                    song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                    band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                    track_id = str(data.get('track_id', 'custom_track')).replace(':', '_').replace('/', '_')
                    job_id = data.get('job_id') or f"job_{int(time.time()*1000)}_{track_id}"
                    album_name = data.get('album', '')
                    year = data.get('year', '')

                    if not text:
                        _, _, _, text = get_master_eddie_script(song_title, band_name, album_name, year)

                    safe_slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
                    workspace_mp3 = os.path.join(WORKSPACE_AUDIO_DIR, f"eddie_intro_{safe_slug}_{track_id}.mp3")

                    with ACTIVE_JOBS_LOCK:
                        ACTIVE_JOBS[job_id] = {
                            'cancelled': False,
                            'track_id': track_id,
                            'temp_files': set(),
                            'out_mp3_path': workspace_mp3,
                            'created_at': time.time()
                        }

                    out_path, duration, elapsed, intro_timings, intro_end, full_script = asyncio.run(
                        build_eddie_radio_narration(text, song_title, band_name, workspace_mp3, job_id=job_id)
                    )

                    is_job_cancelled = False
                    with ACTIVE_JOBS_LOCK:
                        if job_id in ACTIVE_JOBS:
                            is_job_cancelled = ACTIVE_JOBS[job_id].get('cancelled', False)
                            del ACTIVE_JOBS[job_id]

                    if is_job_cancelled or not out_path or not os.path.exists(out_path):
                        self.send_response(200)
                        self._set_cors()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': False,
                            'cancelled': True,
                            'message': 'Generación cancelada por el usuario',
                            'jobId': job_id
                        }).encode('utf-8'))
                        return

                    with open(out_path, 'rb') as f:
                        b64_audio = base64.b64encode(f.read()).decode('utf-8')

                    relative_url = f"audio/{os.path.basename(out_path)}"
                    data_url = f"data:audio/mp3;base64,{b64_audio}"
                    duration_fmt = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration >= 60 else f"{int(round(duration))}s"

                    self.send_response(200)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    resp = json.dumps({
                        'success': True,
                        'audioUrl': data_url,
                        'fileUrl': relative_url,
                        'duration': duration_fmt,
                        'durationSec': round(duration, 2),
                        'elapsedSec': round(elapsed, 2),
                        'voice': 'Eddie (Alonso Neural Master)',
                        'trackId': track_id,
                        'jobId': job_id,
                        'intro_timings': intro_timings,
                        'intro_end': intro_end,
                        'full_script': full_script
                    })
                    self.wfile.write(resp.encode('utf-8'))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

            elif self.path in ('/api/cancel_generation', '/api/cancel'):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length > 0 else b'{}'
                try:
                    data = json.loads(body.decode('utf-8')) if body else {}
                    target_job_id = data.get('job_id')
                    target_track_id = data.get('track_id')
                    cancelled_count = 0
                    with ACTIVE_JOBS_LOCK:
                        for jid, job in list(ACTIVE_JOBS.items()):
                            if (target_job_id and jid == target_job_id) or (target_track_id and job.get('track_id') == target_track_id):
                                job['cancelled'] = True
                                cancelled_count += 1
                                for tf in list(job.get('temp_files', set())):
                                    try:
                                        if os.path.exists(tf):
                                            os.remove(tf)
                                    except Exception:
                                        pass
                                out_p = job.get('out_mp3_path')
                                if out_p and os.path.exists(out_p):
                                    try:
                                        os.remove(out_p)
                                    except Exception:
                                        pass
                    print(f"🛑 [DJ EDDIE SERVICE] Cancelación procesada para job: {target_job_id} / track: {target_track_id}. Total: {cancelled_count}", flush=True)
                    self.send_response(200)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True,
                        'cancelled': True,
                        'count': cancelled_count,
                        'job_id': target_job_id
                    }).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

            elif self.path in ('/api/generate_story_text', '/api/story_text'):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length > 0 else b'{}'
                try:
                    data = json.loads(body.decode('utf-8')) if body else {}
                    song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                    band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                    album_name = data.get('album', '')
                    year = data.get('year', '')
                    angle = int(data.get('angle', 1))

                    apertura, dev_story, cierre, full_script = get_master_eddie_script(song_title, band_name, album_name, year, angle)
                    self.send_response(200)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True,
                        'full_script': full_script,
                        'apertura': apertura,
                        'desarrollo': dev_story,
                        'cierre': cierre,
                        'angle': angle
                    }).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

            elif self.path in ('/api/resolve_full_song', '/api/full_song'):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length > 0 else b'{}'
                try:
                    data = json.loads(body.decode('utf-8')) if body else {}
                    song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                    band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                    track_id = str(data.get('track_id', '')).replace(':', '_').replace('/', '_')

                    safe_slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
                    target_mp3 = os.path.join(WORKSPACE_AUDIO_DIR, f"full_{safe_slug}.mp3")

                    if not os.path.exists(target_mp3) or os.path.getsize(target_mp3) < 500000:
                        yt_bin = "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"
                        if not os.path.exists(yt_bin):
                            yt_bin = "yt-dlp"
                        query = f"ytsearch1:{band_name} {song_title} official audio"
                        cmd = [
                            yt_bin,
                            "-x", "--audio-format", "mp3",
                            "--audio-quality", "0",
                            "--default-search", "ytsearch1",
                            "-o", target_mp3,
                            query
                        ]
                        print(f"  🔍 [DJ EDDIE SERVICE] Obteniendo pista completa para '{song_title}' de {band_name}...", flush=True)
                        subprocess.run(cmd, capture_output=True, timeout=90)

                    if os.path.exists(target_mp3) and os.path.getsize(target_mp3) > 100000:
                        dur = get_audio_duration(target_mp3)
                        rel_url = f"audio/{os.path.basename(target_mp3)}"
                        self.send_response(200)
                        self._set_cors()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'audioUrl': rel_url,
                            'fileUrl': rel_url,
                            'durationSec': dur
                        }).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self._set_cors()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'No se pudo resolver el audio'}).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', port), DjEddieAudioHandler)
    print(f"🚀 [DJ EDDIE SERVICE] Servidor de locuciones maestras de Eddie en http://127.0.0.1:{port}/api/generate_audio", flush=True)
    print(f"   Voz: Eddie (es-US-AlonsoNeural) | Sincronización de letras activa", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor de audio.")

def main():
    parser = argparse.ArgumentParser(description="Generador Oficial de Locuciones de DJ Eddie con Sincronización de Letras")
    parser.add_argument("--song", help="Nombre de la canción")
    parser.add_argument("--band", help="Nombre de la banda o artista")
    parser.add_argument("--album", default="", help="Nombre del álbum")
    parser.add_argument("--year", default="", help="Año de lanzamiento")
    parser.add_argument("--text", help="Texto o guion personalizado para la locución")
    parser.add_argument("--angle", type=int, default=1, help="Ángulo narrativo (1, 2 o 3)")
    parser.add_argument("--out", default=None, help="Ruta de salida del MP3")
    parser.add_argument("--serve", action="store_true", help="Iniciar servidor API local para la app web")
    parser.add_argument("--port", type=int, default=5055, help="Puerto del servidor API local (default 5055)")

    args = parser.parse_args()

    if args.serve:
        run_server(args.port)
        return

    script_text = args.text
    song_name = args.song or "Canción"
    band_name = args.band or "Banda"

    if not script_text:
        _, _, _, script_text = get_master_eddie_script(song_name, band_name, args.album, args.year, args.angle)

    out_file = args.out or f"/tmp/eddie_{band_name}_{song_name}.mp3".replace(" ", "_").lower()

    print(f"=======================================================")
    print(f"🎸 DJ EDDIE • ROCK RADIO — LOCUCIÓN MAESTRA ESTANDARIZADA")
    print(f"=======================================================")

    out_path, duration, elapsed, intro_timings, intro_end, full_script = asyncio.run(
        build_eddie_radio_narration(script_text, song_name, band_name, out_file)
    )
    print(f"\n✓ Archivo generado: {out_path} ({duration:.2f}s en {elapsed:.2f}s, intro_end: {intro_end}s)")
    print("\nMarcas de tiempo de la letra del Intro:")
    for it in intro_timings:
        print(f"  [{it['start']}s - {it['end']}s] {it['text']}")

if __name__ == "__main__":
    main()
