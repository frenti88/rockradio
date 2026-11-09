#!/usr/bin/env python3
"""
ROCK RADIO — Generador Oficial de Locuciones de DJ Eddie con Chatterbox TTS
Utiliza Chatterbox Multilingual TTS y el audio master de referencia de Alonso/Eddie
para sintetizar narraciones radiales de rock con IA.
"""

import sys
import os
import argparse
import wave
import json

def get_eddie_script(song_title, band_name, album_name="", year="", angle=1):
    """
    Construye el guion radial de DJ Eddie respetando la fórmula de 35-50 palabras:
    [Año]. Para el álbum [Álbum], [Banda] [anécdota]... Sube el volumen... — esto es [Canción], de [Banda].
    """
    year_prefix = f"En {year}, " if year else ""
    album_ref = f"para el álbum {album_name}" if album_name else "en una de sus mejores etapas de estudio"
    
    if angle == 1:
        return (
            f"{year_prefix}{album_ref}, {band_name} compuso este himno grabando en cinta analógica "
            f"con guitarras al rojo vivo y una producción impecable que marcó a toda una generación. "
            f"Sube el volumen... — esto es {song_title}, de {band_name}."
        )
    elif angle == 2:
        return (
            f"{year_prefix}con un riff demoledor y la energía pura que solo {band_name} sabe transmitir, "
            f"'{song_title}' se convirtió en una pieza imprescindible de su discografía {album_ref}. "
            f"Sube el volumen... — esto es {song_title}, de {band_name}."
        )
    else:
        return (
            f"{year_prefix}lanzada como parte del aclamado trabajo {album_ref}, esta obra cumbre "
            f"de {band_name} conquistó los diales de rock del mundo entero por su potencia melódica. "
            f"Sube el volumen... — esto es {song_title}, de {band_name}."
        )

def generate_narration(text, output_wav_path, prompt_audio="audio/alphaville_podcast_alonso.mp3", device=None):
    """
    Invoca Chatterbox Multilingual TTS para sintetizar el texto con la voz clonada de Eddie.
    """
    import torch
    import numpy as np
    import perth
    # Parche de compatibilidad para evitar excepción de PerthImplicitWatermarker
    perth.PerthImplicitWatermarker = perth.DummyWatermarker
    
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    
    if device is None:
        device = "cpu"
        
    print(f"🎙️ Inicializando Chatterbox en {device}...", flush=True)
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    
    prompt_path = None
    if prompt_audio and os.path.exists(prompt_audio):
        prompt_path = prompt_audio
        print(f"🎙️ Usando muestra de voz de Eddie (Alonso master): {prompt_path}", flush=True)
    else:
        print("ℹ️ Usando voz base multilingüe en español", flush=True)
        
    print(f"🎙️ Generando locución para texto: \"{text[:60]}...\"", flush=True)
    audio = model.generate(text, language_id="es", audio_prompt_path=prompt_path)
    
    audio_np = (audio.squeeze().cpu().numpy() * 32767).astype(np.int16)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    with wave.open(output_wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(model.sr)
        wf.writeframes(audio_np.tobytes())
        
    print(f"✓ Audio de Eddie generado exitosamente en: {output_wav_path} ({len(audio_np.tobytes())} bytes)", flush=True)
    return output_wav_path

def run_server(port=5055):
    """
    Servidor HTTP local opcional para que el frontend pueda solicitar
    locuciones directas a Chatterbox cuando corre localmente.
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class ChatterboxHandler(BaseHTTPRequestHandler):
        def _set_cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def do_OPTIONS(self):
            self.send_response(200)
            self._set_cors()
            self.end_headers()

        def do_POST(self):
            if self.path == '/api/generate_audio':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    data = json.loads(body.decode('utf-8'))
                    text = data.get('text', '')
                    track_id = data.get('track_id', 'custom_track')
                    out_path = f"/tmp/chatterbox_{track_id}.wav"
                    generate_narration(text, out_path)
                    
                    import base64
                    with open(out_path, 'rb') as f:
                        b64_audio = base64.b64encode(f.read()).decode('utf-8')
                        
                    self.send_response(200)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    resp = json.dumps({'success': True, 'audioUrl': f"data:audio/wav;base64,{b64_audio}"})
                    self.wfile.write(resp.encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self._set_cors()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer(('127.0.0.1', port), ChatterboxHandler)
    print(f"🚀 Servidor local de Chatterbox escuchando en http://127.0.0.1:{port}/api/generate_audio")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor.")

def main():
    parser = argparse.ArgumentParser(description="Generador de locuciones de DJ Eddie con Chatterbox TTS")
    parser.add_argument("--song", help="Nombre de la canción")
    parser.add_argument("--band", help="Nombre de la banda o artista")
    parser.add_argument("--album", default="", help="Nombre del álbum")
    parser.add_argument("--year", default="", help="Año de lanzamiento")
    parser.add_argument("--text", help="Texto o guion personalizado para la locución")
    parser.add_argument("--angle", type=int, default=1, help="Ángulo narrativo (1, 2 o 3)")
    parser.add_argument("--out", default="/tmp/dj_eddie_output.wav", help="Ruta del archivo WAV de salida")
    parser.add_argument("--prompt", default="audio/alphaville_podcast_alonso.mp3", help="Audio de referencia para clonación")
    parser.add_argument("--serve", action="store_true", help="Iniciar servidor API local para el frontend")
    parser.add_argument("--port", type=int, default=5055, help="Puerto del servidor API local")
    
    args = parser.parse_args()
    
    if args.serve:
        run_server(args.port)
        return
        
    script_text = args.text
    if not script_text:
        if not args.song or not args.band:
            parser.error("Debes proporcionar --text o (--song y --band)")
        script_text = get_eddie_script(args.song, args.band, args.album, args.year, args.angle)
        
    print(f"\n=======================================================")
    print(f"🎸 DJ EDDIE • ROCK RADIO — GENERADOR CHATTERBOX")
    print(f"=======================================================")
    print(f"Guion:\n{script_text}\n")
    
    generate_narration(script_text, args.out, args.prompt)

if __name__ == "__main__":
    main()
