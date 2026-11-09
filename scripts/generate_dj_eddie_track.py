#!/usr/bin/env python3
"""
ROCK RADIO — Generador Oficial de Locuciones de DJ Eddie con IA
Implementa los lineamientos de audio y sincronización de letras para DJ Eddie:
- Locutor: Eddie (Voz oficial Alonso: es-US-AlonsoNeural)
- Cadencia de radio: 3 segmentos con pausas calculadas (400ms tras S1, 600ms tras S2, 400ms antes del cierre)
- Procesamiento de cabina radial con FFmpeg: silenceremove (-45dB), pitch shift (1.055), ecualización radial y compresor
- Generación de audio real con duración real (5 a 10s de procesamiento)
- Retorno de marcas de tiempo exactas (intro_timings) para sincronizar la letra del intro y la canción al 100%
- Servidor HTTP local en puerto 5055 para la app web
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
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import edge_tts
except ImportError:
    print("Error: edge_tts no está instalado. Ejecuta: pip install edge-tts", file=sys.stderr)

WORKSPACE_AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio'))
os.makedirs(WORKSPACE_AUDIO_DIR, exist_ok=True)

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe" if os.path.exists("/opt/homebrew/bin/ffprobe") else "ffprobe"

def find_or_download_bg(song_title, band_name):
    """
    Localiza o descarga la pista original/instrumental completa de la canción
    para mezclarla en la cabina de DJ Eddie con ducking dinámico (música de fondo
    al 40% durante la locución de Eddie, subiendo al 100% al terminar el intro).
    """
    slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
    cached_tmp = f"/tmp/bg_{slug}.mp3"
    if os.path.exists(cached_tmp) and os.path.getsize(cached_tmp) > 500000:
        return cached_tmp

    # Buscar en carpeta audio local pistas existentes que no sean narraciones previas de Eddie
    clean_b = band_name.lower().replace(' ', '_')
    clean_s = song_title.lower().replace(' ', '_')
    if os.path.exists(WORKSPACE_AUDIO_DIR):
        for fn in os.listdir(WORKSPACE_AUDIO_DIR):
            if fn.endswith('.mp3') and not fn.startswith('eddie_') and not 'podcast' in fn:
                if clean_b in fn.lower() and clean_s in fn.lower():
                    return os.path.join(WORKSPACE_AUDIO_DIR, fn)

    # Descargar pista con yt-dlp si está disponible
    yt_bin = "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"
    if not os.path.exists(yt_bin):
        yt_bin = "yt-dlp"
    try:
        print(f"  🔍 Buscando pista de audio original para '{song_title}' de {band_name}...", flush=True)
        query = f"ytsearch1:{band_name} {song_title} audio"
        cmd = [
            yt_bin,
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "--default-search", "ytsearch1",
            "--no-playlist",
            "-o", cached_tmp,
            query
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        if os.path.exists(cached_tmp) and os.path.getsize(cached_tmp) > 500000:
            print(f"  ✓ Pista de fondo obtenida exitosamente: {cached_tmp}", flush=True)
            return cached_tmp
    except Exception as e:
        print(f"  [Aviso] No se pudo descargar pista con yt-dlp: {e}", flush=True)

    return None

def get_eddie_script(song_title, band_name, album_name="", year="", angle=1):
    """
    Construye el guion radial de DJ Eddie respetando la fórmula de 35-50 palabras y 3 oraciones estrictas:
    1. Contexto histórico y álbum
    2. Anécdota de grabación o impacto musical
    3. Punchline: 'Sube el volumen... — ¡esto es [Canción], de [Banda]!'
    """
    year_prefix = f"En {year}, " if year else ""
    album_ref = f"para el álbum {album_name}" if album_name else "en una de sus mejores etapas de estudio"
    
    if angle == 1:
        return (
            f"{year_prefix}{album_ref}, {band_name} compuso este himno grabando en cinta analógica "
            f"con guitarras al rojo vivo. "
            f"Fue una sesión legendaria de estudio que capturó pura magia y marcó a toda una generación. "
            f"Sube el volumen... — ¡esto es {song_title}, de {band_name}!"
        )
    elif angle == 2:
        return (
            f"{year_prefix}con un riff demoledor y la energía pura que solo {band_name} sabe transmitir, "
            f"'{song_title}' nació {album_ref}. "
            f"La química de la banda en el estudio convirtió esta toma en una de las grabaciones más potentes de su carrera. "
            f"Sube el volumen... — ¡esto es {song_title}, de {band_name}!"
        )
    else:
        return (
            f"{year_prefix}lanzada como parte del aclamado trabajo {album_ref}, esta obra cumbre "
            f"de {band_name} conquistó los diales del planeta. "
            f"Su impacto en las listas de rock fue rotundo, convirtiéndose en un clásico eterno e infaltable de la radio. "
            f"Sube el volumen... — ¡esto es {song_title}, de {band_name}!"
        )

def parse_radio_script(text, song_title="Rock Classic", band_name="Rock Band"):
    """
    Parsea el guion en las 3 oraciones exactas para que el audio generado y la letra coincidan palabra por palabra.
    """
    norm_text = text.replace('—', ' - ').replace('–', ' - ')
    punchline_match = re.search(r'(Sube el volumen.*)', norm_text, re.IGNORECASE)
    if punchline_match:
        punchline_full = punchline_match.group(1).strip()
        body = norm_text[:punchline_match.start()].strip()
    else:
        punchline_full = f"Sube el volumen... - ¡esto es {song_title}, de {band_name}!"
        body = norm_text

    raw_sentences = [s.strip() for s in re.split(r'\.\s+', body) if s.strip()]
    if len(raw_sentences) >= 2:
        line1 = raw_sentences[0] + ('.' if not raw_sentences[0].endswith('.') else '')
        line2 = '. '.join(raw_sentences[1:])
        if not line2.endswith('.'):
            line2 += '.'
    elif len(raw_sentences) == 1:
        line1 = raw_sentences[0] + ('.' if not raw_sentences[0].endswith('.') else '')
        line2 = "Una sesión legendaria de estudio que capturó pura magia y marcó a toda una generación."
    else:
        line1 = f"Para {song_title}, {band_name} compuso este himno grabando con guitarras al rojo vivo y una producción impecable."
        line2 = "Una pieza imprescindible que marcó a toda una generación."

    line3_a = "Sube el volumen..."
    if ' - ' in punchline_full:
        line3_b = punchline_full.split(' - ', 1)[1].strip()
    elif '...' in punchline_full:
        line3_b = punchline_full.split('...', 1)[1].strip()
    else:
        line3_b = f"¡esto es {song_title}, de {band_name}!"

    if not line3_b.startswith('¡') and not line3_b.startswith('!'):
        line3_b = '¡' + line3_b
    if not line3_b.endswith('!'):
        line3_b = line3_b.rstrip('.') + '!'

    full_script = f"{line1} {line2} {line3_a} — {line3_b}"
    return line1, line2, line3_a, line3_b, full_script

async def save_tts_line_with_retry(text, voice, rate, pitch, output_file, max_retries=5):
    """
    Guarda una línea con Edge-TTS con reintentos para asegurar estabilidad.
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
            print(f"  [Reintento {attempt+1}/{max_retries}] '{clean_text[:35]}...': {e}", flush=True)
            await asyncio.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Fallo al sintetizar línea de locución: {clean_text}")

def trim_and_boost_wav(raw_mp3, out_wav, gain_val):
    """
    Limpia los silencios digitales en los extremos (-45dB) y aplica la ganancia normalizada.
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
    Genera silencio digital estricto para los espacios de respiración de cabina radial.
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
        return 20.0

async def build_eddie_radio_narration(text, song_title="Rock Classic", band_name="Rock Band", out_mp3_path=None):
    """
    Genera la locución oficial de Eddie con todos los lineamientos de producción:
    - Voz Alonso (es-US-AlonsoNeural)
    - 3 secciones con pausas dramáticas exactas
    - Cadena de compresión y ecualización radial analógica
    - Cálculo de timestamps exactos (intro_timings) para sincronizar la letra al 100%
    """
    pid = os.getpid()
    t_start = time.time()
    print(f"\n🎙️ [DJ EDDIE SERVICE] Iniciando generación de locución para: '{song_title}' de {band_name}...", flush=True)

    line1, line2, line3_a, line3_b, full_script = parse_radio_script(text, song_title, band_name)
    print(f"  > Oración 1: {line1}")
    print(f"  > Oración 2: {line2}")
    print(f"  > Oración 3: {line3_a} — {line3_b}")

    tmp_prefix = f"/tmp/dj_eddie_prod_{pid}_{int(t_start*1000)}"

    s1_mp3 = f"{tmp_prefix}_s1.mp3"
    s2_mp3 = f"{tmp_prefix}_s2.mp3"
    s3_a_mp3 = f"{tmp_prefix}_s3a.mp3"
    s3_b_mp3 = f"{tmp_prefix}_s3b.mp3"

    voice = "es-US-AlonsoNeural"
    # Lineamientos de locución radial de Eddie:
    # S1: rate +5%, pitch +1Hz, gain 1.2dB -> 400ms pausa
    # S2: rate +5%, pitch +2Hz, gain 1.6dB -> 600ms pausa
    # S3: "Sube el volumen..." (2.0dB) -> 400ms pausa de tensión -> "¡esto es X de Y!" (rate +7%, pitch +3Hz, gain 2.6dB)
    await save_tts_line_with_retry(line1, voice, "+5%", "+1Hz", s1_mp3)
    await save_tts_line_with_retry(line2, voice, "+5%", "+2Hz", s2_mp3)
    await save_tts_line_with_retry(line3_a, voice, "+5%", "+2Hz", s3_a_mp3)
    await save_tts_line_with_retry(line3_b, voice, "+7%", "+3Hz", s3_b_mp3)

    w_s1 = f"{tmp_prefix}_s1.wav"
    w_sil1 = f"{tmp_prefix}_sil1.wav"
    w_s2 = f"{tmp_prefix}_s2.wav"
    w_sil2 = f"{tmp_prefix}_sil2.wav"
    w_s3a = f"{tmp_prefix}_s3a.wav"
    w_sil3 = f"{tmp_prefix}_sil3.wav"
    w_s3b = f"{tmp_prefix}_s3b.wav"

    trim_and_boost_wav(s1_mp3, w_s1, "1.2dB")
    make_silence_wav(0.40, w_sil1)
    trim_and_boost_wav(s2_mp3, w_s2, "1.6dB")
    make_silence_wav(0.60, w_sil2)
    trim_and_boost_wav(s3_a_mp3, w_s3a, "2.0dB")
    make_silence_wav(0.40, w_sil3)
    trim_and_boost_wav(s3_b_mp3, w_s3b, "2.6dB")

    # Concatenar segmento final con pausa de suspenso (0.40s)
    c2_txt = f"{tmp_prefix}_c2.txt"
    with open(c2_txt, "w") as f:
        f.write(f"file '{w_s3a}'\nfile '{w_sil3}'\nfile '{w_s3b}'\n")
    w_line3 = f"{tmp_prefix}_line3.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", c2_txt, w_line3], capture_output=True, check=True)

    # Medir duraciones de audio reales para sincronización exacta de la letra
    dur0 = get_audio_duration(w_s1)
    dur1 = get_audio_duration(w_s2)
    dur2 = get_audio_duration(w_line3)

    t_cursor = 0.0
    intro_timings = [
        {'start': round(t_cursor, 2), 'end': round(t_cursor + dur0, 2), 'text': line1}
    ]
    t_cursor += dur0 + 0.40
    intro_timings.append({
        'start': round(t_cursor, 2),
        'end': round(t_cursor + dur1, 2),
        'text': line2
    })
    t_cursor += dur1 + 0.60
    intro_timings.append({
        'start': round(t_cursor, 2),
        'end': round(t_cursor + dur2, 2),
        'text': f"{line3_a} — {line3_b}"
    })
    intro_end = round(t_cursor + dur2, 2)

    # Concatenar pista completa de voz
    concat_txt = f"{tmp_prefix}_concat.txt"
    with open(concat_txt, "w") as f:
        for fn in [w_s1, w_sil1, w_s2, w_sil2, w_line3]:
            f.write(f"file '{fn}'\n")

    raw_voice_wav = f"{tmp_prefix}_raw_voice.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, raw_voice_wav], capture_output=True, check=True)

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

    # Masterizar la historia de la canción como audio puro de locución radial SIN música de fondo
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", raw_voice_wav,
        "-af", vc_filter_base,
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        out_mp3_path
    ], capture_output=True, check=True)

    duration = get_audio_duration(out_mp3_path)
    elapsed = time.time() - t_start
    print(f"✓ [DJ EDDIE SERVICE] Historia limpia generada en {elapsed:.2f}s (duración audio: {duration:.2f}s, intro_end: {intro_end}s): {out_mp3_path}", flush=True)

    # Limpieza de archivos temporales de paso
    for tmp_f in [s1_mp3, s2_mp3, s3_a_mp3, s3_b_mp3, w_s1, w_sil1, w_s2, w_sil2, w_s3a, w_sil3, w_s3b, c2_txt, w_line3, concat_txt, raw_voice_wav]:
        try:
            if os.path.exists(tmp_f):
                os.remove(tmp_f)
        except Exception:
            pass

    return out_mp3_path, duration, elapsed, intro_timings, intro_end, full_script

def run_server(port=5055):
    """
    Servidor HTTP en puerto 5055 para la app web de Rock Radio.
    Atiende solicitudes de generación real de locuciones y sincronización de letras.
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
                    'service': 'DJ Eddie • Real Audio Generation Service',
                    'voice': 'Eddie',
                    'voiceModel': 'es-US-AlonsoNeural',
                    'engine': 'Edge-TTS + FFmpeg Master Radio EQ/Compressor',
                    'lyricsSync': True,
                    'port': port,
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
                    album_name = data.get('album', '')
                    year = data.get('year', '')

                    if not text:
                        text = get_eddie_script(song_title, band_name, album_name, year)

                    safe_slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
                    workspace_mp3 = os.path.join(WORKSPACE_AUDIO_DIR, f"eddie_intro_{safe_slug}_{track_id}.mp3")

                    out_path, duration, elapsed, intro_timings, intro_end, full_script = asyncio.run(
                        build_eddie_radio_narration(text, song_title, band_name, workspace_mp3)
                    )

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
            elif self.path in ('/api/resolve_full_song', '/api/full_song'):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    data = json.loads(body.decode('utf-8'))
                    song_title = data.get('song_title') or data.get('songTitle') or 'Canción de Rock'
                    band_name = data.get('band_name') or data.get('bandName') or 'Banda'
                    track_id = str(data.get('track_id', '')).replace(':', '_').replace('/', '_')

                    safe_slug = re.sub(r'[^a-zA-Z0-9_]', '', f"{band_name}_{song_title}".replace(' ', '_').lower())[:40]
                    target_mp3 = os.path.join(WORKSPACE_AUDIO_DIR, f"full_{safe_slug}.mp3")

                    if not os.path.exists(target_mp3) or os.path.getsize(target_mp3) < 1000000:
                        print(f"  🔍 [DJ EDDIE SERVICE] Obteniendo pista completa para '{song_title}' de {band_name}...", flush=True)
                        yt_bin = "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"
                        query = f"ytsearch1:{band_name} {song_title} official audio"
                        cmd = [
                            yt_bin,
                            "-x", "--audio-format", "mp3",
                            "--audio-quality", "0",
                            "--default-search", "ytsearch1",
                            "--no-playlist",
                            "-o", target_mp3,
                            query
                        ]
                        subprocess.run(cmd, capture_output=True, timeout=40)

                    if os.path.exists(target_mp3) and os.path.getsize(target_mp3) > 500000:
                        dur = get_audio_duration(target_mp3)
                        rel_url = f"audio/{os.path.basename(target_mp3)}"
                        dur_fmt = f"{int(dur // 60)}:{int(dur % 60):02d}"
                        self.send_response(200)
                        self._set_cors()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'audioUrl': rel_url,
                            'fileUrl': rel_url,
                            'duration': dur_fmt,
                            'durationSec': round(dur, 2)
                        }).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self._set_cors()
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'No se pudo obtener la canción completa'}).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer(('127.0.0.1', port), DjEddieAudioHandler)
    print(f"🚀 [DJ EDDIE SERVICE] Servidor de locuciones de Eddie escuchando en http://127.0.0.1:{port}/api/generate_audio", flush=True)
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
    if not script_text:
        if not args.song or not args.band:
            parser.error("Debes proporcionar --text o (--song y --band)")
        script_text = get_eddie_script(args.song, args.band, args.album, args.year, args.angle)

    song_name = args.song or "Canción"
    band_name = args.band or "Banda"
    out_file = args.out or f"/tmp/eddie_{band_name}_{song_name}.mp3".replace(" ", "_").lower()

    print(f"=======================================================")
    print(f"🎸 DJ EDDIE • ROCK RADIO — GENERACIÓN DE AUDIO & LETRAS")
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
