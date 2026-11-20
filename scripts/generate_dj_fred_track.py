#!/usr/bin/env python3
"""
ROCK RADIO — FRED REWIND • Generador de Historias mediante Comandos de IA y Fish Audio
======================================================================================
Arquitectura unificada de producción radial asistida por IA:
- Conserva Fish Audio (s2.1-pro-free / s2.1-pro) y la voz configurada de Fred (reference_id).
- Evalúa compatibilidad con S2.1 Pro y Drama 3 sin cambiar el modelo ni la voz activa.
- Intérprete de comandos en lenguaje natural (generación, regeneración de historia, regeneración de voz).
- Motor creativo de intros y outros (10 intros y 8 outros como guía de estilo) con control de diversidad en las últimas 15 historias.
- Guion dual exacto: Texto visible (limpio) + Texto vocal (dirección emocional Fish Audio).
- Duración máxima absoluta de 45.0 segundos (incluyendo 5.0s iniciales de música sin voz y dos pausas exactas de 1.0s).
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
import math
import wave
import array
import unicodedata
import urllib.request
import urllib.error
import urllib.parse
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
PAUSE_MUSIC_SEC = 1.0
OUTRO_MUSIC_TAIL_SEC = 1.2
MAX_TOTAL_DURATION_SEC = 45.0
SAFE_TARGET_TOTAL_SEC = 44.6  # Margen para padding de frames MP3 garantizando <= 45.00s reales

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
    "¡Sube el volumen y escuchemos a {song}, de {band}, aquí en Rock Radio, de vuelta al pasado!",
    "¡Sube el volumen! Escuchemos juntos a {song}, de {band}, aquí en Rock Radio, de vuelta al pasado!",
    "¡Dale volumen y escuchemos a {song}, de {band}, aquí en Rock Radio, de vuelta al pasado!"
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
        "resolution_tag": "[emotional]",
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

EMOTION_VOCAL_PROFILES = {
    "sensibilidad_contenida": {
        "opening": "[soft, intimate, reflective]",
        "story": "[calm, warm, storytelling]",
        "resolution": "[thoughtful, gentle]",
        "closing": "[warm, soft]",
        "temperature": 0.62,
        "top_p": 0.78,
        "closing_boost_db": 0.9,
    },
    "intensidad_historica": {
        "opening": "[confident, intrigued, lively]",
        "story": "[energetic, animated]",
        "resolution": "[excited, dynamic]",
        "closing": "[energetic, smiling, upbeat]",
        "temperature": 0.86,
        "top_p": 0.88,
        "closing_boost_db": 2.8,
    },
    "nostalgia_cercana": {
        "opening": "[warm, nostalgic, gentle]",
        "story": "[warm, conversational]",
        "resolution": "[nostalgic, heartfelt]",
        "closing": "[warm, inviting]",
        "temperature": 0.70,
        "top_p": 0.82,
        "closing_boost_db": 1.4,
    },
    "contraste_cultural": {
        "opening": "[curious, slightly amused, conversational]",
        "story": "[engaging, clear]",
        "resolution": "[surprised, expressive]",
        "closing": "[confident, warm]",
        "temperature": 0.78,
        "top_p": 0.85,
        "closing_boost_db": 1.9,
    },
    "curiosidad_tecnica": {
        "opening": "[curious, intrigued, warm]",
        "story": "[engaged, clear, conversational]",
        "resolution": "[appreciative, confident]",
        "closing": "[warm, upbeat]",
        "temperature": 0.75,
        "top_p": 0.84,
        "closing_boost_db": 1.8,
    },
    "calidez_radial": {
        "opening": "[warm, confident, smiling]",
        "story": "[conversational, friendly]",
        "resolution": "[warm, expressive]",
        "closing": "[upbeat, warm]",
        "temperature": 0.76,
        "top_p": 0.84,
        "closing_boost_db": 2.0,
    },
}


def get_vocal_profile(emotion=None):
    return EMOTION_VOCAL_PROFILES.get(str(emotion or "").strip().lower(), EMOTION_VOCAL_PROFILES["calidez_radial"])


def build_dual_scripts(
    paragraph_1,
    paragraph_2,
    p3_resolution,
    p3_closing,
    model_name=DEFAULT_FISH_MODEL,
    emotion=None,
    tts_p1=None,
    tts_p2=None,
    tts_p3=None,
):
    """
    Estructura el guion en tres bloques narrativos identificables con separación semántica:
    - paragraph_1: apertura y contexto inicial
    - paragraph_2: desarrollo de la anécdota histórica
    - paragraph_3: desenlace + cierre emotivo progresivo
    Genera texto visible limpio y texto vocal expresivo adaptado a la emoción de la anécdota.
    """
    caps = get_fish_model_capabilities(model_name)
    profile = get_vocal_profile(emotion)

    clean_p1 = strip_vocal_tags(paragraph_1)
    clean_p2 = strip_vocal_tags(paragraph_2)
    clean_p3_res = strip_vocal_tags(p3_resolution)
    clean_p3_close = strip_vocal_tags(p3_closing)
    clean_p3 = f"{clean_p3_res} {clean_p3_close}".strip()

    visible_script = " ".join([x for x in (clean_p1, clean_p2, clean_p3) if x]).strip()

    opening_tag = profile["opening"]
    if "?" in clean_p1 and "curious" not in opening_tag:
        opening_tag = "[curious, intrigued, warm]"

    if tts_p1 and tts_p2 and tts_p3:
        vocal_p1 = tts_p1.strip()
        vocal_p2 = tts_p2.strip()
        vocal_p3 = tts_p3.strip()
    elif caps["supports_bracket_tags"]:
        vocal_p1 = f"{opening_tag} {clean_p1}"
        vocal_p2 = f"{profile['story']} {clean_p2}"
        if caps["supports_inline_xml_tags"]:
            emphasis_wrap = "soft" if emotion == "sensibilidad_contenida" else "forceful"
            close_part = f"{profile['closing']} <{emphasis_wrap}>{clean_p3_close}</{emphasis_wrap}>"
        else:
            close_part = f"{profile['closing']} {clean_p3_close}"
        if clean_p3_res:
            vocal_p3 = f"{profile['resolution']} {clean_p3_res} {close_part}".strip()
        else:
            vocal_p3 = close_part
    else:
        vocal_p1 = clean_p1
        vocal_p2 = clean_p2
        vocal_p3 = clean_p3

    vocal_script = " ".join([x for x in (vocal_p1, vocal_p2, vocal_p3) if x]).strip()
    return {
        "visible_script": visible_script,
        "vocal_script": vocal_script,
        "p1_clean": clean_p1,
        "p2_clean": clean_p2,
        "p3_clean": clean_p3,
        "p3_res_clean": clean_p3_res,
        "p3_close_clean": clean_p3_close,
        "vocal_p1": vocal_p1,
        "vocal_p2": vocal_p2,
        "vocal_p3": vocal_p3,
        "temperature": profile["temperature"],
        "top_p": profile["top_p"],
        "closing_boost_db": profile["closing_boost_db"],
        "expressive_instructions": {
            "model": caps["model"],
            "emotion": emotion or "calidez_radial",
            "temperature": profile["temperature"],
            "top_p": profile["top_p"],
            "paragraph_1": opening_tag if caps["supports_bracket_tags"] else "natural",
            "paragraph_2": profile["story"] if caps["supports_bracket_tags"] else "narrative",
            "paragraph_3": f"{profile['resolution']} -> {profile['closing']}" if caps["supports_bracket_tags"] else "progressive_emotional"
        }
    }

# ==============================================================================
# 3. ANÉCDOTAS HISTÓRICAS VERIFICABLES MULTI-ÁNGULO (3 Párrafos <= 45s total)
# ==============================================================================
MASTER_CURATED_STORIES = {
    "tom sawyer": [
        {
            "p1_hook": "Todo comenzó en el invierno de 1980.",
            "p2_anecdote": "En Quebec, Neil Peart adaptó un poema de Pye Dubois sobre el personaje de Mark Twain, mientras Geddy Lee abría con su sintetizador Oberheim.",
            "p3_resolution": "Ese cruce de técnica y rebeldía selló su himno definitivo.",
            "historical_info": "Sesiones de Moving Pictures (1980-1981) en Le Studio, Morin-Heights, Quebec; letra de Neil Peart y Pye Dubois; sintetizador Oberheim de Geddy Lee."
        },
        {
            "p1_hook": "Una pista tan exigente que casi queda fuera.",
            "p2_anecdote": "En Moving Pictures, el trío luchó por capturar su energía exacta hasta que Neil Peart grabó sus redobles explosivos.",
            "p3_resolution": "Aquel desafío técnico se volvió su clásico inmortal.",
            "historical_info": "Complejidad de grabación en consola durante Moving Pictures (1981) y la histórica toma de batería de Neil Peart."
        },
        {
            "p1_hook": "Un reto rítmico que rompió las reglas.",
            "p2_anecdote": "En Morin-Heights, Alex Lifeson grabó acordes cortantes en siete por ocho, fundiendo rock progresivo con fuerza directa.",
            "p3_resolution": "Esa fórmula única los llevó a la cima mundial.",
            "historical_info": "Compás asimétrico en 7/8 y guitarras de Alex Lifeson grabadas en Le Studio para Moving Pictures (1981)."
        }
    ],
    "everybody wants to rule the world": [
        {
            "p1_hook": "Un clásico que casi ni se graba.",
            "p2_anecdote": "Se sumó al final de Songs from the Big Chair en 1985, cuando Chris Hughes pidió un corte luminoso y Roland Orzabal lo tejió en una tarde.",
            "p3_resolution": "Aquella sesión improvisada alcanzó el número uno mundial.",
            "historical_info": "Grabación de última hora en 1985 para Songs from the Big Chair tras petición del productor Chris Hughes; guitarras de 12 cuerdas y ritmo shuffle de Roland Orzabal."
        },
        {
            "p1_hook": "Su brillo oculta una oscura advertencia.",
            "p2_anecdote": "En plena Guerra Fría de 1985, Curt Smith y Roland Orzabal escondieron una crítica al poder tras una melodía vibrante.",
            "p3_resolution": "Ese contraste inolvidable definió toda una era.",
            "historical_info": "Composición de Curt Smith y Roland Orzabal en plena Guerra Fría (1985), contrastando crítica política con sonoridad luminosa."
        },
        {
            "p1_hook": "Nadie en cabina imaginó este éxito.",
            "p2_anecdote": "Aunque el dúo temía que desentonara con la densidad del álbum, sus coros y el solo final brillaron al instante.",
            "p3_resolution": "En marzo de 1985 conquistó las listas globales.",
            "historical_info": "Lanzamiento de marzo de 1985 y contraste tonal dentro de Songs from the Big Chair."
        }
    ],
    "the trooper": [
        {
            "p1_hook": "Inspirada en una batalla del siglo diecinueve.",
            "p2_anecdote": "Basada en la batalla de Balaclava de 1854 y el poema de Alfred, Lord Tennyson, Steve Harris la escribió en 1983 desde la mirada cruda de un soldado en combate mientras Dave Murray y Adrian Smith trazaban el galope de guitarras gemelas.",
            "p3_resolution": "Desde entonces es un himno infaltable en cada escenario.",
            "historical_info": "Batalla de Balaclava (1854, Guerra de Crimea) y poema de Alfred, Lord Tennyson; guitarras de Dave Murray y Adrian Smith en Piece of Mind (1983)."
        },
        {
            "p1_hook": "Grabada en Bahamas sin trucos en cabina.",
            "p2_anecdote": "Para Piece of Mind en 1983 en los estudios Compass Point de Nasáu, Bruce Dickinson desató su voz sobre la escritura directa de Steve Harris, buscando sonar como la banda en vivo.",
            "p3_resolution": "Esa crudeza convirtió el tema en sello indiscutible de Iron Maiden.",
            "historical_info": "Sesiones en Compass Point Studios, Nasáu, Bahamas (1983), álbum Piece of Mind, con Bruce Dickinson y producción de Martin Birch."
        }
    ],
    "africa": [
        {
            "p1_hook": "Una canción nacida en plena madrugada.",
            "p2_anecdote": "En 1982, tras ver un documental en televisión, David Paich imaginó África sin haber pisado el continente y grabó con Jeff Porcaro marimbas, congas y percusiones reales para Toto IV.",
            "p3_resolution": "Casi queda fuera del disco y terminó alcanzando el número uno en Estados Unidos.",
            "historical_info": "Inspiración nocturna de David Paich en 1982 tras ver un documental; grabación acústica multipista con Jeff Porcaro y Emil Richards para Toto IV (1982)."
        },
        {
            "p1_hook": "Un estribillo que el propio grupo dudó en publicar.",
            "p2_anecdote": "Durante las sesiones de Toto IV en Los Ángeles, varios integrantes pensaban que su letra y su mezcla de sintetizadores con percusión africana no encajaban con el rock habitual de la banda.",
            "p3_resolution": "El pulso hipnótico de Jeff Porcaro terminó dándoles su mayor clásico mundial.",
            "historical_info": "Sesiones de Toto IV (1982) en Los Ángeles; dudas iniciales de Steve Lukather y miembros de Toto antes de alcanzar el #1 del Billboard Hot 100 en febrero de 1983."
        }
    ],
    "back in black": [
        {
            "p1_hook": "Nacida tras el golpe más duro del grupo.",
            "p2_anecdote": "Tras perder a Bon Scott en 1980, los Young viajaron a Bahamas con Brian Johnson y una campana de bronce para honrarlo.",
            "p3_resolution": "Su respuesta fue un rugido eterno de hard rock.",
            "historical_info": "Homenaje póstumo a Bon Scott en Compass Point, Bahamas (1980), debutando Brian Johnson junto al productor Mutt Lange."
        },
        {
            "p1_hook": "Seis semanas frenéticas que hicieron historia.",
            "p2_anecdote": "En abril de 1980 junto a Mutt Lange, AC/DC canalizó el duelo por Bon Scott en riffs monolíticos cargados de fuerza.",
            "p3_resolution": "El grupo volvió más sólido que nunca.",
            "historical_info": "Sesiones de abril-mayo de 1980 con Mutt Lange logrando el álbum más vendido del hard rock."
        }
    ],
    "detroit rock city": [
        {
            "p1_hook": "Una tragedia real llevada al estudio.",
            "p2_anecdote": "En 1976, Bob Ezrin sumó sonidos de autos y un choque para narrar el drama de un fanático fallecido rumbo al concierto.",
            "p3_resolution": "Desde entonces abre sus shows como un rito infaltable.",
            "historical_info": "Álbum Destroyer (1976), producción de Bob Ezrin con efectos reales de automóvil inspirada en un accidente verídico."
        },
        {
            "p1_hook": "Un duelo eléctrico al límite en Nueva York.",
            "p2_anecdote": "En Record Plant en 1976, Paul Stanley y Ace Frehley grabaron guitarras armonizadas en homenaje a la devoción por el vivo.",
            "p3_resolution": "Cada acorde conserva intacta aquella descarga.",
            "historical_info": "Record Plant Studios en Nueva York (1976) y armonías gemelas de Paul Stanley y Ace Frehley."
        }
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
        {
            "p1_hook": "Una obra maestra que subió desde una cabaña galesa hasta el Olimpo del rock.",
            "p2_anecdote": "Aislados en Bron-Yr-Aur sin electricidad en 1970, Jimmy Page y Robert Plant concibieron una épica acústica que estalló en Londres con una Telecaster de 1959.",
            "p3_resolution": "Su solo en tres tomas marcó la historia para siempre.",
            "historical_info": "Álbum Led Zeppelin IV (1971); compuesta por Jimmy Page y Robert Plant en Bron-Yr-Aur (Gales); solo de guitarra grabado en Island Studios con Fender Telecaster de 1959."
        }
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
        {
            "p1_hook": "La obra maestra antibélica que cambió la historia del metal.",
            "p2_anecdote": "En 1988, inspirados en la novela Johnny Got His Gun de Dalton Trumbo, James Hetfield y Lars Ulrich retrataron la pesadilla de un soldado atrapado en su propio cuerpo. Fue además su primer videoclip oficial, sincronizando el doble bombo con el fuego de ametralladoras.",
            "p3_resolution": "Ese estallido final les dio su primer Grammy y redefinió el metal.",
            "historical_info": "Álbum ...And Justice for All (1988); escrita por James Hetfield y Lars Ulrich; inspirada en la novela Johnny Got His Gun (1939) de Dalton Trumbo; primer videoclip oficial de Metallica y ganadora del primer Grammy a Mejor Interpretación de Metal."
        }
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
        {
            "p1_hook": "Una noche de fiebre y sedantes en Filadelfia inspiró esta canción.",
            "p2_anecdote": "En 1977, Roger Waters sufrió fuertes dolores estomacales antes de un concierto y un médico le inyectó un tranquilizante para salir al escenario. Años después plasmó aquella desconexión física sobre una maqueta que David Gilmour había descartado de su disco solista.",
            "p3_resolution": "De esa tensión creativa nació uno de los solos de guitarra más recordados de The Wall.",
            "historical_info": "Concierto de Pink Floyd en el Spectrum de Filadelfia (29 de junio de 1977), letra de Roger Waters y música original de David Gilmour para The Wall (1979)."
        },
        {
            "p1_hook": "Dos visiones opuestas chocaron hasta encontrar un equilibrio irrepetible.",
            "p2_anecdote": "Durante la grabación de The Wall en 1979, Roger Waters prefería la versión orquestal de Michael Kamen mientras David Gilmour defendía un pulso más crudo. La mezcla final combinó ambas texturas y culminó con el célebre solo final de Gilmour.",
            "p3_resolution": "Ese choque en el estudio dejó una de las cumbres emocionales de Pink Floyd.",
            "historical_info": "Sesiones de The Wall (1979); arreglos orquestales de Michael Kamen, tensión creativa entre Roger Waters y David Gilmour y solo final de David Gilmour."
        }
    ],
    "subdivisions": [
        {
            "p1_hook": "El refugio sonoro de los espíritus independientes.",
            "p2_anecdote": "En 1982, Neil Peart retrató la presión de los suburbios norteamericanos sobre los jóvenes por encajar o quedar marginados. Geddy Lee tomó el mando con su sintetizador Oberheim y el locutor Mark Dailey aportó su cavernosa voz pronunciando el título.",
            "p3_resolution": "Ese giro electrónico marcó una nueva era para el trío canadiense.",
            "historical_info": "Álbum Signals (1982); letra de Neil Peart, música de Geddy Lee y Alex Lifeson; voz hablada del locutor canadiense Mark Dailey; grabada en Le Studio (Morin-Heights, Quebec)."
        }
    ],
    "forever young": [
        {
            "p1_hook": "Un himno de juventud nacido frente al Muro.",
            "p2_anecdote": "En Berlín Occidental durante 1984, Marian Gold grabó una pista bailable rápida hasta que el estudio bajó el tempo por completo.",
            "p3_resolution": "Aquel cambio inesperado la volvió eterna.",
            "historical_info": "Álbum Forever Young (1984); grabada en Berlín Occidental por Alphaville bajo el miedo nuclear de la Guerra Fría."
        }
    ],
    "help": [
        (
            "En 1965, abrumado por el frenesí agobiante de la Beatlemanía, John Lennon escribió esta confesión directa como un pedido sincero de auxilio emocional. "
            "Aunque la banda la vistió con un ritmo acelerado de rock and roll, Lennon siempre la consideró una de sus páginas más honestas."
        )
    ],
    "hysteria": [
        {
            "p1_hook": "Una canción forjada en pura perseverancia.",
            "p2_anecdote": "Marcada por el accidente en que Rick Allen perdió su brazo izquierdo y aprendió a tocar con pedales electrónicos, Phil Collen tejió los acordes cristalinos con Mutt Lange.",
            "p3_resolution": "El título reflejó la emoción imparable de aquel regreso.",
            "historical_info": "Álbum Hysteria (1987), recuperación de Rick Allen con batería electrónica Simmons/pedales, producción de Robert John 'Mutt' Lange y guitarras de Phil Collen."
        }
    ],
    "radio ga ga": [
        {
            "p1_hook": "Una frase infantil que conquistó estadios enteros.",
            "p2_anecdote": "En 1983, el baterista Roger Taylor escuchó a su hijo pequeño decir 'radio ca-ca' al oír la radio y la convirtió en un homenaje frente al auge de MTV.",
            "p3_resolution": "Su coro de palmas sincronizadas hizo historia en Live Aid.",
            "historical_info": "Álbum The Works (1984); escrita por Roger Taylor a partir de una frase de su hijo Felix; icónica presentación en Live Aid Wembley (1985)."
        }
    ],
    "dream warriors": [
        {
            "p1_hook": "Un himno de metal nacido directo de las pesadillas del cine.",
            "p2_anecdote": "En 1987, George Lynch y Jeff Pilson compusieron este tema para Pesadilla en la Calle del Infierno 3, sumando a Freddy Krueger en su célebre videoclip.",
            "p3_resolution": "La alianza con el cine llevó al grupo a lo más alto de MTV.",
            "historical_info": "Álbum Back for the Attack (1987) y banda sonora de A Nightmare on Elm Street 3: Dream Warriors (1987) con Robert Englund en el video."
        }
    ],
    "heartbeat city": [
        {
            "p1_hook": "El pulso electrónico que definió una época dorada.",
            "p2_anecdote": "En 1984, Ric Ocasek grabó en Londres junto al productor Mutt Lange mezclando sintetizadores Fairlight y cajas de ritmos en una atmósfera nocturna impecable.",
            "p3_resolution": "El tema dio nombre al disco más ambicioso de la banda.",
            "historical_info": "Álbum Heartbeat City (1984), escrita por Ric Ocasek y producida por Mutt Lange en Battery Studios de Londres; interpretada en Live Aid (1985)."
        }
    ],
    "ordinary world": [
        {
            "p1_hook": "El renacimiento más emotivo de los años noventa.",
            "p2_anecdote": "En 1993, Simon Le Bon escribió estos versos en duelo por la muerte de su amigo David Miles, impulsando el inesperado regreso del grupo al top tres mundial.",
            "p3_resolution": "Su mensaje de resiliencia les valió el prestigioso premio Ivor Novello.",
            "historical_info": "Álbum Duran Duran / The Wedding Album (1993); letra de Simon Le Bon dedicada a su amigo David Miles; ganadora del premio Ivor Novello."
        }
    ],
    "the number of the beast": [
        {
            "p1_hook": "Una pesadilla convertida en leyenda del metal.",
            "p2_anecdote": "Tras soñar con La Profecía en 1982, Steve Harris compuso este himno mientras Martin Birch exigía tomas extenuantes a Bruce Dickinson.",
            "p3_resolution": "Aquel grito de furia pura definió la historia del metal.",
            "historical_info": "Álbum The Number of the Beast (1982); compuesta por Steve Harris tras ver Damien: Omen II; grabada por Martin Birch en Battery Studios."
        }
    ],
    "number of the beast": [
        {
            "p1_hook": "Una pesadilla convertida en leyenda del metal.",
            "p2_anecdote": "Tras soñar con La Profecía en 1982, Steve Harris compuso este himno mientras Martin Birch exigía tomas extenuantes a Bruce Dickinson.",
            "p3_resolution": "Aquel grito de furia pura definió la historia del metal.",
            "historical_info": "Álbum The Number of the Beast (1982); compuesta por Steve Harris tras ver Damien: Omen II; grabada por Martin Birch en Battery Studios."
        }
    ],
    "livin' on a prayer": [
        {
            "p1_hook": "Un himno obrero que casi queda descartado.",
            "p2_anecdote": "En 1986, Jon Bon Jovi dudaba de la maqueta original, pero Richie Sambora sumó su legendario talk box y creó a Tommy y Gina.",
            "p3_resolution": "Aquel giro en el estudio los llevó a la cima mundial.",
            "historical_info": "Álbum Slippery When Wet (1986); compuesta por Jon Bon Jovi, Richie Sambora y Desmond Child; guitarra con talk box de Sambora."
        }
    ],
    "living on a prayer": [
        {
            "p1_hook": "Un himno obrero que casi queda descartado.",
            "p2_anecdote": "En 1986, Jon Bon Jovi dudaba de la maqueta original, pero Richie Sambora sumó su legendario talk box y creó a Tommy y Gina.",
            "p3_resolution": "Aquel giro en el estudio los llevó a la cima mundial.",
            "historical_info": "Álbum Slippery When Wet (1986); compuesta por Jon Bon Jovi, Richie Sambora y Desmond Child; guitarra con talk box de Sambora."
        }
    ],
    "nobody's fool": [
        {
            "p1_hook": "La balada que transformó la historia del grupo.",
            "p2_anecdote": "Descubiertos por Jon Bon Jovi en Filadelfia, Tom Keifer grabó en 1986 esta confesión desgarradora con guitarras acústicas y un crescendo eléctrico inolvidable.",
            "p3_resolution": "Aquel himno impulsó a Night Songs al triple platino.",
            "historical_info": "Álbum Night Songs (1986); escrita por Tom Keifer; producida por Andy Johns tras el descubrimiento del grupo por Jon Bon Jovi en 1985."
        }
    ],
    "nobodys fool": [
        {
            "p1_hook": "La balada que transformó la historia del grupo.",
            "p2_anecdote": "Descubiertos por Jon Bon Jovi en Filadelfia, Tom Keifer grabó en 1986 esta confesión desgarradora con guitarras acústicas y un crescendo eléctrico inolvidable.",
            "p3_resolution": "Aquel himno impulsó a Night Songs al triple platino.",
            "historical_info": "Álbum Night Songs (1986); escrita por Tom Keifer; producida por Andy Johns tras el descubrimiento del grupo por Jon Bon Jovi en 1985."
        }
    ],
    "high hopes": [
        {
            "p1_hook": "Un adiós nostálgico cargado de memoria.",
            "p2_anecdote": "En 1994, David Gilmour y Polly Samson evocaron su juventud en Cambridge sobre el río Támesis, coronada por su emotivo solo de lap steel.",
            "p3_resolution": "Las campanas finales sellaron la última gran obra de estudio.",
            "historical_info": "Álbum The Division Bell (1994); escrita por David Gilmour y Polly Samson; grabada en el estudio flotante Astoria."
        }
    ],
    "18 and life": [
        {
            "p1_hook": "Una noticia real convertida en drama de rock.",
            "p2_anecdote": "En 1989, Dave Sabo leyó en un diario sobre un joven condenado a cadena perpetua y compuso con Rachel Bolan este relato para Sebastian Bach.",
            "p3_resolution": "Su fuerza trágica llevó el debut al multiplatino.",
            "historical_info": "Álbum Skid Row (1989); escrita por Dave 'Snake' Sabo y Rachel Bolan; producida por Michael Wagener."
        }
    ],
    "dr. feelgood": [
        {
            "p1_hook": "El rugido que marcó su renacimiento total.",
            "p2_anecdote": "Ya sobrios en 1989, Nikki Sixx y Mick Mars grabaron con Bob Rock esta cruda historia sobre los excesos de Los Ángeles en Vancouver.",
            "p3_resolution": "Aquel golpe de poder les dio su primer número uno.",
            "historical_info": "Álbum Dr. Feelgood (1989); escrita por Nikki Sixx y Mick Mars; producida por Bob Rock en Little Mountain Sound."
        }
    ],
    "life goes on": [
        {
            "p1_hook": "La balada más íntima nacida del duelo.",
            "p2_anecdote": "Para Flesh & Blood en 1990, Bret Michaels escribió este adiós a un amigo cercano, coronado por un emotivo solo de C.C. DeVille.",
            "p3_resolution": "Su honestidad conmovió a millones más allá del glam.",
            "historical_info": "Álbum Flesh & Blood (1990); escrita por Bret Michaels, C.C. DeVille, Bobby Dall y Rikki Rockett; producida por Bruce Fairbairn."
        }
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
    ],
    "shout": [
        {
            "p1_hook": "Un grito de protesta nacido en la sala.",
            "p2_anecdote": "En 1984, Roland Orzabal la compuso en su pequeño estudio casero inspirado en la terapia primaria y la protesta política de la Guerra Fría.",
            "p3_resolution": "Su coro masivo conquistó el número uno mundial.",
            "historical_info": "Álbum Songs from the Big Chair (1985); escrita por Roland Orzabal e Ian Stanley; inspirada en la terapia primaria de Arthur Janov."
        }
    ],
    "drive": [
        {
            "p1_hook": "La balada más conmovedora de su carrera.",
            "p2_anecdote": "En 1984, Benjamin Orr cantó esta pieza escrita por Ric Ocasek para Heartbeat City, que luego emocionó al mundo durante Live Aid.",
            "p3_resolution": "La voz de Orr la convirtió en un clásico inmortal.",
            "historical_info": "Álbum Heartbeat City (1984); escrita por Ric Ocasek, cantada por Benjamin Orr y producida por Mutt Lange."
        }
    ],
    "hold the line": [
        {
            "p1_hook": "El debut explosivo de seis maestros de estudio.",
            "p2_anecdote": "En 1978, David Paich escribió este riff de piano en su casa antes de que Bobby Kimball y Steve Lukather lo grabaran para su primer disco.",
            "p3_resolution": "Ese arranque arrollador los lanzó directo a la fama.",
            "historical_info": "Álbum Toto (1978); escrita por David Paich, voz principal de Bobby Kimball y guitarra de Steve Lukather."
        }
    ],
    "money for nothing": [
        {
            "p1_hook": "Una conversación ajena convertida en himno.",
            "p2_anecdote": "En una tienda de electrodomésticos en Nueva York, Mark Knopfler anotó las quejas de un repartidor viendo MTV y sumó la voz de Sting.",
            "p3_resolution": "Su riff de Les Paul marcó la historia del rock.",
            "historical_info": "Álbum Brothers in Arms (1985); escrita por Mark Knopfler y Sting; grabada en Montserrat."
        }
    ],
    "urgent": [
        {
            "p1_hook": "Un ritmo urgente impulsado por un saxofón legendario.",
            "p2_anecdote": "En 1981, en Nueva York, Mick Jones contrató al veterano de Motown Junior Walker tras escucharlo en un club, grabando su solo en pocas tomas.",
            "p3_resolution": "Aquel estallido de saxo convirtió al tema en un éxito arrollador.",
            "historical_info": "Álbum 4 (1981); compuesta por Mick Jones; producido por Mutt Lange; solo de saxofón por Junior Walker."
        }
    ],
    "eye of the tiger": [
        {
            "p1_hook": "El himno definitivo de la perseverancia en el ring.",
            "p2_anecdote": "En 1982, Sylvester Stallone les pidió una canción para Rocky Tres; Jim Peterik y Frankie Sullivan sincronizaron los golpes del riff con los puñetazos de la película.",
            "p3_resolution": "Esa energía implacable conquistó la cima de los rankings mundiales.",
            "historical_info": "Álbum Eye of the Tiger (1982); compuesta por Frankie Sullivan y Jim Peterik para la película Rocky III a petición de Sylvester Stallone."
        }
    ],
    "dont lose my number": [
        {
            "p1_hook": "Un ritmo trepidante nacido de la improvisación en el piano.",
            "p2_anecdote": "En 1985, Phil Collins admitió que no sabía sobre qué trataba la letra, así que grabó su videoclip parodiando películas famosas y a The Police.",
            "p3_resolution": "Su pegada rítmica lo consagró en las radios de todo el planeta.",
            "historical_info": "Álbum No Jacket Required (1985); producida por Phil Collins y Hugh Padgham; videoclip dirigido por Jim Yukich."
        }
    ],
    "pet sematary": [
        {
            "p1_hook": "Punk rock nacido de una pesadilla literaria en Maine.",
            "p2_anecdote": "En 1989, el escritor Stephen King invitó a la banda a su casa y le dio a Dee Dee su novela; Dee Dee bajó al sótano y escribió la letra en una hora.",
            "p3_resolution": "La canción fue el mayor éxito radial de los Ramones en los ochenta.",
            "historical_info": "Álbum Brain Drain (1989); escrita por Dee Dee Ramone y Daniel Rey para la adaptación de Stephen King."
        }
    ],
    "dreams": [
        {
            "p1_hook": "La magia de diez minutos que definió a Rumours.",
            "p2_anecdote": "En 1976 en Sausalito, Stevie Nicks se apartó al estudio de Sly Stone y compuso Dreams al piano en apenas diez minutos en medio de las tensiones del grupo.",
            "p3_resolution": "Fue el único número uno de Fleetwood Mac en el Billboard Hot 100.",
            "historical_info": "Álbum Rumours (1977); escrita por Stevie Nicks; grabada en Record Plant (Sausalito, California)."
        }
    ],
    "paradise city": [
        {
            "p1_hook": "El himno nacido en una furgoneta rumbo a casa.",
            "p2_anecdote": "En 1986, tras tocar en San Francisco, viajaban agotados en la parte trasera de su furgoneta rentada tocando guitarras acústicas. Slash lanzó el riff inicial y Axl Rose empezó a improvisar sobre escapar hacia la ciudad del paraíso, votando juntos por mantener el famoso estribillo.",
            "p3_resolution": "Su explosión final definió Appetite for Destruction.",
            "historical_info": "Álbum Appetite for Destruction (1987); escrita en 1986 en la parte trasera de una furgoneta regresando de San Francisco a Los Ángeles."
        }
    ],
    "van halen::dreams": [
        {
            "p1_hook": "El vuelo sinfónico que inauguró una nueva era.",
            "p2_anecdote": "En 1986, con Sammy Hagar recién llegado a la banda, Eddie Van Halen compuso la melodía al teclado en su estudio cinco mil ciento cincuenta y Hagar escribió la letra inspirado en la sensación de alcanzar lo imposible, acompañando luego a los Blue Angels de la Marina en su famoso videoclip.",
            "p3_resolution": "Sus agudos y sintetizadores llevaron a Van Halen a otro nivel.",
            "historical_info": "Álbum 5150 (1986); compuesta por Eddie Van Halen y Sammy Hagar; grabada en 5150 Studios con teclados Oberheim."
        }
    ],
    "is this love": [
        {
            "p1_hook": "Una balada pensada originalmente para otra voz legendaria.",
            "p2_anecdote": "En 1986, durante unas vacaciones en el sur de Francia, David Coverdale y el guitarrista John Sykes compusieron este tema pensando en ofrecerlo a Tina Turner. Al escuchar la magia de sus guitarras y el teclado atmosférico, su discográfica insistió en guardarlo para Whitesnake.",
            "p3_resolution": "Se convirtió en el mayor clásico romántico de la banda.",
            "historical_info": "Álbum Whitesnake (1987); escrita por David Coverdale y John Sykes en el sur de Francia."
        }
    ],
    "november rain": [
        {
            "p1_hook": "Axl Rose guardó esta melodía en su piano casi una década antes de grabarla.",
            "p2_anecdote": "Desde 1983 la tocaba en cada piano que encontraba, pero el grupo dudaba en llevar una balada sinfónica al hard rock. En 1991, con una orquesta sintetizada y el solo épico de Slash, se volvió la canción más larga en entrar al Top 10 de Billboard.",
            "p3_resolution": "Su clímax dramático la consagró como la balada definitiva de los noventa.",
            "historical_info": "Álbum Use Your Illusion I (1991); escrita por Axl Rose desde 1983; 8:57 minutos, la canción más larga en alcanzar el Top 10 del Billboard Hot 100."
        }
    ],
    "tratame suavemente": [
        {
            "p1_hook": "Uno de los primeros grandes himnos de Soda Stereo no fue escrito por Gustavo Cerati.",
            "p2_anecdote": "La compuso Daniel Melero, líder de Los Encargados, quien se la cedió al trío para su disco debut de 1984 producido por Federico Moura en Buenos Aires.",
            "p3_resolution": "Aquella joya prestada se volvió indispensable en la historia del rock en español.",
            "historical_info": "Álbum Soda Stereo (1984); compuesta por Daniel Melero (Los Encargados); producida por Federico Moura (Virus) en Estudios CBS, Buenos Aires."
        }
    ]
}

# Metadatos verificables adicionales para canciones clásicas fuera del HTML inicial
SUPPLEMENTAL_VERIFIED_TRACKS = [
    {
        "song_title": "Subdivisions",
        "band_name": "Rush",
        "album": "Signals (1982)",
        "year": "1982",
        "cover": "img/albums/rush_1982_signals.jpg",
        "duration_sec": 338
    },
    {
        "song_title": "One",
        "band_name": "Metallica",
        "album": "...And Justice for All (1988)",
        "year": "1988",
        "cover": "img/albums/metallica_1988_and_justice_for_all.png",
        "duration_sec": 447
    },
    {
        "song_title": "Is This Love",
        "band_name": "Whitesnake",
        "album": "Whitesnake (1987)",
        "year": "1987",
        "cover": "img/albums/whitesnake_1987_whitesnake.jpg",
        "duration_sec": 285
    },
    {
        "song_title": "Dreams",
        "band_name": "Van Halen",
        "album": "5150 (1986)",
        "year": "1986",
        "cover": "img/albums/van_halen_1986_5150.jpg",
        "duration_sec": 294
    },
    {
        "song_title": "Paradise City",
        "band_name": "Guns N' Roses",
        "album": "Appetite for Destruction (1987)",
        "year": "1987",
        "cover": "img/albums/guns_n_roses_1987_appetite.png",
        "duration_sec": 406
    },
    {
        "song_title": "Urgent",
        "band_name": "Foreigner",
        "album": "4 (1981)",
        "year": "1981",
        "cover": "img/albums/foreigner_1981_4.jpg",
        "duration_sec": 271
    },
    {
        "song_title": "Eye of the Tiger",
        "band_name": "Survivor",
        "album": "Eye of the Tiger (1982)",
        "year": "1982",
        "cover": "img/albums/survivor_1982_eye_of_the_tiger.jpg",
        "duration_sec": 245
    },
    {
        "song_title": "Don't Lose My Number",
        "band_name": "Phil Collins",
        "album": "No Jacket Required (1985)",
        "year": "1985",
        "cover": "img/albums/phil_collins_1985_no_jacket_required.jpg",
        "duration_sec": 289
    },
    {
        "song_title": "Pet Sematary",
        "band_name": "Ramones",
        "album": "Brain Drain (1989)",
        "year": "1989",
        "cover": "img/albums/ramones_1989_brain_drain.jpg",
        "duration_sec": 210
    },
    {
        "song_title": "Dreams",
        "band_name": "Fleetwood Mac",
        "album": "Rumours (1977)",
        "year": "1977",
        "cover": "img/albums/fleetwood_mac_1977_rumours.jpg",
        "duration_sec": 257
    },
    {
        "song_title": "Shout",
        "band_name": "Tears for Fears",
        "album": "Songs from the Big Chair (1985)",
        "year": "1985",
        "cover": "img/albums/tff_1985_songs_from_the_big_chair.png",
        "duration_sec": 393
    },
    {
        "song_title": "Drive",
        "band_name": "The Cars",
        "album": "Heartbeat City (1984)",
        "year": "1984",
        "cover": "img/albums/the_cars_1984_heartbeat_city.jpg",
        "duration_sec": 235
    },
    {
        "song_title": "Hold the Line",
        "band_name": "Toto",
        "album": "Toto (1978)",
        "year": "1978",
        "cover": "img/albums/toto_1978_toto.png",
        "duration_sec": 236
    },
    {
        "song_title": "Forever Young",
        "band_name": "Alphaville",
        "album": "Forever Young (1984)",
        "year": "1984",
        "cover": "img/albums/alphaville_1984_forever_young.png",
        "duration_sec": 227
    },
    {
        "song_title": "Money for Nothing",
        "band_name": "Dire Straits",
        "album": "Brothers in Arms (1985)",
        "year": "1985",
        "cover": "img/albums/dire_straits_1985_money_for_nothing.jpg",
        "duration_sec": 248
    },
    {
        "song_title": "18 and Life",
        "band_name": "Skid Row",
        "album": "Skid Row (1989)",
        "year": "1989",
        "cover": "img/albums/skid_row_1989_skid_row.jpg",
        "duration_sec": 233
    },
    {
        "song_title": "Dr. Feelgood",
        "band_name": "Mötley Crüe",
        "album": "Dr. Feelgood (1989)",
        "year": "1989",
        "cover": "img/albums/motley_crue_1989_feelgood.png",
        "duration_sec": 290
    },
    {
        "song_title": "Life Goes On",
        "band_name": "Poison",
        "album": "Flesh & Blood (1990)",
        "year": "1990",
        "cover": "img/albums/poison_1990_flesh_and_blood.jpg",
        "duration_sec": 288
    },
    {
        "song_title": "High Hopes",
        "band_name": "Pink Floyd",
        "album": "The Division Bell (1994)",
        "year": "1994",
        "cover": "img/albums/pink_floyd_1994_the_division_bell.jpg",
        "duration_sec": 511
    },
    {
        "song_title": "Nobody's Fool",
        "band_name": "Cinderella",
        "album": "Night Songs (1986)",
        "year": "1986",
        "cover": "img/albums/cinderella_1986_night_songs.jpg",
        "duration_sec": 289
    },
    {
        "song_title": "Livin' on a Prayer",
        "band_name": "Bon Jovi",
        "album": "Slippery When Wet (1986)",
        "year": "1986",
        "cover": "img/albums/bon_jovi_1986_slippery_when_wet.jpg",
        "duration_sec": 249
    },
    {
        "song_title": "The Number of the Beast",
        "band_name": "Iron Maiden",
        "album": "The Number of the Beast (1982)",
        "year": "1982",
        "cover": "img/albums/iron_maiden_the_number_of_the_beast_2015_remaste.jpg",
        "duration_sec": 291
    },
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
    },
    {
        "song_title": "Radio Ga Ga",
        "band_name": "Queen",
        "album": "The Works (1984)",
        "year": "1984",
        "cover": "img/albums/queen_1984_the_works.jpg",
        "duration_sec": 348
    },
    {
        "song_title": "Dream Warriors",
        "band_name": "Dokken",
        "album": "Back for the Attack (1987)",
        "year": "1987",
        "cover": "img/albums/dokken_1987_back_for_the_attack.jpg",
        "duration_sec": 282
    },
    {
        "song_title": "Heartbeat City",
        "band_name": "The Cars",
        "album": "Heartbeat City (1984)",
        "year": "1984",
        "cover": "img/albums/the_cars_1984_heartbeat_city.jpg",
        "duration_sec": 271
    },
    {
        "song_title": "Ordinary World",
        "band_name": "Duran Duran",
        "album": "Duran Duran (The Wedding Album) (1993)",
        "year": "1993",
        "cover": "img/albums/duran_duran_1993_wedding_album.jpg",
        "duration_sec": 339
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

def fetch_real_album_cover(band_name, song_title, album_name="", year=""):
    """
    Descarga la carátula oficial del álbum desde iTunes Search API (600x600)
    y la guarda en img/albums/ para evitar usar portadas genéricas.
    Retorna (rel_cover_path, detected_album, detected_year, detected_duration_sec).
    """
    try:
        term = f"{band_name} {song_title}".strip()
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(term)}&entity=song&limit=10"
        req = urllib.request.Request(url, headers={"User-Agent": "RockRadio/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results") or []
        if not results:
            return None, album_name, year, None

        b_norm = normalize_text_key(band_name)
        s_norm = normalize_text_key(song_title)
        a_norm = normalize_text_key(re.sub(r"\(\d{4}\)", "", album_name or ""))

        def score_hit(r):
            sc = 0
            r_b = normalize_text_key(r.get("artistName", ""))
            r_s = normalize_text_key(r.get("trackName", ""))
            r_a = normalize_text_key(r.get("collectionName", ""))
            if b_norm and (r_b == b_norm or b_norm in r_b or r_b in b_norm):
                sc += 50
            if s_norm and (r_s == s_norm or s_norm in r_s):
                sc += 40
            if a_norm and a_norm in r_a:
                sc += 30
            if any(w in r_a for w in ("greatest hits", "best of", "essential", "anthology", "live", "collection")):
                sc -= 15
            return sc

        results.sort(key=score_hit, reverse=True)
        hit = results[0]
        art = hit.get("artworkUrl100") or ""
        if not art:
            return None, album_name, year, None
        art_600 = art.replace("100x100bb", "600x600bb")

        det_album = album_name or hit.get("collectionName", "")
        det_year = year or (hit.get("releaseDate", "")[:4] if hit.get("releaseDate") else "")
        if det_album and det_year and det_year not in det_album:
            det_album = f"{det_album} ({det_year})"
        det_dur = int(round((hit.get("trackTimeMillis") or 0) / 1000)) or None

        albums_dir = os.path.join(PROJECT_ROOT, "img", "albums")
        os.makedirs(albums_dir, exist_ok=True)
        album_slug = make_slug(band_name, re.sub(r"\(\d{4}\)", "", det_album or song_title))
        fname = f"{album_slug}.jpg"
        out_path = os.path.join(albums_dir, fname)
        if not os.path.exists(out_path) or os.path.getsize(out_path) < 5000:
            img_req = urllib.request.Request(art_600, headers={"User-Agent": "RockRadio/1.0"})
            with urllib.request.urlopen(img_req, timeout=15) as ir:
                img_bytes = ir.read()
            if len(img_bytes) > 5000:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            return f"img/albums/{fname}", det_album, det_year, det_dur
    except Exception as e:
        print(f"⚠️ No se pudo descargar carátula real para {band_name} - {song_title}: {e}", flush=True)
    return None, album_name, year, None

def resolve_song_metadata(song_query, band_query=None):
    """
    Identifica canción y artista usando metadatos disponibles.
    Solicita aclaración únicamente cuando hay ambigüedad real o múltiples coincidencias sin artista.
    Nunca inventa artistas ni títulos.
    """
    catalog = load_project_catalog_metadata()
    s_norm = normalize_text_key(song_query)
    b_norm = normalize_text_key(band_query) if band_query else ""
    band_aliases = {
        "deff leppard": "def leppard",
        "def lepard": "def leppard",
        "tears for fear": "tears for fears",
        "ac dc": "ac/dc",
        "bonjovi": "bon jovi"
    }
    song_aliases = {
        "living on a prayer": "livin on a prayer",
        "dont loose my number": "don t lose my number",
        "dont lose my number": "don t lose my number",
        "don t loose my number": "don t lose my number",
        "starway yo heaven": "stairway to heaven",
        "starway to heaven": "stairway to heaven"
    }
    if b_norm in band_aliases:
        b_norm = normalize_text_key(band_aliases[b_norm])
    if s_norm in song_aliases:
        s_norm = normalize_text_key(song_aliases[s_norm])

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
        cov = best.get("cover") or ""
        if not cov or "kiss_1976_destroyer" in cov or not os.path.exists(os.path.join(PROJECT_ROOT, cov)):
            real_cov, det_alb, det_yr, det_dur = fetch_real_album_cover(
                best["band_name"], best["song_title"], best.get("album", ""), best.get("year", "")
            )
            if real_cov:
                best["cover"] = real_cov
            if det_alb and not best.get("album"):
                best["album"] = det_alb
            if det_yr and not best.get("year"):
                best["year"] = det_yr
            if det_dur and not best.get("duration_sec"):
                best["duration_sec"] = det_dur
        return {"resolved": True, "ambiguous": False, "metadata": best}

    # If both song and band were explicitly provided by user (e.g. a new song not yet in static catalog),
    # construct clean metadata preserving user-specified names (never inventing unknown band/song).
    if song_query and band_query:
        clean_song = song_query.strip()
        clean_band = band_query.strip()
        real_cov, det_alb, det_yr, det_dur = fetch_real_album_cover(clean_band, clean_song)
        return {
            "resolved": True,
            "ambiguous": False,
            "metadata": {
                "key": make_story_key(clean_band, clean_song),
                "song_title": clean_song,
                "band_name": clean_band,
                "album": det_alb or "",
                "year": det_yr or "",
                "cover": real_cov or "img/albums/kiss_1976_destroyer.png",
                "duration_sec": det_dur or 240,
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

    # Check story generation ("Generar historia de...", "Agrega la historia de...", etc.)
    gen_m = re.match(
        r"^(?:por favor\s+)?(?:genera[r]?|agrega[r]?|añade|añadir|publica[r]?|crea[r]?|haz|quiero|dame|escribe|narra)\s+(?:una\s+|la\s+|el\s+)?(?:nueva\s+)?historia\s+(?:de\s+|de\s+la\s+cancion\s+|sobre\s+|para\s+)?(.+)$",
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

def find_curated_story_entry(song_title, band_name=""):
    """
    Busca la historia curada para una canción, priorizando coincidencia por banda::canción,
    luego coincidencias exactas y límites de palabra para evitar colisiones erróneas.
    """
    clean_key = normalize_text_key(song_title)
    clean_band = normalize_text_key(band_name) if band_name else ""
    if clean_band:
        composed = f"{clean_band}::{clean_key}"
        for k, v in MASTER_CURATED_STORIES.items():
            if normalize_text_key(k) == composed or k.lower().strip() == composed:
                return v if isinstance(v, list) else [v]
    no_space_clean = clean_key.replace(" ", "")
    # 1. Coincidencia exacta o sin espacios (para manejar 'don t' vs 'dont')
    for k, v in MASTER_CURATED_STORIES.items():
        if "::" in k:
            continue
        nk = normalize_text_key(k)
        if nk == clean_key or (len(no_space_clean) >= 6 and nk.replace(" ", "") == no_space_clean):
            return v if isinstance(v, list) else [v]
    # 2. Coincidencia con límites de palabra (whole word)
    padded_clean = f" {clean_key} "
    for k, v in MASTER_CURATED_STORIES.items():
        if "::" in k:
            continue
        nk = normalize_text_key(k)
        if len(nk) >= 4 and f" {nk} " in padded_clean:
            return v if isinstance(v, list) else [v]
        if len(clean_key) >= 6 and f" {clean_key} " in f" {nk} ":
            return v if isinstance(v, list) else [v]
    return None

def get_master_fred_script(song_title, band_name, album_name="", year="", angle=1, opening_text=None):
    """
    Construye el guion maestro estructurado en 3 párrafos claros y concisos
    (<= 45s totales considerando 5s intro + dos pausas musicales de 3s + transición final).
    """
    angles_list = find_curated_story_entry(song_title)

    p1_hook = ""
    p2_anecdote = ""
    p3_resolution = ""
    historical_info = ""

    if angles_list:
        idx = (max(1, int(angle)) - 1) % len(angles_list)
        entry = angles_list[idx]
        if isinstance(entry, dict):
            p1_hook = entry.get("p1_hook", "").strip()
            p2_anecdote = entry.get("p2_anecdote", "").strip()
            p3_resolution = entry.get("p3_resolution", "").strip()
            historical_info = entry.get("historical_info", "").strip()
        else:
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', str(entry).strip()) if s.strip()]
            if len(sents) >= 2:
                p2_anecdote = " ".join(sents[:-1])
                p3_resolution = sents[-1]
            else:
                p2_anecdote = str(entry).strip()
            historical_info = str(entry).strip()
    else:
        year_str = f"en {year}" if year else "en una etapa clave"
        album_str = f"para {album_name}" if album_name else "en el estudio"
        if angle % 3 == 1:
            p1_hook = "Una sesión eléctrica que marcó toda una época."
            p2_anecdote = f"Grabada sobre cinta analógica {year_str} {album_str}, {band_name} buscó capturar toda su química en directo sin artificios."
            p3_resolution = "Ese impulso honesto se convirtió en un clásico inolvidable."
        elif angle % 3 == 2:
            p1_hook = "Un riff nacido de pura intensidad en cabina."
            p2_anecdote = f"Impulsada {year_str} {album_str}, {band_name} apostó por la pegada rítmica y una interpretación sin concesiones."
            p3_resolution = "Su fuerza conquistó de inmediato los diales del mundo."
        else:
            p1_hook = "La historia detrás de una toma definitiva."
            p2_anecdote = f"Construida {year_str} {album_str}, {band_name} pulió cada compás hasta alcanzar una identidad sonora arrolladora."
            p3_resolution = "Hoy sigue resonando con la misma energía original."
        historical_info = f"Metadatos del proyecto: {band_name} — {song_title} ({album_name or 'Clásico'}, {year or 'Rock'})."

    if not opening_text:
        _, opening_text = select_dynamic_opening(song_title, band_name, year)

    paragraph_1 = f"{opening_text} {p1_hook}".strip() if p1_hook else opening_text
    paragraph_2 = p2_anecdote.strip()
    p3_closing = select_closing_line(song_title, band_name, angle - 1)
    paragraph_3 = f"{p3_resolution} {p3_closing}".strip() if p3_resolution else p3_closing
    full_script = " ".join([x for x in (paragraph_1, paragraph_2, paragraph_3) if x]).strip()

    return {
        "opening_text": opening_text,
        "p1_hook": p1_hook,
        "paragraph_1": paragraph_1,
        "paragraph_2": paragraph_2,
        "p3_resolution": p3_resolution,
        "p3_closing": p3_closing,
        "paragraph_3": paragraph_3,
        "historical_info": historical_info,
        "full_script": full_script
    }

def generate_ai_story_script(song_title, band_name, album_name="", year="", angle=1, exclude_opening_ids=None, force_opening_id=None, previous_story_summary=None):
    """
    Redacta la historia radial en exactamente 3 párrafos semánticos (<= 45s incluyendo 5s intro + dos pausas de 3s):
    - Párrafo 1: Apertura dinámica + contexto/gancho de curiosidad (sin adelantar la anécdota)
    - Párrafo 2: Desarrollo de la anécdota histórica verificable
    - Párrafo 3: Desenlace emocional + frase de cierre intensa
    """
    opening_id, apertura = select_dynamic_opening(
        song_title, band_name, year,
        exclude_ids=exclude_opening_ids,
        force_opening_id=force_opening_id
    )
    p3_closing = select_closing_line(song_title, band_name, angle - 1)

    curated_entries = find_curated_story_entry(song_title)
    has_curated = bool(curated_entries)
    curated_count = len(curated_entries) if curated_entries else 0

    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    p1_hook = None
    p2_anecdote = None
    p3_resolution = None
    historical_info = ""
    source = "curated_master"

    need_ai = (not has_curated) or (int(angle) > curated_count)
    if api_key and need_ai:
        try:
            system_prompt = (
                "Eres Fred, cronista y locutor experto de rock clásico en 'Rock Radio: De vuelta al pasado'. "
                "Escribes guiones radiales en 3 párrafos claros con hechos históricos reales y verificables. "
                "REGLA ESTRICTA DE VERACIDAD: Nunca inventes fechas, nombres ni anécdotas falsas."
            )
            avoid_note = f"\nEvita repetir el enfoque previo: {previous_story_summary}\n" if previous_story_summary else ""
            user_prompt = (
                f"Genera en JSON estricto los bloques narrativos para '{song_title}' de '{band_name}' "
                f"(Álbum: '{album_name or 'Clásico'}', Año: '{year or 'Época Clásica'}').\n"
                f"La apertura fija que irá antes de p1_hook es: \"{apertura}\"\n"
                f"El cierre fijo que irá después de p3_resolution es: \"{p3_closing}\"\n"
                f"{avoid_note}"
                "Devuelve ÚNICAMENTE un objeto JSON con estas 4 claves:\n"
                "{\n"
                '  "p1_hook": "1 frase breve de 5 a 8 palabras que despierte curiosidad sin adelantar la anécdota",\n'
                '  "p2_anecdote": "1 oración completa y vívida de 18 a 25 palabras con la anécdota real principal",\n'
                '  "p3_resolution": "1 frase emocional de 7 a 11 palabras con el desenlace que conecta con el cierre",\n'
                '  "historical_info": "Resumen breve del dato histórico verificado"\n'
                "}\n"
                "Sin etiquetas entre corchetes ni markdown."
            )
            payload = {
                "model": "gpt-4o-mini",
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 240
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                parsed = json.loads(resp_data["choices"][0]["message"]["content"])
                cand_hook = strip_vocal_tags(parsed.get("p1_hook", ""))
                cand_anec = strip_vocal_tags(parsed.get("p2_anecdote", ""))
                cand_res = strip_vocal_tags(parsed.get("p3_resolution", ""))
                if 10 <= len(cand_anec.split()) <= 32 and cand_res:
                    p1_hook = cand_hook
                    p2_anecdote = cand_anec
                    p3_resolution = cand_res
                    historical_info = strip_vocal_tags(parsed.get("historical_info", ""))
                    source = "openai_gpt_4o_mini"
        except Exception as e:
            print(f"⚠️ [ROCK RADIO AI] Usando catálogo curado por: {e}", flush=True)

    if not p2_anecdote:
        master = get_master_fred_script(song_title, band_name, album_name, year, angle, opening_text=apertura)
        p1_hook = master["p1_hook"]
        p2_anecdote = master["paragraph_2"]
        p3_resolution = master["p3_resolution"]
        historical_info = master["historical_info"]

    paragraph_1 = f"{apertura} {p1_hook}".strip() if p1_hook else apertura
    paragraph_2 = p2_anecdote.strip()
    paragraph_3 = f"{p3_resolution} {p3_closing}".strip() if p3_resolution else p3_closing
    full_script = " ".join([x for x in (paragraph_1, paragraph_2, paragraph_3) if x]).strip()
    total_words = len(full_script.split())

    return {
        "success": True,
        "opening_id": opening_id,
        "opening_text": apertura,
        "p1_hook": p1_hook or "",
        "paragraph_1": paragraph_1,
        "paragraph_2": paragraph_2,
        "p3_resolution": p3_resolution or "",
        "p3_closing": p3_closing,
        "paragraph_3": paragraph_3,
        "historical_info": historical_info,
        "apertura": paragraph_1,
        "desarrollo": paragraph_2,
        "cierre": paragraph_3,
        "full_script": full_script,
        "source": source,
        "words": total_words,
        "duration_est_sec": round(INTRO_MUSIC_SEC + (PAUSE_MUSIC_SEC * 2) + total_words / 2.25 + OUTRO_MUSIC_TAIL_SEC, 1)
    }

def condense_paragraph_text(text, song_title, band_name, role_label="anécdota", excess_sec=2.0):
    """
    Si el segmento supera los 45s (incluyendo intro de 5s y dos pausas de 3s), resume limpiamente
    el párrafo indicado conservando hechos reales y oraciones completas, sin acelerar ni cortar frases.
    """
    text = (text or "").strip()
    if not text:
        return ""
    words = text.split()
    if len(words) <= 10:
        return text

    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    target_words = max(10, int(len(words) - max(4, excess_sec * 2.2)))

    if api_key:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Resume textos de locución radial en español conservando hechos reales y una oración completa natural."},
                    {"role": "user", "content": f"Condensa este bloque ({role_label}) sobre '{song_title}' de {band_name} a máximo {target_words} palabras en 1 oración completa y natural:\n\n{text}"}
                ],
                "temperature": 0.25,
                "max_tokens": 110
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
                if 8 <= len(short.split()) < len(words):
                    if not short.endswith(('.', '!', '?')):
                        short += '.'
                    return short
        except Exception as e:
            print(f"⚠️ [CONDENSE] Fallo OpenAI al resumir {role_label}, aplicando compresión sintáctica limpia: {e}", flush=True)

    # Rule-based clean sentence/clause condensation (always leaves complete grammatical sentences)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sents) > 1:
        return sents[0]

    clauses = [c.strip() for c in text.split(",") if c.strip()]
    if len(clauses) >= 3:
        reduced = f"{clauses[0]}, {clauses[-1]}"
        if not reduced.endswith(('.', '!', '?')):
            reduced += "."
        return reduced
    if len(clauses) == 2 and len(words) > 16:
        # Keep the richer clause if complete enough
        candidate = clauses[1] if len(clauses[1].split()) >= len(clauses[0].split()) else clauses[0]
        if not candidate.endswith(('.', '!', '?')):
            candidate += "."
        return candidate
    return text

condense_anecdote_text = condense_paragraph_text

# ==============================================================================
# 7. DICCIONARIO FONÉTICO DE RESPALDO (PARA EDGE-TTS SI FALTAN CREDENCIALES)
# ==============================================================================
ENGLISH_PHONETICS = [
    (r'\bFred Rewind\b', 'Fred Riuáind'),
    (r'\bRock Radio\b', 'Rok Réidio'),
    (r'\bDJ Fredd?\b', 'Dí-yéi Fred'),
    (r'\bRush\b', 'Rásh'),
    (r'\bTom Sawyer\b', 'Tom Sóyer'),
    (r'\bTears for Fears\b', 'Tíars for Fíars'),
    (r'\bEverybody Wants to Rule the World\b', 'Évribadi Uónts tu Rul de Uérld'),
    (r'\bIron Maiden\b', 'Áiron Méiden'),
    (r'\bThe Number of the Beast\b', 'De Námber of de Bíst'),
    (r'\bNumber of the Beast\b', 'Námber of de Bíst'),
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
        p1 = sentences[0]
        if len(sentences) >= 4 and ("Rock Radio" in sentences[0] or "De vuelta al pasado" in sentences[0]) and len(sentences[0].split()) <= 8:
            p1 = f"{sentences[0]} {sentences[1]}"
            p3 = sentences[-1]
            p2 = " ".join(sentences[2:-1])
        else:
            p3 = sentences[-1]
            p2 = " ".join(sentences[1:-1])
        if p2:
            return p1, p2, p3, f"{p1} {p2} {p3}"

    res = generate_ai_story_script(song_title, band_name, year=year)
    return res["paragraph_1"], res["paragraph_2"], res["paragraph_3"], res["full_script"]

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

def _fish_audio_tts_sync(text, out_mp3_path, reference_id=DEFAULT_FISH_VOICE, model=DEFAULT_FISH_MODEL, temperature=None, top_p=None):
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
    if temperature is not None:
        payload["temperature"] = float(temperature)
    if top_p is not None:
        payload["top_p"] = float(top_p)
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

async def synthesize_fish_audio_tts(sem, text, out_mp3_path, reference_id=DEFAULT_FISH_VOICE, model=DEFAULT_FISH_MODEL, temperature=None, top_p=None):
    async with sem:
        await asyncio.to_thread(_fish_audio_tts_sync, text, out_mp3_path, reference_id, model, temperature, top_p)

async def synthesize_single_segment(text, out_mp3_path, use_fish=True, fish_voice=DEFAULT_FISH_VOICE, fish_model=DEFAULT_FISH_MODEL, is_closing=False, temperature=None, top_p=None):
    if use_fish:
        await asyncio.to_thread(_fish_audio_tts_sync, text, out_mp3_path, fish_voice, fish_model, temperature, top_p)
    else:
        if edge_tts is None:
            raise RuntimeError("edge_tts no está instalado y FISH_API_KEY no está disponible.")
        pitch = "+2Hz" if is_closing else "+0Hz"
        await edge_tts.Communicate(apply_english_phonetics(text), DEFAULT_VOICE, rate="+0%", pitch=pitch).save(out_mp3_path)
    return out_mp3_path

async def synthesize_segments(p1_text, p2_text, p3_text, tmp_prefix, temp_files, use_fish=True, fish_voice=DEFAULT_FISH_VOICE, fish_model=DEFAULT_FISH_MODEL, job_id=None, temperature=None, top_p=None):
    """
    Envía exactamente 3 solicitudes separadas a Fish Audio (paragraph_1, paragraph_2, paragraph_3)
    usando la misma voz (reference_id) y configuraciones consistentes.
    """
    p1_mp3 = f"{tmp_prefix}_p1.mp3"
    p2_mp3 = f"{tmp_prefix}_p2.mp3"
    p3_mp3 = f"{tmp_prefix}_p3.mp3"
    new_temps = [p1_mp3, p2_mp3, p3_mp3]
    temp_files.extend(new_temps)

    if job_id:
        with ACTIVE_JOBS_LOCK:
            if job_id in ACTIVE_JOBS:
                ACTIVE_JOBS[job_id]['temp_files'].update(new_temps)

    if use_fish:
        sem = asyncio.Semaphore(1)
        await synthesize_fish_audio_tts(sem, p1_text, p1_mp3, reference_id=fish_voice, model=fish_model, temperature=temperature, top_p=top_p)
        await synthesize_fish_audio_tts(sem, p2_text, p2_mp3, reference_id=fish_voice, model=fish_model, temperature=temperature, top_p=top_p)
        await synthesize_fish_audio_tts(sem, p3_text, p3_mp3, reference_id=fish_voice, model=fish_model, temperature=temperature, top_p=top_p)
    else:
        await synthesize_single_segment(p1_text, p1_mp3, use_fish=False, is_closing=False)
        await synthesize_single_segment(p2_text, p2_mp3, use_fish=False, is_closing=False)
        await synthesize_single_segment(p3_text, p3_mp3, use_fish=False, is_closing=True)

    return p1_mp3, p2_mp3, p3_mp3

def _get_wav_duration(wav_path):
    with wave.open(wav_path, "rb") as w:
        return w.getnframes() / float(w.getframerate())

def _make_silence_wav(duration_sec, out_wav_path, sample_rate=44100, channels=2):
    n_frames = max(1, int(round(duration_sec * sample_rate)))
    with wave.open(out_wav_path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00" * (n_frames * channels * 2))

def _concat_wavs(wav_paths, out_wav_path):
    with wave.open(wav_paths[0], "rb") as w0:
        params = w0.getparams()
    with wave.open(out_wav_path, "wb") as out_w:
        out_w.setparams(params)
        for p in wav_paths:
            with wave.open(p, "rb") as wi:
                out_w.writeframes(wi.readframes(wi.getnframes()))

def _apply_progressive_closing_ramp(in_wav, eq_wav, out_wav, p3_res_clean, p3_close_clean, boost_db=2.8):
    """
    Aplica un incremento progresivo y natural en Párrafo 3 (desenlace -> cierre emotivo)
    mediante rampa raised-cosine exacta por muestra + mezcla suave del realce de presencia (3.2 kHz),
    evitando saltos de volumen y conservando margen limpio antes del limitador final.
    """
    with wave.open(in_wav, "rb") as wi, wave.open(eq_wav, "rb") as we:
        params = wi.getparams()
        sr = wi.getframerate()
        ch = wi.getnchannels()
        n_frames = wi.getnframes()
        raw_in = array.array("h", wi.readframes(n_frames))
        raw_eq = array.array("h", we.readframes(we.getnframes()))

    n_pairs = min(len(raw_in), len(raw_eq)) // ch
    if n_pairs <= 0:
        shutil.copyfile(in_wav, out_wav)
        return 0.0

    # Localizar pausa natural entre el desenlace y el cierre icónico
    total_chars = max(1, len(p3_res_clean) + len(p3_close_clean) + 1)
    if p3_res_clean and len(p3_res_clean) >= 6:
        est_frac = len(p3_res_clean) / total_chars
        win = max(1, int(0.02 * sr))
        search_start = max(1, int((max(0.10, est_frac - 0.16)) * n_pairs))
        search_end = min(n_pairs - win - 1, int((min(0.84, est_frac + 0.16)) * n_pairs))
        best_frame = int(est_frac * n_pairs)
        min_energy = float("inf")
        for f_idx in range(search_start, max(search_start + 1, search_end), win):
            s0 = f_idx * ch
            s1 = min(len(raw_in), (f_idx + win) * ch)
            energy = sum(abs(raw_in[k]) for k in range(s0, s1))
            if energy < min_energy:
                min_energy = energy
                best_frame = f_idx
        ramp_start = max(0, best_frame - int(0.25 * sr))
        ramp_end = min(n_pairs - 1, best_frame + int(0.55 * sr))
        t_split_sec = round(best_frame / float(sr), 3)
    else:
        ramp_start = 0
        ramp_end = min(n_pairs - 1, int(0.80 * sr))
        t_split_sec = 0.0

    ramp_len = max(1, ramp_end - ramp_start)
    max_linear = 10.0 ** (boost_db / 20.0)
    out_arr = array.array("h", [0] * (n_pairs * ch))

    for i in range(n_pairs):
        if i <= ramp_start:
            smooth = 0.0
        elif i >= ramp_end:
            smooth = 1.0
        else:
            alpha = (i - ramp_start) / float(ramp_len)
            smooth = 0.5 * (1.0 - math.cos(math.pi * alpha))

        gain = 1.0 + (max_linear - 1.0) * smooth if smooth <= 0.0 else (10.0 ** ((boost_db * smooth) / 20.0))
        base_idx = i * ch
        for c in range(ch):
            idx = base_idx + c
            blended = raw_in[idx] * (1.0 - smooth) + raw_eq[idx] * smooth
            val = int(round(blended * gain))
            if val > 32760:
                val = 32760
            elif val < -32760:
                val = -32760
            out_arr[idx] = val

    with wave.open(out_wav, "wb") as wo:
        wo.setparams(params)
        wo.writeframes(out_arr.tobytes())

    return t_split_sec

def _process_paragraph_to_core_wav(in_mp3, out_wav, norm_gain_db=0.0):
    """
    Aplica la cadena vocal unificada y recorta únicamente silencio digital muerto (<-50dB)
    para preservar pausas musicales exactas de 3.0s entre párrafos.
    """
    gain_filter = f",volume={norm_gain_db:+.2f}dB" if abs(norm_gain_db) >= 0.05 else ""
    vocal_core = (
        "aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "highpass=f=80,"
        "equalizer=f=380:width_type=o:width=1.2:g=-1.5,"
        "equalizer=f=3000:width_type=o:width=1.1:g=2.0,"
        "deesser=i=0.25:m=0.5:f=0.5:s=o,"
        "acompressor=threshold=-20dB:ratio=3.2:attack=8:release=90:makeup=1.8,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB,"
        "areverse,silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB,areverse,"
        "afade=t=in:st=0:d=0.015,"
        f"areverse,afade=t=in:st=0:d=0.015,areverse{gain_filter}"
    )
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", in_mp3,
        "-af", vocal_core,
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        out_wav
    ], capture_output=True, check=True)

def master_radio_segment(p1_mp3, p2_mp3, p3_mp3, p3_res_clean, p3_close_clean, out_mp3_path, tmp_prefix, temp_files, bed_seek_sec=15.0):
    """
    Pipeline de masterización cinematográfica en 3 párrafos y mezcla continua:
    1. Procesa P1, P2 y P3 con la misma cadena vocal y normaliza su timbre/volumen base (~ -13.5 LUFS, +40% voz).
    2. Aplica aumento progresivo en P3 (+2.6 dB con rampa raised-cosine + presencia 3.2 kHz sobre el cierre).
    3. Ensambla pausas exactas de 3.000s entre P1->P2 y P2->P3 mediante WAV PCM de precisión por muestra.
    4. Mezcla sobre una única base musical continua (0:00 a fin) sin reinicios ni cortes:
       - 0:00–0:05 música sola al 100%
       - Lookahead sidechain ducking (150ms anticipado, attack=200ms, release=450ms, reducción ~12–18dB)
       - Recuperación progresiva durante las dos pausas de 3.0s y transición final suave
       - Limitador True Peak final a -0.8 dBTP
    """
    p1_core = f"{tmp_prefix}_p1_core.wav"
    p2_core = f"{tmp_prefix}_p2_core.wav"
    p3_core = f"{tmp_prefix}_p3_core.wav"
    p1_norm = f"{tmp_prefix}_p1_norm.wav"
    p2_norm = f"{tmp_prefix}_p2_norm.wav"
    p3_norm = f"{tmp_prefix}_p3_norm.wav"
    p3_eq = f"{tmp_prefix}_p3_eq.wav"
    p3_mast = f"{tmp_prefix}_p3_mast.wav"
    sil_pause_wav = f"{tmp_prefix}_sil_pause3s.wav"
    voice_master_wav = f"{tmp_prefix}_voice_m.wav"
    temp_files.extend([
        p1_core, p2_core, p3_core, p1_norm, p2_norm, p3_norm,
        p3_eq, p3_mast, sil_pause_wav, voice_master_wav
    ])

    _process_paragraph_to_core_wav(p1_mp3, p1_core, 0.0)
    _process_paragraph_to_core_wav(p2_mp3, p2_core, 0.0)
    _process_paragraph_to_core_wav(p3_mp3, p3_core, 0.0)

    # Igualar sonoridad base (LUFS) para coherencia de timbre entre los 3 segmentos (+40% volumen vocal)
    target_lufs = -13.5
    p1_lufs = get_integrated_lufs(p1_core)
    p2_lufs = get_integrated_lufs(p2_core)
    p3_base_lufs = get_integrated_lufs(p3_core)

    g1 = max(-4.0, min(13.0, target_lufs - p1_lufs))
    g2 = max(-4.0, min(13.0, target_lufs - p2_lufs))
    # Como P3 recibe un realce progresivo en el cierre, ajustamos su base ~0.8 dB abajo para mantener headroom limpio
    g3 = max(-4.0, min(12.0, target_lufs - p3_base_lufs - 0.8))

    _process_paragraph_to_core_wav(p1_mp3, p1_norm, g1)
    _process_paragraph_to_core_wav(p2_mp3, p2_norm, g2)
    _process_paragraph_to_core_wav(p3_mp3, p3_norm, g3)

    # Preparar copia con presencia @ 3.2 kHz para mezcla progresiva hacia el cierre
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", p3_norm,
        "-af", "equalizer=f=3200:width_type=o:width=1.0:g=1.4",
        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
        p3_eq
    ], capture_output=True, check=True)

    boost_db = 2.6
    t_split_p3 = _apply_progressive_closing_ramp(p3_norm, p3_eq, p3_mast, p3_res_clean, p3_close_clean, boost_db=boost_db)

    _make_silence_wav(PAUSE_MUSIC_SEC, sil_pause_wav)
    _concat_wavs([p1_norm, sil_pause_wav, p2_norm, sil_pause_wav, p3_mast], voice_master_wav)

    dur_p1 = _get_wav_duration(p1_norm)
    dur_p2 = _get_wav_duration(p2_norm)
    dur_p3 = _get_wav_duration(p3_mast)
    voice_dur = _get_wav_duration(voice_master_wav)

    tail_dur = min(OUTRO_MUSIC_TAIL_SEC, max(0.35, SAFE_TARGET_TOTAL_SEC - INTRO_MUSIC_SEC - voice_dur))
    total_target_dur = min(SAFE_TARGET_TOTAL_SEC, round(INTRO_MUSIC_SEC + voice_dur + tail_dur, 3))
    fade_out_start = round(max(INTRO_MUSIC_SEC + voice_dur + 0.05, total_target_dur - tail_dur), 3)
    if fade_out_start >= total_target_dur - 0.15:
        fade_out_start = round(max(INTRO_MUSIC_SEC + voice_dur - 0.10, total_target_dur - tail_dur), 3)
    actual_fade_dur = round(max(0.25, total_target_dur - fade_out_start), 3)

    tmp_out = f"{out_mp3_path}.tmp.mp3"
    temp_files.append(tmp_out)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp3_path)), exist_ok=True)

    has_bed = os.path.exists(DEFAULT_MUSIC_BED) and os.path.getsize(DEFAULT_MUSIC_BED) > 10000

    # Voz principal retrasada exactamente 5.000s (0:00-0:05 música sola) con control limpio de picos
    delayed_voice_mix = (
        f"[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"alimiter=limit=-1.2dB:attack=5:release=50:asc=true:level=false,"
        f"adelay={int(INTRO_MUSIC_SEC * 1000)}|{int(INTRO_MUSIC_SEC * 1000)},"
        f"apad=whole_dur={total_target_dur:.3f},"
        f"atrim=0:{total_target_dur:.3f}[vox_mix]"
    )
    # Señal sidechain anticipada 150ms (4850ms) para atenuación suave ANTES de cada entrada de Fred
    lookahead_ms = max(0, int(INTRO_MUSIC_SEC * 1000) - 150)
    delayed_voice_sc = (
        f"[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"adelay={lookahead_ms}|{lookahead_ms},"
        f"apad=whole_dur={total_target_dur:.3f},"
        f"atrim=0:{total_target_dur:.3f}[vox_sc]"
    )

    if has_bed:
        filter_complex = (
            f"{delayed_voice_mix};"
            f"{delayed_voice_sc};"
            f"[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"atrim=start={bed_seek_sec}:duration={total_target_dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.40,afade=t=out:st={fade_out_start:.3f}:d={actual_fade_dur:.3f},"
            f"highpass=f=95,lowpass=f=9000,volume=0.336[bed_pre];"
            f"[bed_pre][vox_sc]sidechaincompress=threshold=0.014:ratio=3.2:attack=200:release=450:level_sc=2.8[bed_ducked];"
            f"[vox_mix][bed_ducked]amix=inputs=2:duration=first:normalize=0,"
            f"alimiter=limit=-0.8dB:attack=5:release=50:asc=true:level=false[aout]"
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
        filter_complex = (
            f"{delayed_voice_mix},"
            f"alimiter=limit=-0.8dB:attack=5:release=50:asc=true:level=false[aout]"
        )
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

    return {
        "tmp_out": tmp_out,
        "voice_dur": voice_dur,
        "actual_dur": actual_dur,
        "dur_p1": round(dur_p1, 3),
        "dur_p2": round(dur_p2, 3),
        "dur_p3": round(dur_p3, 3),
        "pause_1_sec": PAUSE_MUSIC_SEC,
        "pause_2_sec": PAUSE_MUSIC_SEC,
        "tail_dur": round(actual_fade_dur, 3),
        "t_split_p3_sec": t_split_p3,
        "p1_lufs": round(p1_lufs, 2),
        "p2_lufs": round(p2_lufs, 2),
        "p3_base_lufs": round(p3_base_lufs, 2),
        "closing_boost_db": boost_db
    }

# ==============================================================================
# 9. INTEGRACIÓN SEGURA EN EL CATÁLOGO DEL REPRODUCTOR (index.html + Clones)
# ==============================================================================
def find_existing_catalog_pair(band_name, song_title):
    """Busca un par existente en BASE_DJ_FRED_TRACKS por bandName y songTitle normalizados."""
    if not os.path.exists(INDEX_HTML_PATH):
        return None, None
    try:
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        m_arr = re.search(r"const BASE_DJ_FRED_TRACKS\s*=\s*\[([\s\S]*?)\n\s*\];", html)
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
    Integra o actualiza la historia y canción en BASE_DJ_FRED_TRACKS dentro de index.html
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
    has_local_full = bool(full_song_audio and os.path.exists(os.path.join(PROJECT_ROOT, full_song_audio)))
    if has_local_full:
        song_dur = get_audio_duration(os.path.join(PROJECT_ROOT, full_song_audio))
        song_audio_url = full_song_audio
        song_summary = f"Canción original completa ({story_record['band_name']} — {story_record['song_title']})"
    else:
        song_dur = float(story_record.get("song_duration_sec") or 240)
        song_audio_url = ""
        song_summary = f"Canción original desde Spotify ({story_record['band_name']} — {story_record['song_title']})"

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
        "summary": song_summary,
        "status": "con_audio",
        "audioUrl": song_audio_url,
        "fileUrl": song_audio_url,
        "hasRealAudio": True,
        "relatedIntroId": intro_id,
        "lyrics": []
    }
    entries_to_write.append(song_obj)

    # Locate BASE_DJ_FRED_TRACKS = [ ... ];
    m_arr = re.search(r"(const BASE_DJ_FRED_TRACKS\s*=\s*\[)([\s\S]*?)(\n\s*\];)", html)
    if not m_arr:
        return False

    arr_body = m_arr.group(2)

    # Replace or insert each object cleanly inside BASE_DJ_FRED_TRACKS (keeping intro -> song paired)
    for entry in entries_to_write:
        js_text = format_js_entry(entry)
        obj_pat = re.compile(
            r"\n\s*\{\s*\n\s*id:\s*'" + re.escape(entry["id"]) + r"'[\s\S]*?\n\s*\}(?=,|\s*$)",
            re.MULTILINE
        )
        if obj_pat.search(arr_body):
            arr_body = obj_pat.sub("\n" + js_text, arr_body, count=1)
        elif not entry["isIntro"] and entry.get("relatedIntroId"):
            intro_pat = re.compile(
                r"(\n\s*\{\s*\n\s*id:\s*'" + re.escape(entry["relatedIntroId"]) + r"'[\s\S]*?\n\s*\})(,|\s*$)",
                re.MULTILINE
            )
            if intro_pat.search(arr_body):
                arr_body = intro_pat.sub(lambda m: m.group(1) + ",\n" + js_text + m.group(2), arr_body, count=1)
            else:
                arr_body = arr_body.rstrip() + ",\n" + js_text
        else:
            arr_body = arr_body.rstrip() + ",\n" + js_text

    new_html = html[:m_arr.start(2)] + arr_body + html[m_arr.end(2):]

    # Increment clean reset key so returning browsers pick up regenerated base story duration & lyrics
    reset_m = re.search(r"dj_fred_reset_v(\d+)_clean", new_html)
    if reset_m:
        next_ver = int(reset_m.group(1)) + 1
        new_html = re.sub(r"dj_fred_reset_v\d+_clean", f"dj_fred_reset_v{next_ver}_clean", new_html)

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
    job_id=None,
    song_duration_sec=None
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
    if song_duration_sec is None and existing_record:
        song_duration_sec = existing_record.get("song_duration_sec")

    existing_pair_slug, existing_audio_url = find_existing_catalog_pair(band_name, song_title)
    if not out_mp3_path:
        if existing_audio_url and existing_audio_url.startswith("audio/"):
            out_mp3_path = os.path.join(PROJECT_ROOT, existing_audio_url)
        else:
            slug = existing_pair_slug or make_slug(band_name, song_title)
            out_mp3_path = os.path.join(WORKSPACE_AUDIO_DIR, f"fred_intro_{slug}.mp3")

    rel_audio_file = os.path.relpath(out_mp3_path, PROJECT_ROOT).replace("\\", "/")

    # 1. Preparar guion estructurado en 3 párrafos (nuevo, regenerado o reutilizado)
    if mode == "regenerate_voice" and existing_record:
        opening_id = existing_record.get("opening_id", 1)
        opening_text = existing_record.get("opening_text") or existing_record.get("apertura", "")
        paragraph_1 = existing_record.get("paragraph_1") or existing_record.get("apertura", "")
        paragraph_2 = existing_record.get("paragraph_2") or existing_record.get("desarrollo", "")
        p3_resolution = existing_record.get("p3_resolution", "")
        p3_closing = existing_record.get("p3_closing") or existing_record.get("cierre", "")
        historical_info = existing_record.get("historical_info", "")
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
            prev_summary = existing_record.get("paragraph_2") or existing_record.get("desarrollo")

        ai_script = generate_ai_story_script(
            song_title, band_name, album_name, year,
            angle=next_angle,
            exclude_opening_ids=excl_openings,
            previous_story_summary=prev_summary
        )
        opening_id = ai_script["opening_id"]
        opening_text = ai_script["opening_text"]
        paragraph_1 = ai_script["paragraph_1"]
        paragraph_2 = ai_script["paragraph_2"]
        p3_resolution = ai_script["p3_resolution"]
        p3_closing = ai_script["p3_closing"]
        historical_info = ai_script["historical_info"]
        angle_index = next_angle
        script_source = ai_script["source"]

    dual = build_dual_scripts(paragraph_1, paragraph_2, p3_resolution, p3_closing, model_name=selected_model)

    print(f"\n🎙️ [ROCK RADIO AI] Iniciando '{song_title}' — {band_name} (modo={mode}, modelo={selected_model}, voz={selected_voice[:8]}...)", flush=True)
    print(f"   Apertura #{opening_id}: {opening_text}", flush=True)

    tmp_prefix = f"/tmp/rockradio_{pid}_{int(t_start*1000)}"
    temp_files = []

    try:
        # 2. Síntesis inicial con Fish Audio (estrictamente 3 llamadas: P1, P2, P3)
        p1_mp3, p2_mp3, p3_mp3 = await synthesize_segments(
            dual["vocal_p1"], dual["vocal_p2"], dual["vocal_p3"],
            tmp_prefix, temp_files,
            use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model, job_id=job_id
        )

        # 3. Medir duración real descontando intro (5s) + dos pausas musicales (3s + 3s) + transición final
        for pass_num in range(1, 4):
            dur_p1_raw = get_audio_duration(p1_mp3)
            dur_p2_raw = get_audio_duration(p2_mp3)
            dur_p3_raw = get_audio_duration(p3_mp3)
            # Restar ~0.35s estimados de aire muerto por segmento al recortar <-50dB
            speech_est = max(0.0, dur_p1_raw - 0.15) + max(0.0, dur_p2_raw - 0.15) + max(0.0, dur_p3_raw - 0.15)
            predicted_final = INTRO_MUSIC_SEC + PAUSE_MUSIC_SEC * 2 + speech_est + 0.55

            if predicted_final <= SAFE_TARGET_TOTAL_SEC:
                break

            excess = predicted_final - (SAFE_TARGET_TOTAL_SEC - 1.2)
            print(f"⏱️ [ROCK RADIO AI] Duración estimada {predicted_final:.2f}s excede límite (45s). Condensando sin acelerar (pase {pass_num})...", flush=True)

            if pass_num == 1:
                new_p2 = condense_paragraph_text(dual["p2_clean"], song_title, band_name, role_label="párrafo 2 (anécdota)", excess_sec=excess)
                if new_p2 != dual["p2_clean"]:
                    dual = build_dual_scripts(dual["p1_clean"], new_p2, dual["p3_res_clean"], dual["p3_close_clean"], model_name=selected_model)
                    p2_new = f"{tmp_prefix}_p2_c{pass_num}.mp3"
                    temp_files.append(p2_new)
                    await synthesize_single_segment(dual["vocal_p2"], p2_new, use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model)
                    p2_mp3 = p2_new
                    continue

            # Si aún excede o P2 no redujo suficiente, simplificar gancho de P1 o desenlace de P3 preservando oraciones completas
            new_p1 = opening_text if len(dual["p1_clean"]) > len(opening_text) else dual["p1_clean"]
            new_res = condense_paragraph_text(dual["p3_res_clean"], song_title, band_name, role_label="párrafo 3 (desenlace)", excess_sec=excess) if pass_num >= 3 else dual["p3_res_clean"]
            if pass_num >= 3 and new_res == dual["p3_res_clean"]:
                new_res = ""

            p1_changed = new_p1 != dual["p1_clean"]
            p3_changed = new_res != dual["p3_res_clean"]
            if not p1_changed and not p3_changed:
                new_p2_short = condense_paragraph_text(dual["p2_clean"], song_title, band_name, role_label="párrafo 2 (anécdota)", excess_sec=excess + 2.0)
                if new_p2_short != dual["p2_clean"]:
                    dual = build_dual_scripts(new_p1, new_p2_short, new_res, dual["p3_close_clean"], model_name=selected_model)
                    p2_new = f"{tmp_prefix}_p2_c{pass_num}.mp3"
                    temp_files.append(p2_new)
                    await synthesize_single_segment(dual["vocal_p2"], p2_new, use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model)
                    p2_mp3 = p2_new
                continue

            dual = build_dual_scripts(new_p1, dual["p2_clean"], new_res, dual["p3_close_clean"], model_name=selected_model)
            if p1_changed:
                p1_new = f"{tmp_prefix}_p1_c{pass_num}.mp3"
                temp_files.append(p1_new)
                await synthesize_single_segment(dual["vocal_p1"], p1_new, use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model)
                p1_mp3 = p1_new
            if p3_changed:
                p3_new = f"{tmp_prefix}_p3_c{pass_num}.mp3"
                temp_files.append(p3_new)
                await synthesize_single_segment(dual["vocal_p3"], p3_new, use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model, is_closing=True)
                p3_mp3 = p3_new

        # 4. Masterización FFmpeg/Python (5s intro + dos pausas de 3s + ducking lookahead + cierre progresivo + -1dBTP)
        bed_seek = 15.0 + ((angle_index - 1) * 8.0) % 40.0
        mix_info = master_radio_segment(
            p1_mp3, p2_mp3, p3_mp3,
            dual["p3_res_clean"], dual["p3_close_clean"],
            out_mp3_path, tmp_prefix, temp_files, bed_seek_sec=bed_seek
        )
        tmp_out = mix_info["tmp_out"]
        voice_dur = mix_info["voice_dur"]
        actual_final_dur = mix_info["actual_dur"]

        # 5. Validación estricta del archivo generado antes de reemplazar el existente
        if not os.path.exists(tmp_out) or os.path.getsize(tmp_out) < 10000:
            raise RuntimeError("El archivo de audio generado está vacío o incompleto.")
        if actual_final_dur <= 0 or actual_final_dur > MAX_TOTAL_DURATION_SEC:
            raise RuntimeError(f"La duración final ({actual_final_dur:.2f}s) incumple el límite máximo absoluto de {MAX_TOTAL_DURATION_SEC}s.")

        # Reemplazo atómico seguro (conserva anterior si ocurrió error arriba)
        os.replace(tmp_out, out_mp3_path)

        # 6. Calcular marcas de tiempo exactas (5s intro + P1 + 3s pausa + P2 + 3s pausa + P3)
        dur_p1 = mix_info["dur_p1"]
        dur_p2 = mix_info["dur_p2"]
        dur_p3 = mix_info["dur_p3"]
        p1_start = round(INTRO_MUSIC_SEC, 2)
        p1_end = round(p1_start + dur_p1, 2)
        pause1_end = round(p1_end + PAUSE_MUSIC_SEC, 2)
        p2_start = pause1_end
        p2_end = round(p2_start + dur_p2, 2)
        pause2_end = round(p2_end + PAUSE_MUSIC_SEC, 2)
        p3_start = pause2_end
        p3_end = round(min(actual_final_dur, p3_start + dur_p3), 2)

        lyrics_timings = [
            {
                "start": 0.0,
                "end": p1_start,
                "text": "🎸 📻 Intro musical — Rock Radio: De vuelta al pasado..."
            },
            {
                "start": p1_start,
                "end": p1_end,
                "text": dual["p1_clean"]
            },
            {
                "start": p1_end,
                "end": pause1_end,
                "text": "🎶 Pausa musical (3s) — Rock Radio: De vuelta al pasado..."
            },
            {
                "start": p2_start,
                "end": p2_end,
                "text": dual["p2_clean"]
            },
            {
                "start": p2_end,
                "end": pause2_end,
                "text": "🎶 Pausa musical (3s) — Rock Radio: De vuelta al pasado..."
            },
            {
                "start": p3_start,
                "end": p3_end,
                "text": dual["p3_clean"]
            }
        ]

        # 7. Persistencia completa con separación semántica (Sección 7)
        record = {
            "song_title": song_title,
            "band_name": band_name,
            "album": album_name,
            "year": year,
            "cover": cover,
            "full_song_audio": full_song_audio,
            "visible_script": dual["visible_script"],
            "vocal_script": dual["vocal_script"],
            "paragraph_1": dual["p1_clean"],
            "paragraph_2": dual["p2_clean"],
            "paragraph_3": dual["p3_clean"],
            "p3_resolution": dual["p3_res_clean"],
            "p3_closing": dual["p3_close_clean"],
            "paragraphs": [
                {"id": "paragraph_1", "role": "presentacion", "start": p1_start, "end": p1_end, "duration_sec": dur_p1, "text": dual["p1_clean"], "vocal_text": dual["vocal_p1"]},
                {"id": "paragraph_2", "role": "desarrollo", "start": p2_start, "end": p2_end, "duration_sec": dur_p2, "text": dual["p2_clean"], "vocal_text": dual["vocal_p2"]},
                {"id": "paragraph_3", "role": "desenlace_cierre", "start": p3_start, "end": p3_end, "duration_sec": dur_p3, "text": dual["p3_clean"], "vocal_text": dual["vocal_p3"]}
            ],
            "pauses_sec": {
                "intro_music": INTRO_MUSIC_SEC,
                "pause_after_p1": PAUSE_MUSIC_SEC,
                "pause_after_p2": PAUSE_MUSIC_SEC,
                "outro_fade": mix_info["tail_dur"]
            },
            "historical_info": historical_info,
            "expressive_instructions": dual["expressive_instructions"],
            "apertura": dual["p1_clean"],
            "desarrollo": dual["p2_clean"],
            "cierre": dual["p3_clean"],
            "opening_id": opening_id,
            "opening_text": opening_text,
            "fish_model": selected_model if use_fish else DEFAULT_VOICE,
            "voice_reference_id": selected_voice if use_fish else DEFAULT_VOICE,
            "voice_duration_sec": round(voice_dur, 2),
            "final_duration_sec": round(actual_final_dur, 2),
            "intro_music_sec": INTRO_MUSIC_SEC,
            "audio_metrics": {
                "p1_lufs": mix_info["p1_lufs"],
                "p2_lufs": mix_info["p2_lufs"],
                "p3_base_lufs": mix_info["p3_base_lufs"],
                "closing_boost_db": mix_info["closing_boost_db"],
                "p3_ramp_split_sec": mix_info["t_split_p3_sec"]
            },
            "audio_file": rel_audio_file,
            "angle_index": angle_index,
            "script_source": script_source,
            "lyrics_timings": lyrics_timings,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }
        if song_duration_sec is not None:
            record["song_duration_sec"] = song_duration_sec

        meta_store["stories"][story_key] = record
        meta_store["last_generated_key"] = story_key
        recent = list(meta_store.get("recent_openings", []))
        recent.append(opening_id)
        meta_store["recent_openings"] = recent[-10:]
        save_stories_metadata(meta_store)

        # 8. Integrar en catálogo del reproductor (index.html + clones)
        update_player_catalog(record)

        elapsed = time.time() - t_start
        print(
            f"✅ [ROCK RADIO AI] Completado en {elapsed:.2f}s | '{song_title}' ({band_name}) | "
            f"P1: {dur_p1:.2f}s -> [3.0s] -> P2: {dur_p2:.2f}s -> [3.0s] -> P3: {dur_p3:.2f}s | "
            f"Final: {actual_final_dur:.2f}s (<=45s) | Archivo: {rel_audio_file}",
            flush=True
        )
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
            fish_model=fish_model,
            song_duration_sec=target_record.get("song_duration_sec")
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
        fish_model=fish_model,
        song_duration_sec=md.get("duration_sec")
    )
    return {"success": True, "status": "completed", "intent": intent, "record": rec}

# Wrapper compatible con llamadas heredadas
async def build_fred_radio_narration(text, song_title="Rock Classic", band_name="Rock Band", out_mp3_path=None, job_id=None, engine=None, fish_voice=None):
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
    MAX_BODY_BYTES = 65536

    class DjFredAudioHandler(BaseHTTPRequestHandler):
        def _allowed_origin(self):
            origin = self.headers.get('Origin', '')
            if re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', origin):
                return origin
            if origin in (
                'https://www.trackstories.space',
                'https://trackstories.space',
                'https://www.rockradio.lat',
                'https://rockradio.lat',
            ):
                return origin
            return None

        def _set_cors(self):
            allowed = self._allowed_origin()
            if allowed:
                self.send_header('Access-Control-Allow-Origin', allowed)
                self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')

        def _send_json(self, code, payload):
            self.send_response(code)
            self._set_cors()
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-Content-Type-Options', 'nosniff')
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
            try:
                length = int(self.headers.get('Content-Length', 0))
            except (TypeError, ValueError):
                self._send_json(400, {'success': False, 'error': 'Content-Length inválido'})
                return
            if length < 0 or length > MAX_BODY_BYTES:
                self._send_json(413, {'success': False, 'error': 'Cuerpo de solicitud excede el límite permitido'})
                return
            body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
            except Exception:
                self._send_json(400, {'success': False, 'error': 'JSON inválido'})
                return
            if not isinstance(data, dict):
                self._send_json(400, {'success': False, 'error': 'Formato JSON inválido'})
                return

            if self.path in ('/api/execute_command', '/api/command'):
                cmd_text = str(data.get('command') or data.get('prompt') or '')[:500]
                try:
                    res = asyncio.run(execute_ai_command(cmd_text))
                    self._send_json(200 if res.get('success') else 422, res)
                except Exception as e:
                    print(f"❌ [API execute_command] Error interno: {e}", flush=True)
                    self._send_json(500, {'success': False, 'status': 'error', 'error': 'Error interno en el servidor'})

            elif self.path == '/api/generate_audio':
                song_title = str(data.get('song_title') or data.get('songTitle') or 'Canción de Rock')[:120]
                band_name = str(data.get('band_name') or data.get('bandName') or 'Banda')[:120]
                album_name = str(data.get('album', ''))[:120]
                year = str(data.get('year', ''))[:16]
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
                    print(f"❌ [API generate_audio] Error interno: {e}", flush=True)
                    self._send_json(500, {'success': False, 'error': 'Error interno al generar audio'})

            elif self.path in ('/api/generate_story_text', '/api/story_text'):
                song_title = str(data.get('song_title') or data.get('songTitle') or 'Canción de Rock')[:120]
                band_name = str(data.get('band_name') or data.get('bandName') or 'Banda')[:120]
                album_name = str(data.get('album', ''))[:120]
                year = str(data.get('year', ''))[:16]
                try:
                    angle = max(1, min(100, int(data.get('angle', 1))))
                except (TypeError, ValueError):
                    angle = 1
                res = generate_ai_story_script(song_title, band_name, album_name, year, angle)
                self._send_json(200, res)
            else:
                self._send_json(404, {'error': 'Endpoint no encontrado'})

    server = ThreadingHTTPServer(('127.0.0.1', port), DjFredAudioHandler)
    print(f"🚀 [ROCK RADIO AI] Servidor en http://127.0.0.1:{port} (Fish Audio {DEFAULT_FISH_MODEL} | Voz {DEFAULT_FISH_VOICE})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor.")

# ==============================================================================
# 12. GUÍA DE ESTILO (10 INTROS + 8 OUTROS), MOTOR CREATIVO (15 HISTORIAS) Y CLI
# ==============================================================================
# Las 10 intros y 8 outros se conservan como GUÍA DE ESTILO (personalidad, ritmo
# e intención narrativa de DJ Fred en Rock Radio), NO como catálogo cerrado.
RADIO_OVERLAY_INTROS = [
    {"id": "intro_01_aguja_vinilo", "name": "La aguja sobre el vinilo", "moods": ["classic", "recording", "default"],
     "short": "Hay canciones que empiezan antes de la primera nota. Estás en Rock Radio, soy Fred."},
    {"id": "intro_02_viaje_inesperado", "name": "El viaje inesperado", "moods": ["nostalgic", "historical", "default"],
     "short": "Ajusta tu reloj para viajar al pasado. Soy Fred, en Rock Radio."},
    {"id": "intro_03_frecuencia_perdida", "name": "La frecuencia perdida", "moods": ["mystery", "classic", "default"],
     "short": "Acabas de encontrar una frecuencia llena de historias. Soy Fred, esto es Rock Radio."},
    {"id": "intro_04_cinta_olvidada", "name": "La cinta olvidada", "moods": ["recording", "studio", "default"],
     "short": "Imagina encontrar una vieja cinta con un secreto. Soy Fred, en Rock Radio."},
    {"id": "intro_05_confesiones_madrugada", "name": "Confesiones de madrugada", "moods": ["ballad", "nostalgic", "emotional"],
     "short": "Baja el ruido de afuera y escucha sin afán. Te habla Fred, desde Rock Radio."},
    {"id": "intro_06_detras_escenario", "name": "Detrás del escenario", "moods": ["concert", "energetic", "rock"],
     "short": "¿Sabes qué pasó cuando se apagaron las luces? Soy Fred, y esto es Rock Radio."},
    {"id": "intro_07_archivo_confidencial", "name": "Archivo confidencial", "moods": ["mystery", "historical", "studio"],
     "short": "Hoy abrimos un viejo archivo lleno de secretos. Soy Fred, en Rock Radio."},
    {"id": "intro_08_la_primera_vez", "name": "La primera vez", "moods": ["nostalgic", "ballad", "classic"],
     "short": "Esta historia puede cambiar cómo escuchas este clásico. Soy Fred, en Rock Radio."},
    {"id": "intro_09_rebobinando_historia", "name": "Rebobinando la historia", "moods": ["historical", "nostalgic", "default"],
     "short": "Hoy regresamos al instante exacto en que nació esta historia. Soy Fred, en Rock Radio."},
    {"id": "intro_10_antes_darle_play", "name": "Antes de darle play", "moods": ["default", "mystery", "energetic"],
     "short": "Antes de que siga sonando, quiero contarte algo. Soy Fred, estás en Rock Radio."}
]

RADIO_OVERLAY_OUTROS = [
    {"id": "outro_01_revelador", "name": "Revelador", "moods": ["mystery", "studio", "default"],
     "fmt": lambda s, b: f"Quizá ahora la escuches distinto: {s}, de {b}."},
    {"id": "outro_02_nostalgico", "name": "Nostálgico", "moods": ["nostalgic", "ballad"],
     "fmt": lambda s, b: f"Cierra los ojos y regresa a esa época con {s}, de {b}."},
    {"id": "outro_03_emotivo", "name": "Emotivo", "moods": ["ballad", "emotional", "nostalgic"],
     "fmt": lambda s, b: f"Hay cosas que solo una canción puede contar. Escucha {s}, de {b}."},
    {"id": "outro_04_rock_energico", "name": "Rock enérgico", "moods": ["energetic", "rock", "concert"],
     "fmt": lambda s, b: f"Ahora deja que las guitarras hagan el resto. ¡{s}, de {b}!"},
    {"id": "outro_05_intriga", "name": "Intriga", "moods": ["mystery", "historical"],
     "fmt": lambda s, b: f"¿La volverás a escuchar igual? Descúbrelo con {s}, de {b}."},
    {"id": "outro_06_radio_vintage", "name": "Radio vintage", "moods": ["recording", "studio", "classic"],
     "fmt": lambda s, b: f"La música sigue girando: {s}, de {b}, en Rock Radio."},
    {"id": "outro_07_cinematografico", "name": "Cinematográfico", "moods": ["ballad", "historical", "emotional"],
     "fmt": lambda s, b: f"Aquí terminan mis palabras y comienza la música: {s}, de {b}."},
    {"id": "outro_08_firma_rock_radio", "name": "Firma de Rock Radio", "moods": ["default", "classic", "energetic"],
     "fmt": lambda s, b: f"Ya sabes lo que ocurrió. Ahora siéntelo: {s}, de {b}. Rock Radio."}
]

CREATIVE_INTRO_STRATEGIES = (
    "curiosidad",
    "pregunta",
    "viaje_temporal",
    "confidencia",
    "contraste",
    "escena_historica",
    "memoria_musical",
    "inicio_directo",
)

CREATIVE_OUTRO_STRATEGIES = (
    "revelacion",
    "nostalgia",
    "expectativa",
    "energia",
    "reflexion",
    "continuidad_narrativa",
    "transicion_directa",
)

CLICHE_OPENERS = (
    "imagina que",
    "sabias que",
    "hay canciones que",
    "antes de escuchar",
)

CLOSING_INVITATIONS = (
    "sube el volumen",
    "dale play",
    "cierra los ojos",
    "deja que suene",
    "escucha con atencion",
    "deja que las guitarras",
)

HISTORY_WINDOW_SIZE = 15


def _norm_narrative_text(text):
    decomposed = unicodedata.normalize("NFD", str(text or "").lower())
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9\s]+", " ", stripped).strip()


def _narrative_tokens(text):
    return [tok for tok in _norm_narrative_text(text).split() if tok]


def _jaccard_text(a, b):
    ta, tb = set(_narrative_tokens(a)), set(_narrative_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _extract_year_from_text(text):
    match = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", str(text or ""))
    return match.group(1) if match else ""


def _infer_story_emotion(song_title, band_name, p2_text, p3_resolution=""):
    """Determina la emoción principal guiada por la anécdota (no rígidamente por el género)."""
    txt = _norm_narrative_text(f"{song_title} {band_name} {p2_text} {p3_resolution}")
    if any(k in txt for k in ["duelo", "dolor", "sedante", "fiebre", "enfermo", "desconexion", "trist", "soledad", "melancol", "perdida"]):
        return "sensibilidad_contenida"
    if any(k in txt for k in ["casi queda fuera", "dudo", "dudaba", "contraste", "oscura", "guerra fria", "advertencia", "ultima hora", "improvisada"]):
        return "contraste_cultural"
    if any(k in txt for k in ["batalla", "combate", "caballeria", "galope", "rugido", "escenario", "explosivo"]):
        return "intensidad_historica"
    if any(k in txt for k in ["sintetizador", "compas", "siete por ocho", "poema", "estudio", "maqueta", "marimba", "documental", "toma"]):
        return "curiosidad_tecnica"
    if any(k in txt for k in ["piano", "balada", "orquesta", "recuerdo", "juventud", "muro"]):
        return "nostalgia_cercana"
    return "calidez_radial"


def load_recent_overlay_history(limit=HISTORY_WINDOW_SIZE):
    """Recupera las últimas 15 historias generadas desde data/stories_metadata.json (sin bloquear si no existe)."""
    if not os.path.exists(STORIES_METADATA_PATH):
        return []
    try:
        with open(STORIES_METADATA_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        return []

    history = meta.get("overlay_narrative_history", [])
    if isinstance(history, list) and history:
        return [item for item in history if isinstance(item, dict)][-limit:]

    # Retrocompatibilidad: reconstruir historial ligero desde radio_overlays existentes
    overlays = meta.get("radio_overlays", {})
    if not isinstance(overlays, dict) or not overlays:
        return []
    ordered = sorted(
        overlays.values(),
        key=lambda item: str(item.get("generated_at", "")) if isinstance(item, dict) else ""
    )
    rebuilt = []
    for item in ordered[-limit:]:
        if not isinstance(item, dict):
            continue
        p1 = str(item.get("paragraph_1", "")).strip()
        p3 = str(item.get("paragraph_3", "")).strip()
        rebuilt.append({
            "song_title": item.get("song_title", ""),
            "band_name": item.get("band_name", ""),
            "intro_strategy": item.get("intro_strategy", ""),
            "outro_strategy": item.get("outro_strategy", ""),
            "emotion": item.get("emotion", ""),
            "paragraph_1": p1,
            "paragraph_3": p3,
            "mentions_brand": ("fred" in _norm_narrative_text(p1 + " " + p3) or "rock radio" in _norm_narrative_text(p1 + " " + p3)),
            "generated_at": item.get("generated_at", ""),
        })
    return rebuilt[-limit:]


def score_narrative_diversity(p1, p3, intro_strategy, outro_strategy, recent_history):
    """Evalúa originalidad y antirrepetición (0 a 100) frente a las últimas 15 historias sin dependencias externas."""
    score = 100.0
    notes = []
    norm_p1 = _norm_narrative_text(p1)
    norm_p3 = _norm_narrative_text(p3)
    p1_prefix = " ".join(_narrative_tokens(p1)[:4])
    mentions_brand = ("fred" in norm_p1 or "rock radio" in norm_p1 or "rock radio" in norm_p3)
    uses_cliche = any(norm_p1.startswith(c) for c in CLICHE_OPENERS)

    if uses_cliche:
        score -= 10.0
        notes.append("apertura_formula")

    if not recent_history:
        return round(max(0.0, score), 2), notes

    window = recent_history[-HISTORY_WINDOW_SIZE:]
    last_item = window[-1]
    if intro_strategy and last_item.get("intro_strategy") == intro_strategy:
        score -= 32.0
        notes.append("intro_strategy_consecutiva")
    if outro_strategy and last_item.get("outro_strategy") == outro_strategy:
        score -= 32.0
        notes.append("outro_strategy_consecutiva")

    brand_recent_count = 0
    cliche_recent_count = 0
    for idx, prev in enumerate(window):
        prev_p1 = str(prev.get("paragraph_1", ""))
        prev_p3 = str(prev.get("paragraph_3", ""))
        norm_prev_p1 = _norm_narrative_text(prev_p1)
        norm_prev_p3 = _norm_narrative_text(prev_p3)
        recency_weight = 1.0 + (idx / max(1, len(window))) * 0.5

        if norm_p1 and norm_prev_p1:
            if norm_p1 == norm_prev_p1:
                score -= 55.0
                notes.append("intro_literal_repetida")
            else:
                sim1 = _jaccard_text(p1, prev_p1)
                if sim1 >= 0.65:
                    score -= 26.0 * recency_weight
                    notes.append("intro_muy_similar")
                elif p1_prefix and p1_prefix == " ".join(_narrative_tokens(prev_p1)[:4]):
                    score -= 14.0 * recency_weight
                    notes.append("estructura_inicio_similar")

        if norm_p3 and norm_prev_p3:
            if norm_p3 == norm_prev_p3:
                score -= 55.0
                notes.append("outro_literal_repetido")
            elif _jaccard_text(p3, prev_p3) >= 0.68:
                score -= 22.0 * recency_weight
                notes.append("outro_muy_similar")

        if intro_strategy and outro_strategy:
            if prev.get("intro_strategy") == intro_strategy and prev.get("outro_strategy") == outro_strategy:
                score -= 14.0 * recency_weight
                notes.append("combinacion_intro_outro_repetida")

        for inv in CLOSING_INVITATIONS:
            if inv in norm_p3 and inv in norm_prev_p3 and idx >= len(window) - 4:
                score -= 12.0
                notes.append(f"invitacion_final_repetida:{inv}")

        if prev.get("mentions_brand") or ("fred" in norm_prev_p1) or ("rock radio" in norm_prev_p1) or ("rock radio" in norm_prev_p3):
            brand_recent_count += 1
        if any(norm_prev_p1.startswith(c) for c in CLICHE_OPENERS):
            cliche_recent_count += 1

    if mentions_brand and brand_recent_count >= max(3, len(window) // 3):
        score -= 18.0
        notes.append("marca_fred_o_rock_radio_frecuente")
    if uses_cliche and cliche_recent_count >= 1:
        score -= 16.0
        notes.append("muletilla_repetida")

    return round(max(0.0, score), 2), sorted(set(notes))


def _generate_openai_creative_candidates(song_title, band_name, p1_hook, p2_anecdote, p3_resolution, historical_info, emotion, recent_history):
    """Genera 3 propuestas creativas de intro/outro usando la API de OpenAI si OPENAI_API_KEY está disponible."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return []

    model_name = os.environ.get("OPENAI_STORY_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    history_summary = [
        {
            "song": h.get("song_title", ""),
            "intro_strategy": h.get("intro_strategy", ""),
            "outro_strategy": h.get("outro_strategy", ""),
            "p1": str(h.get("paragraph_1", ""))[:120],
            "p3": str(h.get("paragraph_3", ""))[:120],
        }
        for h in recent_history[-HISTORY_WINDOW_SIZE:]
    ]
    style_intros = [i["short"] for i in RADIO_OVERLAY_INTROS[:5]]
    style_outros = [o["fmt"](song_title, band_name) for o in RADIO_OVERLAY_OUTROS[:4]]

    prompt = (
        "Eres DJ Fred de Rock Radio (locutor experimentado de rock clásico, cercano, curioso, nostálgico, "
        "hablas de tú al oyente en español natural y humano). "
        "Usa las referencias de estilo SOLO para captar voz y ritmo, NUNCA para copiarlas ni para repetir 'Soy Fred, en Rock Radio' en cada pista.\n"
        f"Canción: {song_title} | Banda: {band_name} | Emoción guiada por la anécdota: {emotion}\n"
        f"Hechos verificados (NO inventes ningún dato, fecha ni escena): {p1_hook} {p2_anecdote} {p3_resolution} ({historical_info})\n"
        f"Referencias de estilo intro: {json.dumps(style_intros, ensure_ascii=False)}\n"
        f"Referencias de estilo outro: {json.dumps(style_outros, ensure_ascii=False)}\n"
        f"Historial reciente (últimas {len(history_summary)} historias a evitar repetir): {json.dumps(history_summary, ensure_ascii=False)}\n"
        "Genera EXACTAMENTE 3 propuestas distintas en JSON válido con clave 'candidates' (lista de 3 objetos). "
        "Cada objeto debe tener: intro_strategy (una de "
        f"{list(CREATIVE_INTRO_STRATEGIES)}), outro_strategy (una de {list(CREATIVE_OUTRO_STRATEGIES)}), "
        "paragraph_1 (máx 22 palabras, original, sin muletillas como 'Imagina que...' o '¿Sabías que...?'), "
        "paragraph_2 (anécdota verificada concisa, máx 38 palabras), "
        "p3_resolution (desenlace fiel, máx 16 palabras), "
        "p3_closing (outro original ligado al desenlace que mencione claramente canción y artista, máx 18 palabras). "
        "Responde únicamente con el JSON."
    )

    payload = json.dumps({
        "model": model_name,
        "temperature": 0.85,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Devuelve únicamente JSON válido con la clave 'candidates'."},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        candidates = parsed.get("candidates", [])
        valid = []
        for c in candidates:
            if not isinstance(c, dict):
                continue
            p1 = str(c.get("paragraph_1", "")).strip()
            p2 = str(c.get("paragraph_2", "")).strip() or p2_anecdote
            res_txt = str(c.get("p3_resolution", "")).strip() or p3_resolution
            closing = str(c.get("p3_closing", "")).strip()
            if not p1 or not closing:
                continue
            if _norm_narrative_text(song_title) not in _norm_narrative_text(closing) or _norm_narrative_text(band_name) not in _norm_narrative_text(closing):
                closing = f"{closing.rstrip('.')} {song_title}, de {band_name}."
            i_strat = str(c.get("intro_strategy", "curiosidad")).strip().lower()
            o_strat = str(c.get("outro_strategy", "revelacion")).strip().lower()
            if i_strat not in CREATIVE_INTRO_STRATEGIES:
                i_strat = "curiosidad"
            if o_strat not in CREATIVE_OUTRO_STRATEGIES:
                o_strat = "revelacion"
            valid.append({
                "intro_strategy": i_strat,
                "outro_strategy": o_strat,
                "emotion": emotion,
                "paragraph_1": p1,
                "paragraph_2": p2,
                "p3_resolution": res_txt,
                "p3_closing": closing,
                "paragraph_3": f"{res_txt} {closing}".strip(),
                "source_mode": "openai_creative",
            })
        return valid[:3]
    except Exception:
        return []


def _build_local_creative_candidates(song_title, band_name, p1_hook, p2_anecdote, p3_resolution, historical_info, emotion, recent_history):
    """Construye 3 propuestas variadas (intros y outros originales por estrategia) sin depender de API externa."""
    year = _extract_year_from_text(f"{p1_hook} {p2_anecdote} {historical_info}")
    hook_clean = p1_hook.strip().rstrip(".")
    hook_lower = hook_clean[:1].lower() + hook_clean[1:] if hook_clean else "esta historia merece una segunda escucha"
    res_clean = p3_resolution.strip()

    # Decidir si incluir una mención orgánica a la emisora solo cuando hace varias historias que no aparece
    recent_brand_hits = sum(
        1 for h in recent_history[-4:]
        if h.get("mentions_brand")
        or "fred" in _norm_narrative_text(f"{h.get('paragraph_1', '')} {h.get('paragraph_3', '')}")
        or "rock radio" in _norm_narrative_text(f"{h.get('paragraph_1', '')} {h.get('paragraph_3', '')}")
    )
    allow_light_brand = (recent_brand_hits == 0 and len(recent_history) >= 2)

    intro_builders = {
        "curiosidad": lambda: f"Quizá has escuchado este tema muchas veces, pero fíjate en un detalle clave: {hook_lower}.",
        "pregunta": lambda: f"¿Qué ocurre cuando un giro inesperado cambia el destino de un disco de {band_name}? {hook_clean}.",
        "viaje_temporal": (
            (lambda: f"Regresa por un instante a {year}. En ese momento, {hook_lower}.")
            if year else
            (lambda: f"Volvamos al momento exacto en que {band_name} trabajaba en este tema: {hook_lower}.")
        ),
        "confidencia": (
            (lambda: f"Te comparto un hallazgo de Rock Radio sobre {band_name}: {hook_lower}.")
            if allow_light_brand else
            (lambda: f"Quiero compartirte un dato que pocos recuerdan sobre {band_name}: {hook_lower}.")
        ),
        "contraste": lambda: f"A primera escucha parece una cosa, pero su origen cuenta otra historia: {hook_lower}.",
        "escena_historica": (
            (lambda: f"Sitúate en {year} junto a {band_name}: {hook_lower}.")
            if year else
            (lambda: f"Detrás de esta grabación de {band_name} hay una escena real muy particular: {hook_lower}.")
        ),
        "memoria_musical": lambda: f"Al volver a escuchar a {band_name}, conviene recordar de dónde vino ese sonido: {hook_lower}.",
        "inicio_directo": lambda: f"{hook_clean}. Y lo que ocurrió con {band_name} terminó marcando este clásico.",
    }

    outro_builders = {
        "revelacion": lambda: f"Con ese origen en mente, cada compás suena distinto. {song_title}, de {band_name}.",
        "nostalgia": (
            (lambda: f"Desde {year} hasta hoy, el pulso sigue intacto. Aquí tienes {song_title}, de {band_name}.")
            if year else
            (lambda: f"Aquel momento sigue vivo cada vez que suena {song_title}, de {band_name}.")
        ),
        "expectativa": lambda: f"Ahora deja que los instrumentos terminen de contarlo: {song_title}, de {band_name}.",
        "energia": lambda: f"Todo ese impulso estalla a partir de aquí. {song_title}, de {band_name}.",
        "reflexion": lambda: f"A veces una decisión inesperada define toda una carrera. {song_title}, de {band_name}.",
        "continuidad_narrativa": lambda: f"De aquel punto de partida nació exactamente lo que vas a escuchar: {song_title}, de {band_name}.",
        "transicion_directa": (
            (lambda: f"En Rock Radio, {song_title}, de {band_name}.")
            if allow_light_brand else
            (lambda: f"Aquí la tienes: {song_title}, de {band_name}.")
        ),
    }

    # Priorizar estrategias coherentes con la emoción de la anécdota sin repetir la inmediatamente anterior
    emotion_intro_prefs = {
        "sensibilidad_contenida": ["confidencia", "memoria_musical", "contraste", "viaje_temporal", "inicio_directo"],
        "contraste_cultural": ["contraste", "pregunta", "curiosidad", "viaje_temporal", "inicio_directo"],
        "intensidad_historica": ["escena_historica", "inicio_directo", "viaje_temporal", "pregunta", "curiosidad"],
        "curiosidad_tecnica": ["curiosidad", "confidencia", "escena_historica", "pregunta", "contraste"],
        "nostalgia_cercana": ["memoria_musical", "viaje_temporal", "confidencia", "curiosidad", "escena_historica"],
        "calidez_radial": ["curiosidad", "confidencia", "memoria_musical", "inicio_directo", "viaje_temporal"],
    }
    emotion_outro_prefs = {
        "sensibilidad_contenida": ["reflexion", "expectativa", "nostalgia", "transicion_directa"],
        "contraste_cultural": ["revelacion", "reflexion", "continuidad_narrativa", "expectativa"],
        "intensidad_historica": ["energia", "transicion_directa", "continuidad_narrativa", "expectativa"],
        "curiosidad_tecnica": ["revelacion", "continuidad_narrativa", "expectativa", "reflexion"],
        "nostalgia_cercana": ["nostalgia", "reflexion", "expectativa", "transicion_directa"],
        "calidez_radial": ["continuidad_narrativa", "revelacion", "expectativa", "transicion_directa"],
    }

    last_intro = recent_history[-1].get("intro_strategy", "") if recent_history else ""
    last_outro = recent_history[-1].get("outro_strategy", "") if recent_history else ""

    intro_pool = [s for s in emotion_intro_prefs.get(emotion, list(CREATIVE_INTRO_STRATEGIES)) if s != last_intro]
    for s in CREATIVE_INTRO_STRATEGIES:
        if s not in intro_pool and s != last_intro:
            intro_pool.append(s)

    outro_pool = [s for s in emotion_outro_prefs.get(emotion, list(CREATIVE_OUTRO_STRATEGIES)) if s != last_outro]
    for s in CREATIVE_OUTRO_STRATEGIES:
        if s not in outro_pool and s != last_outro:
            outro_pool.append(s)

    # Barajar ligeramente las posiciones secundarias para no elegir siempre el mismo orden
    top_intros = intro_pool[:5]
    top_outros = outro_pool[:5]
    random.shuffle(top_intros)
    random.shuffle(top_outros)

    candidates = []
    for idx in range(3):
        i_strat = top_intros[idx % len(top_intros)]
        o_strat = top_outros[idx % len(top_outros)]
        p1 = intro_builders[i_strat]().strip()
        p3_closing = outro_builders[o_strat]().strip()
        p3 = f"{res_clean} {p3_closing}".strip()
        candidates.append({
            "intro_strategy": i_strat,
            "outro_strategy": o_strat,
            "emotion": emotion,
            "paragraph_1": p1,
            "paragraph_2": p2_anecdote.strip(),
            "p3_resolution": res_clean,
            "p3_closing": p3_closing,
            "paragraph_3": p3,
            "source_mode": "local_creative",
        })
    return candidates


def select_creative_overlay_script(
    song_title,
    band_name,
    p1_hook,
    p2_anecdote,
    p3_resolution,
    historical_info="",
    recent_history=None,
    custom_p1=None,
    custom_p2=None,
    custom_p3=None,
    custom_intro_strategy=None,
    custom_outro_strategy=None,
    custom_emotion=None,
):
    """Genera 2-3 propuestas creativas, las evalúa frente a las últimas 15 historias y elige aleatoriamente entre las mejores."""
    history = load_recent_overlay_history(HISTORY_WINDOW_SIZE) if recent_history is None else recent_history
    emotion = custom_emotion or _infer_story_emotion(song_title, band_name, custom_p2 or p2_anecdote, p3_resolution)

    if custom_p1 and custom_p2 and custom_p3:
        p1 = custom_p1.strip()
        p2 = custom_p2.strip()
        p3 = custom_p3.strip()
        i_strat = (custom_intro_strategy or "curiosidad").strip().lower()
        o_strat = (custom_outro_strategy or "revelacion").strip().lower()
        if i_strat not in CREATIVE_INTRO_STRATEGIES:
            i_strat = "curiosidad"
        if o_strat not in CREATIVE_OUTRO_STRATEGIES:
            o_strat = "revelacion"
        score, notes = score_narrative_diversity(p1, p3, i_strat, o_strat, history)
        # Separar resolución y cierre para el ramp vocal del párrafo 3
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p3) if s.strip()]
        if len(sentences) >= 2:
            res_part = " ".join(sentences[:-1])
            close_part = sentences[-1]
        else:
            res_part = p3_resolution.strip()
            close_part = p3
        chosen = {
            "intro_strategy": i_strat,
            "outro_strategy": o_strat,
            "emotion": emotion,
            "paragraph_1": p1,
            "paragraph_2": p2,
            "p3_resolution": res_part,
            "p3_closing": close_part,
            "paragraph_3": p3,
            "diversity_score": score,
            "diversity_notes": notes,
            "source_mode": "agent_custom",
        }
        return chosen, [chosen]

    candidates = _generate_openai_creative_candidates(
        song_title, band_name, p1_hook, p2_anecdote, p3_resolution, historical_info, emotion, history
    )
    if len(candidates) < 2:
        candidates = _build_local_creative_candidates(
            song_title, band_name, p1_hook, p2_anecdote, p3_resolution, historical_info, emotion, history
        )

    scored = []
    for cand in candidates:
        div_score, notes = score_narrative_diversity(
            cand["paragraph_1"],
            cand["paragraph_3"],
            cand["intro_strategy"],
            cand["outro_strategy"],
            history,
        )
        # Penalización suave por longitud excesiva para proteger los 45 segundos
        total_words = len(f"{cand['paragraph_1']} {cand['paragraph_2']} {cand['paragraph_3']}".split())
        length_penalty = max(0.0, (total_words - 78) * 1.2)
        final_score = round(max(0.0, div_score - length_penalty), 2)
        cand["diversity_score"] = final_score
        cand["diversity_notes"] = notes
        scored.append(cand)

    scored.sort(key=lambda c: c["diversity_score"], reverse=True)
    best_score = scored[0]["diversity_score"]
    # Variación aleatoria entre las mejores propuestas válidas (nunca elegir sistemáticamente solo la primera)
    top_pool = [c for c in scored if c["diversity_score"] >= best_score - 12.0]
    chosen = random.choice(top_pool)
    return chosen, scored


def _shorten_sentence_naturally(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return text
    candidate = " ".join(words[:max_words])
    for sep in [". ", "; ", ", "]:
        idx = candidate.rfind(sep)
        if idx > len(candidate) * 0.55:
            return candidate[:idx].strip().rstrip(",;:") + "."
    return candidate.rstrip(",;:") + "."


async def generate_voice_only_radio_intro(
    song_title,
    band_name,
    out_mp3_path=None,
    fish_voice=None,
    fish_model=None,
    custom_p1=None,
    custom_p2=None,
    custom_p3=None,
    intro_strategy=None,
    outro_strategy=None,
    emotion=None,
    dry_run_script=False,
    tts_p1=None,
    tts_p2=None,
    tts_p3=None,
):
    """
    Genera la pista vocal masterizada para overlay de radio tradicional sobre la canción original:
    - 5.0s de música inicial sin voz (reservados por el reproductor)
    - Párrafo 1 (Intro creativa y original)
    - Pausa musical exacta de 1.0s
    - Párrafo 2 (Anécdota verificable)
    - Pausa musical exacta de 1.0s
    - Párrafo 3 (Desenlace + Outro original ligado a la historia)
    - 2.0s de subida progresiva final (reservados por el reproductor)
    - Límite estricto: 5.0 + d1 + 1.0 + d2 + 1.0 + d3 + 2.0 <= 45.0s
    """
    selected_voice = fish_voice or DEFAULT_FISH_VOICE
    selected_model = fish_model or DEFAULT_FISH_MODEL
    use_fish = bool(os.environ.get("FISH_API_KEY", "").strip())

    slug = make_slug(band_name, song_title)
    if not out_mp3_path:
        out_mp3_path = os.path.join(WORKSPACE_AUDIO_DIR, f"fred_voice_{slug}.mp3")
    os.makedirs(os.path.dirname(out_mp3_path), exist_ok=True)

    curated = find_curated_story_entry(song_title, band_name)
    if curated and isinstance(curated[0], dict):
        # Elegir un ángulo verificado (rotando aleatoriamente si hay varios ángulos)
        entry = random.choice(curated) if len(curated) > 1 and not custom_p2 else curated[0]
        p1_hook = entry.get("p1_hook", "").strip()
        p2_anecdote = entry.get("p2_anecdote", "").strip()
        p3_resolution = entry.get("p3_resolution", "").strip()
        historical_info = entry.get("historical_info", "").strip()
    else:
        p1_hook = "Una historia real que vale la pena descubrir."
        p2_anecdote = f"{band_name} grabó {song_title} buscando capturar toda su energía cruda en el estudio."
        p3_resolution = "Una toma que quedó grabada para siempre en la historia del rock."
        historical_info = f"{band_name} — {song_title}"

    recent_history = load_recent_overlay_history(HISTORY_WINDOW_SIZE)
    chosen, candidates = select_creative_overlay_script(
        song_title,
        band_name,
        p1_hook,
        p2_anecdote,
        p3_resolution,
        historical_info=historical_info,
        recent_history=recent_history,
        custom_p1=custom_p1,
        custom_p2=custom_p2,
        custom_p3=custom_p3,
        custom_intro_strategy=intro_strategy,
        custom_outro_strategy=outro_strategy,
        custom_emotion=emotion,
    )

    if dry_run_script:
        return {
            "success": True,
            "dry_run_script": True,
            "song_title": song_title,
            "band_name": band_name,
            "intro_strategy": chosen["intro_strategy"],
            "outro_strategy": chosen["outro_strategy"],
            "emotion": chosen["emotion"],
            "diversity_score": chosen["diversity_score"],
            "diversity_notes": chosen["diversity_notes"],
            "source_mode": chosen["source_mode"],
            "paragraph_1": chosen["paragraph_1"],
            "paragraph_2": chosen["paragraph_2"],
            "paragraph_3": chosen["paragraph_3"],
            "candidates": [
                {
                    "intro_strategy": c["intro_strategy"],
                    "outro_strategy": c["outro_strategy"],
                    "diversity_score": c["diversity_score"],
                    "paragraph_1": c["paragraph_1"],
                    "paragraph_3": c["paragraph_3"],
                }
                for c in candidates
            ],
            "history_window_checked": len(recent_history),
            "historical_info": historical_info,
        }

    intro_delay_sec = 5.0
    pause_sec = 1.0
    ramp_sec = 2.0

    tmp_prefix = os.path.join("/tmp", f"rockradio_voice_{os.getpid()}_{int(time.time()*1000)}")
    temp_files = []

    try:
        for attempt in range(3):
            if attempt == 0:
                paragraph_1 = chosen["paragraph_1"].strip()
                paragraph_2 = chosen["paragraph_2"].strip()
                p3_res = chosen["p3_resolution"].strip()
                p3_closing = chosen["p3_closing"].strip()
                paragraph_3 = chosen["paragraph_3"].strip()
            elif attempt == 1:
                # Si excedió 45s, recortar adornos preservando la idea y sin acelerar voz
                paragraph_1 = _shorten_sentence_naturally(chosen["paragraph_1"].strip(), 15)
                paragraph_2 = _shorten_sentence_naturally(chosen["paragraph_2"].strip(), 32)
                p3_res = _shorten_sentence_naturally(chosen["p3_resolution"].strip(), 13)
                p3_closing = chosen["p3_closing"].strip()
                paragraph_3 = f"{p3_res} {p3_closing}".strip()
            else:
                paragraph_1 = _shorten_sentence_naturally(p1_hook.strip(), 12)
                paragraph_2 = _shorten_sentence_naturally(chosen["paragraph_2"].strip(), 25)
                p3_res = _shorten_sentence_naturally(chosen["p3_resolution"].strip(), 11)
                p3_closing = f"Escucha {song_title}, de {band_name}."
                paragraph_3 = f"{p3_res} {p3_closing}".strip()

            dual = build_dual_scripts(
                paragraph_1,
                paragraph_2,
                p3_res,
                p3_closing,
                model_name=selected_model,
                emotion=chosen["emotion"],
                tts_p1=tts_p1 if attempt == 0 else None,
                tts_p2=tts_p2 if attempt == 0 else None,
                tts_p3=tts_p3 if attempt == 0 else None,
            )
            att_prefix = f"{tmp_prefix}_a{attempt}"
            p1_mp3, p2_mp3, p3_mp3 = await synthesize_segments(
                dual["vocal_p1"], dual["vocal_p2"], dual["vocal_p3"],
                att_prefix, temp_files,
                use_fish=use_fish, fish_voice=selected_voice, fish_model=selected_model,
                temperature=dual["temperature"], top_p=dual["top_p"]
            )

            p1_core = f"{att_prefix}_p1_core.wav"
            p2_core = f"{att_prefix}_p2_core.wav"
            p3_core = f"{att_prefix}_p3_core.wav"
            p1_norm = f"{att_prefix}_p1_norm.wav"
            p2_norm = f"{att_prefix}_p2_norm.wav"
            p3_norm = f"{att_prefix}_p3_norm.wav"
            p3_eq = f"{att_prefix}_p3_eq.wav"
            p3_mast = f"{att_prefix}_p3_mast.wav"
            sil_pause = f"{att_prefix}_sil_pause.wav"
            voice_wav = f"{att_prefix}_voice_only.wav"
            temp_files.extend([
                p1_core, p2_core, p3_core, p1_norm, p2_norm, p3_norm,
                p3_eq, p3_mast, sil_pause, voice_wav
            ])

            _process_paragraph_to_core_wav(p1_mp3, p1_core, 0.0)
            _process_paragraph_to_core_wav(p2_mp3, p2_core, 0.0)
            _process_paragraph_to_core_wav(p3_mp3, p3_core, 0.0)

            d1 = _get_wav_duration(p1_core)
            d2 = _get_wav_duration(p2_core)
            d3 = _get_wav_duration(p3_core)
            voice_total = d1 + pause_sec + d2 + pause_sec + d3
            total_presentation = intro_delay_sec + voice_total + ramp_sec

            if total_presentation <= 45.0 or attempt == 2:
                target_lufs = -13.5
                g1 = max(-4.0, min(13.0, target_lufs - get_integrated_lufs(p1_core)))
                g2 = max(-4.0, min(13.0, target_lufs - get_integrated_lufs(p2_core)))
                g3 = max(-4.0, min(12.0, target_lufs - get_integrated_lufs(p3_core) - 0.8))

                _process_paragraph_to_core_wav(p1_mp3, p1_norm, g1)
                _process_paragraph_to_core_wav(p2_mp3, p2_norm, g2)
                _process_paragraph_to_core_wav(p3_mp3, p3_norm, g3)

                subprocess.run([
                    FFMPEG_BIN, "-y", "-i", p3_norm,
                    "-af", "equalizer=f=3200:width_type=o:width=1.0:g=1.6",
                    "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
                    p3_eq
                ], capture_output=True, check=True)

                _apply_progressive_closing_ramp(
                    p3_norm, p3_eq, p3_mast, p3_res, p3_closing,
                    boost_db=dual["closing_boost_db"]
                )

                _make_silence_wav(pause_sec, sil_pause)
                _concat_wavs([p1_norm, sil_pause, p2_norm, sil_pause, p3_mast], voice_wav)

                tmp_out = out_mp3_path + ".tmp.mp3"
                subprocess.run([
                    FFMPEG_BIN, "-y", "-i", voice_wav,
                    "-af", "alimiter=limit=0.912:attack=2:release=50",
                    "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100",
                    tmp_out
                ], capture_output=True, check=True)
                os.replace(tmp_out, out_mp3_path)

                dur = get_audio_duration(out_mp3_path)
                total_presentation = round(intro_delay_sec + dur + ramp_sec, 2)
                pause1_start = round(d1, 2)
                pause1_end = round(d1 + pause_sec, 2)
                pause2_start = round(d1 + pause_sec + d2, 2)
                pause2_end = round(d1 + pause_sec + d2 + pause_sec, 2)
                outro_end = round(dur, 2)

                overlay_timings = {
                    "introDelaySec": intro_delay_sec,
                    "pause1Start": pause1_start,
                    "pause1End": pause1_end,
                    "pause2Start": pause2_start,
                    "pause2End": pause2_end,
                    "outroEnd": outro_end,
                    "rampSec": ramp_sec,
                    "totalPresentationSec": total_presentation
                }

                # Persistir metadatos y ventana de últimas 15 historias en data/stories_metadata.json
                generated_at = datetime.now(timezone.utc).isoformat()
                mentions_brand = (
                    "fred" in _norm_narrative_text(f"{paragraph_1} {paragraph_3}")
                    or "rock radio" in _norm_narrative_text(f"{paragraph_1} {paragraph_3}")
                )
                try:
                    meta = {}
                    if os.path.exists(STORIES_METADATA_PATH):
                        with open(STORIES_METADATA_PATH, "r", encoding="utf-8") as f:
                            meta = json.load(f)

                    li = meta.get("last_overlay_intros", [])
                    lo = meta.get("last_overlay_outros", [])
                    li.append(chosen["intro_strategy"])
                    lo.append(chosen["outro_strategy"])
                    meta["last_overlay_intros"] = li[-HISTORY_WINDOW_SIZE:]
                    meta["last_overlay_outros"] = lo[-HISTORY_WINDOW_SIZE:]

                    hist = meta.get("overlay_narrative_history", [])
                    if not isinstance(hist, list):
                        hist = []
                    hist.append({
                        "song_title": song_title,
                        "band_name": band_name,
                        "intro_strategy": chosen["intro_strategy"],
                        "outro_strategy": chosen["outro_strategy"],
                        "emotion": chosen["emotion"],
                        "paragraph_1": paragraph_1,
                        "paragraph_3": paragraph_3,
                        "mentions_brand": mentions_brand,
                        "diversity_score": chosen["diversity_score"],
                        "generated_at": generated_at,
                    })
                    meta["overlay_narrative_history"] = hist[-HISTORY_WINDOW_SIZE:]

                    overlays = meta.get("radio_overlays", {})
                    overlays[slug] = {
                        "song_title": song_title,
                        "band_name": band_name,
                        "intro_id": f"creative_{chosen['intro_strategy']}",
                        "intro_name": chosen["intro_strategy"],
                        "intro_strategy": chosen["intro_strategy"],
                        "outro_id": f"creative_{chosen['outro_strategy']}",
                        "outro_name": chosen["outro_strategy"],
                        "outro_strategy": chosen["outro_strategy"],
                        "emotion": chosen["emotion"],
                        "source_mode": chosen["source_mode"],
                        "diversity_score": chosen["diversity_score"],
                        "paragraph_1": paragraph_1,
                        "paragraph_2": paragraph_2,
                        "paragraph_3": paragraph_3,
                        "vocal_p1": dual["vocal_p1"],
                        "vocal_p2": dual["vocal_p2"],
                        "vocal_p3": dual["vocal_p3"],
                        "model": selected_model,
                        "voice": selected_voice,
                        "segment_durations_sec": {"p1": round(d1, 2), "p2": round(d2, 2), "p3": round(d3, 2)},
                        "voice_duration_sec": round(dur, 2),
                        "overlay_timings": overlay_timings,
                        "audio_file": os.path.relpath(out_mp3_path, PROJECT_ROOT).replace("\\", "/"),
                        "ducking": {"intro_db": -8, "voice_db": -17, "pause_db": -7.5, "normal_db": 0},
                        "generated_at": generated_at
                    }
                    meta["radio_overlays"] = overlays
                    with open(STORIES_METADATA_PATH, "w", encoding="utf-8") as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)
                except Exception as meta_err:
                    print(f"⚠️ No se pudo persistir metadata overlay: {meta_err}", flush=True)

                return {
                    "success": True,
                    "voice_only": True,
                    "song_title": song_title,
                    "band_name": band_name,
                    "intro_strategy": chosen["intro_strategy"],
                    "outro_strategy": chosen["outro_strategy"],
                    "emotion": chosen["emotion"],
                    "source_mode": chosen["source_mode"],
                    "diversity_score": chosen["diversity_score"],
                    "audio_file": os.path.relpath(out_mp3_path, PROJECT_ROOT).replace("\\", "/"),
                    "duration_sec": round(dur, 2),
                    "total_presentation_sec": total_presentation,
                    "within_45s": total_presentation <= 45.0,
                    "overlay_timings": overlay_timings,
                    "paragraph_1": paragraph_1,
                    "paragraph_2": paragraph_2,
                    "paragraph_3": paragraph_3,
                    "visible_script": f"{paragraph_1} {paragraph_2} {paragraph_3}",
                    "historical_info": historical_info
                }
            else:
                print(f"⏱️ Intento {attempt + 1} excedió 45s ({total_presentation:.2f}s). Acortando guion y regenerando...", flush=True)
    finally:
        for tf in temp_files:
            try:
                if os.path.exists(tf):
                    os.remove(tf)
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(description="Rock Radio — Motor de Historias IA y Fish Audio")
    parser.add_argument("--command", "-c", help="Comando en lenguaje natural (ej: 'Generar historia de Tom Sawyer de Rush')")
    parser.add_argument("--song", help="Nombre de la canción")
    parser.add_argument("--band", help="Nombre de la banda o artista")
    parser.add_argument("--album", default="", help="Nombre del álbum")
    parser.add_argument("--year", default="", help="Año de lanzamiento")
    parser.add_argument("--mode", choices=["generate", "regenerate_story", "regenerate_voice"], default="generate")
    parser.add_argument("--voice-only", action="store_true", help="Generar solo pista vocal para overlay en vivo sobre la canción")
    parser.add_argument("--p1", "--paragraph-1", dest="p1", default=None, help="Párrafo 1 personalizado (intro creativa generada por IA)")
    parser.add_argument("--p2", "--paragraph-2", dest="p2", default=None, help="Párrafo 2 personalizado (anécdota verificada)")
    parser.add_argument("--p3", "--paragraph-3", dest="p3", default=None, help="Párrafo 3 personalizado (desenlace + outro creativo)")
    parser.add_argument("--intro-strategy", choices=list(CREATIVE_INTRO_STRATEGIES), default=None, help="Estrategia narrativa de intro")
    parser.add_argument("--outro-strategy", choices=list(CREATIVE_OUTRO_STRATEGIES), default=None, help="Estrategia narrativa de outro")
    parser.add_argument("--emotion", default=None, help="Emoción dominante guiada por la anécdota")
    parser.add_argument("--dry-run-script", action="store_true", help="Solo generar y evaluar propuestas de guion sin invocar síntesis TTS")
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

    if (args.voice_only or args.dry_run_script) and args.song and args.band:
        res = asyncio.run(generate_voice_only_radio_intro(
            args.song, args.band,
            out_mp3_path=args.out,
            fish_voice=args.fish_voice,
            fish_model=args.fish_model,
            custom_p1=args.p1,
            custom_p2=args.p2,
            custom_p3=args.p3,
            intro_strategy=args.intro_strategy,
            outro_strategy=args.outro_strategy,
            emotion=args.emotion,
            dry_run_script=args.dry_run_script,
        ))
        print("\n" + json.dumps(res, ensure_ascii=False, indent=2))
        if not args.dry_run_script and not res.get("within_45s"):
            print(f"⚠️ Advertencia: presentación total ({res['total_presentation_sec']}s) supera 45.0s")
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

