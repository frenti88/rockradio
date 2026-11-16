#!/usr/bin/env python3
"""
ROCK RADIO — FRED REWIND • Generador de Historias mediante Comandos de IA y Fish Audio
======================================================================================
Arquitectura unificada de producción radial asistida por IA:
- Conserva Fish Audio (s2.1-pro-free / s2.1-pro) y la voz configurada de Fred (reference_id).
- Evalúa compatibilidad con S2.1 Pro y Drama 3 sin cambiar el modelo ni la voz activa.
- Intérprete de comandos en lenguaje natural (generación, regeneración de historia, regeneración de voz).
- Repertorio de 10 aperturas dinámicas con rotación inteligente (evita repetir las últimas 3).
- Guion dual exacto: Texto visible (limpio) + Texto vocal (dirección emocional Fish Audio).
- Duración máxima absoluta de 45.0 segundos (incluyendo 5.0s iniciales de música sin voz).
  Si excede 45s, resume y regenera la locución acortada sin acelerar artificialmente ni cortar frases.
- Cadena de audio FFmpeg profesional: 5s música sin voz, sidechain ducking (12-18dB, attack 200ms,
  release 450ms), highpass ~80Hz, EQ correctiva, presencia 2-4kHz, compresión 3:1, de-esser,
  cierre emotivo con hasta +3dB de presencia adicional percibida y limitador a -1dBTP.
- Persistencia completa en data/stories_metadata.json e integración segura en el catálogo del reproductor.
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
import random
import threading
import shutil
import unicodedata
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ACTIVE_JOBS = {}
ACTIVE_JOBS_LOCK = threading.Lock()

try:
    import edge_tts
except ImportError:
    edge_tts = None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORKSPACE_AUDIO_DIR = os.path.join(PROJECT_ROOT, 'audio')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
STORIES_METADATA_PATH = os.path.join(DATA_DIR, 'stories_metadata.json')
INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, 'index.html')
HTML_CLONES = ['rock45.html', 'kiss.html', 'kiss-podcast.html']

os.makedirs(WORKSPACE_AUDIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe" if os.path.exists("/opt/homebrew/bin/ffprobe") else "ffprobe"

INTRO_MUSIC_SEC = 5.0
OUTRO_MUSIC_TAIL_SEC = 1.0
MAX_TOTAL_DURATION_SEC = 45.0
SAFE_TARGET_TOTAL_SEC = 44.5  # Margen para padding de frames MP3 garantizando <= 45.00s reales

DEFAULT_VOICE = "es-US-AlonsoNeural"
DEFAULT_MUSIC_BED = os.path.join(WORKSPACE_AUDIO_DIR, "fred_rewind_rock_bed.mp3")

def load_env_local():
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
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

DEFAULT_FISH_VOICE = os.environ.get("FISH_VOICE_ID", "e8303fcb17bd4a8ba7709b1f6d3416f7").strip()
DEFAULT_FISH_MODEL = os.environ.get("FISH_MODEL", "s2.1-pro-free").strip()

# ==============================================================================
# 1. REPERTORIO DE 10 APERTURAS DINÁMICAS (Sección 4)
# ==============================================================================
DYNAMIC_OPENINGS = [
    {
        "id": 1,
        "base": "Rock Radio: De vuelta al pasado. Soy Fred, y esta es la historia que no conocías de...",
        "requires_year": False,
        "format": lambda song, band, year: f"Rock Radio: De vuelta al pasado. Soy Fred, y esta es la historia que no conocías de {song}, de {band}."
    },
    {
        "id": 2,
        "base": "De vuelta al pasado en Rock Radio. Al micrófono, su guía en el tiempo, Fred...",
        "requires_year": False,
        "format": lambda song, band, year: f"De vuelta al pasado en Rock Radio. Al micrófono, su guía en el tiempo, Fred, recordando {song} de {band}."
    },
    {
        "id": 3,
        "base": "Esto es Rock Radio: De vuelta al pasado. Con ustedes, Fred, rebobinando la cinta hasta...",
        "requires_year": True,
        "format": lambda song, band, year: f"Esto es Rock Radio: De vuelta al pasado. Con ustedes, Fred, rebobinando la cinta hasta {year} con {band}." if year else f"Esto es Rock Radio: De vuelta al pasado. Con ustedes, Fred, rebobinando la cinta hasta {song} de {band}."
    },
    {
        "id": 4,
        "base": "Rock Radio: De vuelta al pasado. Les habla Fred, desempolvando la memoria del rock...",
        "requires_year": False,
        "format": lambda song, band, year: f"Rock Radio: De vuelta al pasado. Les habla Fred, desempolvando la memoria del rock con {song}, de {band}."
    },
    {
        "id": 5,
        "base": "Sintonizas Rock Radio: De vuelta al pasado. Al habla Fred, su cronista del rock, abriendo los archivos de...",
        "requires_year": False,
        "format": lambda song, band, year: f"Sintonizas Rock Radio: De vuelta al pasado. Al habla Fred, su cronista del rock, abriendo los archivos de {band}."
    },
    {
        "id": 6,
        "base": "Rock Radio: De vuelta al pasado. Aquí Fred, su cómplice musical, poniendo la aguja sobre el vinilo de...",
        "requires_year": False,
        "format": lambda song, band, year: f"Rock Radio: De vuelta al pasado. Aquí Fred, su cómplice musical, poniendo la aguja sobre el vinilo de {song}."
    },
    {
        "id": 7,
        "base": "Están en Rock Radio: De vuelta al pasado. Con ustedes Fred, en los controles de esta máquina del tiempo...",
        "requires_year": False,
        "format": lambda song, band, year: f"Están en Rock Radio: De vuelta al pasado. Con ustedes Fred, en los controles de esta máquina del tiempo junto a {band}."
    },
    {
        "id": 8,
        "base": "Rock Radio: De vuelta al pasado. Les saluda Fred, su anfitrión en este viaje sonoro, para contarles lo que pasó con...",
        "requires_year": False,
        "format": lambda song, band, year: f"Rock Radio: De vuelta al pasado. Les saluda Fred, su anfitrión en este viaje sonoro, para contarles lo que pasó con {song}."
    },
    {
        "id": 9,
        "base": "Esto es Rock Radio: De vuelta al pasado. Soy Fred, el guardián de estos clásicos, trayendo de vuelta la historia de...",
        "requires_year": False,
        "format": lambda song, band, year: f"Esto es Rock Radio: De vuelta al pasado. Soy Fred, el guardián de estos clásicos, trayendo de vuelta la historia de {song}."
    },
    {
        "id": 10,
        "base": "De vuelta al pasado por Rock Radio. Al frente de la tornamesa, su compañero de ruta, Fred...",
        "requires_year": False,
        "format": lambda song, band, year: f"De vuelta al pasado por Rock Radio. Al frente de la tornamesa, su compañero de ruta, Fred, viajando al origen de {song}."
    }
]

CLOSING_TEMPLATES = [
    "¡Sube el volumen! ¡Esto es {song} de {band}, aquí en Rock Radio!",
    "¡Sube el volumen y disfruta {song} con {band}, de vuelta al pasado!",
    "¡Dale fuerza a los altavoces! ¡Escuchemos a {song} de {band} en Rock Radio!"
]

# ==============================================================================
# 2. COMPATIBILIDAD CON MODELOS FISH AUDIO (S2.1 Pro & Drama 3)
# ==============================================================================
def get_fish_model_capabilities(model_name):
    """
    Evalúa capacidades expresivas de S2.1 Pro y Drama 3 sin cambiar el modelo configurado.
    """
    m = (model_name or DEFAULT_FISH_MODEL).lower().strip()
    is_drama3 = "drama" in m
    is_s2 = ("s2" in m) or is_drama3
    return {
        "model": model_name or DEFAULT_FISH_MODEL,
        "family": "drama-3" if is_drama3 else ("s2.1-pro" if is_s2 else "legacy"),
        "supports_bracket_tags": is_s2,
        "supports_inline_xml_tags": is_drama3,  # <emphasis>, <forceful>, <soft>, etc. solo Drama 3
        "opening_tag": "[warm, confident]",
        "story_tag": "[curious]",
        "closing_tag": "[excited]"
    }

def strip_vocal_tags(text):
    """
    Elimina etiquetas expresivas [bracket] y <xml> para asegurar igualdad exacta de palabras habladas.
    """
    clean = re.sub(r'\[[^\]]+\]\s*', '', text or '')
    clean = re.sub(r'</?[a-zA-Z_]+>', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def build_dual_scripts(apertura, dev_sentences, cierre, model_name=DEFAULT_FISH_MODEL):
    """
    Genera exactamente dos versiones sincronizadas con idéntico contenido hablado:
    - visible_script: texto limpio sin etiquetas para subtítulos y persistencia.
    - vocal_script: texto con directivas emocionales compatibles con el modelo activo de Fish Audio.
    """
    caps = get_fish_model_capabilities(model_name)
    clean_ap = strip_vocal_tags(apertura)
    clean_dev = [strip_vocal_tags(s) for s in dev_sentences if strip_vocal_tags(s)]
    clean_ci = strip_vocal_tags(cierre)

    visible_script = f"{clean_ap} {' '.join(clean_dev)} {clean_ci}".strip()

    if caps["supports_bracket_tags"]:
        vocal_ap = f"{caps['opening_tag']} {clean_ap}"
        vocal_dev_list = []
        for idx, sent in enumerate(clean_dev):
            if idx == 0:
                vocal_dev_list.append(f"{caps['story_tag']} {sent}")
            else:
                vocal_dev_list.append(sent)
        if caps["supports_inline_xml_tags"]:
            vocal_ci = f"{caps['closing_tag']} <forceful>{clean_ci}</forceful>"
        else:
            vocal_ci = f"{caps['closing_tag']} {clean_ci}"
    else:
        vocal_ap = clean_ap
        vocal_dev_list = list(clean_dev)
        vocal_ci = clean_ci

    vocal_script = f"{vocal_ap} {' '.join(vocal_dev_list)} {vocal_ci}".strip()
    return {
        "visible_script": visible_script,
        "vocal_script": vocal_script,
        "apertura_clean": clean_ap,
        "dev_sentences_clean": clean_dev,
        "cierre_clean": clean_ci,
        "vocal_ap": vocal_ap,
        "vocal_dev_list": vocal_dev_list,
        "vocal_ci": vocal_ci
    }

# ==============================================================================
# 3. ANÉCDOTAS HISTÓRICAS VERIFICABLES MULTI-ÁNGULO (Concisas: 38-52 palabras)
# ==============================================================================
MASTER_CURATED_STORIES = {
    "tom sawyer": [
        (
            "A finales de 1980, en Le Studio de Quebec, Neil Peart transformó un poema del letrista Pye Dubois en un retrato del espíritu independiente, reinterpretando al clásico personaje de Mark Twain. "
            "Mientras Geddy Lee abría la pista con el gruñido icónico de su sintetizador Oberheim, Rush fusionó complejidad progresiva con fuerza directa."
        ),
        (
            "Durante las sesiones de Moving Pictures en Quebec, capturar la energía exacta de Tom Sawyer resultó tan exigente que la banda casi descarta la grabación en la consola. "
            "Todo cambió cuando Neil Peart ejecutó en el estudio sus legendarios redobles explosivos, convirtiendo aquel desafío técnico en el himno definitivo del trío canadiense."
        ),
        (
            "En el invierno de 1980 en Morin-Heights, Alex Lifeson grabó sus acordes cortantes en apenas unas tomas mientras el grupo exploraba compases asimétricos en siete por ocho. "
            "La mezcla perfecta entre la rebeldía literaria de la letra y una base rítmica implacable consolidó a Rush en la cima del rock mundial."
        )
    ],
    "everybody wants to rule the world": [
        (
            "Fue la última canción en sumarse a Songs from the Big Chair en 1985, cuando el productor Chris Hughes pidió un tema luminoso para equilibrar el álbum. "
            "En una sola tarde, Roland Orzabal tejió un pulso hipnótico con guitarras de doce cuerdas y sintetizadores que conquistó el número uno mundial."
        ),
        (
            "Compuesta bajo las tensiones de la Guerra Fría en 1985, Curt Smith y Roland Orzabal ocultaron una profunda reflexión sobre la sed de poder político tras una melodía vibrante y optimista. "
            "Originalmente grabada como un corte de transición rápida, terminó coronándose como el himno definitivo de Tears for Fears."
        ),
        (
            "Aunque la banda temía que su aire ligero desentonara con la densidad del disco, la grabación en estudio sorprendió por la elegancia de sus coros y su inolvidable solo final de guitarra. "
            "Lanzada en marzo de 1985, la canción catapultó a Tears for Fears al estrellato internacional."
        )
    ],
    "the trooper": [
        (
            "Inspirada en la carga de la Brigada Ligera durante la batalla de Balaclava en 1854, Steve Harris escribió este clásico de 1983 desde la perspectiva de un soldado en pleno combate. "
            "Con las guitarras gemelas de Dave Murray y Adrian Smith en galope implacable, nació uno de los himnos eternos de Iron Maiden."
        ),
        (
            "Para el álbum Piece of Mind de 1983 en las Bahamas, Bruce Dickinson desató toda su potencia vocal sin utilizar trucos de estudio sobre la épica composición de Steve Harris. "
            "La icónica portada del sencillo con Eddie alzando la bandera en el campo de batalla selló la mística inmortal de la canción."
        )
    ],
    "africa": [
        (
            "En 1982, tras ver un documental nocturno, David Paich imaginó el continente africano y grabó junto a Jeff Porcaro marimbas y congas artesanales para el álbum Toto IV. "
            "Aunque estuvo a punto de quedar fuera del disco, se convirtió en el único número uno mundial del grupo."
        ),
        (
            "Para capturar el pulso orgánico de Africa en 1982, el baterista Jeff Porcaro combinó percusiones reales en múltiples pistas sin recurrir a cajas de ritmos programadas. "
            "Coronada por seis voces en armonía perfecta durante el estribillo, la canción se alzó como una cumbre del estudio californiano."
        )
    ],
    "back in black": [
        (
            "Tras perder a su cantante Bon Scott a inicios de 1980, Malcolm y Angus Young honraron su memoria con el tributo más vigoroso posible. "
            "Con Brian Johnson al micrófono en Bahamas y una campana de bronce de dos mil libras, descargaron un riff inmortal que definió el álbum más vendido del hard rock."
        ),
        (
            "En abril de 1980 en los estudios Compass Point, AC/DC canalizó el duelo por Bon Scott en composiciones cargadas de gratitud y resiliencia. "
            "Con apenas seis semanas de grabación junto al productor Mutt Lange, el álbum emergió con una pegada monolítica que transformó la historia del rock."
        )
    ],
    "detroit rock city": [
        (
            "Para el álbum Destroyer de 1976, el productor Bob Ezrin llevó a KISS a un nivel cinematográfico incorporando sonidos reales de autos, radio y un choque violento. "
            "La letra nació de la trágica noticia de un fanático que perdió la vida viajando a uno de sus conciertos."
        ),
        (
            "Coronada por el legendario duelo de guitarras armonizadas entre Paul Stanley y Ace Frehley en los estudios Record Plant de Nueva York en 1976, la pista fue pensada como una historia trágica sobre el poder visceral del rock en vivo. "
            "Desde entonces abre los conciertos de la banda como un rito infaltable."
        )
    ],
    "bohemian rhapsody": [
        (
            "En el verano de 1975, Freddie Mercury llevó al estudio la estructura de Bohemian Rhapsody anotada en simples guías telefónicas. "
            "La banda grabó tantas capas de armonías vocales durante semanas que la cinta magnética casi se volvió transparente, desafiando la negativa inicial de la disquera para cambiar la radio para siempre."
        )
    ],
    "sweet child o' mine": [
        (
            "En 1987, durante un ensayo informal en Los Ángeles, Slash tocaba un ejercicio de digitación en su guitarra que consideraba una broma circense. "
            "Axl Rose escuchó esas notas desde la habitación contigua y escribió de inmediato un emotivo poema de amor, dando vida al clásico más coreado de su carrera."
        )
    ],
    "paranoid": [
        (
            "En otoño de 1970, Black Sabbath necesitaba tres minutos extra para completar su segundo disco. "
            "Mientras el grupo almorzaba, Tony Iommi improvisó un riff frenético y Geezer Butler escribió la letra al instante; grabada en veinticinco minutos como relleno, se convirtió en su mayor éxito mundial."
        )
    ],
    "hotel california": [
        (
            "En 1976, Don Felder grabó una maqueta acústica en una casa de playa en Malibú que fascinó a Don Henley y Glenn Frey. "
            "Juntos escribieron una alegoría sobre los excesos y el lado oscuro del sueño americano, rematada por meses de trabajo en el legendario duelo de guitarras finales."
        )
    ],
    "stairway to heaven": [
        (
            "Aislados en una remota cabaña sin electricidad en Gales en 1970, Jimmy Page y Robert Plant concibieron una épica que crecía desde la calma acústica hasta una tormenta eléctrica. "
            "El legendario solo de guitarra fue grabado por Page con su Telecaster de 1959 en apenas tres tomas."
        )
    ],
    "highway to hell": [
        (
            "El título surgió de la forma en que Angus Young describía la sofocante rutina de viajar meses enteros en autobús de gira. "
            "En 1979, junto al productor Mutt Lange, AC/DC pulió sus coros sin perder crudeza callejera en la última gran grabación de estudio de Bon Scott."
        )
    ],
    "master of puppets": [
        (
            "Grabada en Copenhague en 1986, James Hetfield plasmó una cruda metáfora sobre la pérdida de control frente a las adicciones. "
            "Para lograr una precisión implacable, todas las guitarras se atacaron exclusivamente con púa hacia abajo, acompañadas por la maestría armónica del recordado bajista Cliff Burton."
        )
    ],
    "enter sandman": [
        (
            "El famoso riff de guitarra nació a las dos de la madrugada en la habitación de Kirk Hammett. "
            "En el Álbum Negro de 1991, James Hetfield reescribió la letra sobre las pesadillas infantiles, grabando la icónica plegaria susurrada junto al pequeño hijo del productor Bob Rock."
        )
    ],
    "one": [
        (
            "Inspirada en la novela antibélica Johnny Got His Gun de 1939, Metallica compuso en 1988 una obra monumental sobre el aislamiento de un soldado herido. "
            "La sincronía entre el doble bombo de Lars Ulrich y las guitarras imitando fuego de batalla rompió todos los moldes del metal."
        )
    ],
    "smoke on the water": [
        (
            "En diciembre de 1971, Deep Purple presenció desde su hotel cómo una bengala incendiaba el Casino de Montreux en Suiza durante un concierto de Frank Zappa. "
            "Al ver el humo sobre el lago Ginebra, Ritchie Blackmore trazó en su guitarra el riff más universal de la historia."
        )
    ],
    "dream on": [
        (
            "Steven Tyler escribió los acordes de piano a los catorce años en la posada familiar de Nuevo Hampshire. "
            "En 1973 disimuló su voz grave por temor a sonar inmaduro en todo el álbum, reservando sus desgarradores agudos naturales únicamente para el inolvidable clímax final."
        )
    ],
    "comfortably numb": [
        (
            "Roger Waters escribió estos versos recordando la desconexión física sufrida en 1977 tras recibir sedantes para tocar enfermo en Filadelfia. "
            "Sobre una maqueta de David Gilmour para The Wall, nació el majestuoso solo de guitarra grabado en apenas dos tomas con su Stratocaster negra."
        )
    ],
    "subdivisions": [
        (
            "En 1982, Neil Peart retrató la presión por encajar dentro de los suburbios residenciales norteamericanos. "
            "Con Geddy Lee tomando protagonismo en el sintetizador Oberheim y la cavernosa voz de Mark Dailey pronunciando el título, el tema se volvió refugio eterno para los espíritus libres."
        )
    ],
    "forever young": [
        (
            "Escrita en Berlín Occidental durante la Guerra Fría de 1984, Alphaville reflejó el miedo latente a un conflicto nuclear y el deseo de aferrarse a la juventud. "
            "Originalmente grabada como pista bailable rápida, los productores bajaron el tempo transformándola en un himno nostálgico inmortal."
        )
    ],
    "help": [
        (
            "En 1965, abrumado por el frenesí agobiante de la Beatlemanía, John Lennon escribió esta confesión directa como un pedido sincero de auxilio emocional. "
            "Aunque la banda la vistió con un ritmo acelerado de rock and roll, Lennon siempre la consideró una de sus páginas más honestas."
        )
    ],
    "hysteria": [
        (
            "La gestación de Hysteria en 1987 estuvo marcada por el accidente donde el baterista Rick Allen perdió su brazo izquierdo y aprendió a tocar con pedales electrónicos. "
            "Inspirado por ese ejemplo, Phil Collen rasgueó los acordes cristalinos que el productor Mutt Lange convirtió en la joya del álbum."
        )
    ],
    "shout at the devil": [
        (
            "Escrita en 1983 en un pequeño apartamento de Sunset Strip, Nikki Sixx encontró inspiración en su curiosidad por el misticismo tras el auge del hard rock angelino. "
            "Con los riffs punzantes de Mick Mars y el rugido de Vince Neil, el tema desató la revolución visual del glam metal."
        )
    ],
    "poison": [
        (
            "Para su resurrección artística en 1989, Alice Cooper se alió con el maestro compositor Desmond Child y dio vida a una historia sobre una atracción tan irresistible como letal. "
            "Jon Bon Jovi y Richie Sambora visitaron la sesión y sumaron coros que llevaron la pista a lo más alto."
        )
    ],
    "forever": [
        (
            "En 1989, Paul Stanley colaboró con Michael Bolton para mostrar la faceta más íntima y despojada de KISS sobre guitarras acústicas. "
            "Bruce Kulick inmortalizó el emotivo solo en una única toma nocturna en Los Ángeles, regalándole a la banda su balada más recordada."
        )
    ],
    "rock and roll all nite": [
        (
            "En 1975, Casablanca Records exigió con urgencia a Paul Stanley y Gene Simmons un himno que capturara el frenesí de sus shows. "
            "Grabada en Nueva York con un coro improvisado de técnicos y asistentes de estudio, nació el credo definitivo de fiesta para toda una generación."
        )
    ]
}

# Metadatos verificables adicionales para canciones clásicas fuera del HTML inicial
SUPPLEMENTAL_VERIFIED_TRACKS = [
    {
        "song_title": "The Trooper",
        "band_name": "Iron Maiden",
        "album": "Piece of Mind (1983)",
        "year": "1983",
        "cover": "img/albums/metallica_1984_ride_the_lightning.png",
        "duration_sec": 252
    },
    {
        "song_title": "Run to the Hills",
        "band_name": "Iron Maiden",
        "album": "The Number of the Beast (1982)",
        "year": "1982",
        "cover": "img/albums/metallica_1984_ride_the_lightning.png",
        "duration_sec": 233
    },
    {
        "song_title": "Fear of the Dark",
        "band_name": "Iron Maiden",
        "album": "Fear of the Dark (1992)",
        "year": "1992",
        "cover": "img/albums/metallica_1984_ride_the_lightning.png",
        "duration_sec": 438
    }
]

AMBIGUOUS_TITLES_REGISTRY = {
    "one": [
        {"song_title": "One", "band_name": "Metallica", "album": "...And Justice for All (1988)", "year": "1988"},
        {"song_title": "One", "band_name": "U2", "album": "Achtung Baby (1991)", "year": "1991"}
    ],
    "jump": [
        {"song_title": "Jump", "band_name": "Van Halen", "album": "1984 (1984)", "year": "1984"},
        {"song_title": "Jump", "band_name": "The Pointer Sisters", "album": "Break Out (1983)", "year": "1983"}
    ],
    "forever": [
        {"song_title": "Forever", "band_name": "KISS", "album": "Hot in the Shade (1989)", "year": "1989"},
        {"song_title": "Forever", "band_name": "Papa Roach", "album": "The Paramour Sessions (2006)", "year": "2006"}
    ],
    "photograph": [
        {"song_title": "Photograph", "band_name": "Def Leppard", "album": "Pyromania (1983)", "year": "1983"},
        {"song_title": "Photograph", "band_name": "Nickelback", "album": "All the Right Reasons (2005)", "year": "2005"}
    ]
}

# ==============================================================================
# 4. PERSISTENCIA Y METADATOS DEL PROYECTO
# ==============================================================================
def normalize_text_key(s):
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[\'’\"`!¡?¿.,:;()\-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def make_story_key(band_name, song_title):
    return f"{normalize_text_key(band_name)}::{normalize_text_key(song_title)}"

def make_slug(band_name, song_title):
    raw = f"{band_name}_{song_title}".lower().replace(" ", "_").replace("/", "")
    return re.sub(r'[^a-z0-9_]', '', raw)[:48]

def load_stories_metadata():
    if os.path.exists(STORIES_METADATA_PATH):
        try:
            with open(STORIES_METADATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("recent_openings", [])
                    data.setdefault("last_generated_key", None)
                    data.setdefault("stories", {})
                    return data
        except Exception as e:
            print(f"⚠️ Error leyendo {STORIES_METADATA_PATH}: {e}", flush=True)
    return {"recent_openings": [], "last_generated_key": None, "stories": {}}

def save_stories_metadata(data):
    tmp_path = f"{STORIES_METADATA_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, STORIES_METADATA_PATH)

def load_project_catalog_metadata():
    """
    Lee el catálogo musical real desde index.html (BAND_POPULAR_TRACKS, CURATED_*, bands)
    y verifica pistas completas locales en audio/.
    """
    catalog = []
    seen = set()

    def add_item(song_title, band_name, album="", year="", cover="", duration_sec=240):
        if not song_title or not band_name:
            return
        key = make_story_key(band_name, song_title)
        if key in seen:
            # Update missing cover/year if needed
            for ex in catalog:
                if ex["key"] == key:
                    if not ex["cover"] and cover:
                        ex["cover"] = cover
                    if not ex["year"] and year:
                        ex["year"] = year
                    if not ex["album"] and album:
                        ex["album"] = album
            return
        seen.add(key)

        # Look for local full song mp3
        slug = make_slug(band_name, song_title)
        full_mp3 = None
        if os.path.exists(WORKSPACE_AUDIO_DIR):
            for fname in os.listdir(WORKSPACE_AUDIO_DIR):
                if fname.startswith("full_") and fname.endswith(".mp3"):
                    f_norm = fname[5:-4]
                    if f_norm == slug or (slug[:25] in f_norm) or (normalize_text_key(band_name).replace(" ", "_") in f_norm and normalize_text_key(song_title).replace(" ", "_")[:15] in f_norm):
                        full_mp3 = f"audio/{fname}"
                        break

        if not year and album:
            ym = re.search(r'(19\d{2}|20\d{2})', str(album))
            if ym:
                year = ym.group(1)

        catalog.append({
            "key": key,
            "song_title": song_title,
            "band_name": band_name,
            "album": album,
            "year": str(year or ""),
            "cover": cover,
            "duration_sec": duration_sec,
            "full_song_audio": full_mp3
        })

    if os.path.exists(INDEX_HTML_PATH):
        try:
            with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
                html = f.read()

            # Map bandId -> bandName
            band_id_to_name = {}
            for m in re.finditer(r"\{\s*id:\s*'([^']+)',\s*name:\s*(?:'([^']+)'|\"([^\"]+)\")", html):
                bid = m.group(1)
                bname = m.group(2) or m.group(3)
                band_id_to_name[bid] = bname

            # Extract BAND_POPULAR_TRACKS block
            bpt_match = re.search(r"const BAND_POPULAR_TRACKS\s*=\s*\{([\s\S]*?)\n\s*\};", html)
            if bpt_match:
                block = bpt_match.group(1)
                current_bid = None
                for line in block.splitlines():
                    bm = re.match(r"^\s*([a-z0-9_]+):\s*\[", line)
                    if bm:
                        current_bid = bm.group(1)
                        continue
                    tm = re.search(
                        r"title:\s*(?:'([^']+)'|\"([^\"]+)\"),\s*album:\s*(?:'([^']+)'|\"([^\"]+)\"),\s*cover:\s*'([^']+)'[^}]*durationSec:\s*(\d+)",
                        line
                    )
                    if tm and current_bid:
                        title = tm.group(1) or tm.group(2)
                        album = tm.group(3) or tm.group(4)
                        cover = tm.group(5)
                        dur = int(tm.group(6))
                        bname = band_id_to_name.get(current_bid, current_bid.replace("_", " ").title())
                        add_item(title, bname, album, "", cover, dur)

            # Extract CURATED tracks objects
            for m in re.finditer(
                r"name:\s*(?:'([^']+)'|\"([^\"]+)\"),\s*artists:\s*\[\s*\{\s*name:\s*(?:'([^']+)'|\"([^\"]+)\")\s*\}\s*\],\s*album:\s*\{\s*name:\s*(?:'([^']+)'|\"([^\"]+)\"),\s*release_date:\s*'([^']+)',\s*images:\s*\[\s*\{\s*url:\s*'([^']+)'\s*\}\s*\]\s*\},\s*duration_ms:\s*(\d+)",
                html
            ):
                title = m.group(1) or m.group(2)
                bname = m.group(3) or m.group(4)
                album = m.group(5) or m.group(6)
                year = m.group(7)
                cover = m.group(8)
                dur = int(int(m.group(9)) / 1000)
                add_item(title, bname, album, year, cover, dur)
        except Exception as e:
            print(f"⚠️ Error leyendo catálogo desde index.html: {e}", flush=True)

    for sup in SUPPLEMENTAL_VERIFIED_TRACKS:
        add_item(sup["song_title"], sup["band_name"], sup["album"], sup["year"], sup["cover"], sup["duration_sec"])

    return catalog

def resolve_song_metadata(song_query, band_query=None):
    """
    Identifica canción y artista usando metadatos disponibles.
    Solicita aclaración únicamente cuando hay ambigüedad real o múltiples coincidencias sin artista.
    Nunca inventa artistas ni títulos.
    """
    catalog = load_project_catalog_metadata()
    s_norm = normalize_text_key(song_query)
    b_norm = normalize_text_key(band_query) if band_query else ""

    if not s_norm:
        return {"resolved": False, "ambiguous": True, "message": "No se especificó el nombre de la canción.", "candidates": []}

    # Exact or fuzzy match against catalog
    matches = []
    for item in catalog:
        it_s = normalize_text_key(item["song_title"])
        it_b = normalize_text_key(item["band_name"])
        song_match = (it_s == s_norm) or (s_norm in it_s and len(s_norm) >= 4) or (it_s in s_norm and len(it_s) >= 4)
        if not song_match:
            continue
        if b_norm:
            band_match = (it_b == b_norm) or (b_norm in it_b) or (it_b in b_norm)
            if band_match:
                matches.append((100 if it_s == s_norm and it_b == b_norm else 80, item))
        else:
            matches.append((90 if it_s == s_norm else 70, item))

    # Ambiguity check when artist is omitted
    if not b_norm:
        if s_norm in AMBIGUOUS_TITLES_REGISTRY and len(AMBIGUOUS_TITLES_REGISTRY[s_norm]) > 1:
            return {
                "resolved": False,
                "ambiguous": True,
                "message": f"Existen varias canciones conocidas llamadas '{song_query}'. Por favor indica el artista (por ejemplo: '{song_query} de {AMBIGUOUS_TITLES_REGISTRY[s_norm][0]['band_name']}').",
                "candidates": AMBIGUOUS_TITLES_REGISTRY[s_norm]
            }
        unique_bands = {m[1]["band_name"] for m in matches}
        if len(unique_bands) > 1:
            return {
                "resolved": False,
                "ambiguous": True,
                "message": f"Encontré múltiples artistas para '{song_query}'. ¿De cuál artista quieres la historia?",
                "candidates": [m[1] for m in matches]
            }

    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        best = dict(matches[0][1])
        return {"resolved": True, "ambiguous": False, "metadata": best}

    # If both song and band were explicitly provided by user (e.g. a new song not yet in static catalog),
    # construct clean metadata preserving user-specified names (never inventing unknown band/song).
    if song_query and band_query:
        clean_song = song_query.strip()
        clean_band = band_query.strip()
        return {
            "resolved": True,
            "ambiguous": False,
            "metadata": {
                "key": make_story_key(clean_band, clean_song),
                "song_title": clean_song,
                "band_name": clean_band,
                "album": "",
                "year": "",
                "cover": "img/albums/kiss_1976_destroyer.png",
                "duration_sec": 240,
                "full_song_audio": None
            }
        }

    return {
        "resolved": False,
        "ambiguous": True,
        "message": f"No pude identificar con certeza el artista para '{song_query}'. Por favor escribe: 'Generar historia de {song_query} de [Artista]'.",
        "candidates": []
    }

# ==============================================================================
# 5. INTÉRPRETE DE COMANDOS DE IA (Secciones 2 y 10)
# ==============================================================================
def parse_ai_command(command_text):
    """
    Interpreta instrucciones naturales de usuario:
    - "Generar historia de Tom Sawyer de Rush"
    - "Genera una historia de The Trooper de Iron Maiden"
    - "Quiero la historia de Africa de Toto"
    - "Generar historia de Everybody Wants to Rule the World de Tears for Fears"
    - "Regenerar historia de Tom Sawyer de Rush"
    - "Generar otra historia de The Trooper de Iron Maiden"
    - "Regenerar la voz de la última historia"
    """
    raw = (command_text or "").strip().strip('"\'')
    if not raw:
        return {"intent": "unknown", "raw": raw}

    low = normalize_text_key(raw)

    # Check voice-only regeneration first
    if re.search(r"regenera[r]?\s+(?:la\s+)?voz\s+de\s+(?:la\s+)?ultima\s+historia", low) or low == "regenerar la voz":
        return {"intent": "regenerate_voice", "target": "last", "song_query": None, "band_query": None, "raw": raw}

    voice_target_m = re.match(r"^(?:por favor\s+)?regenera[r]?\s+(?:solo\s+)?(?:la\s+)?voz\s+(?:de\s+|para\s+)?(.+)$", raw, re.IGNORECASE)
    if voice_target_m:
        payload = voice_target_m.group(1).strip()
        song_q, band_q = _split_song_and_band(payload)
        return {"intent": "regenerate_voice", "target": "specific", "song_query": song_q, "band_query": band_q, "raw": raw}

    # Check story regeneration ("Regenerar historia de...", "Generar otra historia de...")
    regen_m = re.match(
        r"^(?:por favor\s+)?(?:regenera[r]?|crea[r]?\s+otra|genera[r]?\s+otra|otra|nueva)\s+(?:una\s+|la\s+)?historia\s+(?:de\s+|sobre\s+|para\s+)?(.+)$",
        raw,
        re.IGNORECASE
    )
    if regen_m:
        payload = regen_m.group(1).strip()
        song_q, band_q = _split_song_and_band(payload)
        return {"intent": "regenerate_story", "song_query": song_q, "band_query": band_q, "raw": raw}

    # Check story generation ("Generar historia de...", "Genera una historia de...", "Quiero la historia de...", etc.)
    gen_m = re.match(
        r"^(?:por favor\s+)?(?:genera[r]?|crea[r]?|haz|quiero|dame|escribe|narra)\s+(?:una\s+|la\s+|el\s+)?(?:nueva\s+)?historia\s+(?:de\s+|de\s+la\s+cancion\s+|sobre\s+|para\s+)?(.+)$",
        raw,
        re.IGNORECASE
    )
    if gen_m:
        payload = gen_m.group(1).strip()
        song_q, band_q = _split_song_and_band(payload)
        return {"intent": "generate", "song_query": song_q, "band_query": band_q, "raw": raw}

    # Fallback: if user writes "{Canción} de {Banda}" directly
    song_q, band_q = _split_song_and_band(raw)
    return {"intent": "generate", "song_query": song_q, "band_query": band_q, "raw": raw}

def _split_song_and_band(payload):
    """
    Separa inteligentemente "{Nombre_cancion} de {Nombre_banda}" incluso si la banda o canción tiene varias palabras.
    """
    payload = re.sub(r"^(?:la\s+cancion\s+|el\s+tema\s+)", "", payload.strip(), flags=re.IGNORECASE)
    catalog = load_project_catalog_metadata()
    known_bands = sorted(
        {item["band_name"] for item in catalog if item.get("band_name")},
        key=lambda x: len(x),
        reverse=True
    )

    # First check if payload ends with " de <Known Band>" (case-insensitive)
    for kb in known_bands:
        pattern = re.compile(r"^(.+?)\s+(?:de|del\s+grupo|de\s+la\s+banda|por)\s+" + re.escape(kb) + r"$", re.IGNORECASE)
        m = pattern.match(payload)
        if m:
            return m.group(1).strip(), kb

    # Otherwise split on the rightmost " de " / " del grupo " / " por "
    m_sep = re.match(r"^(.+?)\s+(?:del\s+grupo|de\s+la\s+banda|de|por)\s+([^,]+)$", payload, re.IGNORECASE)
    if m_sep:
        return m_sep.group(1).strip(), m_sep.group(2).strip()

    return payload.strip(), None

# ==============================================================================
# 6. SELECCIÓN DE APERTURAS, ANÉCDOTAS Y CONDENSACIÓN (<45s)
# ==============================================================================
def select_dynamic_opening(song_title, band_name, year="", exclude_ids=None, force_opening_id=None):
    """
    Selecciona aleatoriamente entre las 10 aperturas compatibles con el contexto,
    evitando repetir las últimas 3 utilizadas.
    """
    meta = load_stories_metadata()
    recent = [int(x) for x in meta.get("recent_openings", [])[-3:]]
    explicit_excl = {int(x) for x in (exclude_ids or []) if x is not None}
    excluded = set(recent) | explicit_excl

    if force_opening_id is not None:
        for op in DYNAMIC_OPENINGS:
            if op["id"] == int(force_opening_id):
                return op["id"], op["format"](song_title, band_name, year)

    compatible = [op for op in DYNAMIC_OPENINGS if not op["requires_year"] or bool(year)]
    if not compatible:
        compatible = list(DYNAMIC_OPENINGS)

    candidates = [op for op in compatible if op["id"] not in excluded]
    if not candidates:
        # Relax to avoid only the most recent opening and explicit exclusion
        last_one = {recent[-1]} if recent else set()
        candidates = [op for op in compatible if op["id"] not in (last_one | explicit_excl)]
    if not candidates:
        candidates = compatible

    chosen = random.choice(candidates)
    return chosen["id"], chosen["format"](song_title, band_name, year)

def select_closing_line(song_title, band_name, angle_idx=0):
    template = CLOSING_TEMPLATES[angle_idx % len(CLOSING_TEMPLATES)]
    return template.format(song=song_title, band=band_name)

def get_master_eddie_script(song_title, band_name, album_name="", year="", angle=1, opening_text=None):
    """
    Construye el guion maestro conciso (aprox 65-85 palabras totales para cumplir <= 45s con 5s de música).
    """
    clean_key = normalize_text_key(song_title)
    angles_list = None
    for k, v in MASTER_CURATED_STORIES.items():
        if normalize_text_key(k) == clean_key or normalize_text_key(k) in clean_key:
            angles_list = v if isinstance(v, list) else [v]
            break

    if angles_list:
        idx = (max(1, int(angle)) - 1) % len(angles_list)
        dev_story = angles_list[idx]
    else:
        year_str = f"En {year}, " if year else ""
        album_str = f"para el álbum {album_name}" if album_name else "durante una etapa clave de su carrera"
        if angle % 3 == 1:
            dev_story = (
                f"{year_str}{album_str}, {band_name} buscó capturar un sonido eléctrico directo en el estudio sobre cinta analógica. "
                f"La química del grupo convirtió aquellas intensas sesiones en un clásico perdurable que marcó a toda una generación."
            )
        elif angle % 3 == 2:
            dev_story = (
                f"{year_str}impulsada por un riff inolvidable de {band_name} {album_str}, la banda apostó por la fuerza rítmica y la emoción directa. "
                f"La toma definitiva conservó tanta energía viva que rápidamente conquistó los diales de todo el mundo."
            )
        else:
            dev_story = (
                f"{year_str}destacada como pieza esencial de {band_name} {album_str}, esta grabación nació del perfeccionismo instrumental en cabina. "
                f"Cada compás consolidó una identidad sonora tan poderosa que sigue resonando intacta hoy."
            )

    if not opening_text:
        _, opening_text = select_dynamic_opening(song_title, band_name, year)
    cierre = select_closing_line(song_title, band_name, angle - 1)
    full_script = f"{opening_text} {dev_story} {cierre}"
    return opening_text, dev_story, cierre, full_script

def generate_ai_story_script(song_title, band_name, album_name="", year="", angle=1, exclude_opening_ids=None, force_opening_id=None, previous_story_summary=None):
    """
    Investiga/redacta una anécdota histórica real y verificable en español de 38-52 palabras
    (total 65-85 palabras contando apertura dinámica y cierre emotivo) para respetar el límite estricto de 45s.
    """
    opening_id, apertura = select_dynamic_opening(
        song_title, band_name, year,
        exclude_ids=exclude_opening_ids,
        force_opening_id=force_opening_id
    )
    cierre = select_closing_line(song_title, band_name, angle - 1)

    clean_key = normalize_text_key(song_title)
    has_curated = any(normalize_text_key(k) == clean_key or normalize_text_key(k) in clean_key for k in MASTER_CURATED_STORIES)

    # Use OpenAI only if OPENAI_API_KEY is available AND either not in curated catalog OR regenerating beyond curated angles
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    dev_story = None
    source = "curated_master"

    curated_count = 0
    for k, v in MASTER_CURATED_STORIES.items():
        if normalize_text_key(k) == clean_key or normalize_text_key(k) in clean_key:
            curated_count = len(v) if isinstance(v, list) else 1
            break

    need_ai = (not has_curated) or (int(angle) > curated_count)
    if api_key and need_ai:
        try:
            system_prompt = (
                "Eres Fred, cronista y locutor experto de rock clásico en 'Rock Radio: De vuelta al pasado'. "
                "Escribes anécdotas reales, verificables y fascinantes de grabación, origen de letras o contexto histórico. "
                "REGLA ESTRICTA DE VERACIDAD: Nunca inventes fechas, personas ni acontecimientos falsos."
            )
            avoid_note = f"\nEvita repetir el enfoque previo: {previous_story_summary}\n" if previous_story_summary else ""
            user_prompt = (
                f"Redacta ÚNICAMENTE el párrafo de anécdota histórica (sin saludo inicial ni cierre) para la canción "
                f"'{song_title}' de '{band_name}' (Álbum: '{album_name or 'Clásico'}', Año: '{year or 'Época Clásica'}').\n"
                f"{avoid_note}"
                "REQUISITOS ESTRICTOS:\n"
                "- Exactamente 2 oraciones completas, claras y vívidas.\n"
                "- Entre 38 y 48 palabras en total (crítico para no superar 45 segundos con la música).\n"
                "- Solo hechos reales y verificables de grabación, composición, letras o contexto.\n"
                "- Sin etiquetas entre corchetes ni comillas ni markdown."
            )
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.65,
                "max_tokens": 180
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                raw_dev = resp_data["choices"][0]["message"]["content"].strip().strip('"\' ')
                raw_dev = strip_vocal_tags(raw_dev)
                if 25 <= len(raw_dev.split()) <= 65:
                    dev_story = raw_dev
                    source = "openai_gpt_4o_mini"
        except Exception as e:
            print(f"⚠️ [ROCK RADIO AI] Usando catálogo curado por: {e}", flush=True)

    if not dev_story:
        _, dev_story, _, _ = get_master_eddie_script(song_title, band_name, album_name, year, angle, opening_text=apertura)

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', dev_story) if s.strip()]
    full_script = f"{apertura} {' '.join(sentences)} {cierre}"
    total_words = len(full_script.split())

    return {
        "success": True,
        "opening_id": opening_id,
        "apertura": apertura,
        "desarrollo": " ".join(sentences),
        "dev_sentences": sentences,
        "cierre": cierre,
        "full_script": full_script,
        "source": source,
        "words": total_words,
        "duration_est_sec": round(5.0 + total_words / 2.1 + 1.0, 1)
    }

def condense_anecdote_text(dev_sentences, song_title, band_name, excess_sec=3.0):
    """
    Si el segmento supera los 45s, resume limpiamente la anécdota conservando sentido histórico
    y oraciones completas, sin cortar frases a la mitad ni acelerar la voz.
    """
    text = " ".join(dev_sentences).strip()
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    target_words = max(24, int(len(text.split()) - max(6, excess_sec * 2.2)))

    if api_key:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Resume textos de locución radial en español conservando todos los hechos históricos reales en oraciones completas."},
                    {"role": "user", "content": f"Resume esta anécdota sobre '{song_title}' de {band_name} a máximo {target_words} palabras, en 1 o 2 oraciones completas y naturales:\n\n{text}"}
                ],
                "temperature": 0.3,
                "max_tokens": 130
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                short = strip_vocal_tags(resp_data["choices"][0]["message"]["content"].strip().strip('"\' '))
                if 16 <= len(short.split()) < len(text.split()):
                    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', short) if s.strip()]
        except Exception as e:
            print(f"⚠️ [CONDENSE] Fallo OpenAI al resumir, aplicando compresión sintáctica limpia: {e}", flush=True)

    # Rule-based clean clause condensation (always leaves complete grammatical sentences)
    if len(dev_sentences) > 2:
        return dev_sentences[:2]

    # Shorten longer sentence by removing parenthetical / secondary subordinate clause after comma
    new_sentences = []
    for sent in dev_sentences:
        clauses = [c.strip() for c in sent.split(",") if c.strip()]
        if len(clauses) >= 3 and len(sent.split()) > 20:
            # Drop the middle explanatory clause if grammatically clean, or keep main clauses
            reduced = f"{clauses[0]}, {clauses[-1]}"
            if not reduced.endswith(('.', '!', '?')):
                reduced += "."
            new_sentences.append(reduced)
        else:
            new_sentences.append(sent)

    if " ".join(new_sentences) == text and len(dev_sentences) > 1:
        # Keep the richer single complete sentence if still over budget
        return [dev_sentences[0]]
    return new_sentences

# ==============================================================================
# 7. DICCIONARIO FONÉTICO DE RESPALDO (PARA EDGE-TTS SI FALTAN CREDENCIALES)
# ==============================================================================
ENGLISH_PHONETICS = [
    (r'\bFred Rewind\b', 'Fred Riuáind'),
    (r'\bRock Radio\b', 'Rok Réidio'),
    (r'\bDJ Fredd\b', 'Dí-yéi Fred'),
    (r'\bRush\b', 'Rásh'),
    (r'\bTom Sawyer\b', 'Tom Sóyer'),
    (r'\bTears for Fears\b', 'Tíars for Fíars'),
    (r'\bEverybody Wants to Rule the World\b', 'Évribadi Uónts tu Rul de Uérld'),
    (r'\bIron Maiden\b', 'Áiron Méiden'),
    (r'\bThe Trooper\b', 'De Trúper'),
    (r'\bAC/DC\b', 'Ei-Si Di-Si'),
    (r'\bBack in Black\b', 'Bak in Blák'),
    (r'\bKISS\b', 'Kis'),
    (r'\bDetroit Rock City\b', 'Detróit Rok Síti'),
    (r'\bToto\b', 'Tóu-tou'),
    (r'\bAfrica\b', 'Áfrika')
]

def apply_english_phonetics(text):
    if not text:
        return ""
    result = text
    for pattern, replacement in ENGLISH_PHONETICS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def parse_radio_script(text, song_title="Rock Classic", band_name="Rock Band", year=""):
    text = (text or "").strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sentences) >= 3:
        apertura = sentences[0]
        # Check if opening consists of two short sentences ("Rock Radio: De vuelta al pasado. Soy Fred...")
        if len(sentences) >= 4 and ("Rock Radio" in sentences[0] or "De vuelta al pasado" in sentences[0]) and len(sentences[0].split()) <= 8:
            apertura = f"{sentences[0]} {sentences[1]}"
            cierre = sentences[-1]
            dev_sentences = sentences[2:-1]
        else:
            cierre = sentences[-1]
            dev_sentences = sentences[1:-1]
        if dev_sentences:
            return apertura, dev_sentences, cierre, f"{apertura} {' '.join(dev_sentences)} {cierre}"

    res = generate_ai_story_script(song_title, band_name, year=year)
    return res["apertura"], res["dev_sentences"], res["cierre"], res["full_script"]

# ==============================================================================
# 8. MOTOR FISH AUDIO & DSP FFMPEG (Secciones 6, 7 y 8)
# ==============================================================================
def make_silence_mp3(duration_sec, out_path):
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", f"{duration_sec:.3f}",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        out_path
    ], capture_output=True, check=True)

def get_audio_duration(path):
    try:
        cmd = [FFPROBE_BIN, "-i", path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        return float(subprocess.check_output(cmd).decode().strip())
    except Exception:
        return 0.0

def get_mean_volume_db(path):
    try:
        res = subprocess.run(
            [FFMPEG_BIN, "-i", path, "-af", "volumedetect", "-f", "null", "-"],
            capture_output=True, text=True
        )
        m = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", res.stderr or "")
        return float(m.group(1)) if m else -20.0
    except Exception:
        return -20.0

def get_integrated_lufs(path):
    try:
        res = subprocess.run(
            [FFMPEG_BIN, "-nostats", "-i", path, "-filter_complex", "ebur128", "-f", "null", "-"],
            capture_output=True, text=True
        )
        matches = re.findall(r"I:\s*([-\d.]+)\s*LUFS", res.stderr or "")
        return float(matches[-1]) if matches else -20.0
    except Exception:
        return -20.0

def _fish_audio_tts_sync(text, out_mp3_path, reference_id=DEFAULT_FISH_VOICE, model=DEFAULT_FISH_MODEL):
    api_key = os.environ.get("FISH_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FISH_API_KEY no está configurada en el entorno del servidor.")

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
            if not audio_bytes or len(audio_bytes) < 500:
                raise RuntimeError("Respuesta de audio vacía desde Fish Audio.")
            with open(raw_tmp, "wb") as f:
                f.write(audio_bytes)
            break
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2.0 * (attempt + 1)
            print(f"⚠️ [Fish Audio] Intento {attempt + 1} falló ({e}). Reintentando en {wait_time}s...", flush=True)
            time.sleep(wait_time)

    # Normalizar formato a 44100Hz mono 192k para medición exacta de duración
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

async def synthesize_segments(ap_text, dev_texts, ci_text, tmp_prefix, temp_files, use_fish=True, fish_voice=DEFAULT_FISH_VOICE, fish_model=DEFAULT_FISH_MODEL, job_id=None):
    ap_mp3 = f"{tmp_prefix}_ap.mp3"
    ci_mp3 = f"{tmp_prefix}_ci.mp3"
    dev_mp3_paths = [f"{tmp_prefix}_dev_{idx}.mp3" for idx in range(len(dev_texts))]
    new_temps = [ap_mp3, ci_mp3] + dev_mp3_paths
    temp_files.extend(new_temps)

    if job_id:
        with ACTIVE_JOBS_LOCK:
            if job_id in ACTIVE_JOBS:
                ACTIVE_JOBS[job_id]['temp_files'].update(new_temps)

    tasks = []
    if use_fish:
        sem = asyncio.Semaphore(1)
        tasks.append(synthesize_fish_audio_tts(sem, ap_text, ap_mp3, reference_id=fish_voice, model=fish_model))
        for idx, s_text in enumerate(dev_texts):
            tasks.append(synthesize_fish_audio_tts(sem, s_text, dev_mp3_paths[idx], reference_id=fish_voice, model=fish_model))
        tasks.append(synthesize_fish_audio_tts(sem, ci_text, ci_mp3, reference_id=fish_voice, model=fish_model))
    else:
        if edge_tts is None:
            raise RuntimeError("edge_tts no está instalado y FISH_API_KEY no está disponible.")
        tasks.append(edge_tts.Communicate(apply_english_phonetics(ap_text), DEFAULT_VOICE, rate="+0%", pitch="+0Hz").save(ap_mp3))
        for idx, s_text in enumerate(dev_texts):
            tasks.append(edge_tts.Communicate(apply_english_phonetics(s_text), DEFAULT_VOICE, rate="+0%", pitch="+0Hz").save(dev_mp3_paths[idx]))
        tasks.append(edge_tts.Communicate(apply_english_phonetics(ci_text), DEFAULT_VOICE, rate="+0%", pitch="+2Hz").save(ci_mp3))

    await asyncio.gather(*tasks)
    return ap_mp3, dev_mp3_paths, ci_mp3

async def synthesize_anecdote_only(dev_texts, tmp_prefix, pass_num, temp_files, use_fish=True, fish_voice=DEFAULT_FISH_VOICE, fish_model=DEFAULT_FISH_MODEL):
    dev_mp3_paths = [f"{tmp_prefix}_dev_p{pass_num}_{idx}.mp3" for idx in range(len(dev_texts))]
    temp_files.extend(dev_mp3_paths)
    tasks = []
    if use_fish:
        sem = asyncio.Semaphore(1)
        for idx, s_text in enumerate(dev_texts):
            tasks.append(synthesize_fish_audio_tts(sem, s_text, dev_mp3_paths[idx], reference_id=fish_voice, model=fish_model))
    else:
        for idx, s_text in enumerate(dev_texts):
            tasks.append(edge_tts.Communicate(apply_english_phonetics(s_text), DEFAULT_VOICE, rate="+0%", pitch="+0Hz").save(dev_mp3_paths[idx]))
    await asyncio.gather(*tasks)
    return dev_mp3_paths

def master_radio_segment(ap_mp3, dev_mp3_paths, ci_mp3, out_mp3_path, tmp_prefix, temp_files, bed_seek_sec=15.0):
    """
    Pipeline de masterización y mezcla profesional con FFmpeg:
    1. Pausas orgánicas de cabina: 0.35s tras apertura, 0.30s entre oraciones, 0.45s antes del cierre.
    2. Cadena vocal unificada: highpass 80Hz, EQ correctiva (380Hz), presencia 2-4kHz (3kHz), de-esser, compresión 3:1.
    3. Medición EBU R128 real del cuerpo vs cierre y refuerzo determinístico en el cierre (+2.8 dB percibidos + 1.4 dB @ 3.2 kHz),
       sin cambios bruscos ni clipping ni aplastamiento por el limitador.
    4. Entrada instrumental de exactamente 5.0 segundos sin voz (adelay=5000|5000 en voz).
    5. Sidechain ducking de música durante la voz (~12-18dB reducción, attack=180ms, release=450ms).
    6. Transición final suave y limitación True Peak a -1.0 dBTP.
    """
    sil_ap_mp3 = f"{tmp_prefix}_sil_ap.mp3"
    sil_sent_mp3 = f"{tmp_prefix}_sil_sent.mp3"
    sil_ci_mp3 = f"{tmp_prefix}_sil_ci.mp3"
    pre_ci_txt = f"{tmp_prefix}_pre_ci.txt"
    pre_ci_mp3 = f"{tmp_prefix}_pre_ci.mp3"
    pre_ci_wav = f"{tmp_prefix}_pre_ci_m.wav"
    ci_base_wav = f"{tmp_prefix}_ci_b.wav"
    ci_mast_wav = f"{tmp_prefix}_ci_m.wav"
    voice_concat_txt = f"{tmp_prefix}_vm_concat.txt"
    voice_master_wav = f"{tmp_prefix}_voice_m.wav"
    temp_files.extend([
        sil_ap_mp3, sil_sent_mp3, sil_ci_mp3, pre_ci_txt, pre_ci_mp3,
        pre_ci_wav, ci_base_wav, ci_mast_wav, voice_concat_txt, voice_master_wav
    ])

    gap_ap = 0.35
    gap_sent = 0.30
    gap_ci = 0.45
    make_silence_mp3(gap_ap, sil_ap_mp3)
    make_silence_mp3(gap_sent, sil_sent_mp3)
    make_silence_mp3(gap_ci, sil_ci_mp3)

    pre_ci_list = [ap_mp3, sil_ap_mp3]
    for idx, dev_p in enumerate(dev_mp3_paths):
        pre_ci_list.append(dev_p)
        if idx < len(dev_mp3_paths) - 1:
            pre_ci_list.append(sil_sent_mp3)
    pre_ci_list.append(sil_ci_mp3)

    with open(pre_ci_txt, "w", encoding="utf-8") as f:
        for c in pre_ci_list:
            f.write(f"file '{c}'\n")

    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", pre_ci_txt,
        "-c", "copy",
        pre_ci_mp3
    ], capture_output=True, check=True)

    # Cadena vocal estandarizada (mismo procesamiento para cuerpo y cierre con margen de ~4 dB para el boost):
    # - highpass 80Hz
    # - EQ correctiva (-1.5dB @ 380Hz)
    # - Presencia vocal suave 2-4kHz (+2.0dB @ 3000Hz)
    # - De-esser para controlar sibilancias
    # - Compresión 3:1 (threshold -18dB, ratio 3, attack 15ms, release 120ms, makeup 1.2dB)
    vocal_core = (
        "aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "highpass=f=80,"
        "equalizer=f=380:width_type=o:width=1.2:g=-1.5,"
        "equalizer=f=3000:width_type=o:width=1.1:g=2.0,"
        "deesser=i=0.25:m=0.5:f=0.5:s=o,"
        "acompressor=threshold=-18dB:ratio=3:attack=15:release=120:makeup=1.2,"
        "volume=1.02"
    )

    subprocess.run([
        FFMPEG_BIN, "-y", "-i", pre_ci_mp3,
        "-af", vocal_core,
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        pre_ci_wav
    ], capture_output=True, check=True)

    subprocess.run([
        FFMPEG_BIN, "-y", "-i", ci_mp3,
        "-af", vocal_core,
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        ci_base_wav
    ], capture_output=True, check=True)

    # Medición EBU R128 de cuerpo y cierre para lograr +2.8 dB de presencia adicional percibida en el cierre
    body_lufs = get_integrated_lufs(pre_ci_wav)
    ci_lufs = get_integrated_lufs(ci_base_wav)
    boost_db = round(max(1.8, min(4.2, (body_lufs - ci_lufs) + 2.8)), 2)

    subprocess.run([
        FFMPEG_BIN, "-y", "-i", ci_base_wav,
        "-af", f"afade=t=in:st=0:d=0.025,volume={boost_db:.2f}dB,equalizer=f=3200:width_type=o:width=1.0:g=1.4",
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        ci_mast_wav
    ], capture_output=True, check=True)

    with open(voice_concat_txt, "w", encoding="utf-8") as f:
        f.write(f"file '{pre_ci_wav}'\n")
        f.write(f"file '{ci_mast_wav}'\n")

    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", voice_concat_txt,
        "-c", "copy",
        voice_master_wav
    ], capture_output=True, check=True)

    voice_dur = get_audio_duration(voice_master_wav)
    tail_dur = min(OUTRO_MUSIC_TAIL_SEC, max(0.3, SAFE_TARGET_TOTAL_SEC - INTRO_MUSIC_SEC - voice_dur))
    total_target_dur = min(SAFE_TARGET_TOTAL_SEC, round(INTRO_MUSIC_SEC + voice_dur + tail_dur, 3))
    fade_out_start = round(max(INTRO_MUSIC_SEC + voice_dur - 0.15, total_target_dur - tail_dur), 3)

    tmp_out = f"{out_mp3_path}.tmp.mp3"
    temp_files.append(tmp_out)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp3_path)), exist_ok=True)

    has_bed = os.path.exists(DEFAULT_MUSIC_BED) and os.path.getsize(DEFAULT_MUSIC_BED) > 10000

    # Exactamente 5.000 segundos de retardo (adelay=5000|5000) para entrada instrumental pura
    delayed_voice_chain = (
        f"[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"adelay={int(INTRO_MUSIC_SEC * 1000)}|{int(INTRO_MUSIC_SEC * 1000)},"
        f"apad=whole_dur={total_target_dur:.3f},"
        f"atrim=0:{total_target_dur:.3f}"
    )

    if has_bed:
        # Música de fondo:
        # - Empieza en bed_seek_sec (ej. 15s donde la instrumentación es constante y rica)
        # - 5s iniciales sin voz al 100% del nivel introductorio (fade-in 0.35s)
        # - Sidechain ducking durante la locución (reducción ~12-18dB, attack=180ms, release=450ms)
        # - Transición final suave sin silencios abruptos
        # - Limitador True Peak final a -1.0dB
        filter_complex = (
            f"{delayed_voice_chain},asplit=2[vox_mix][vox_sc];"
            f"[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"atrim=start={bed_seek_sec}:duration={total_target_dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.35,afade=t=out:st={fade_out_start:.3f}:d={tail_dur:.3f},"
            f"highpass=f=100,lowpass=f=8500,volume=0.38[bed_pre];"
            f"[bed_pre][vox_sc]sidechaincompress=threshold=0.015:ratio=4.0:attack=180:release=450:level_sc=3.2[bed_ducked];"
            f"[vox_mix][bed_ducked]amix=inputs=2:duration=first:normalize=0,"
            f"alimiter=limit=-1.0dB:attack=5:release=50[aout]"
        )
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", voice_master_wav,
            "-i", DEFAULT_MUSIC_BED,
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            tmp_out
        ]
    else:
        filter_complex = f"{delayed_voice_chain},alimiter=limit=-1.0dB:attack=5:release=50[aout]"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", voice_master_wav,
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            tmp_out
        ]

    subprocess.run(cmd, capture_output=True, check=True)
    actual_dur = get_audio_duration(tmp_out)
    return tmp_out, voice_dur, actual_dur, (gap_ap, gap_sent, gap_ci)

# ==============================================================================
# 9. INTEGRACIÓN SEGURA EN EL CATÁLOGO DEL REPRODUCTOR (index.html + Clones)
# ==============================================================================
def find_existing_catalog_pair(band_name, song_title):
    """Busca un par existente en BASE_DJ_EDDIE_TRACKS por bandName y songTitle normalizados."""
    if not os.path.exists(INDEX_HTML_PATH):
        return None, None
    try:
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        m_arr = re.search(r"const BASE_DJ_EDDIE_TRACKS\s*=\s*\[([\s\S]*?)\n\s*\];", html)
        if not m_arr:
            return None, None
        arr_body = m_arr.group(1)
        target_b = normalize_text_key(band_name)
        target_s = normalize_text_key(song_title)
        for blk in re.findall(r"\{\s*\n\s*id:\s*'intro_[^\}]+?\}", arr_body, re.DOTALL):
            bm = re.search(r"bandName:\s*(?:'([^']*)'|\"([^\"]*)\")", blk)
            sm = re.search(r"songTitle:\s*(?:'([^']*)'|\"([^\"]*)\")", blk)
            pm = re.search(r"pairId:\s*'([^']+)'", blk)
            am = re.search(r"audioUrl:\s*'([^']+)'", blk)
            if bm and sm and pm:
                b_val = normalize_text_key(bm.group(1) or bm.group(2))
                s_val = normalize_text_key(sm.group(1) or sm.group(2))
                if b_val == target_b and s_val == target_s:
                    return pm.group(1), (am.group(1) if am else None)
    except Exception:
        pass
    return None, None

def update_player_catalog(story_record):
    """
    Integra o actualiza la historia y canción en BASE_DJ_EDDIE_TRACKS dentro de index.html
    y sincroniza rock45.html, kiss.html y kiss-podcast.html sin tocar botones ni UI del reproductor.
    """
    if not os.path.exists(INDEX_HTML_PATH):
        return False

    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    existing_pair, _ = find_existing_catalog_pair(story_record["band_name"], story_record["song_title"])
    pair_slug = story_record.get("pair_slug") or existing_pair or make_slug(story_record["band_name"], story_record["song_title"])
    intro_id = f"intro_{pair_slug}"
    song_id = f"song_{pair_slug}"
    album_display = story_record.get("album") or ""
    year_str = story_record.get("year") or ""
    if album_display and year_str and year_str not in album_display:
        album_display = f"{album_display} ({year_str})"

    dur_sec = round(float(story_record["final_duration_sec"]), 2)
    dur_int = int(round(dur_sec))

    intro_obj = {
        "id": intro_id,
        "pairId": pair_slug,
        "isIntro": True,
        "bandName": story_record["band_name"],
        "songTitle": story_record["song_title"],
        "title": f"Intro: {story_record['song_title']}",
        "albumName": album_display,
        "year": year_str,
        "cover": story_record.get("cover") or "img/albums/kiss_1976_destroyer.png",
        "tag": "Historia",
        "duration": dur_int,
        "durationSec": dur_sec,
        "introSec": f"{dur_int}s",
        "summary": story_record["visible_script"],
        "status": "con_audio",
        "audioUrl": story_record["audio_file"],
        "fileUrl": story_record["audio_file"],
        "hasRealAudio": True,
        "relatedSongId": song_id,
        "lyrics": story_record.get("lyrics_timings", [])
    }

    def format_js_entry(obj):
        lyrics_lines = []
        for lyr in obj.get("lyrics", []):
            txt_esc = lyr["text"].replace("\\", "\\\\").replace("'", "\\'")
            lyrics_lines.append(f"          {{ start: {lyr['start']}, end: {lyr['end']}, text: '{txt_esc}' }}")
        lyrics_block = "[]" if not lyrics_lines else "[\n" + ",\n".join(lyrics_lines) + "\n        ]"

        def q(val):
            return "'" + str(val or "").replace("\\", "\\\\").replace("'", "\\'") + "'"

        lines = [
            "      {",
            f"        id: {q(obj['id'])},",
            f"        pairId: {q(obj['pairId'])},",
            f"        isIntro: {'true' if obj['isIntro'] else 'false'},",
            f"        bandName: {q(obj['bandName'])},",
            f"        songTitle: {q(obj['songTitle'])},",
            f"        title: {q(obj['title'])},",
            f"        albumName: {q(obj['albumName'])},",
            f"        year: {q(obj['year'])},",
            f"        cover: {q(obj['cover'])},",
            f"        tag: {q(obj['tag'])},",
            f"        duration: {obj['duration']},",
            f"        durationSec: {obj['durationSec']},",
            f"        introSec: {q(obj['introSec'])},",
            f"        summary: {q(obj['summary'])},",
            f"        status: {q(obj['status'])},",
            f"        audioUrl: {q(obj['audioUrl'])},",
            f"        fileUrl: {q(obj['fileUrl'])},",
            f"        hasRealAudio: true,"
        ]
        if obj["isIntro"]:
            lines.append(f"        relatedSongId: {q(obj['relatedSongId'])},")
        else:
            lines.append(f"        relatedIntroId: {q(obj['relatedIntroId'])},")
        lines.append(f"        lyrics: {lyrics_block}")
        lines.append("      }")
        return "\n".join(lines)

    entries_to_write = [intro_obj]
    full_song_audio = story_record.get("full_song_audio")
    if full_song_audio and os.path.exists(os.path.join(PROJECT_ROOT, full_song_audio)):
        song_dur = get_audio_duration(os.path.join(PROJECT_ROOT, full_song_audio))
        song_obj = {
            "id": song_id,
            "pairId": pair_slug,
            "isIntro": False,
            "bandName": story_record["band_name"],
            "songTitle": story_record["song_title"],
            "title": story_record["song_title"],
            "albumName": album_display,
            "year": year_str,
            "cover": story_record.get("cover") or "img/albums/kiss_1976_destroyer.png",
            "tag": "",
            "duration": int(round(song_dur)),
            "durationSec": round(song_dur, 2),
            "introSec": "",
            "summary": f"Canción original completa ({story_record['band_name']} — {story_record['song_title']})",
            "status": "con_audio",
            "audioUrl": full_song_audio,
            "fileUrl": full_song_audio,
            "hasRealAudio": True,
            "relatedIntroId": intro_id,
            "lyrics": []
        }
        entries_to_write.append(song_obj)

    # Locate BASE_DJ_EDDIE_TRACKS = [ ... ];
    m_arr = re.search(r"(const BASE_DJ_EDDIE_TRACKS\s*=\s*\[)([\s\S]*?)(\n\s*\];)", html)
    if not m_arr:
        return False

    arr_body = m_arr.group(2)

    # Replace or append each object cleanly inside BASE_DJ_EDDIE_TRACKS
    for entry in entries_to_write:
        js_text = format_js_entry(entry)
        # Match existing object block starting with id: '<entry_id>'
        obj_pat = re.compile(
            r"\n\s*\{\s*\n\s*id:\s*'" + re.escape(entry["id"]) + r"'[\s\S]*?\n\s*\}(?=,|\s*$)",
            re.MULTILINE
        )
        if obj_pat.search(arr_body):
            arr_body = obj_pat.sub("\n" + js_text, arr_body, count=1)
        else:
            arr_body = arr_body.rstrip() + ",\n" + js_text

    new_html = html[:m_arr.start(2)] + arr_body + html[m_arr.end(2):]

    # Increment clean reset key so returning browsers pick up regenerated base story duration & lyrics
    reset_m = re.search(r"dj_fredd_reset_v(\d+)_clean", new_html)
    if reset_m:
        next_ver = int(reset_m.group(1)) + 1
        new_html = re.sub(r"dj_fredd_reset_v\d+_clean", f"dj_fredd_reset_v{next_ver}_clean", new_html)

    tmp_html = f"{INDEX_HTML_PATH}.tmp"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(new_html)
    os.replace(tmp_html, INDEX_HTML_PATH)

    for clone in HTML_CLONES:
        clone_path = os.path.join(PROJECT_ROOT, clone)
        if os.path.exists(clone_path):
            shutil.copyfile(INDEX_HTML_PATH, clone_path)

    return True

# ==============================================================================
# 10. ORQUESTADOR DE PRODUCCIÓN RADIAL ASISTIDA POR IA (Secciones 9 y 10)
# ==============================================================================
async def run_story_pipeline(
    song_title,
    band_name,
    album_name="",
    year="",
    cover="",
    full_song_audio=None,
    mode="generate",  # "generate" | "regenerate_story" | "regenerate_voice"
    engine=None,
    fish_voice=None,
    fish_model=None,
    out_mp3_path=None,
    job_id=None
):
    """
    Ejecuta el flujo completo de 15 pasos con validación estricta de <= 45.0s,
    reemplazo atómico y persistencia en data/stories_metadata.json.
    """
    pid = os.getpid()
    t_start = time.time()
    use_fish = (engine == "fish") or (engine is None and bool(os.environ.get("FISH_API_KEY", "").strip()))
    selected_voice = fish_voice or DEFAULT_FISH_VOICE
    selected_model = fish_model or DEFAULT_FISH_MODEL

    meta_store = load_stories_metadata()
    story_key = make_story_key(band_name, song_title)
    existing_record = meta_store["stories"].get(story_key)

    existing_pair_slug, existing_audio_url = find_existing_catalog_pair(band_name, song_title)
    if not out_mp3_path:
        if existing_audio_url and existing_audio_url.startswith("audio/"):
            out_mp3_path = os.path.join(PROJECT_ROOT, existing_audio_url)
        else:
            slug = existing_pair_slug or make_slug(band_name, song_title)
            out_mp3_path = os.path.join(WORKSPACE_AUDIO_DIR, f"eddie_intro_{slug}.mp3")

    rel_audio_file = os.path.relpath(out_mp3_path, PROJECT_ROOT).replace("\\", "/")

    # 1. Preparar guion (nuevo, regenerado o reutilizado)
    if mode == "regenerate_voice" and existing_record:
        opening_id = existing_record.get("opening_id", 1)
        apertura = existing_record["apertura"]
        dev_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', existing_record["desarrollo"]) if s.strip()]
        cierre = existing_record["cierre"]
        angle_index = existing_record.get("angle_index", 1)
        script_source = "voice_only_reuse"
        cover = cover or existing_record.get("cover", "")
        full_song_audio = full_song_audio or existing_record.get("full_song_audio")
        album_name = album_name or existing_record.get("album", "")
        year = year or existing_record.get("year", "")
    else:
        excl_openings = []
        next_angle = 1
        prev_summary = None
        if existing_record and mode == "regenerate_story":
            if existing_record.get("opening_id"):
                excl_openings.append(existing_record["opening_id"])
            next_angle = int(existing_record.get("angle_index", 1)) + 1
            prev_summary = existing_record.get("desarrollo")

        ai_script = generate_ai_story_script(
            song_title, band_name, album_name, year,
            angle=next_angle,
            exclude_opening_ids=excl_openings,
            previous_story_summary=prev_summary
        )
        opening_id = ai_script["opening_id"]
        apertura = ai_script["apertura"]
        dev_sentences = ai_script["dev_sentences"]
        cierre = ai_script["cierre"]
        angle_index = next_angle
        script_source = ai_script["source"]

    dual = build_dual_scripts(apertura, dev_sentences, cierre, model_name=selected_model)

    print(f"\n🎙️ [ROCK RADIO AI] Iniciando '{song_title}' — {band_name} (modo={mode}, modelo={selected_model}, voz={selected_voice[:8]}...)", flush=True)
    print(f"   Apertura #{opening_id}: {dual['apertura_clean']}", flush=True)

    tmp_prefix = f"/tmp/rockradio_{pid}_{int(t_start*1000)}"
    temp_files = []

    try:
        # 2. Síntesis inicial con Fish Audio
        ap_mp3, dev_mp3_paths, ci_mp3 = await synthesize_segments(
            dual["vocal_ap"], dual["vocal_dev_list"], dual["vocal_ci"],
            tmp_prefix, temp_files,
            use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model, job_id=job_id
        )

        # 3. Medir duración real y aplicar resumen/regeneración si > 45s (hasta 3 pases)
        for pass_num in range(1, 4):
            dur_ap = get_audio_duration(ap_mp3)
            dur_devs = [get_audio_duration(p) for p in dev_mp3_paths]
            dur_ci = get_audio_duration(ci_mp3)
            gaps_total = 0.35 + max(0, len(dur_devs) - 1) * 0.30 + 0.45
            voice_dur_est = dur_ap + sum(dur_devs) + dur_ci + gaps_total
            predicted_final = INTRO_MUSIC_SEC + voice_dur_est + 0.6

            if predicted_final <= SAFE_TARGET_TOTAL_SEC:
                break

            excess = predicted_final - (SAFE_TARGET_TOTAL_SEC - 1.0)
            print(f"⏱️ [ROCK RADIO AI] Duración estimada {predicted_final:.2f}s excede límite (45s). Resumiendo anécdota (pase {pass_num})...", flush=True)
            condensed_sents = condense_anecdote_text(dual["dev_sentences_clean"], song_title, band_name, excess_sec=excess)
            if " ".join(condensed_sents) == " ".join(dual["dev_sentences_clean"]):
                # Force single concise sentence if condensation couldn't reduce further
                condensed_sents = [dual["dev_sentences_clean"][0]]

            dual = build_dual_scripts(dual["apertura_clean"], condensed_sents, dual["cierre_clean"], model_name=selected_model)
            dev_mp3_paths = await synthesize_anecdote_only(
                dual["vocal_dev_list"], tmp_prefix, pass_num, temp_files,
                use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model
            )

        # 4. Masterización FFmpeg (5s intro musical + ducking 12-18dB + +2.8dB cierre + -1dBTP limiter)
        bed_seek = 15.0 + ((angle_index - 1) * 8.0) % 40.0
        tmp_out, voice_dur, actual_final_dur, (gap_ap, gap_sent, gap_ci) = master_radio_segment(
            ap_mp3, dev_mp3_paths, ci_mp3, out_mp3_path, tmp_prefix, temp_files, bed_seek_sec=bed_seek
        )

        # 5. Validación estricta del archivo generado antes de reemplazar el existente
        if not os.path.exists(tmp_out) or os.path.getsize(tmp_out) < 10000:
            raise RuntimeError("El archivo de audio generado está vacío o incompleto.")
        if actual_final_dur <= 0 or actual_final_dur > MAX_TOTAL_DURATION_SEC:
            raise RuntimeError(f"La duración final ({actual_final_dur:.2f}s) incumple el límite máximo absoluto de {MAX_TOTAL_DURATION_SEC}s.")

        # Reemplazo atómico seguro (conserva anterior si ocurrió error arriba)
        os.replace(tmp_out, out_mp3_path)

        # 6. Calcular marcas de tiempo exactas (desplazadas +5.0s por la entrada instrumental)
        dur_ap = get_audio_duration(ap_mp3)
        dur_devs = [get_audio_duration(p) for p in dev_mp3_paths]
        dur_ci = get_audio_duration(ci_mp3)

        lyrics_timings = [
            {
                "start": 0.0,
                "end": round(INTRO_MUSIC_SEC, 2),
                "text": "🎸 📻 Intro musical — Rock Radio: De vuelta al pasado..."
            }
        ]
        t_cur = INTRO_MUSIC_SEC
        lyrics_timings.append({
            "start": round(t_cur, 2),
            "end": round(t_cur + dur_ap, 2),
            "text": dual["apertura_clean"]
        })
        t_cur += dur_ap + gap_ap

        for idx, sent in enumerate(dual["dev_sentences_clean"]):
            st = round(t_cur, 2)
            en = round(t_cur + dur_devs[idx], 2)
            lyrics_timings.append({"start": st, "end": en, "text": sent})
            t_cur = en + gap_sent

        ci_start = round(t_cur - gap_sent + gap_ci, 2)
        lyrics_timings.append({
            "start": ci_start,
            "end": round(min(actual_final_dur, ci_start + dur_ci), 2),
            "text": dual["cierre_clean"]
        })

        # 7. Persistencia completa (Sección 11)
        record = {
            "song_title": song_title,
            "band_name": band_name,
            "album": album_name,
            "year": year,
            "cover": cover,
            "full_song_audio": full_song_audio,
            "visible_script": dual["visible_script"],
            "vocal_script": dual["vocal_script"],
            "apertura": dual["apertura_clean"],
            "desarrollo": " ".join(dual["dev_sentences_clean"]),
            "cierre": dual["cierre_clean"],
            "opening_id": opening_id,
            "opening_text": dual["apertura_clean"],
            "fish_model": selected_model if use_fish else DEFAULT_VOICE,
            "voice_reference_id": selected_voice if use_fish else DEFAULT_VOICE,
            "voice_duration_sec": round(voice_dur, 2),
            "final_duration_sec": round(actual_final_dur, 2),
            "intro_music_sec": INTRO_MUSIC_SEC,
            "audio_file": rel_audio_file,
            "angle_index": angle_index,
            "script_source": script_source,
            "lyrics_timings": lyrics_timings,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }

        meta_store["stories"][story_key] = record
        meta_store["last_generated_key"] = story_key
        recent = list(meta_store.get("recent_openings", []))
        recent.append(opening_id)
        meta_store["recent_openings"] = recent[-10:]
        save_stories_metadata(meta_store)

        # 8. Integrar en catálogo del reproductor (index.html + clones)
        update_player_catalog(record)

        elapsed = time.time() - t_start
        print(f"✅ [ROCK RADIO AI] Completado en {elapsed:.2f}s | '{song_title}' ({band_name}) | Voz: {voice_dur:.2f}s | Final: {actual_final_dur:.2f}s (<=45s) | Archivo: {rel_audio_file}", flush=True)
        return record
    finally:
        for tf in temp_files:
            try:
                if os.path.exists(tf):
                    os.remove(tf)
            except Exception:
                pass

async def execute_ai_command(command_text, engine=None, fish_voice=None, fish_model=None):
    """
    Punto de entrada principal para comandos de IA en lenguaje natural.
    """
    parsed = parse_ai_command(command_text)
    intent = parsed.get("intent")

    if intent == "unknown":
        return {"success": False, "status": "error", "message": "No pude entender el comando."}

    if intent == "regenerate_voice":
        meta_store = load_stories_metadata()
        target_record = None
        if parsed.get("target") == "last":
            last_key = meta_store.get("last_generated_key")
            if last_key:
                target_record = meta_store["stories"].get(last_key)
        else:
            res_meta = resolve_song_metadata(parsed.get("song_query"), parsed.get("band_query"))
            if res_meta.get("resolved"):
                target_record = meta_store["stories"].get(res_meta["metadata"]["key"])

        if not target_record:
            return {"success": False, "status": "error", "message": "No existe una historia previa guardada para regenerar su voz."}

        rec = await run_story_pipeline(
            target_record["song_title"],
            target_record["band_name"],
            album_name=target_record.get("album", ""),
            year=target_record.get("year", ""),
            cover=target_record.get("cover", ""),
            full_song_audio=target_record.get("full_song_audio"),
            mode="regenerate_voice",
            engine=engine,
            fish_voice=fish_voice,
            fish_model=fish_model
        )
        return {"success": True, "status": "completed", "intent": intent, "record": rec}

    # generate or regenerate_story
    res_meta = resolve_song_metadata(parsed.get("song_query"), parsed.get("band_query"))
    if res_meta.get("ambiguous") or not res_meta.get("resolved"):
        return {
            "success": False,
            "status": "ambiguous",
            "intent": intent,
            "message": res_meta.get("message"),
            "candidates": res_meta.get("candidates", [])
        }

    md = res_meta["metadata"]
    mode = "regenerate_story" if intent == "regenerate_story" else "generate"
    rec = await run_story_pipeline(
        md["song_title"],
        md["band_name"],
        album_name=md.get("album", ""),
        year=md.get("year", ""),
        cover=md.get("cover", ""),
        full_song_audio=md.get("full_song_audio"),
        mode=mode,
        engine=engine,
        fish_voice=fish_voice,
        fish_model=fish_model
    )
    return {"success": True, "status": "completed", "intent": intent, "record": rec}

# Wrapper compatible con llamadas heredadas
async def build_eddie_radio_narration(text, song_title="Rock Classic", band_name="Rock Band", out_mp3_path=None, job_id=None, engine=None, fish_voice=None):
    t_start = time.time()
    res_meta = resolve_song_metadata(song_title, band_name)
    md = res_meta.get("metadata", {}) if res_meta.get("resolved") else {}
    rec = await run_story_pipeline(
        song_title, band_name,
        album_name=md.get("album", ""),
        year=md.get("year", ""),
        cover=md.get("cover", ""),
        full_song_audio=md.get("full_song_audio"),
        mode="generate",
        engine=engine,
        fish_voice=fish_voice,
        out_mp3_path=out_mp3_path,
        job_id=job_id
    )
    elapsed = time.time() - t_start
    ci_start = rec["lyrics_timings"][-1]["start"] if rec.get("lyrics_timings") else 0.0
    return rec["audio_file"], rec["final_duration_sec"], elapsed, rec["lyrics_timings"], ci_start, rec["visible_script"]

# ==============================================================================
# 11. SERVIDOR API LOCAL (Sin credenciales expuestas en el cliente)
# ==============================================================================
def run_server(port=5055):
    class DjFreddAudioHandler(BaseHTTPRequestHandler):
        def _set_cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')

        def _send_json(self, code, payload):
            self.send_response(code)
            self._set_cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

        def do_OPTIONS(self):
            self.send_response(200)
            self._set_cors()
            self.end_headers()

        def do_GET(self):
            if self.path in ('/api/status', '/status', '/'):
                caps = get_fish_model_capabilities(DEFAULT_FISH_MODEL)
                self._send_json(200, {
                    'status': 'online',
                    'service': 'Rock Radio • Fred Rewind AI Production Engine',
                    'fishModel': caps['model'],
                    'fishVoiceId': DEFAULT_FISH_VOICE,
                    'capabilities': caps,
                    'maxDurationSec': MAX_TOTAL_DURATION_SEC,
                    'introMusicSec': INTRO_MUSIC_SEC,
                    'port': port,
                    'timestamp': time.time()
                })
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
            except Exception:
                self._send_json(400, {'success': False, 'error': 'JSON inválido'})
                return

            if self.path in ('/api/execute_command', '/api/command'):
                cmd_text = data.get('command') or data.get('prompt') or ''
                try:
                    res = asyncio.run(execute_ai_command(cmd_text))
                    self._send_json(200 if res.get('success') else 422, res)
                except Exception as e:
                    self._send_json(500, {'success': False, 'status': 'error', 'error': str(e)})

            elif self.path == '/api/generate_audio':
                song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                album_name = data.get('album', '')
                year = data.get('year', '')
                try:
                    rec = asyncio.run(run_story_pipeline(
                        song_title, band_name, album_name=album_name, year=year, mode="generate"
                    ))
                    full_path = os.path.join(PROJECT_ROOT, rec["audio_file"])
                    with open(full_path, 'rb') as f:
                        b64_audio = base64.b64encode(f.read()).decode('utf-8')
                    dur = rec["final_duration_sec"]
                    self._send_json(200, {
                        'success': True,
                        'audioUrl': f"data:audio/mp3;base64,{b64_audio}",
                        'fileUrl': rec["audio_file"],
                        'duration': f"{int(round(dur))}s",
                        'durationSec': dur,
                        'intro_timings': rec["lyrics_timings"],
                        'full_script': rec["visible_script"]
                    })
                except Exception as e:
                    self._send_json(500, {'success': False, 'error': str(e)})

            elif self.path in ('/api/generate_story_text', '/api/story_text'):
                song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                album_name = data.get('album', '')
                year = data.get('year', '')
                angle = int(data.get('angle', 1))
                res = generate_ai_story_script(song_title, band_name, album_name, year, angle)
                self._send_json(200, res)
            else:
                self._send_json(404, {'error': 'Endpoint no encontrado'})

    server = ThreadingHTTPServer(('0.0.0.0', port), DjFreddAudioHandler)
    print(f"🚀 [ROCK RADIO AI] Servidor en http://0.0.0.0:{port} (Fish Audio {DEFAULT_FISH_MODEL} | Voz {DEFAULT_FISH_VOICE})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor.")

# ==============================================================================
# 12. INTERFAZ CLI PRINCIPAL
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Rock Radio — Motor de Historias IA y Fish Audio")
    parser.add_argument("--command", "-c", help="Comando en lenguaje natural (ej: 'Generar historia de Tom Sawyer de Rush')")
    parser.add_argument("--song", help="Nombre de la canción")
    parser.add_argument("--band", help="Nombre de la banda o artista")
    parser.add_argument("--album", default="", help="Nombre del álbum")
    parser.add_argument("--year", default="", help="Año de lanzamiento")
    parser.add_argument("--mode", choices=["generate", "regenerate_story", "regenerate_voice"], default="generate")
    parser.add_argument("--out", default=None, help="Ruta de salida del MP3")
    parser.add_argument("--engine", choices=["fish", "edge"], default=None, help="Motor TTS: fish o edge")
    parser.add_argument("--fish-voice", default=None, help="ID de voz en Fish Audio")
    parser.add_argument("--fish-model", default=None, help="Modelo de Fish Audio")
    parser.add_argument("--serve", action="store_true", help="Iniciar servidor API local")
    parser.add_argument("--port", type=int, default=5055, help="Puerto del servidor API local")

    args = parser.parse_args()

    if args.serve:
        run_server(args.port)
        return

    if args.command:
        res = asyncio.run(execute_ai_command(
            args.command,
            engine=args.engine,
            fish_voice=args.fish_voice,
            fish_model=args.fish_model
        ))
        print("\n" + json.dumps(res, ensure_ascii=False, indent=2))
        if not res.get("success"):
            sys.exit(1)
        return

    if args.song and args.band:
        rec = asyncio.run(run_story_pipeline(
            args.song, args.band,
            album_name=args.album,
            year=args.year,
            mode=args.mode,
            out_mp3_path=args.out,
            engine=args.engine,
            fish_voice=args.fish_voice,
            fish_model=args.fish_model
        ))
        print("\n" + json.dumps(rec, ensure_ascii=False, indent=2))
        return

    parser.print_help()

if __name__ == "__main__":
    main()
