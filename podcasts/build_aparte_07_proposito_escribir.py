#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 7 (Solo Fred): "Encuentra un propósito para escribir"
Intimate solo monologue narrated by Fred (g.DEFAULT_FISH_VOICE) in Fish Audio drama-3,
with expressive natural variations, thoughts out loud, short anecdotes, soft laughs,
sighs, reflective pauses, custom Drive background music bed, and minimalist SVG cover.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_07"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE

# (id, gap_ms_before, text)
CHUNKS = [
    (
        "01_intro", 0,
        "Hola… ¿qué tal? Bienvenido a Aparte. Hoy estoy solo frente al micrófono, sin invitados, sin libreto rígido… "
        "solo con un café tibio y una idea que me viene dando vueltas en la cabeza toda la semana: ¿para qué escribimos?"
    ),
    (
        "02_duda", 450,
        "A ver… suena a pregunta de taller literario, ¿cierto? (chuckle) Pero te juro que no va por ahí. "
        "Hace unos días me senté frente a la pantalla en blanco, con el cursor parpadeando… y durante veinte minutos no escribí ni una línea decente. "
        "Borré tres párrafos, abrí el celular, volví, miré el techo… (sigh) Y ahí me cayó el veinte: no era falta de ideas. Era falta de propósito."
    ),
    (
        "03_orwell", 550,
        "Pensé mucho en George Orwell. Orwell decía que sus experiencias y sus preocupaciones políticas eran exactamente lo que le daba sentido a toda su obra. "
        "Él no se sentaba a escribir simplemente para llenar páginas o para sonar inteligente. Tenía algo que necesitaba decir. Una urgencia. Un para qué."
    ),
    (
        "04_peor_dia", 480,
        "Y eso lo cambia todo, ¿sabes? Porque tener una intención clara para escribir es lo único que te va a hacer volver a la silla… "
        "es lo que te va a empujar incluso en tu peor día, cuando estás cansado, cuando nadie te lee, cuando sientes que todo lo que escribes suena horrible. "
        "(chuckle) Que, seamos honestos, pasa más seguido de lo que admitimos."
    ),
    (
        "05_rumbo", 520,
        "Como todo en la vida, sin rumbo es muy difícil llegar a algún lugar. "
        "La mayoría de la gente deambula… escribe un día porque le dio inspiración, lo deja tres semanas, cambia de tema, persigue la tendencia del momento… "
        "y al final del año siente que caminó muchísimo pero no llegó a ninguna parte. Asegúrate de tener rumbo."
    ),
    (
        "06_cuatro_lineas_intro", 650,
        "Y para que esto no se quede en filosofía abstracta —ni en una charla eterna— quiero dejarte cuatro ideas muy concretas. "
        "En cuatro líneas, para que no se te escape ninguna."
    ),
    (
        "07_regla_1_observa", 450,
        "Primera: observa lo que te rodea. "
        "De verdad, levanta la cabeza. Las mejores historias no están escondidas en una biblioteca secreta; están en la fila del café, en una conversación a medias en el bus, "
        "en ese detalle pequeño que todo el mundo pasa por alto porque va mirando el teléfono. Si no observas, no tienes materia prima."
    ),
    (
        "08_regla_2_reescribe", 520,
        "Segunda: reescribe con esmero. "
        "El primer borrador casi siempre es un desastre… y está perfecto que lo sea. (laughing) El mío de esta mañana parecía escrito por alguien con sueño y prisa. "
        "Escribir de verdad empieza cuando vuelves sobre tus palabras, tachas lo que sobra y pules la idea hasta que brilla."
    ),
    (
        "09_regla_3_minimalista", 520,
        "Tercera: sé minimalista. "
        "Si puedes decirlo en diez palabras claras, no uses cuarenta palabras adornadas. La claridad es una forma de respeto hacia quien te lee o te escucha. "
        "Menos ruido, más verdad."
    ),
    (
        "10_regla_4_meta", 520,
        "Y cuarta: ten una meta. "
        "No tiene que ser escribir la gran novela del siglo. Puede ser publicar un texto corto cada domingo, terminar un ensayo, o simplemente aclarar tus propios pensamientos en un cuaderno. "
        "Pero ponle nombre, ponle dirección."
    ),
    (
        "11_resumen_cierre", 750,
        "Así que, en cuatro líneas, para que te lo lleves hoy: "
        "observa lo que te rodea. Reescribe con esmero. Sé minimalista. Ten una meta. "
        "Encuentra tu propósito para escribir… y vuelve a él, incluso en tus peores días. "
        "Hasta aquí por hoy. Esto fue Aparte. Ideas que merecen ser escuchadas."
    ),
]


def write_cover_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <rect width="800" height="800" fill="#365314"/>
  <g transform="translate(400, 385)" fill="none" stroke="#ECFCCB" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="0" cy="0" r="135"/>
    <polygon points="0,-95 28,-12 0,95 -28,-12" fill="#BEF264" stroke="#ECFCCB" stroke-width="14"/>
    <circle cx="0" cy="0" r="16" fill="#365314" stroke="none"/>
    <line x1="0" y1="-135" x2="0" y2="-112"/>
    <line x1="0" y1="112" x2="0" y2="135"/>
    <line x1="-135" y1="0" x2="-112" y2="0"/>
    <line x1="112" y1="0" x2="135" y2="0"/>
  </g>
  <text x="400" y="690" text-anchor="middle" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="34" font-weight="700" letter-spacing="8" fill="#ECFCCB" opacity="0.92">APARTE</text>
</svg>
"""
    (OUT_DIR / "cover_ep07_escribir.svg").write_text(svg, encoding="utf-8")


def load_wav_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            arr = arr.reshape(-1, 2).mean(axis=1)
        return arr


def main():
    write_cover_svg()
    sr = 48000
    clips = []

    for tid, gap_ms, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"

        if not (mp3.exists() and mp3.stat().st_size > 2000):
            print(f"[TTS] {tid} (fred)...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), reference_id=VOICE_FRED, model="drama-3")
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

    lead_in_samples = int(2.4 * sr)
    tail_samples = int(5.5 * sr)

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

    voice_full = Path("/tmp/aparte_07_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled Solo Fred episode: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_07_bed.wav")
    print(f"[BED] Rendering custom Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_proposito_escribir.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            "[0:a]asplit=2[v_mix][v_sc];"
            "[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume=0.12[b_raw];"
            "[b_raw][v_sc]sidechaincompress=threshold=0.012:ratio=4.5:attack=50:release=450:makeup=1[b_duck];"
            "[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            "loudnorm=I=-16:TP=-1.0:LRA=11[out]",
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
