#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 4:
"Resumen Semanal: IA, Diseño y Tech (16–23 Nov 2026)"
Relaxed, morning-radio style conversation between two friends:
  - Fred  (g.DEFAULT_FISH_VOICE)
  - María (1cb68a6f33be463ebb0902d4aa4740af)

Covers all 16 weekly stories across 5 blocks + Medellín local agenda,
with natural voice overlaps, laughter, humor, unexpected moments, and
the custom Drive background music bed (aparte_custom_bed.mp3).
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_04"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_MARIA = "1cb68a6f33be463ebb0902d4aa4740af"

# (id, speaker, gap_ms_before, text)
TURNS = [
    (
        "01_fred_intro", "fred", 0,
        "¡Muy buenos días, gente! Bienvenidos a una nueva edición matutina de Aparte. "
        "Hoy venimos en modo café largo y charla entre amigos con nuestro compilatorio semanal de noticias, del dieciséis al veintitrés de noviembre de 2026. "
        "María, dime la verdad... ¿sobreviviste a esta semana de noticias o ya te explotó la cabeza?"
    ),
    (
        "02_maria_intro", "maria", 180,
        "(laughing) ¡Hola, Fred! Mira, casi me explota dos veces: una con la bolsa y otra con los agentes de IA. "
        "Tenemos dieciséis historias buenísimas repartidas en cinco bloques: diseño y UX, inteligencia artificial, tecnología, creatividad y hasta agenda en Medellín. Así que sírvanse café y arranquemos sin solemnidad."
    ),
    # BLOQUE 1: UX, Sistemas de Diseño e Interfaces Agénticas
    (
        "03_fred_b1_ux", "fred", 320,
        "Arranquemos por nuestra casa: UX y sistemas de diseño. Esta semana se habló muchísimo de que las pantallas estáticas y los menús rígidos están cediendo paso a interfaces guiadas por intención. "
        "Hacia 2027, los diseñadores vamos a pasar menos tiempo moviendo botoncitos y más tiempo diseñando cómo comunicar límites de la IA sin frustrar al usuario, y poniendo la accesibilidad desde el minuto uno."
    ),
    (
        "04_maria_b1_ds", "maria", -220,
        "¡Y ahí conecta perfecto lo de Design Systems Collective! Porque un sistema de diseño ya no es una librería bonita en Figma. "
        "Ahora proponen tres capas: fundamentos, reglas y contexto. ¿Para quién? Para que agentes de código como Claude Code puedan leer tu sistema y generar componentes directo a producción sin pasar por maquetas eternas."
    ),
    (
        "05_fred_b1_atlassian", "fred", 240,
        "Eso me lleva a una que me sorprendió bastante en Lenny's Newsletter. Sherif Mansour, líder de IA en Atlassian, dijo que el trabajo real de un Product Manager es construir un cerebro compartido. "
        "Y ojo al dato: Atlassian está contratando más perfiles junior que nunca."
    ),
    (
        "06_maria_b1_juniors", "maria", -240,
        "¡Espera! ¿Más juniors? Pero si todo el mundo anda diciendo que la IA mató a los juniors... (chuckle)"
    ),
    (
        "07_fred_b1_juniors_r", "fred", 140,
        "Pues justo por eso: dicen que como los juniors no cargan diez años de mañas heredadas, adoptan flujos nativos de IA muchísimo más rápido. "
        "Y bueno, para cerrar el bloque de diseño con un toque filosófico: el Diccionario Cambridge eligió Humano como palabra del año 2026."
    ),
    (
        "08_maria_b1_humano", "maria", 200,
        "(laughing) Qué ironía tan poética... Y mira el estudio conductual que salió con eso: cuando alguien pide consejo a una IA, los demás lo perciben como menos sociable y menos confiable que si consultara a un humano. "
        "Ah, y en un experimento con más de mil doscientas personas, descubrieron que si eres extrovertido, te va mejor creativamente con una IA extrovertida. ¡Hasta la IA tiene que hacer match de personalidad!"
    ),
    # BLOQUE 2: IA, Modelos y Gobernanza
    (
        "09_fred_b2_claude", "fred", 420,
        "Pasemos al bloque de inteligencia artificial, que estuvo movidísimo. Anthropic soltó siete novedades de golpe: Claude Meetings, Whiteboards, Sheets, Data... básicamente quieren mudarte toda la oficina a una sola pestaña. "
        "Y me encantó el comando advisor: un modelo ligero hace el trabajo diario y solo llama al modelo grande, Fable 5.2, cuando la decisión se pone pesada."
    ),
    (
        "10_maria_b2_gemini", "maria", 200,
        "Y del otro lado, Gemini 4 Neon está dando de qué hablar en programación, simulaciones físicas y demos 3D interactivas dentro de Anti-Gravity a una fracción del costo. "
        "De hecho, en Every compararon GPT-6.2 Astra y Sol contra Gemini 4 Neon, y a Neon lo coronaron favorito para escribir y programar. "
        "Ah, y Mike Taylor propuso un truco buenísimo: deja de decirle a la IA escribe con tono cercano; muéstrale tus textos y pon a un modelo juez a afinar tus reglas a ciegas."
    ),
    (
        "11_fred_b2_mckinsey", "fred", 260,
        "Eso sí es práctico. Pero bajémosle un segundo al entusiasmo porque McKinsey lanzó una advertencia seria sobre agentes autónomos: "
        "dicen que la agencia no es una función técnica, es una transferencia de derechos de decisión. Cuando una IA ya no solo responde sino que ejecuta, ¿quién responde si mete la pata? Las juntas directivas ya están sudando frío."
    ),
    (
        "12_maria_b2_aceite", "maria", 220,
        "Y hablando de sudar frío... ¿leíste la historia de Juan Merodio sobre el darwinismo cognitivo? "
        "Un productor de aceite de oliva que dependía de textos hechos por IA se quedó completamente en blanco diez segundos eternos frente a un comprador japonés porque no dominaba su propio discurso. (sigh) ¡Qué pesadilla!"
    ),
    (
        "13_fred_b2_socratico", "fred", -200,
        "Diez segundos en una reunión de negocios se sienten como tres horas. (chuckle) "
        "La receta que da me parece oro puro: usa la IA al menos una hora a la semana como tutor socrático que te explique cosas difíciles y te haga examen en voz alta. Que te vuelva más capaz, no más perezoso."
    ),
    (
        "14_maria_b2_geopolitica", "maria", 280,
        "Y para cerrar IA con geopolítica: España sacó el Real Decreto 1032 de 2026 obligando a los grandes centros de datos a cubrir el ochenta por ciento de su electricidad con renovables hora a hora, justo con Amazon invirtiendo treinta y tres mil setecientos millones de euros en Aragón. "
        "Mientras tanto, Donald Trump amenaza con aranceles fuertes a tecnológicas estadounidenses que monten centros de datos fuera del país. Tener fierros físicos en tu territorio hoy es soberanía pura."
    ),
    # BLOQUE 3: Tecnología, Infraestructura y Seguridad
    (
        "15_fred_b3_infra", "fred", 420,
        "Vámonos al bloque tech, que estuvo intenso. ByteByteGo nos dio un repaso súper claro: Docker empaqueta contenedores en una máquina, Kubernetes los orquesta y los autocuración en muchos nodos; Redis vuela en RAM respaldado por AOF y RDB; "
        "y explicaron cómo funcionan las marcas de agua criptográficas en textos de Claude... aunque en escritura técnica todavía hay falsos negativos."
    ),
    (
        "16_maria_b3_nvidia", "maria", 220,
        "Y aquí viene el terremoto de la semana en bolsa: la SEC amplió su revisión contable sobre Nvidia y la acción se desplomó un catorce por ciento. "
        "De paso arrastró a Anthropic casi un nueve por ciento abajo en su segundo día en el Nasdaq. Todos hablando otra vez de burbuja en infraestructura de cómputo."
    ),
    (
        "17_fred_b3_riemann", "fred", 200,
        "¡Espera! Que en medio de esa caída, un matemático de Anthropic salió a decir que encontró con Claude una posible demostración de la hipótesis de Riemann. "
        "Obvio falta verificación, pero imagínate esa semana: te cae la acción un nueve por ciento el martes y el miércoles casi resuelves uno de los mayores misterios de las matemáticas. (laughing)"
    ),
    (
        "18_maria_b3_signal", "maria", -220,
        "(laughing) ¡Nadie se aburre en 2026! Y un aplauso para Signal, que activó por defecto el bloqueo de capturas de pantalla en iOS 27 y Android para que los asistentes del sistema no anden leyendo tus chats privados. Privacidad ante todo."
    ),
    # BLOQUE 4: Diseño, Branding y Creatividad
    (
        "19_fred_b4_contra", "fred", 420,
        "Cambiemos de ritmo al bloque de creatividad y branding. Contra Labs analizó a más de dos millones de creativos independientes y llegó a una conclusión contundente: "
        "cuando ejecutar se vuelve gratis e instantáneo, el criterio estético y el gusto humano son el único activo realmente escaso."
    ),
    (
        "20_maria_b4_branding", "maria", 200,
        "Totalmente, y por eso disfruté tanto la curaduría manual, cero algoritmos, de BRRRANDING esta semana: destacaron el rediseño de TapTap, la Sociedad Hortícola de Pensilvania que tiene doscientos años y la app Fluz. Se nota cuando hay ojo humano detrás."
    ),
    (
        "21_fred_b4_allende", "fred", 240,
        "Y me encantó la nota de Jardín Mental sobre Isabel Allende. ¿Sabías que desde 1981 empieza todos sus libros exactamente el ocho de enero? "
        "Empezó escribiendo en una cocina después de turnos de doce horas, sin esquema previo, y reescribe casi el noventa y ocho por ciento de sus manuscritos en papel. "
        "Eso combinado con la técnica de inversión: definir primero el final para construir la historia hacia atrás."
    ),
    (
        "22_maria_b4_allende_r", "maria", 180,
        "(chuckle) Qué disciplina tan brutal. Y uno que a veces no puede ni escribir un correo de tres párrafos sin revisar el celular cuatro veces."
    ),
    # BLOQUE 5: Fintech y Agenda Local Medellín
    (
        "23_fred_b5_fintech", "fred", 400,
        "Cerramos las noticias con fintech y nuestra agenda local. En Estados Unidos, OneMain Financial recibió luz verde de Utah y la FDIC para abrir OneMain Bank con trescientos cuarenta y un millones de capital, lo que les permitirá ofrecer tasas uniformes del treinta y seis por ciento anual en todo el país. "
        "Mientras tanto, la fintech Dave pidió licencia bancaria nacional... justo en medio de demandas del Departamento de Justicia por patrones oscuros y comisiones en adelantos de efectivo."
    ),
    (
        "24_maria_b5_medellin", "maria", 240,
        "¡Uy, qué momento para pedir licencia bancaria! (laughing) "
        "Pero vámonos a algo mucho más sabroso: la agenda de esta semana en Medellín. El jueves veintiséis de noviembre está Venture Mind, para hablar de IA y vehículos de inversión en el Hotel Belisario. "
        "El viernes veintisiete, la jornada creativa Muestra tus Chimbadas en La House Of Demons... ¡me encanta ese nombre!"
    ),
    (
        "25_fred_b5_alumbrados", "fred", -200,
        "(laughing) Solo en Medellín un evento creativo tiene ese nombre tan genial. Y además llega el encendido oficial de los Alumbrados Navideños en Parques del Río. Plan completo para salir de la pantalla un rato."
    ),
    # CIERRE Y DEBATE
    (
        "26_maria_cierre", "maria", 380,
        "Antes de irnos, dejemos tres preguntas sobre la mesa para que las piensen con su café: "
        "Si los sistemas de diseño ahora los leen agentes de IA, ¿qué va a diferenciar a un diseñador senior en 2027? "
        "¿Estamos usando la IA como tutor o cayendo en el darwinismo cognitivo? "
        "Y cuando un agente autónomo cometa un error financiero o de privacidad... ¿quién paga los platos rotos?"
    ),
    (
        "27_fred_outro", "fred", 240,
        "Tremendas preguntas para arrancar la semana. María, un gustazo compartir este café contigo como siempre. "
        "Gracias a todos por acompañarnos en este resumen semanal de Aparte. Ideas que merecen ser escuchadas. ¡Que tengan una semana increíble!"
    ),
    (
        "28_maria_outro", "maria", 160,
        "¡Nos escuchamos la próxima semana! Chao, chao."
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

    for tid, speaker, gap_ms, text in TURNS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"
        voice_id = VOICE_FRED if speaker == "fred" else VOICE_MARIA

        if not (mp3.exists() and mp3.stat().st_size > 4000):
            print(f"[TTS] {tid} ({speaker})...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), reference_id=voice_id, model="drama-3")
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
        clips.append((speaker, gap_ms, load_wav_mono(wav)))

    lead_in_samples = int(2.2 * sr)
    tail_samples = int(4.0 * sr)

    cursor = lead_in_samples
    placements = []
    max_end = lead_in_samples
    for speaker, gap_ms, audio in clips:
        start = max(lead_in_samples, cursor + int(gap_ms * sr / 1000.0))
        end = start + len(audio)
        placements.append((speaker, start, audio))
        cursor = end
        if end > max_end:
            max_end = end

    total_samples = max_end + tail_samples
    stereo = np.zeros((total_samples, 2), dtype=np.float32)

    for speaker, start, audio in placements:
        if speaker == "fred":
            l_gain, r_gain = 1.06, 0.94
        else:
            l_gain, r_gain = 0.94, 1.06
        end = start + len(audio)
        stereo[start:end, 0] += audio * l_gain
        stereo[start:end, 1] += audio * r_gain

    peak = np.max(np.abs(stereo)) + 1e-9
    if peak > 0.95:
        stereo = stereo * (0.95 / peak)

    voice_full = Path("/tmp/aparte_04_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled 2-host weekly news dialogue: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_04_bed.wav")
    print(f"[BED] Rendering custom Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_resumen_semanal_nov_2026.mp3"
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
