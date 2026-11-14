#!/usr/bin/env python3
"""
FRED REWIND — Generador Oficial de Historias y Locuciones de DJ Fredd con IA
Identidad Oficial:
- Producto: Fred Rewind (1 'd')
- Locutor: DJ Fredd (2 'd's)
- Frase Insignia: La música tiene memoria.
- Concepto: De regreso al pasado.
- Voz oficial: es-CO-GonzaloNeural (FM classic rock host, voz cálida medio-grave, dicción evocadora)
- Apertura Obligatoria: "Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd." (Pausa reflexiva 550ms)
- Desarrollo: Anécdota musical auténtica de 30 a 50 segundos de locución real (85-130 palabras) con pausas naturales
- Cierre Obligatorio: "¡Sube el volumen y escuchemos a {nombre_cancion} aquí en Fred Rewind, de regreso al pasado!"
- Masterización radial analógica con FFmpeg: calidez en graves (120Hz), claridad vocal sin sibilancia (2.8kHz),
  aire analógico (10kHz), compresor broadcast LA-2A y limitador a -1.0dB true peak.
- Sincronización milimétrica de letra/guion (intro_timings) sin desfase ni solapamiento.
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
import urllib.request
import urllib.error
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler

ACTIVE_JOBS = {}
ACTIVE_JOBS_LOCK = threading.Lock()

try:
    import edge_tts
except ImportError:
    edge_tts = None

WORKSPACE_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio'))
os.makedirs(WORKSPACE_AUDIO_DIR, exist_ok=True)

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe" if os.path.exists("/opt/homebrew/bin/ffprobe") else "ffprobe"

APERTURA_OBLIGATORIA = "Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd."

DEFAULT_VOICE = "es-US-AlonsoNeural"
DEFAULT_FISH_VOICE = os.environ.get("FISH_VOICE_ID", "e8303fcb17bd4a8ba7709b1f6d3416f7")
DEFAULT_FISH_MODEL = os.environ.get("FISH_MODEL", "s2.1-pro-free")
DEFAULT_MUSIC_BED = os.path.join(WORKSPACE_AUDIO_DIR, "fred_rewind_rock_bed.mp3")

def load_env_local():
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(workspace_dir, '.env.local')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"\'')
                    if k and k not in os.environ:
                        os.environ[k] = v
load_env_local()


MASTER_CURATED_STORIES = {
    "bohemian rhapsody": (
        "En el caluroso verano de 1975, Freddie Mercury llegó a los estudios Rockfield en Gales con la estructura de Bohemian Rhapsody concebida en pequeñas hojas de papel y guías telefónicas. "
        "Mercury, Brian May y Roger Taylor pasaron semanas grabando armonías vocales durante doce horas al día, regrabando tantas capas que la cinta de dos pulgadas se volvió prácticamente transparente por el desgaste físico del cabezal. "
        "Cuando los ejecutivos discográficos insistieron en que una pieza operística de casi seis minutos jamás sonaría en las radios comerciales, la banda entregó una copia exclusiva al legendario locutor Kenny Everett, desatando una fascinación colectiva que cambió para siempre los horizontes de la música contemporánea."
    ),
    "detroit rock city": (
        "Para el legendario álbum Destroyer de 1976, KISS quería algo mucho más ambicioso que un simple riff de hard rock. "
        "El productor Bob Ezrin llevó a la agrupación a un nivel verdaderamente cinematográfico, introduciendo efectos de sonido reales de autos encendiéndose, transmisiones de radio y un choque violento. "
        "La lírica estuvo inspirada en una desgarradora noticia real: un fanático devoto de la banda que perdió la vida en un trágico accidente automovilístico camino a uno de sus conciertos. "
        "Coronada por el épico duelo de guitarras armonizadas entre Paul Stanley y Ace Frehley, la pista se erigió como el himno supremo de la ciudad del motor."
    ),
    "sweet child o' mine": (
        "En 1987, durante un ensayo informal en la casa comunal de la banda en Sunset Strip, Slash comenzó a ejecutar un ejercicio técnico de digitación en su guitarra que él mismo consideraba una melodía circense sin importancia. "
        "Sin embargo, en la habitación contigua, Axl Rose escuchó fascinado aquellas notas y de inmediato comenzó a ensamblar un emotivo poema de amor dedicado a su pareja Erin Everly. "
        "En el estudio, cuando la banda no sabía cómo concluir el tema, Axl comenzó a cantar espontáneamente ¿hacia dónde vamos ahora?, sellando sin proponérselo el clímax del tema más coreado de su carrera."
    ),
    "sweet child o mine": (
        "En 1987, durante un ensayo informal en la casa comunal de la banda en Sunset Strip, Slash comenzó a ejecutar un ejercicio técnico de digitación en su guitarra que él mismo consideraba una melodía circense sin importancia. "
        "Sin embargo, en la habitación contigua, Axl Rose escuchó fascinado aquellas notas y de inmediato comenzó a ensamblar un emotivo poema de amor dedicado a su pareja Erin Everly. "
        "En el estudio, cuando la banda no sabía cómo concluir el tema, Axl comenzó a cantar espontáneamente ¿hacia dónde vamos ahora?, sellando sin proponérselo el clímax del tema más coreado de su carrera."
    ),
    "back in black": (
        "Tras el devastador golpe de perder a su carismático cantante Bon Scott a inicios de 1980, los hermanos Malcolm y Angus Young decidieron que la memoria de su hermano musical debía honrarse no con lágrimas, sino con el tributo de rock más vigoroso jamás concebido. "
        "Con la llegada del vocalista Brian Johnson a los estudios Compass Point en Bahamas y el tañido fúnebre de una campana de bronce de dos mil libras forjada a medida, la banda descargó un riff monolítico cargado de gratitud y resiliencia, transformando al disco en el segundo álbum más vendido en la historia de la música."
    ),
    "paranoid": (
        "En el otoño de 1970, durante las sesiones finales de su segundo disco en los estudios Regent Sound de Londres, Black Sabbath descubrió que el álbum necesitaba tres minutos adicionales para completar la duración requerida por el sello discográfico. "
        "Mientras el resto del grupo almorzaba en un pub cercano, el guitarrista Tony Iommi se quedó solo en la sala improvisando un riff frenético y punzante. "
        "Al regresar la banda, el bajista Geezer Butler escribió apresuradamente los versos sobre la alienación mental en un trozo de papel mientras Ozzy Osbourne memorizaba la melodía. "
        "Grabada en apenas veinticinco minutos como un simple relleno de última hora, la pieza se convirtió en el mayor éxito planetario del heavy metal."
    ),
    "rock and roll all nite": (
        "A principios de 1975, en una habitación del hotel Hyatt de Los Ángeles conocida popularmente como el Riot House, Paul Stanley y Gene Simmons recibieron una advertencia urgente de Casablanca Records: la banda necesitaba con urgencia un himno unificador que capturara la energía electrizante de sus conciertos. "
        "Stanley ideó el contagioso estribillo mientras rasgueaba su guitarra en el hotel, mientras Simmons aportó versos inspirados en una vieja composición suya. "
        "Grabada en los estudios Electric Lady de Nueva York junto a un coro improvisado que incluía miembros del equipo técnico y secretarias, la canción se convirtió en el credo definitivo de toda una generación."
    ),
    "hotel california": (
        "En el verano de 1976, el guitarrista Don Felder grabó una maqueta instrumental en una modesta grabadora de cuatro pistas mientras descansaba en una casa de playa en Malibú. "
        "Don Henley y Glenn Frey quedaron fascinados por su aire exótico y misterioso, escribiendo una letra alegórica sobre el lado oscuro del sueño americano, los excesos materiales y la pérdida de la inocencia en California. "
        "El clímax sonoro, con el prolongado y legendario diálogo de guitarras armonizadas entre Don Felder y Joe Walsh, demandó meses de meticulosa producción, dando origen a una de las piezas más aclamadas del siglo veinte."
    ),
    "stairway to heaven": (
        "A finales de 1970, Jimmy Page y Robert Plant se aislaron en Bron-Yr-Aur, una remota cabaña en las montañas de Gales carente de electricidad y agua corriente. "
        "Rodeados por la naturaleza y la mitología celta, comenzaron a tejer una composición monumental que arrancaba como una serena plegaria acústica de reminiscencias renacentistas y crecía gradualmente en tempo y potencia eléctrica. "
        "En los estudios Island de Londres, Jimmy Page inmortalizó el solo de guitarra más legendario de la historia del rock utilizando su célebre Telecaster de 1959, grabado de forma magistral en tan solo tres tomas irrepetibles."
    ),
    "highway to hell": (
        "El título de este himno inmortal provino de la peculiar manera en que Angus Young describía la agotadora y sofocante rutina de viajar durante meses en autobús bajo el calor de las giras. "
        "En la primavera de 1979, AC/DC reclutó en Londres al productor Mutt Lange, quien pulió minuciosamente las armonías vocales y reforzó la contundencia de la base rítmica sin restar ni una gota de la autenticidad callejera del grupo. "
        "Trágicamente, este grito de rebeldía pura fue la última gran grabación de estudio del carismático Bon Scott antes de su repentina muerte, dejando su legado sellado para siempre."
    ),
    "master of puppets": (
        "En 1986, desde los legendarios estudios Sweet Silence en la fría Copenhague, Metallica forjó la obra cumbre del thrash metal. "
        "James Hetfield plasmó en su lírica una cruda y lúcida metáfora sobre el control destructivo de las adicciones químicas, personificadas en un titiritero invisible que manipula a sus víctimas. "
        "Para alcanzar una precisión rítmica quirúrgica e implacable, todas las guitarras rítmicas fueron grabadas pista tras pista atacando exclusivamente con púa hacia abajo. "
        "Además, el virtuoso bajista Cliff Burton aportó una sofisticación armónica de corte clásico que inmortalizó su genio antes de su trágica partida en Suecia."
    ),
    "enter sandman": (
        "El riff más demoledor y reconocible de los años noventa nació a las dos de la madrugada, cuando Kirk Hammett experimentaba en su habitación inspirado por la densidad del rock pesado. "
        "Al entrar a grabar con el productor Bob Rock para el célebre Álbum Negro, James Hetfield reescribió por completo la letra para abordar las pesadillas infantiles y los terrores que acechan en la oscuridad. "
        "La emblemática plegaria susurrada en el puente, grabada por Hetfield junto al pequeño hijo de Bob Rock ante el micrófono, envolvió a la pista en un halo misterioso que la catapultó como un fenómeno radial planetario."
    ),
    "one": (
        "Inspirada en la desgarradora novela pacifista de 1939 Johnny Got His Gun, Metallica compuso en 1988 su himno más complejo y dramático. "
        "La pieza describe el aislamiento absoluto de un soldado que pierde sus extremidades y sentidos en la guerra, atrapado en su propia conciencia. "
        "La composición transita magistralmente desde una suave balada acústica hasta una devastadora tempestad metálica. "
        "La sincronía descomunal entre el doble bombo de Lars Ulrich y las guitarras rítmicas imitando el ametrallamiento de un campo de batalla rompió paradigmas, convirtiéndose en el primer video de la banda en rotar masivamente en la televisión mundial."
    ),
    "poison": (
        "A finales de los años ochenta, tras superar sus momentos personales más difíciles, Alice Cooper se alió con el rey indiscutible de los éxitos radiales, Desmond Child, para dar vida al álbum Trash. "
        "El resultado fue una resurrección espectacular para el pionero del shock rock. "
        "Con un riff cortante e hipnótico y una letra que retrata una atracción tan irresistible como destructiva, la química en el estudio fue arrolladora. "
        "Grandes figuras como Jon Bon Jovi y Richie Sambora visitaron la sesión y terminaron grabando coros de apoyo en el estribillo final, convirtiendo la pieza en un clásico definitivo del dial."
    ),
    "forever": (
        "En 1989, para el álbum Hot in the Shade, Paul Stanley decidió unir fuerzas con el maestro del pop Michael Bolton para componer una de las baladas más conmovedoras en la historia de KISS. "
        "Lejos del maquillaje teatral y de los artificios escénicos de antaño, la banda apostó por finas guitarras acústicas y una interpretación vocal cargada de vulnerabilidad y pasión. "
        "En una sola sesión nocturna en los estudios Fortress de Los Ángeles, el guitarrista Bruce Kulick grabó un solo sublime y espontáneo en una sola toma que capturó pura magia emotiva, llevando a la agrupación a lo más alto de los rankings internacionales."
    ),
    "africa": (
        "A principios de los años ochenta, el tecladista y compositor David Paich se sintió profundamente conmovido tras ver documentales sobre la belleza del continente africano, recordando además los relatos de misioneros que conoció en su infancia. "
        "Junto al virtuoso baterista Jeff Porcaro, experimentaron durante horas en el estudio tocando marimbas, congas y cajas rítmicas artesanales para lograr un latido sonoro casi biológico. "
        "Con una armonización coral impecable de seis voces y el brillo elegante de los sintetizadores de la época, la grabación se convirtió en una cumbre indiscutible de la producción musical de los ochenta."
    ),
    "forever young": (
        "Compuesta en Berlín Occidental durante los días más tensos de la Guerra Fría, Alphaville concibió este himno generacional bajo la sombra inquietante de la amenaza nuclear entre las superpotencias. "
        "El cantante Marian Gold plasmó en sus versos el anhelo desesperado de detener el transcurso del tiempo, celebrar la juventud y encontrar belleza en medio de un planeta frágil y convulso. "
        "Aunque inicialmente fue grabada como una canción electrónica bailable, los productores acertadamente redujeron el tempo para transformarla en una balada solemne con sintetizadores nostálgicos y una melodía conmovedora que ha trascendido generaciones."
    ),
    "subdivisions": (
        "En 1982, el brillante letrista y baterista Neil Peart volcó su mirada hacia los suburbios residenciales de Norteamérica para retratar la presión social, el aislamiento y el dilema de los jóvenes obligados a encajar o ser marginados por el sistema. "
        "En el estudio de grabación, Geddy Lee asumió un audaz protagonismo con el sintetizador Oberheim, marcando un giro de modernidad y frescura sonora para el trío canadiense. "
        "Con la icónica y cavernosa voz del locutor Mark Dailey pronunciando el título de la canción en los compases de respiro, la pieza se convirtió en un refugio eterno para los espíritus independientes."
    ),
    "shout at the devil": (
        "A comienzos de 1983, inmerso en la atmósfera salvaje de Sunset Strip en Los Ángeles, Nikki Sixx escribió este clásico en su precario apartamento, inspirado por su curiosidad hacia el misticismo y los textos arcanos. "
        "Originalmente planeada bajo el título de Gritar con el Diablo, la banda aceptó modificarla a Gritarle al Diablo ante la preocupación de los productores por una censura radiofónica inminente. "
        "Con una muralla de riffs agresivos de Mick Mars y la actitud desafiante de Vince Neil, la canción desató una auténtica revolución visual y sonora que definió para siempre el movimiento del glam metal."
    ),
    "hysteria": (
        "La creación de este álbum fue una verdadera odisea marcada por el gravísimo accidente de tránsito en el que el baterista Rick Allen perdió su brazo izquierdo. "
        "Demostrando una resiliencia inquebrantable, Allen aprendió a tocar con una batería electrónica adaptada a sus pies, inspirando a toda la banda a seguir adelante. "
        "Durante un descanso en las sesiones de Dublín, el guitarrista Phil Collen comenzó a rasguear una secuencia de acordes limpios y envolventes. "
        "Al escucharlo, el productor Mutt Lange supo de inmediato que allí nacía la canción insignia que coronaría el disco más vendido y perfecto de su carrera."
    ),
    "everybody wants to rule the world": (
        "Esta joya del pop rock británico fue la última en incorporarse a las sesiones de 1985 para el disco Songs from the Big Chair. "
        "El productor Chris Hughes sentía que el álbum necesitaba un tema luminoso y dinámico para equilibrar la densidad temática de los demás cortes. "
        "En una sola tarde de inspiración, Roland Orzabal compuso una base rítmica irresistible con guitarras de doce cuerdas y sintetizadores en compás de doce por ocho. "
        "Con una lírica penetrante sobre la sed insaciable de poder político y el destino común, la canción conquistó el número uno planetario de forma arrolladora."
    ),
    "help": (
        "En 1965, durante la cumbre de la Beatlemanía, The Beatles filmaban su segunda película entre las Bahamas y Londres. "
        "John Lennon, sintiendo el peso abrumador de la fama mundial y un profundo agotamiento emocional, compuso esta confesión directa y honesta en su mansión de Kenwood. "
        "Aunque Paul McCartney y la banda la vistieron con un ritmo de rock and roll enérgico y brillante, Lennon siempre la consideró uno de sus temas más sinceros y personales de toda su carrera."
    ),
    "smoke on the water": (
        "En diciembre de 1971, Deep Purple viajó a Montreux en Suiza para grabar en el Casino frente al lago Ginebra usando el estudio móvil de The Rolling Stones. "
        "Durante un concierto de Frank Zappa, un asistente disparó una bengala hacia el techo de mimbre, provocando un devastador incendio que consumió todo el edificio. "
        "Desde la ventana de su hotel, la banda observó una inmensa columna de humo extendiéndose sobre las aguas del lago. "
        "Inspirado por esa visión dramática y guiado por el riff más icónico de Ritchie Blackmore con su Stratocaster, nació el clásico más coreado en la historia del rock."
    ),
    "dream on": (
        "Steven Tyler compuso las notas iniciales de este himno en un viejo piano vertical de la posada de su familia en Sunapee, Nuevo Hampshire, cuando apenas tenía catorce años. "
        "Años más tarde, durante las difíciles sesiones de grabación del primer disco de Aerosmith en Boston, Tyler temía que su voz sonara inmadura ante el micrófono, por lo que utilizó un tono vocal más grave en todo el álbum excepto en esta pista. "
        "En el clímax final, Steven liberó su registro natural alcanzando notas agudas desgarradoras que catapultaron a la banda hacia el estrellato definitivo."
    ),
    "comfortably numb": (
        "Nacida inicialmente como una maqueta descartada para el álbum en solitario de David Gilmour, la música cobró una dimensión trascendental cuando Roger Waters la integró a la ópera rock The Wall. "
        "Waters escribió los versos recordando el shock físico y la desconexión emocional que sufrió en Filadelfia en 1977 tras recibir inyecciones de sedantes para poder salir al escenario con fiebre alta. "
        "Grabado en apenas dos tomas con su legendaria Black Stratocaster, el majestuoso solo final de David Gilmour es aclamado mundialmente como la cúspide emotiva de la guitarra eléctrica en el rock."
    )
}

def get_master_eddie_script(song_title, band_name, album_name="", year="", angle=1):
    """
    Construye el guion maestro de DJ Fredd respetando los lineamientos obligatorios:
    1. Apertura: 'Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.'
    2. Desarrollo: Anécdota musical auténtica de 30 a 50 segundos de locución real (85-130 palabras).
    3. Cierre: '¡Sube el volumen y escuchemos a {song_title} aquí en Fred Rewind, de regreso al pasado!'
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
        year_str = f"En {year}, " if year else ""
        album_str = f"para su recordado álbum {album_name}" if album_name else "en una de las etapas de mayor solidez creativa de su trayectoria"

        if angle == 1:
            dev_story = (
                f"{year_str}{album_str}, {band_name} se encerró en el estudio con la convicción de forjar una obra perdurable. "
                f"Porque la música tiene memoria, registrando cada instrumento directamente sobre cinta analógica y con guitarras al rojo vivo, "
                f"la química grupal capturó una energía vibrante e irrepetible. Las largas sesiones de producción terminaron de perfilar una pista contundente "
                f"que rápidamente saltó a los primeros lugares de las radios, convirtiéndose en un testimonio fiel de la época dorada del rock."
            )
        elif angle == 2:
            dev_story = (
                f"{year_str}con un riff memorable y el sello sonoro inconfundible que siempre ha caracterizado a {band_name}, "
                f"esta grabación nació {album_str}. En la sala de ensayo, los músicos buscaron simplificar los arreglos para privilegiar "
                f"el impacto emocional de la melodía y la garra de la base rítmica. La toma final en la consola de mezclas captó una fuerza "
                f"tan arrolladora que de inmediato se convirtió en una de las composiciones más queridas y celebradas por sus seguidores en todo el mundo. "
                f"La música tiene memoria, y esta joya sonora lo demuestra compás a compás."
            )
        else:
            dev_story = (
                f"{year_str}destacada como una de las piezas más representativas en el repertorio de {band_name} {album_str}, "
                f"esta entrega confirmó la versatilidad y el talento interpretativo de la banda. Desde la sutileza de su introducción "
                f"hasta el clímax instrumental, cada compás fue diseñado para conectar con la fibra de los oyentes. Como siempre recordamos aquí en Fred Rewind, "
                f"la música tiene memoria, y este clásico perdura tan fresco y poderoso como el primer día."
            )

    cierre = f"¡Sube el volumen y escuchemos a {song_title} aquí en Fred Rewind, de regreso al pasado!"
    full_script = f"{APERTURA_OBLIGATORIA} {dev_story} {cierre}"
    return APERTURA_OBLIGATORIA, dev_story, cierre, full_script

def generate_ai_story_script(song_title, band_name, album_name="", year="", angle=1):
    """
    Genera un guion de DJ Fredd usando IA (OpenAI gpt-4o-mini o Gemini) o catálogo maestro de respaldo.
    Cumple rigurosamente:
    - APERTURA: 'Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.'
    - DESARROLLO: Anécdota musical auténtica de al menos 30 segundos narrados (90-130 palabras).
    - CIERRE: '¡Sube el volumen y escuchemos a {song_title} aquí en Fred Rewind, de regreso al pasado!'
    - Frase insignia: 'La música tiene memoria'.
    """
    cierre = f"¡Sube el volumen y escuchemos a {song_title} aquí en Fred Rewind, de regreso al pasado!"
    api_key = os.environ.get('OPENAI_API_KEY')

    if api_key:
        try:
            import requests
            system_prompt = (
                "Eres DJ Fredd, el respetado locutor de radio de rock clásico de la emisora 'Fred Rewind'. "
                "Tu frase insignia es 'La música tiene memoria' y el concepto del programa es 'De regreso al pasado'. "
                "Hablas con tono cálido, medio-grave, melómano, apasionado por las historias musicales de los 60s, 70s, 80s y 90s, "
                "con estilo de radio clásica FM en español latinoamericano. "
                "Tu tarea es escribir el guion oficial para narrar la historia detrás de una canción."
            )
            user_prompt = (
                f"Escribe la historia oficial para la canción '{song_title}' de '{band_name}' "
                f"(Álbum: '{album_name or 'Clásico'}', Año: '{year or 'Época Clásica'}').\n\n"
                "ESTRUCTURA OBLIGATORIA:\n"
                f"1. APERTURA EXACTA:\n\"{APERTURA_OBLIGATORIA}\"\n\n"
                "2. DESARROLLO (Anécdota musical auténtica):\n"
                "- Narra una historia real, interesante y verificable sobre la composición, grabación en el estudio, anécdotas de los músicos o el impacto histórico que la convirtió en un clásico.\n"
                "- Duración mínima narrada: al menos 30 a 45 segundos de locución real (entre 90 y 130 palabras en el desarrollo).\n"
                "- No inventes fechas ni acontecimientos falsos.\n"
                "- Incorpora de forma natural y elegante la frase insignia: 'La música tiene memoria'.\n"
                "- Puntuación cuidada con comas y puntos para pausas orgánicas de respiración en la voz de radio. No uses etiquetas técnicas ni acotaciones entre paréntesis.\n\n"
                f"3. CIERRE EXACTO:\n\"{cierre}\""
            )
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 380
            }
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            if resp.status_code == 200:
                resp_data = resp.json()
                raw_text = resp_data["choices"][0]["message"]["content"].strip()

                desarrollo = raw_text
                desarrollo = re.sub(r'^(?:"?Estás escuchando Fred Rewind, de regreso al pasado\.\s*Soy DJ Fredd\.?"?)\s*', '', desarrollo, flags=re.IGNORECASE).strip()
                desarrollo = re.sub(r'(?:"?¡?Sube el volumen y escuchemos a .*? aquí en Fred Rewind, de regreso al pasado!?"?)\s*$', '', desarrollo, flags=re.IGNORECASE).strip()
                desarrollo = desarrollo.strip('"\' ')

                if len(desarrollo.split()) >= 60:
                    full_script = f"{APERTURA_OBLIGATORIA} {desarrollo} {cierre}"
                    word_count = len(desarrollo.split())
                    dur_est = round(word_count / 2.3)
                    return {
                        "success": True,
                        "full_script": full_script,
                        "apertura": APERTURA_OBLIGATORIA,
                        "desarrollo": desarrollo,
                        "cierre": cierre,
                        "source": "openai_gpt_4o_mini",
                        "words": word_count,
                        "duration_est_sec": dur_est
                    }
        except Exception as e:
            print(f"⚠️ [DJ FREDD AI] Fallback a historias maestras por: {e}", flush=True)

    # Fallback to master curated stories
    apertura, dev_story, cierre_text, full_script = get_master_eddie_script(song_title, band_name, album_name, year, angle)
    word_count = len(dev_story.split())
    dur_est = round(word_count / 2.3)
    return {
        "success": True,
        "full_script": full_script,
        "apertura": apertura,
        "desarrollo": dev_story,
        "cierre": cierre_text,
        "source": "curated_master",
        "words": word_count,
        "duration_est_sec": dur_est
    }


# ==============================================================================
# DICCIONARIO FONÉTICO MAESTRO PARA PRONUNCIACIÓN NATIVA EN INGLÉS (DJ FREDD)
# Utiliza límites de palabras exactos (\\b) para que nombres propios, bandas,
# discos, canciones, estudios y términos técnicos se pronuncien en inglés con total fluidez.
# ==============================================================================
ENGLISH_PHONETICS = [
    # Marca y Estación
    (r'\bFred Rewind\b', 'Fred Riuáind'),
    (r'\bDJ Fredd\b', 'Dí-yéi Fred'),
    (r'\bDJ Eddie\b', 'Dí-yéi Fred'),
    (r'\bDJ\b', 'Dí-yéi'),
    (r'\bRewind\b', 'Riuáind'),

    # Bandas y Agrupaciones
    (r'\bThe Beatles\b', 'De Bítels'),
    (r'\bBeatles\b', 'Bítels'),
    (r'\bBeatlemanía\b', 'Bítel-manía'),
    (r'\bThe Rolling Stones\b', 'De Róling Stóuns'),
    (r'\bRolling Stones\b', 'Róling Stóuns'),
    (r'\bThe Who\b', 'De Ju'),
    (r'\bThe Doors\b', 'De Dors'),
    (r'\bThe Police\b', 'De Polís'),
    (r'\bThe Clash\b', 'De Klash'),
    (r'\bLed Zeppelin\b', 'Led Zépelin'),
    (r'\bPink Floyd\b', 'Pink Flóid'),
    (r'\bDeep Purple\b', 'Dip Pérpol'),
    (r'\bBlack Sabbath\b', 'Blak Sábas'),
    (r'\bQueen\b', 'Cuín'),
    (r'\bAC/DC\b', 'Ei-Si Di-Si'),
    (r'\bACDC\b', 'Ei-Si Di-Si'),
    (r'\bAerosmith\b', 'Éro-smiz'),
    (r'\bKiss\b', 'Kis'),
    (r'\bKISS\b', 'Kis'),
    (r'\bKISS Army\b', 'Kis Ármi'),
    (r'\bGuns N\' Roses\b', 'Gans en Róuses'),
    (r'\bGuns N Roses\b', 'Gans en Róuses'),
    (r'\bGuns and Roses\b', 'Gans and Róuses'),
    (r'\bMetallica\b', 'Metálica'),
    (r'\bIron Maiden\b', 'Áiron Méiden'),
    (r'\bJudas Priest\b', 'Yúdas Prist'),
    (r'\bDef Leppard\b', 'Def Lépard'),
    (r'\bMötley Crüe\b', 'Mótli Krú'),
    (r'\bMotley Crue\b', 'Mótli Krú'),
    (r'\bBon Jovi\b', 'Bon Yóvi'),
    (r'\bScorpions\b', 'Scór-pions'),
    (r'\bTwisted Sister\b', 'Tuísted Síster'),
    (r'\bDire Straits\b', 'Dáir Stréits'),
    (r'\bFleetwood Mac\b', 'Flít-wud Mak'),
    (r'\bThe Eagles\b', 'De Ígols'),
    (r'\bEagles\b', 'Ígols'),
    (r'\bLynyrd Skynyrd\b', 'Lénard Skínard'),
    (r'\bCreedence Clearwater Revival\b', 'Kridens Klir-uóter Rivaival'),
    (r'\bCreedence\b', 'Kridens'),
    (r'\bVan Halen\b', 'Van Jéilen'),
    (r'\bRush\b', 'Rásh'),
    (r'\bToto\b', 'Tóu-tou'),
    (r'\bAlphaville\b', 'Álfa-vil'),
    (r'\bTears for Fears\b', 'Tíars for Fíars'),
    (r'\bBoston\b', 'Bóston'),
    (r'\bJourney\b', 'Yérni'),
    (r'\bForeigner\b', 'Fóreiner'),
    (r'\bKansas\b', 'Kánsas'),
    (r'\bSurvivor\b', 'Ser-váivor'),
    (r'\bEurope\b', 'Yúrop'),
    (r'\bWhitesnake\b', 'Uáit-sneik'),
    (r'\bDio\b', 'Dí-o'),
    (r'\bDokken\b', 'Dóken'),
    (r'\bQuiet Riot\b', 'Kuáiet Rái-ot'),
    (r'\bSkid Row\b', 'Skid Róu'),
    (r'\bNirvana\b', 'Nir-vána'),
    (r'\bPearl Jam\b', 'Perl Yam'),
    (r'\bSoundgarden\b', 'Sáund-garden'),
    (r'\bAlice in Chains\b', 'Ális in Chéins'),

    # Músicos, Productores y Locutores
    (r'\bJohn Lennon\b', 'Yón Lénon'),
    (r'\bLennon\b', 'Lénon'),
    (r'\bPaul McCartney\b', 'Pol Macárney'),
    (r'\bMcCartney\b', 'Macárney'),
    (r'\bGeorge Harrison\b', 'Yorch Járison'),
    (r'\bRingo Starr\b', 'Ringo Star'),
    (r'\bFreddie Mercury\b', 'Frédi Mérkuri'),
    (r'\bBrian May\b', 'Bráian Méi'),
    (r'\bRoger Taylor\b', 'Róyer Téilor'),
    (r'\bJohn Deacon\b', 'Yón Díkon'),
    (r'\bRobert Plant\b', 'Róbert Plánt'),
    (r'\bJimmy Page\b', 'Yími Péiy'),
    (r'\bJohn Paul Jones\b', 'Yón Pol Yóuns'),
    (r'\bJohn Bonham\b', 'Yón Bón-jam'),
    (r'\bMick Jagger\b', 'Mik Yáguer'),
    (r'\bKeith Richards\b', 'Kiz Ríchards'),
    (r'\bPaul Stanley\b', 'Pol Stánli'),
    (r'\bGene Simmons\b', 'Yin Símons'),
    (r'\bAce Frehley\b', 'Eis Fréili'),
    (r'\bPeter Criss\b', 'Píter Cris'),
    (r'\bBruce Kulick\b', 'Brus Kúlik'),
    (r'\bBob Ezrin\b', 'Bob Éz-rin'),
    (r'\bMichael Bolton\b', 'Máikel Bólton'),
    (r'\bAxl Rose\b', 'Áksel Róus'),
    (r'\bSlash\b', 'Slásh'),
    (r'\bDuff McKagan\b', 'Daf Mac-Kágan'),
    (r'\bIzzy Stradlin\b', 'Ízi Strád-lin'),
    (r'\bSteven Adler\b', 'Stíven Ádler'),
    (r'\bJames Hetfield\b', 'Yéims Jét-fild'),
    (r'\bKirk Hammett\b', 'Kerk Jámet'),
    (r'\bLars Ulrich\b', 'Lars Úl-rik'),
    (r'\bCliff Burton\b', 'Klif Bér-ton'),
    (r'\bBob Rock\b', 'Bob Rok'),
    (r'\bAngus Young\b', 'Ángus Yang'),
    (r'\bMalcolm Young\b', 'Málcolm Yang'),
    (r'\bBon Scott\b', 'Bon Skot'),
    (r'\bBrian Johnson\b', 'Bráian Yónson'),
    (r'\bOzzy Osbourne\b', 'Ózi Ósborn'),
    (r'\bRandy Rhoads\b', 'Rándi Róuds'),
    (r'\bTony Iommi\b', 'Tóni Aiómi'),
    (r'\bGeezer Butler\b', 'Guízer Bátler'),
    (r'\bAlice Cooper\b', 'Ális Kú-per'),
    (r'\bDesmond Child\b', 'Déz-mond Cháild'),
    (r'\bJon Bon Jovi\b', 'Yon Bon Yóvi'),
    (r'\bRichie Sambora\b', 'Ríchi Sambóra'),
    (r'\bJoe Elliott\b', 'Yóu Éliot'),
    (r'\bRick Allen\b', 'Rik Álen'),
    (r'\bSteve Clark\b', 'Stiv Klark'),
    (r'\bPhil Collen\b', 'Fil Kólen'),
    (r'\bMutt Lange\b', 'Mat Lang'),
    (r'\bNikki Sixx\b', 'Níki Síks'),
    (r'\bVince Neil\b', 'Vins Níl'),
    (r'\bMick Mars\b', 'Mik Mars'),
    (r'\bTommy Lee\b', 'Tómi Lí'),
    (r'\bKlaus Meine\b', 'Kláus Máine'),
    (r'\bRudolf Schenker\b', 'Rúdolf Shénker'),
    (r'\bMatthias Jabs\b', 'Matías Yabs'),
    (r'\bDon Henley\b', 'Don Jénli'),
    (r'\bGlenn Frey\b', 'Glen Frái'),
    (r'\bDon Felder\b', 'Don Félder'),
    (r'\bJoe Walsh\b', 'Yóu Uólsh'),
    (r'\bTimothy B. Schmit\b', 'Tímosi Shmit'),
    (r'\bJeff Porcaro\b', 'Yef Porcáro'),
    (r'\bDavid Paich\b', 'Déivid Péich'),
    (r'\bSteve Lukather\b', 'Stiv Lukáser'),
    (r'\bMarian Gold\b', 'Már-ian Góld'),
    (r'\bGeddy Lee\b', 'Guédi Lí'),
    (r'\bAlex Lifeson\b', 'Áleks Láif-son'),
    (r'\bNeil Peart\b', 'Nil Pírt'),
    (r'\bDee Snider\b', 'Di Snáider'),
    (r'\bEddie Ojeda\b', 'Édi Oyéda'),
    (r'\bRonnie James Dio\b', 'Róni Yéims Dí-o'),
    (r'\bGeorge Lynch\b', 'Yorch Linch'),
    (r'\bDon Dokken\b', 'Don Dóken'),
    (r'\bKurt Cobain\b', 'Kert Kobéin'),
    (r'\bDave Grohl\b', 'Déiv Groul'),
    (r'\bKrist Novoselic\b', 'Krist Novosélik'),
    (r'\bEddie Vedder\b', 'Édi Vé-der'),
    (r'\bChris Cornell\b', 'Kris Kornél'),
    (r'\bSteven Tyler\b', 'Stíven Táiler'),
    (r'\bDavid Gilmour\b', 'Déivid Guílmor'),
    (r'\bRoger Waters\b', 'Róyer Uóters'),
    (r'\bRitchie Blackmore\b', 'Ríchi Blákmor'),
    (r'\bFrank Zappa\b', 'Frank Zápa'),
    (r'\bKenny Everett\b', 'Kéni Éver-et'),
    (r'\bNeil Bogart\b', 'Nil Bóugart'),
    (r'\bChris Hughes\b', 'Kris Jiús'),
    (r'\bRoland Orzabal\b', 'Róuland Or-zábal'),
    (r'\bErin Everly\b', 'Érin Éver-li'),
    (r'\bMark Dailey\b', 'Mark Déi-li'),

    # Canciones y Álbumes
    (r'\bBohemian Rhapsody\b', 'Boují-mian Rápsodi'),
    (r'\bA Night at the Opera\b', 'Ei Náit at de Ópera'),
    (r'\bSweet Child O\' Mine\b', 'Suít Cháild o Máin'),
    (r'\bSweet Child of Mine\b', 'Suít Cháild ov Máin'),
    (r'\bAppetite for Destruction\b', 'Ápetait for Destrák-shon'),
    (r'\bDetroit Rock City\b', 'Detróit Rok Síti'),
    (r'\bDestroyer\b', 'Destróier'),
    (r'\bRock and Roll All Nite\b', 'Rok and Roul Ol Náit'),
    (r'\bAlive!\b', 'Aláiv'),
    (r'\bBack in Black\b', 'Bak in Blák'),
    (r'\bHighway to Hell\b', 'Jái-wei tu Jel'),
    (r'\bHotel California\b', 'Joutél Califórnia'),
    (r'\bStairway to Heaven\b', 'Stér-wei tu Jéven'),
    (r'\bParanoid\b', 'Pár-anoid'),
    (r'\bIron Man\b', 'Áiron Man'),
    (r'\bWar Pigs\b', 'Uór Pigs'),
    (r'\bMaster of Puppets\b', 'Máster ov Pá-pets'),
    (r'\bRide the Lightning\b', 'Ráid de Láit-ning'),
    (r'\bEnter Sandman\b', 'Énter Sánd-man'),
    (r'\bThe Black Album\b', 'De Blak Álbum'),
    (r'\bÁlbum Negro\b', 'Álbum Negro'),
    (r'\bJohnny Got His Gun\b', 'Yóni Got Jis Gan'),
    (r'\bOne\b', 'Uan'),
    (r'\bPoison\b', 'Póison'),
    (r'\bTrash\b', 'Trash'),
    (r'\bForever\b', 'For-éver'),
    (r'\bHot in the Shade\b', 'Jot in de Shéid'),
    (r'\bAfrica\b', 'Áfrika'),
    (r'\bRosanna\b', 'Rou-sána'),
    (r'\bToto IV\b', 'Tóu-tou Cuátro'),
    (r'\bForever Young\b', 'For-éver Yang'),
    (r'\bSubdivisions\b', 'Sab-diví-shons'),
    (r'\bSignals\b', 'Sígnals'),
    (r'\bMoving Pictures\b', 'Múving Pík-churs'),
    (r'\bTom Sawyer\b', 'Tom Sóyer'),
    (r'\bShout at the Devil\b', 'Sháut at de Dévil'),
    (r'\bDr\. Feelgood\b', 'Dóktor Fíl-gud'),
    (r'\bHysteria\b', 'Jistíria'),
    (r'\bPyromania\b', 'Pairo-méinia'),
    (r'\bPour Some Sugar on Me\b', 'Por Sam Shúgar on Mí'),
    (r'\bSongs from the Big Chair\b', 'Songs from de Big Chér'),
    (r'\bEverybody Wants to Rule the World\b', 'Évribadi Uónts tu Rul de Uérld'),
    (r'\bSmoke on the Water\b', 'Smóuk on de Uóter'),
    (r'\bMachine Head\b', 'Mashín Jed'),
    (r'\bDream On\b', 'Drim On'),
    (r'\bWalk This Way\b', 'Uók Dis Uéi'),
    (r'\bComfortably Numb\b', 'Kómforta-bli Nam'),
    (r'\bWish You Were Here\b', 'Uísh Yú Uér Jír'),
    (r'\bThe Wall\b', 'De Uól'),
    (r'\bHelp!\b', '¡Jelp!'),
    (r'\bHelp\b', 'Jelp'),
    (r'\bYesterday\b', 'Yéster-dei'),
    (r'\bHey Jude\b', 'Jéi Yúd'),
    (r'\bLet It Be\b', 'Let It Bí'),
    (r'\bCome Together\b', 'Kam Tu-gué-der'),
    (r'\bSomething\b', 'Sám-zing'),
    (r'\bA Day in the Life\b', 'Ei Déi in de Láif'),
    (r'\bWe Will Rock You\b', 'Ui Uíl Rok Yú'),
    (r'\bWe Are the Champions\b', 'Ui Ar de Chám-pions'),
    (r'\bAnother One Bites the Dust\b', 'Anó-der Uan Báits de Dast'),
    (r'\bThe Price\b', 'De Práis'),
    (r'\bWe\'re Not Gonna Take It\b', 'Uir Not Gó-na Téik It'),
    (r'\bRainbow in the Dark\b', 'Réin-bou in de Dárk'),
    (r'\bHoly Diver\b', 'Jóu-li Dáiver'),
    (r'\bDream Warriors\b', 'Drim Uórriors'),
    (r'\bCrazy Train\b', 'Kréisi Tréin'),
    (r'\bMr\. Crowley\b', 'Míster Króu-li'),
    (r'\bWind of Change\b', 'Uínd ov Chéiny'),
    (r'\bRock You Like a Hurricane\b', 'Rok Yú Láik ei Jér-ri-kein'),
    (r'\bDon\'t Stop Believin\'\b', 'Dount Stop Bilívin'),
    (r'\bEye of the Tiger\b', 'Ái ov de Táiguer'),
    (r'\bThe Final Countdown\b', 'De Fáinal Káunt-daun'),
    (r'\bJump\b', 'Yamp'),

    # Lugares, Estudios y Términos Técnicos
    (r'\bSunset Strip\b', 'Sánset Strip'),
    (r'\bAbbey Road\b', 'Ábi Róud'),
    (r'\bRockfield\b', 'Rók-fild'),
    (r'\bCompass Point\b', 'Kómpas Póint'),
    (r'\bSweet Silence\b', 'Suít Sáilens'),
    (r'\bIsland Studios\b', 'Áiland Stúdios'),
    (r'\bElectric Lady\b', 'Iléktrik Léidi'),
    (r'\bRegent Sound\b', 'Ríyent Sáund'),
    (r'\bFortress\b', 'Fórtres'),
    (r'\bKenwood\b', 'Kén-wud'),
    (r'\bBron-Yr-Aur\b', 'Bron-er-áur'),
    (r'\bMontreux\b', 'Mon-tró'),
    (r'\bSunapee\b', 'Sána-pi'),
    (r'\bRiot House\b', 'Rái-ot Jáus'),
    (r'\bHyatt\b', 'Jái-at'),
    (r'\bCasablanca Records\b', 'Kasa-blánka Rékords'),
    (r'\bCapital Radio\b', 'Cápital Réidio'),
    (r'\bOberheim\b', 'Óber-jaim'),
    (r'\bTelecaster\b', 'Tel-e-káster'),
    (r'\bStratocaster\b', 'Strato-káster'),
    (r'\bBlack Stratocaster\b', 'Blak Strato-káster'),
    (r'\bGibson\b', 'Guíb-son'),
    (r'\bLes Paul\b', 'Les Pol'),
    (r'\brock and roll\b', 'rok and roul'),
    (r'\bhard rock\b', 'jard rok'),
    (r'\bheavy metal\b', 'jevi metal'),
    (r'\bglam rock\b', 'glam rok'),
    (r'\bthrash metal\b', 'zrash metal'),
    (r'\bshock rock\b', 'shok rok'),
    (r'\bpop rock\b', 'pop rok'),
    (r'\briff\b', 'rif'),
    (r'\briffs\b', 'rifs'),
    (r'\btrack\b', 'trak'),
    (r'\btracks\b', 'traks'),
    (r'\bhit\b', 'jit'),
    (r'\bhits\b', 'jits'),
    (r'\bsingle\b', 'sínguel'),
    (r'\bsingles\b', 'sínguels'),
    (r'\bfrontman\b', 'front-man'),
    (r'\bline-up\b', 'láin-ap'),
    (r'\bshow\b', 'shóu'),
    (r'\bshows\b', 'shóus'),
    (r'\blive\b', 'láiv'),
    (r'\bplay\b', 'pléi'),
    (r'\bplaylist\b', 'pléi-list'),
    (r'\bLP\b', 'el-pé')
]

def apply_english_phonetics(text):
    """
    Sustituye nombres propios, bandas, discos y términos en inglés por su pronunciación fonética nativa
    para que la voz neural de DJ Fredd (es-CO-GonzaloNeural) los pronuncie de forma natural y auténtica.
    """
    if not text:
        return ""
    result = text
    for pattern, replacement in ENGLISH_PHONETICS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def parse_radio_script(text, song_title="Rock Classic", band_name="Rock Band"):
    """
    Parsea y normaliza cualquier guion para garantizar la estructura oficial de Fred Rewind:
    - Apertura estándar de DJ Fredd
    - Oraciones del desarrollo separadas para pausas naturales de respiración y sincronización
    - Cierre estándar de DJ Fredd
    """
    text = (text or "").strip()
    cierre = f"¡Sube el volumen y escuchemos a {song_title} aquí en Fred Rewind, de regreso al pasado!"

    # Detectar o extraer apertura si ya viene en el texto
    ap_match = re.search(r'^(Estás escuchando (?:Fred Rewind|Rock Radio)[^\.]*\.\s*Soy DJ (?:Fredd|Eddie)\.?)', text, re.IGNORECASE)
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

    # Dividir desarrollo en oraciones naturales por puntuación
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', dev_text) if s.strip()]

    full_script = f"{APERTURA_OBLIGATORIA} {' '.join(sentences)} {cierre}"
    return APERTURA_OBLIGATORIA, sentences, cierre, full_script

def make_silence_mp3(duration_sec, out_path):
    """
    Genera silencio digital estricto para los espacios de respiración en cabina radial.
    """
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", f"{duration_sec:.3f}",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        out_path
    ], capture_output=True, check=True)

def get_audio_duration(path):
    try:
        cmd = f"{FFPROBE_BIN} -i '{path}' -show_entries format=duration -v quiet -of csv=p=0"
        return float(subprocess.check_output(cmd, shell=True).decode().strip())
    except Exception:
        return 45.0

def _fish_audio_tts_sync(text, out_mp3_path, reference_id=DEFAULT_FISH_VOICE, model=DEFAULT_FISH_MODEL):
    api_key = os.environ.get("FISH_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FISH_API_KEY no está configurada en el entorno.")

    raw_tmp = f"{out_mp3_path}.fish_raw.mp3"
    payload = {
        "text": text,
        "reference_id": reference_id,
        "format": "mp3",
        "mp3_bitrate": 192,
        "normalize": True,
        "latency": "normal"
    }
    max_retries = 4
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                "https://api.fish.audio/v1/tts",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "model": model
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                audio_bytes = resp.read()
            with open(raw_tmp, "wb") as f:
                f.write(audio_bytes)
            break
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2.0 * (attempt + 1)
            print(f"⚠️ [Fish Audio] Intento {attempt + 1} falló ({e}). Reintentando en {wait_time}s...", flush=True)
            time.sleep(wait_time)

    # Normalizar a 44100Hz mono 192k MP3 para concatenación limpia sin saltos
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", raw_tmp,
        "-ar", "44100", "-ac", "1",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        out_mp3_path
    ], capture_output=True, check=True)
    try:
        os.remove(raw_tmp)
    except Exception:
        pass

async def synthesize_fish_audio_tts(sem, text, out_mp3_path, reference_id=DEFAULT_FISH_VOICE, model=DEFAULT_FISH_MODEL):
    async with sem:
        await asyncio.to_thread(_fish_audio_tts_sync, text, out_mp3_path, reference_id, model)

async def build_eddie_radio_narration(text, song_title="Rock Classic", band_name="Rock Band", out_mp3_path=None, job_id=None, engine=None, fish_voice=None):
    """
    Genera la locución oficial de DJ Fredd con los lineamientos de audio maestro:
    1. Pronunciación natural multilingüe (Fish Audio S2.1 Pro Free) o fonética inglesa (Edge-TTS).
    2. Cadencia de radio FM cálida, entusiasta y enérgica.
    3. Momentos de respiración calibrados después de puntos finales y apertura (550ms tras apertura, 450ms entre oraciones).
    4. Pausa dramática previa al cierre (650ms) y energía motivada en la presentación musical.
    5. Masterización analógica con FFmpeg: calidez vocal 120Hz, corte de asperezas, brillo aéreo 10kHz y compresión broadcast.
    6. Marcas de tiempo (intro_timings) 100% exactas para sincronización milimétrica en pantalla.
    7. Cancelación segura y limpieza estricta de archivos temporales.
    """
    pid = os.getpid()
    t_start = time.time()
    use_fish = (engine == "fish") or (engine is None and bool(os.environ.get("FISH_API_KEY", "").strip()))
    selected_fish_voice = fish_voice or DEFAULT_FISH_VOICE
    engine_label = f"Fish Audio ({DEFAULT_FISH_MODEL}, voz={selected_fish_voice[:8]}...)" if use_fish else f"Edge-TTS ({DEFAULT_VOICE})"
    print(f"\n🎙️ [DJ FREDD SERVICE] Generando locución maestra ({engine_label}) para: '{song_title}' de {band_name} (job: {job_id})...", flush=True)

    apertura, dev_sentences, cierre, full_script = parse_radio_script(text, song_title, band_name)
    tmp_prefix = f"/tmp/fred_rewind_{pid}_{int(t_start*1000)}"

    voice = DEFAULT_VOICE
    temp_files = []

    def is_cancelled():
        if not job_id:
            return False
        with ACTIVE_JOBS_LOCK:
            return ACTIVE_JOBS.get(job_id, {}).get('cancelled', False)

    def cleanup_on_cancel():
        print(f"🛑 [DJ FREDD SERVICE] Cancelación en curso para '{song_title}' (job: {job_id}). Limpiando temporales...", flush=True)
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

    # 1. Preparar textos hablados
    if use_fish:
        ap_tts = f"[excited] {apertura}"
        dev_tts_list = list(dev_sentences)
        ci_tts = f"[excited] {cierre}"
    else:
        ap_spoken = apply_english_phonetics(apertura)
        ap_tts = ap_spoken.replace("Fred Riuáind,", "Fred Riuáind...").replace("Fred Riuáind", "Fred Riuáind...")

        dev_tts_list = []
        for s in dev_sentences:
            s_spoken = apply_english_phonetics(s)
            dev_tts_list.append(s_spoken)

        ci_spoken = apply_english_phonetics(cierre)
        ci_tts = ci_spoken.replace("Fred Riuáind,", "Fred Riuáind...").replace("Fred Riuáind", "Fred Riuáind...")

    # Rutas de chunks individuales
    ap_mp3 = f"{tmp_prefix}_ap.mp3"
    temp_files.append(ap_mp3)

    dev_mp3_paths = []
    for idx in range(len(dev_sentences)):
        p = f"{tmp_prefix}_dev_{idx}.mp3"
        dev_mp3_paths.append(p)
        temp_files.append(p)

    ci_mp3 = f"{tmp_prefix}_ci.mp3"
    temp_files.append(ci_mp3)

    if job_id:
        with ACTIVE_JOBS_LOCK:
            if job_id in ACTIVE_JOBS:
                ACTIVE_JOBS[job_id]['temp_files'].update(temp_files)

    # 2. Síntesis concurrente
    tts_tasks = []
    if use_fish:
        sem = asyncio.Semaphore(1)
        tts_tasks.append(synthesize_fish_audio_tts(sem, ap_tts, ap_mp3, reference_id=selected_fish_voice))
        for idx, s_text in enumerate(dev_tts_list):
            tts_tasks.append(synthesize_fish_audio_tts(sem, s_text, dev_mp3_paths[idx], reference_id=selected_fish_voice))
        tts_tasks.append(synthesize_fish_audio_tts(sem, ci_tts, ci_mp3, reference_id=selected_fish_voice))
    else:
        if edge_tts is None:
            raise RuntimeError("edge_tts no está instalado y FISH_API_KEY no está disponible.")
        tts_tasks.append(edge_tts.Communicate(ap_tts, voice, rate="+0%", pitch="+0Hz").save(ap_mp3))
        for idx, s_text in enumerate(dev_tts_list):
            tts_tasks.append(edge_tts.Communicate(s_text, voice, rate="+0%", pitch="+0Hz").save(dev_mp3_paths[idx]))
        tts_tasks.append(edge_tts.Communicate(ci_tts, voice, rate="+2%", pitch="+0Hz").save(ci_mp3))

    await asyncio.gather(*tts_tasks)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    # 3. Medición milimétrica de duraciones de cada segmento
    dur_ap = get_audio_duration(ap_mp3)
    dur_dev_list = [get_audio_duration(p) for p in dev_mp3_paths]
    dur_ci = get_audio_duration(ci_mp3)

    # 4. Generación de silencios orgánicos de cabina
    sil_ap_mp3 = f"{tmp_prefix}_sil_ap.mp3"
    sil_sent_mp3 = f"{tmp_prefix}_sil_sent.mp3"
    sil_ci_mp3 = f"{tmp_prefix}_sil_ci.mp3"
    temp_files.extend([sil_ap_mp3, sil_sent_mp3, sil_ci_mp3])

    make_silence_mp3(0.55, sil_ap_mp3)    # Pausa tras identificador de emisora y locutor
    make_silence_mp3(0.45, sil_sent_mp3)  # Respiración natural tras cada punto final
    make_silence_mp3(0.65, sil_ci_mp3)    # Pausa dramática previa al sube el volumen

    # 5. Ensamblaje secuencial de la pista vocal sin solapamientos
    concat_list = [ap_mp3, sil_ap_mp3]
    for idx, dev_p in enumerate(dev_mp3_paths):
        concat_list.append(dev_p)
        if idx < len(dev_mp3_paths) - 1:
            concat_list.append(sil_sent_mp3)
    concat_list.append(sil_ci_mp3)
    concat_list.append(ci_mp3)

    concat_txt = f"{tmp_prefix}_concat.txt"
    temp_files.append(concat_txt)
    with open(concat_txt, 'w') as f:
        for c in concat_list:
            f.write(f"file '{c}'\n")

    raw_concat_mp3 = f"{tmp_prefix}_raw.mp3"
    temp_files.append(raw_concat_mp3)
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy",
        raw_concat_mp3
    ], capture_output=True, check=True)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    # 6. Masterización analógica con mezcla de música de fondo tenue instrumental sin derechos de autor
    if not out_mp3_path:
        out_mp3_path = f"/tmp/dj_fredd_{pid}.mp3"
    os.makedirs(os.path.dirname(os.path.abspath(out_mp3_path)), exist_ok=True)

    total_voice_dur = get_audio_duration(raw_concat_mp3)
    ci_start = round(dur_ap + 0.55 + sum(dur_dev_list) + max(0, len(dur_dev_list) - 1) * 0.45 + 0.65, 2)

    has_bed = os.path.exists(DEFAULT_MUSIC_BED) and os.path.getsize(DEFAULT_MUSIC_BED) > 10000

    if has_bed:
        # Colchón musical tenue instrumental:
        # - atrim: recortado a la duración de la voz
        # - afade in: entrada suave en 1.8 segundos
        # - afade out: bajada suave de 2.2 segundos exactamente al iniciar el cierre institucional
        # - highpass 120Hz & lowpass 6500Hz: despeja frecuencias de graves y presencia para la voz
        # - volume 0.075 (-22.5dB): nivel tenue perfecto de colchón de radio
        # - Ecualización cálida analógica para la voz
        # - Compresión broadcast y limitador True Peak a -1.0dB
        filter_complex = (
            f"[1:a]atrim=0:{total_voice_dur},aresample=44100,"
            f"afade=t=in:st=0:d=1.8,afade=t=out:st={ci_start}:d=2.2,"
            f"highpass=f=120,lowpass=f=6500,volume=0.075[bed];"
            f"[0:a]aresample=44100,"
            f"highpass=f=65,"
            f"equalizer=f=120:width_type=o:width=1.0:g=1.8,"
            f"equalizer=f=450:width_type=o:width=1.2:g=-1.2,"
            f"equalizer=f=2800:width_type=o:width=1.0:g=1.4,"
            f"equalizer=f=10000:width_type=o:width=1.5:g=1.2[vox];"
            f"[vox][bed]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
            f"[mixed]acompressor=threshold=-18dB:ratio=2.6:attack=15:release=120:makeup=1.8,"
            f"alimiter=limit=-1.0dB:attack=5:release=50[aout]"
        )
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", raw_concat_mp3,
            "-i", DEFAULT_MUSIC_BED,
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            out_mp3_path
        ]
    else:
        master_filter = (
            "aresample=44100,"
            "highpass=f=65,"
            "equalizer=f=120:width_type=o:width=1.0:g=1.8,"
            "equalizer=f=450:width_type=o:width=1.2:g=-1.2,"
            "equalizer=f=2800:width_type=o:width=1.0:g=1.4,"
            "equalizer=f=10000:width_type=o:width=1.5:g=1.2,"
            "acompressor=threshold=-18dB:ratio=2.6:attack=15:release=120:makeup=1.8,"
            "alimiter=limit=-1.0dB:attack=5:release=50"
        )
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", raw_concat_mp3,
            "-af", master_filter,
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            out_mp3_path
        ]

    subprocess.run(cmd, capture_output=True, check=True)

    if is_cancelled():
        cleanup_on_cancel()
        return None, 0, 0, [], 0, ""

    duration = get_audio_duration(out_mp3_path)
    elapsed = time.time() - t_start

    # 7. Construcción milimétrica de marcas de tiempo (intro_timings)
    intro_timings = []
    # Apertura
    intro_timings.append({
        'start': 0.0,
        'end': round(dur_ap, 2),
        'text': apertura
    })

    curr_t = dur_ap + 0.55
    for idx, sent in enumerate(dev_sentences):
        st = round(curr_t, 2)
        en = round(curr_t + dur_dev_list[idx], 2)
        intro_timings.append({
            'start': st,
            'end': en,
            'text': sent
        })
        curr_t = en + 0.45

    ci_start = round(curr_t - 0.45 + 0.65, 2)
    intro_timings.append({
        'start': ci_start,
        'end': round(ci_start + dur_ci, 2),
        'text': cierre
    })
    intro_end = ci_start

    story_alone_dur = round(ci_start - 0.65 - (dur_ap + 0.55), 2)
    print(f"✓ [DJ FREDD SERVICE] Locución maestra generada en {elapsed:.2f}s | Duración total: {duration:.2f}s | Anécdota sola: {story_alone_dur:.2f}s", flush=True)

    # 8. Limpieza rigurosa de archivos temporales
    for tmp_f in temp_files:
        try:
            if os.path.exists(tmp_f):
                os.remove(tmp_f)
        except Exception:
            pass

    return out_mp3_path, duration, elapsed, intro_timings, intro_end, full_script

def run_server(port=5055):
    """
    Servidor HTTP en puerto 5055 para la app web de Fred Rewind.
    Atiende solicitudes de generación de locuciones, cancelación inmediata y sincronización de letras.
    """
    class DjFreddAudioHandler(BaseHTTPRequestHandler):
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
                    'service': 'Fred Rewind • Servicio Oficial de Audio con DJ Fredd',
                    'voice': 'DJ Fredd',
                    'voiceModel': 'es-US-AlonsoNeural (Español Latino Natural)',
                    'musicBed': 'Slow Burn - Kevin MacLeod (CC-BY 4.0 Royalty-Free Commercial Instrumental Bed)',
                    'engine': 'Edge-TTS + Master Radio FM Analog Chain + Colchón Instrumental',
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
                        res = generate_ai_story_script(song_title, band_name, album_name, year)
                        text = res['full_script']

                    safe_slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
                    workspace_mp3 = os.path.join(WORKSPACE_AUDIO_DIR, f"fredd_intro_{safe_slug}_{track_id}.mp3")

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
                        'voice': 'DJ Fredd (es-US-AlonsoNeural • Español Latino Natural + Colchón Instrumental)',
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
                    print(f"🛑 [DJ FREDD SERVICE] Cancelación procesada para job: {target_job_id} / track: {target_track_id}. Total: {cancelled_count}", flush=True)
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

                    story_res = generate_ai_story_script(song_title, band_name, album_name, year, angle)
                    self.send_response(200)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(story_res).encode('utf-8'))
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
                        print(f"  🔍 [DJ FREDD SERVICE] Obteniendo pista completa para '{song_title}' de {band_name}...", flush=True)
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

    server = ThreadingHTTPServer(('0.0.0.0', port), DjFreddAudioHandler)
    print(f"🚀 [DJ FREDD SERVICE] Servidor de locuciones maestras en http://0.0.0.0:{port}/api/generate_audio", flush=True)
    print(f"   Voz: DJ Fredd (es-US-AlonsoNeural • Español Latino Natural + Colchón Instrumental) | Sincronización activa", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor de audio.")

def main():
    parser = argparse.ArgumentParser(description="Generador Oficial de Locuciones de DJ Fredd con Sincronización de Letras")
    parser.add_argument("--song", help="Nombre de la canción")
    parser.add_argument("--band", help="Nombre de la banda o artista")
    parser.add_argument("--album", default="", help="Nombre del álbum")
    parser.add_argument("--year", default="", help="Año de lanzamiento")
    parser.add_argument("--text", help="Texto o guion personalizado para la locución")
    parser.add_argument("--angle", type=int, default=1, help="Ángulo narrativo (1, 2 o 3)")
    parser.add_argument("--out", default=None, help="Ruta de salida del MP3")
    parser.add_argument("--engine", choices=["fish", "edge"], default=None, help="Motor TTS: fish (Fish Audio) o edge (Edge-TTS)")
    parser.add_argument("--fish-voice", default=None, help="ID de voz en Fish Audio")
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

    out_file = args.out or f"/tmp/fredd_{band_name}_{song_name}.mp3".replace(" ", "_").lower()

    print(f"=======================================================")
    print(f"🎙️ FRED REWIND • DJ FREDD — LOCUCIÓN MAESTRA ESTANDARIZADA")
    print(f"=======================================================")

    out_path, duration, elapsed, intro_timings, intro_end, full_script = asyncio.run(
        build_eddie_radio_narration(
            script_text,
            song_name,
            band_name,
            out_file,
            engine=args.engine,
            fish_voice=args.fish_voice
        )
    )
    print(f"\n✓ Archivo generado: {out_path} ({duration:.2f}s en {elapsed:.2f}s, intro_end: {intro_end}s)")
    print("\nMarcas de tiempo de la letra del Intro:")
    for it in intro_timings:
        print(f"  [{it['start']}s - {it['end']}s] {it['text']}")

if __name__ == "__main__":
    main()
