#!/usr/bin/env python3
"""
TrackStories — Automated Documentary Production Pipeline
GLAM ROCK: Cuando el rock conquistó los 80
Resumable pipeline:
  - Generates original stereo instrumental beds & ambiences (numpy -> WAV 48kHz)
  - Synthesizes 13 DJ Fredd narration scenes via Fish Audio (drama-3)
  - Mixes voice + ducked original score + fades -> masters to -16 LUFS / -1 dBTP
  - Builds full continuous narration+score master MP3
  - Generates complete manifest.json with exact measured durations
"""
import json
import os
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path
import numpy as np

REPO = Path("/home/antigravity/frenti88/rockradio")
BASE = REPO / "specials" / "glam-rock-80s"
FISH_API_KEY = os.environ.get("FISH_API_KEY", "").strip()
FISH_VOICE_ID = "5b32e58542a740e59792a3573f337645"  # DJ Fredd official voice

SCENES = [
    {
        "scene_id": "ch01_s01",
        "chapter": 1,
        "chapter_title": "Una noche que cambiaría el rock",
        "emotion": "intriga_y_expectativa",
        "bed_key": "intro_crescendo",
        "bed_freqs": [110.0, 164.81, 220.0, 261.63],
        "text": (
            "Los Ángeles. Comienzos de los años ochenta. "
            "Hay músicos que apenas tienen dinero para pagar el alquiler, pero salen a la calle vestidos como si fueran los dueños de Hollywood. "
            "Botas de cuero, maquillaje, guitarras al límite y suficiente laca para poner nervioso a cualquier bombero. "
            "Algunos todavía no han vendido un solo disco. Otros están a punto de cambiar la historia del rock. "
            "Bienvenidos a TrackStories. Soy DJ Fredd, y durante la próxima hora vamos a viajar desde los clubes sudorosos de Sunset Strip hasta los estadios más grandes del planeta. "
            "Vamos a descubrir las rivalidades, las noches absurdas, las tragedias reales y las canciones que convirtieron a los ochenta en una década irrepetible."
        ),
        "followed_by_song": None,
    },
    {
        "scene_id": "ch02_s01",
        "chapter": 2,
        "chapter_title": "Antes de los 80: los padres del espectáculo",
        "emotion": "descubrimiento_y_fascinacion",
        "bed_key": "discovery_70s",
        "bed_freqs": [130.81, 196.0, 246.94, 329.63],
        "text": (
            "Antes de que California encendiera la mecha, el espectáculo ya tenía padres muy claros al otro lado del Atlántico. "
            "En los años setenta, David Bowie, T. Rex, Slade y Sweet demostraron en el Reino Unido que el rock podía ser teatro, provocación y coro gigante al mismo tiempo. "
            "En Nueva York, los New York Dolls llevaron esa actitud a las calles, mientras Alice Cooper convertía cada concierto en una película de terror. "
            "Y entonces llegó KISS. Cuatro neoyorquinos con maquillaje icónico, plataformas imposibles y pirotecnia que transformaron un recital en una experiencia inolvidable. "
            "En mil novecientos setenta y cinco, lanzaron un himno que resumía toda esa filosofía de celebración sin frenos. Escuchemos cómo empezó la fiesta."
        ),
        "followed_by_song": {
            "title": "Rock and Roll All Nite",
            "artist": "KISS",
            "album": "Dressed to Kill",
            "year": 1975,
            "duration_sec": 169,
            "cover": "img/albums/kiss_1975_alive.png",
        },
    },
    {
        "scene_id": "ch03_s01",
        "chapter": 3,
        "chapter_title": "Sunset Strip: el lugar donde comenzó el incendio",
        "emotion": "rebeldia_y_ambicion",
        "bed_key": "sunset_groove",
        "bed_freqs": [82.41, 123.47, 164.81, 196.0],
        "text": (
            "Si KISS construyó el manual del espectáculo, Sunset Strip en Hollywood fue el laboratorio donde una nueva generación lo llevó al extremo. "
            "En apenas dos kilómetros de asfalto convivían el Whisky a Go Go, el Roxy, el Troubadour y Gazzarri's. "
            "La regla era brutal: si querías tocar, tenías que empapelar la ciudad con volantes y llenar la sala por tu cuenta. "
            "Allí coincidieron bandas hambrientas como Ratt y cuatro jóvenes dispuestos a todo llamados Mötley Crüe. "
            "En mil novecientos ochenta y uno, sin una gran disquera detrás, autoeditaron su debut Too Fast for Love. "
            "Y la canción que abría aquel disco sonaba exactamente como una descarga eléctrica en medio de la noche californiana."
        ),
        "followed_by_song": {
            "title": "Live Wire",
            "artist": "Mötley Crüe",
            "album": "Too Fast for Love",
            "year": 1981,
            "duration_sec": 196,
            "cover": "img/albums/motley_crue_1981_too_fast.png",
        },
    },
    {
        "scene_id": "ch04_s01",
        "chapter": 4,
        "chapter_title": "1983: cuando la televisión cambió las reglas",
        "emotion": "sorpresa_y_triunfo",
        "bed_key": "mtv_triumph",
        "bed_freqs": [146.83, 220.0, 293.66, 369.99],
        "text": (
            "Hasta comienzos de mil novecientos ochenta y tres, las grandes disqueras seguían mirando a esas bandas con desconfianza. "
            "Pero había aparecido un factor que lo cambiaría todo: MTV. De pronto, la música ya no solo se escuchaba en la radio; ahora se veía en la sala de millones de hogares. "
            "Y en noviembre de ese año ocurrió lo impensable. Quiet Riot, una banda que había sobrevivido a años de puertas cerradas, lanzó Metal Health. "
            "Su productor les insistió en grabar una versión de un viejo éxito británico de Slade de mil novecientos setenta y tres. Al principio la banda ni siquiera quería grabarla. "
            "Irónicamente, esa canción desplazó a The Police del primer lugar del Billboard doscientos y se convirtió en el primer álbum de heavy metal en llegar al número uno en Estados Unidos."
        ),
        "followed_by_song": {
            "title": "Cum On Feel the Noize",
            "artist": "Quiet Riot",
            "album": "Metal Health",
            "year": 1983,
            "duration_sec": 290,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch05_s01",
        "chapter": 5,
        "chapter_title": "La explosión: maquillaje, guitarras y millones de seguidores",
        "emotion": "diversion_y_energia",
        "bed_key": "party_glam",
        "bed_freqs": [98.0, 146.83, 196.0, 246.94],
        "text": (
            "Con la puerta abierta por Quiet Riot, Hollywood se convirtió en una fiebre del oro. "
            "Los ejecutivos recorrían Sunset Strip buscando a la próxima sensación televisiva. Ratt entendió el juego al instante. "
            "En mil novecientos ochenta y cuatro publicaron Out of the Cellar y lanzaron un videoclip tan divertido como inolvidable, con el comediante Milton Berle en escena. "
            "Era la prueba definitiva de que el sonido de los clubes ya pertenecía a toda una generación frente al televisor."
        ),
        "followed_by_song": {
            "title": "Round and Round",
            "artist": "Ratt",
            "album": "Out of the Cellar",
            "year": 1984,
            "duration_sec": 264,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch05_s02",
        "chapter": 5,
        "chapter_title": "La explosión: maquillaje, guitarras y millones de seguidores",
        "emotion": "humor_y_celebracion",
        "bed_key": "party_glam_2",
        "bed_freqs": [110.0, 164.81, 220.0, 277.18],
        "text": (
            "Y si Ratt afinó el sonido, cuatro muchachos llegados desde Pensilvania llevaron la estética al límite absoluto. Se llamaban Poison. "
            "Vivían en un pequeño almacén lleno de ropa brillante, pintalabios y amplificadores. "
            "Muchos críticos se burlaban de sus peinados gigantes, pero nadie podía negar que sabían escribir coros imposibles de olvidar. "
            "En mil novecientos ochenta y seis, Talk Dirty to Me convirtió la extravagancia en pura celebración rockera."
        ),
        "followed_by_song": {
            "title": "Talk Dirty to Me",
            "artist": "Poison",
            "album": "Look What the Cat Dragged In",
            "year": 1986,
            "duration_sec": 224,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch06_s01",
        "chapter": 6,
        "chapter_title": "Cuando el glam y el hard rock conquistaron el mundo",
        "emotion": "grandeza_y_euforia",
        "bed_key": "stadium_anthem",
        "bed_freqs": [123.47, 185.0, 246.94, 311.13],
        "text": (
            "A mediados de la década, el fenómeno ya no era exclusivo de Los Ángeles. "
            "Desde Nueva Jersey, Bon Jovi representaba un hard rock melódico más cercano al espíritu obrero de estadio que al descontrol californiano. "
            "En mil novecientos ochenta y seis estaban grabando Slippery When Wet junto al compositor Desmond Child. "
            "Curiosamente, a Jon Bon Jovi no le convencía la primera maqueta de una canción sobre una pareja trabajadora llamada Tommy y Gina. "
            "Fue el guitarrista Richie Sambora quien insistió en rescatarla, sumando una línea de bajo demoledora y un efecto casi olvidado llamado talk box. "
            "El resultado conquistó el planeta entero."
        ),
        "followed_by_song": {
            "title": "Livin' on a Prayer",
            "artist": "Bon Jovi",
            "album": "Slippery When Wet",
            "year": 1986,
            "duration_sec": 249,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch06_s02",
        "chapter": 6,
        "chapter_title": "Cuando el glam y el hard rock conquistaron el mundo",
        "emotion": "admiracion_y_potencia",
        "bed_key": "stadium_hysteria",
        "bed_freqs": [138.59, 207.65, 277.18, 329.63],
        "text": (
            "Al otro lado del océano, en Sheffield, Inglaterra, Def Leppard venía de la nueva ola del heavy metal británico, "
            "pero junto al productor Mutt Lange redefinió lo que podía lograrse en un estudio de grabación. "
            "Tras tres años de trabajo obsesivo, su álbum Hysteria de mil novecientos ochenta y siete sonaba gigantesco. "
            "Y su mayor himno nació casi por accidente al final de las sesiones, cuando Joe Elliott tarareó un ritmo acústico que Lange transformó en una explosión de estadio."
        ),
        "followed_by_song": {
            "title": "Pour Some Sugar on Me",
            "artist": "Def Leppard",
            "album": "Hysteria",
            "year": 1987,
            "duration_sec": 267,
            "cover": "img/albums/def_leppard_1987_hysteria.png",
        },
    },
    {
        "scene_id": "ch07_s01",
        "chapter": 7,
        "chapter_title": "Detrás del maquillaje también había corazones rotos",
        "emotion": "intimidad_y_vulnerabilidad",
        "bed_key": "ballad_warm",
        "bed_freqs": [146.83, 185.0, 220.0, 293.66],
        "text": (
            "Pero el secreto mejor guardado de aquella década no estaba solo en el volumen ni en la fiesta. Estaba en las baladas. "
            "Las llamadas power ballads mostraron que detrás del cuero, las luces y la pose de estrellas invencibles, había músicos con heridas muy reales. "
            "La historia más recordada ocurrió en una lavandería de Dallas, en plena gira. "
            "Bret Michaels, el cantante de Poison, llamó a su novia desde un teléfono público mientras esperaba su ropa. Al otro lado de la línea escuchó la voz de otro hombre. "
            "Destrozado, volvió a la lavandería con una guitarra acústica y escribió la canción que en mil novecientos ochenta y ocho le dio a Poison su único número uno en Estados Unidos."
        ),
        "followed_by_song": {
            "title": "Every Rose Has Its Thorn",
            "artist": "Poison",
            "album": "Open Up and Say... Ahh!",
            "year": 1988,
            "duration_sec": 260,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch08_s01",
        "chapter": 8,
        "chapter_title": "El precio de vivir con el volumen al máximo",
        "emotion": "sobriedad_y_resiliencia",
        "bed_key": "tension_resilience",
        "bed_freqs": [110.0, 130.81, 164.81, 220.0],
        "text": (
            "Vivir con el volumen al máximo también cobró facturas enormes. Las giras interminables, la presión comercial y los excesos empujaron a muchos músicos al borde del abismo. "
            "Pero aquella década también dejó historias extraordinarias de carácter y coraje. "
            "El treinta y uno de diciembre de mil novecientos ochenta y cuatro, Rick Allen, baterista de Def Leppard, perdió su brazo izquierdo en un accidente automovilístico en Inglaterra. "
            "Cualquier otra banda habría buscado un reemplazo. Def Leppard decidió esperarlo. "
            "Con una batería electrónica diseñada a medida y pedales especiales, Rick volvió a tocar en agosto de mil novecientos ochenta y seis ante decenas de miles de personas en Castle Donington, recibiendo una de las ovaciones más emocionantes en la historia del rock."
        ),
        "followed_by_song": None,
    },
    {
        "scene_id": "ch08_s02",
        "chapter": 8,
        "chapter_title": "El precio de vivir con el volumen al máximo",
        "emotion": "tension_y_respeto",
        "bed_key": "senate_drama",
        "bed_freqs": [98.0, 116.54, 146.83, 196.0],
        "text": (
            "Y en septiembre de mil novecientos ochenta y cinco, el rock enfrentó otra batalla, esta vez en el Senado de Estados Unidos. "
            "El comité PMRC buscaba etiquetar y censurar letras consideradas ofensivas. "
            "Muchos esperaban que el cantante de Twisted Sister, Dee Snider, llegara como una caricatura escandalosa. "
            "En cambio, se presentó con calma, elocuencia y lucidez, defendiendo la libertad creativa y dejando en silencio a los senadores. "
            "Demostró que debajo del maquillaje había inteligencia y convicción."
        ),
        "followed_by_song": None,
    },
    {
        "scene_id": "ch09_s01",
        "chapter": 9,
        "chapter_title": "Cuando el mundo empezó a escuchar otra cosa",
        "emotion": "cambio_y_melancolia",
        "bed_key": "transition_90s",
        "bed_freqs": [87.31, 130.81, 174.61, 207.65],
        "text": (
            "Hacia finales de los ochenta, la fórmula empezó a mostrar señales de agotamiento. "
            "Las discográficas firmaban copias de copias, repitiendo los mismos peinados y los mismos videoclips. "
            "Sin embargo, algunas bandas jóvenes como Skid Row todavía lograron inyectar una rabia más cruda y pesada, "
            "tendiendo un puente entre la energía callejera de los ochenta y la tormenta alternativa que ya se acercaba desde Seattle. "
            "Cuando Nirvana y el grunge estallaron en mil novecientos noventa y uno, no borraron el glam de la noche a la mañana, pero sí confirmaron que una generación entera estaba buscando otro espejo."
        ),
        "followed_by_song": {
            "title": "Youth Gone Wild",
            "artist": "Skid Row",
            "album": "Skid Row",
            "year": 1989,
            "duration_sec": 210,
            "cover": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        },
    },
    {
        "scene_id": "ch10_s01",
        "chapter": 10,
        "chapter_title": "Cuando el concierto termina, la música permanece",
        "emotion": "nostalgia_y_legado",
        "bed_key": "finale_epic",
        "bed_freqs": [130.81, 164.81, 196.0, 261.63],
        "text": (
            "Volvamos por un instante a aquella noche en Sunset Strip donde empezó todo. "
            "Músicos con más sueños que dinero, cargando amplificadores bajo las luces de neón. "
            "Hubo excesos, contradicciones y caídas, pero también hubo talento genuino, canciones construidas para emocionar a estadios enteros y una alegría contagiosa que hoy sigue llenando giras alrededor del mundo. "
            "Porque las modas pasan, los peinados cambian y las décadas se cierran, pero una gran canción guarda para siempre el instante exacto en que nos hizo sentir vivos. "
            "Esto fue Glam Rock: Cuando el rock conquistó los ochenta. Soy DJ Fredd. TrackStories. La música tiene memoria."
        ),
        "followed_by_song": None,
    },
]


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return round(float(out), 2)


def synth_fish_audio(text: str, out_mp3: Path):
    if out_mp3.exists() and out_mp3.stat().st_size > 8000:
        print(f"  [REUSE] {out_mp3.name}", flush=True)
        return
    sys.path.insert(0, str(REPO / "scripts"))
    import generate_dj_fred_track as g
    g._fish_audio_tts_sync(text, str(out_mp3), model="drama-3")
    print(f"  [TTS OK] {out_mp3.name} ({out_mp3.stat().st_size} B)", flush=True)


def generate_bed_wav(out_wav: Path, duration_sec: float, freqs: list, sr: int = 48000):
    if out_wav.exists() and out_wav.stat().st_size > 10000:
        return
    n = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float32)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        # Warm analog pad with subtle detuning and slow LFO swell
        lfo = 0.65 + 0.35 * np.sin(2 * np.pi * (0.08 + 0.03 * i) * t)
        sig_l = np.sin(2 * np.pi * f * t) * 0.5 + np.sin(2 * np.pi * (f * 2.002) * t) * 0.15
        sig_r = np.sin(2 * np.pi * (f * 1.003) * t) * 0.5 + np.sin(2 * np.pi * (f * 1.998) * t) * 0.15
        left += sig_l * lfo / len(freqs)
        right += sig_r * lfo / len(freqs)
    # Soft fade in/out
    fade = min(int(sr * 2.5), n // 4)
    env = np.ones(n, dtype=np.float32)
    env[:fade] = np.linspace(0, 1, fade, dtype=np.float32)
    env[-fade:] = np.linspace(1, 0, fade, dtype=np.float32)
    left *= env * 0.22
    right *= env * 0.22
    stereo = np.stack([left, right], axis=1)
    pcm = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def mix_and_master_scene(voice_mp3: Path, bed_wav: Path, out_mp3: Path, pad_pre: float = 2.0, pad_post: float = 2.5):
    if out_mp3.exists() and out_mp3.stat().st_size > 10000:
        print(f"  [REUSE MIX] {out_mp3.name}", flush=True)
        return
    # Delay voice by pad_pre, duck bed to -18dB, mix, and normalize to -16 LUFS / -1 dBTP
    delay_ms = int(pad_pre * 1000)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(voice_mp3),
        "-i", str(bed_wav),
        "-filter_complex",
        f"[0:a]aresample=48000,adelay={delay_ms}|{delay_ms},apad=pad_dur={pad_post}[v];"
        f"[1:a]aresample=48000,volume=0.18[b];"
        f"[v][b]amix=inputs=2:duration=first:dropout_transition=2,"
        f"loudnorm=I=-16:TP=-1.0:LRA=11[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
        str(out_mp3),
    ]
    subprocess.run(cmd, check=True)
    print(f"  [MIX MASTER] {out_mp3.name} ({probe_duration(out_mp3)}s)", flush=True)


def main():
    manifest_segments = []
    mixed_files = []
    cursor_sec = 0.0
    total_narration_sec = 0.0
    total_songs_sec = 0.0

    for sc in SCENES:
        sid = sc["scene_id"]
        print(f"=== Scene {sid} (Cap {sc['chapter']}) ===", flush=True)
        voice_path = BASE / "narration" / f"{sid}.mp3"
        synth_fish_audio(sc["text"], voice_path)
        v_dur = probe_duration(voice_path)

        bed_path = BASE / "original-music" / f"bed_{sc['bed_key']}.wav"
        generate_bed_wav(bed_path, v_dur + 6.0, sc["bed_freqs"])

        mix_path = BASE / "mixes" / f"{sid}_mix.mp3"
        mix_and_master_scene(voice_path, bed_path, mix_path)
        m_dur = probe_duration(mix_path)
        mixed_files.append(mix_path)

        manifest_segments.append({
            "type": "narration",
            "scene_id": sid,
            "chapter": sc["chapter"],
            "chapter_title": sc["chapter_title"],
            "emotion": sc["emotion"],
            "start_sec": round(cursor_sec, 2),
            "end_sec": round(cursor_sec + m_dur, 2),
            "duration_sec": m_dur,
            "voice_file": f"specials/glam-rock-80s/narration/{sid}.mp3",
            "bed_file": f"specials/glam-rock-80s/original-music/bed_{sc['bed_key']}.wav",
            "mix_file": f"specials/glam-rock-80s/mixes/{sid}_mix.mp3",
            "status": "COMPLETADO",
            "license": "ORIGINAL_TRACKSTORIES",
            "text": sc["text"],
        })
        cursor_sec += m_dur
        total_narration_sec += m_dur

        if sc["followed_by_song"]:
            s = sc["followed_by_song"]
            s_dur = float(s["duration_sec"])
            manifest_segments.append({
                "type": "song",
                "chapter": sc["chapter"],
                "chapter_title": sc["chapter_title"],
                "title": s["title"],
                "artist": s["artist"],
                "album": s["album"],
                "year": s["year"],
                "cover": s["cover"],
                "start_sec": round(cursor_sec, 2),
                "end_sec": round(cursor_sec + s_dur, 2),
                "duration_sec": s_dur,
                "status": "REQUIERE_LICENCIA_LOCAL_USA_SPOTIFY",
                "playback_mode": "SPOTIFY_WEB_PLAYBACK",
            })
            cursor_sec += s_dur
            total_songs_sec += s_dur

    # Concatenate all mastered narration+score scenes into one continuous documentary master
    concat_list = Path("/tmp/glam_concat.txt")
    concat_list.write_text("\n".join(f"file '{p}'" for p in mixed_files) + "\n", encoding="utf-8")
    master_path = BASE / "masters" / "glam_rock_80s_narration_master.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(master_path),
        ],
        check=True,
    )
    master_dur = probe_duration(master_path)

    manifest = {
        "id": "glam-rock-80s",
        "title": "GLAM ROCK: Cuando el rock conquistó los 80",
        "subtitle": "Una hora entre guitarras, grandes escenarios, excesos y canciones que hicieron historia.",
        "narrator": "DJ Fredd",
        "brand": "TrackStories — La música tiene memoria",
        "artwork": "specials/glam-rock-80s/artwork/glam_rock_80s_cover.jpg",
        "narration_master_file": "specials/glam-rock-80s/masters/glam_rock_80s_narration_master.mp3",
        "narration_master_duration_sec": master_dur,
        "songs_duration_sec": round(total_songs_sec, 2),
        "total_experience_duration_sec": round(cursor_sec, 2),
        "mix_specs": {"target_lufs": -16, "true_peak_dbtp": -1.0, "sample_rate_hz": 48000},
        "segments": manifest_segments,
    }
    (BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"DONE! Narration master={master_dur}s, Songs={total_songs_sec}s, Total Experience={round(cursor_sec,2)}s", flush=True)


if __name__ == "__main__":
    main()
