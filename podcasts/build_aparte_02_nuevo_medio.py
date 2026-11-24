#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 2: "A cada nuevo medio se le tacha de trampa"
Conversational 2-host podcast featuring:
  - Fred  (5b32e58542a740e59792a3573f337645)
  - Lucía (bfed5c0810a347dbb62e8ccce7f59c48)

Features natural pauses, laughter, hesitation, thinking out loud, real
interruption overlaps (negative gap_ms), subtle stereo panning, and the
upbeat morning-news Music Bed with sidechain ducking mastered to -16 LUFS.
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
from build_aparte_podcast import generate_editorial_bed, probe_dur

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_02"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_LUCIA = "1cb68a6f33be463ebb0902d4aa4740af"

# Each turn: (id, speaker, gap_ms_before, text)
# Negative gap_ms_before creates a natural conversational interruption/overlap.
TURNS = [
    (
        "01_fred_intro", "fred", 0,
        "Bienvenidos a Aparte. Ideas que merecen ser escuchadas. Hoy no estoy solo en el micrófono, estoy con mi coanfitriona Lucía, "
        "y traemos un tema que, la verdad, a los dos nos tocó el ego hace no mucho. ¿Cómo estás, Lucía?"
    ),
    (
        "02_lucia_saludo", "lucia", 250,
        "(chuckle) Hola, Fred. Muy bien, aunque... a ver, déjame decirlo desde ya para que conste en actas: yo también estaba en contra. "
        "Yo era súper escéptica con todo esto de la inteligencia artificial."
    ),
    (
        "03_fred_monet", "fred", 200,
        "Es que el título de hoy lo resume todo: a cada nuevo medio se le tacha de trampa. "
        "Y fíjate en este dato para arrancar: la obra Impresión, sol naciente de Monet... no habría existido si alguien no hubiera inventado el medio adecuado."
    ),
    (
        "04_lucia_chiang", "lucia", 300,
        "Totalmente. Pero antes de llegar a Monet, déjame confesar mi etapa de escéptica profesional. "
        "Cuando Ted Chiang escribió en The New Yorker que la inteligencia artificial no iba a crear arte, uff, me sentí reivindicada. "
        "Lo reenvié a medio mundo. A gente que ni siquiera me lo había pedido. (laughing) Perdón a todos esos amigos."
    ),
    (
        "05_fred_maquina", "fred", -250,
        "(chuckle) Lo típico, el reenvío pasivo-agresivo de domingo. Pero el argumento de Chiang era bueno, ¿no? "
        "Eso de que el arte es la suma de miles de pequeñas decisiones."
    ),
    (
        "06_lucia_boligrafos", "lucia", 220,
        "Sí, y que si una máquina toma la mayoría por ti, le quita la esencia. En las cenas yo lo resumía diciendo que la IA era, cito textual, "
        "una máquina expendedora con ambiciones... lo que provocaba unas miradas de incredulidad tremendas. "
        "Es que escribir es mi terreno, Fred. Tengo como catorce bolígrafos favoritos y opiniones muy firmes sobre los puntos y comas."
    ),
    (
        "07_fred_gato", "fred", 180,
        "Me imagino tu cara cuando apareció una máquina prometiendo escribir por ti."
    ),
    (
        "08_lucia_oxford", "lucia", 150,
        "(laughing) Reaccioné exactamente como un gato ante un gato nuevo: me quedé muy quieta, la observé desde el otro lado de la habitación y esperé a que se fuera. "
        "Y la primera vez que me enfadé de verdad fue cuando un cliente me dijo que mi escritura era demasiado artificial... por usar mi querida coma de Oxford y mi confiable raya. "
        "(sigh) A partir de ahí se volvió personal."
    ),
    (
        "09_fred_giro", "fred", 450,
        "Uf, qué golpe bajo. Pero algo cambió, ¿verdad? Porque no estamos aquí solo para quejarnos."
    ),
    (
        "10_lucia_principiante", "lucia", 320,
        "No, y aquí viene lo raro. La IA nunca ha creado nada de lo que yo me sienta orgullosa. "
        "Pero hizo algo más extraño y, sinceramente, mejor: me dio el valor suficiente para volver a ser principiante en ámbitos que durante años me habían dado miedo explorar."
    ),
    (
        "11_fred_portero", "fred", 300,
        "A ver, explícame eso. Porque suena a que el problema no era la tecnología, sino algo más... emocional."
    ),
    (
        "12_lucia_portero", "lucia", 250,
        "Es que cada medio tiene su portero. Y no hablo de una persona real, es más bien una sensación. "
        "En un taller de cerámica, es la sensación de que todos saben dónde está escondido el mejor esmalte y acordaron no decírtelo. "
        "En programación, es la sospecha de que ya deberías saber qué es una terminal... antes de que te permitan preguntar qué es una terminal."
    ),
    (
        "13_fred_impostor", "fred", -300,
        "¡Exacto! El portero no comprueba tu talento, comprueba si pareces encajar. "
        "Y uno se acerca a la puerta, hace contacto visual, dice... mmm, no importa, yo soy diseñador o escritor, esto no es lo mío, y se va a casa."
    ),
    (
        "14_lucia_35anos", "lucia", 220,
        "El famoso síndrome del impostor. Me llevó como treinta y cinco años aceptar que, sin importar el éxito, todos lo sentimos. "
        "Y aquí es donde la IA tuvo un papel más grande del que me gustaría admitir. No porque hiciera el trabajo por mí, sino porque por fin pude hacer la pregunta tonta. "
        "A las once de la noche. Cuarenta veces seguidas. Sin que nadie suspirara, mirara el móvil o me dijera: bueno, eso es bastante básico."
    ),
    (
        "15_fred_tobogan", "fred", 280,
        "Me encanta esa imagen: la curva de aprendizaje deja de ser la cuesta de Sísifo y se convierte en un tobogán. "
        "A ver, ¿qué tipo de preguntas tontas hacías a las once de la noche?"
    ),
    (
        "16_lucia_tres_preguntas", "lucia", 240,
        "Pues... mmm, por ejemplo: ¿cómo se escribe un personaje verdaderamente tridimensional? ¿Qué es un repositorio web? ¿Y qué es lo que no entiendo de Picasso? "
        "Tres preguntas, tres formatos. Mi yo del pasado habría necesitado un curso, un amigo desarrollador muy paciente y media licenciatura en historia del arte. "
        "Mi nueva yo solo necesitaba una noche... y cero dignidad. (laughing)"
    ),
    (
        "17_fred_stanford", "fred", 300,
        "Y hay ciencia detrás de eso, ojo. Cuando investigadores de Stanford y el MIT le dieron un asistente de IA a más de cinco mil agentes de atención al cliente, "
        "los más nuevos y con menos experiencia lograron un treinta y cuatro por ciento más de productividad por hora. ¿Y los veteranos? Prácticamente sin cambios."
    ),
    (
        "18_lucia_traduccion", "lucia", 200,
        "Traducción: la IA es un desperdicio para los expertos y un regalo para los principiantes. "
        "Y en cada medio nuevo... ¿adivina quién es el principiante? Resultó que, en gran parte, yo misma me había estado cerrando la puerta."
    ),
    (
        "19_fred_historia", "fred", 550,
        "Y lo más reconfortante de todo es que ya hemos estado aquí antes. Muchas, muchísimas veces. "
        "¿Sabes cuál fue el primer pánico tecnológico de la historia? Alrededor del año 370 antes de Cristo, Platón transcribió las quejas de Sócrates... ¡sobre la escritura!"
    ),
    (
        "20_lucia_socrates", "lucia", -280,
        "(laughing) ¡La escritura! Mi terreno. Sócrates decía que escribir haría que la gente olvidara y solo tuviera una apariencia de sabiduría. "
        "Y lo más irónico es que solo sabemos que Sócrates odiaba escribir... porque alguien lo escribió."
    ),
    (
        "21_fred_trithemius", "fred", 260,
        "Y espérate, que en 1492 el abad alemán Johannes Trithemius escribió Elogio de los escribas, defendiendo que los monjes debían seguir copiando libros a mano "
        "porque la imprenta los volvería perezosos. ¿Y qué hizo después con su libro?"
    ),
    (
        "22_lucia_imprenta", "lucia", 150,
        "Lo mandó imprimir. (laughing) ¡Menudo personaje! Un ícono absoluto."
    ),
    (
        "23_fred_baudelaire", "fred", 280,
        "Y saltemos a 1859. Charles Baudelaire, en el Salón de París, anunció que la fotografía era el escondite de los pintores perezosos y sin talento. "
        "Si hubiera tenido sección de comentarios en internet, viviría metido ahí. Y por esa misma época, Paul Delaroche declaró que la pintura había muerto."
    ),
    (
        "24_lucia_pintura", "lucia", 250,
        "Claro, la pintura lleva muerta unos ciento sesenta y cinco años y goza de una salud excelente. Tiene galerías, podcasts y probablemente un fondo fiduciario. "
        "Mientras tanto, la fotografía se volvió un arte con sus propios genios... y sus propios esnobs que ahora dicen exactamente lo mismo de las cámaras de los teléfonos."
    ),
    (
        "25_fred_tubo", "fred", 380,
        "Es un patrón que se repite. Cada medio nuevo es tachado de trampa por quienes dominan el anterior. "
        "Y aquí volvemos a Monet y al tubo de pintura. Antes de 1841, los pintores guardaban el óleo en vejigas de cerdo atadas con cuerda."
    ),
    (
        "26_lucia_renoir", "lucia", 200,
        "Qué imagen tan poco glamurosa... Hasta que un retratista estadounidense sin recursos, John Goffe Rand, patentó el tubo de pintura plegable. "
        "De repente, la pintura se volvió portátil, los artistas salieron al aire libre, y Renoir dijo después que sin esos tubos no habría habido ni Monet, ni Cézanne, ni Impresionismo. "
        "Más fácil no significaba peor. Significaba que más gente podía entrar a la sala."
    ),
    (
        "27_fred_sennett", "fred", 500,
        "Ahora, hablemos de artesanía. El sociólogo Richard Sennett dice que la técnica es una conversación con el material. "
        "Tú presionas, el material se resiste, y esa resistencia te obliga a mejorar. La madera tiene vetas, la arcilla se desmorona si te impacientas..."
    ),
    (
        "28_lucia_acuarela", "lucia", -220,
        "Y la acuarela hace lo que le da la gana y se seca con una forma que parece la de un familiar decepcionado. (chuckle) "
        "Pero, ¿sabes qué? La IA también se defiende. Solo que de una manera más humillante: hace exactamente lo que dijiste en lugar de lo que querías decir. "
        "A menudo con entusiasmo desbordado y usando viñetas para recalcarlo. ¡Qué horror!"
    ),
    (
        "29_fred_brecha", "fred", 260,
        "Es una evaluación diaria de tu propia claridad. Esa brecha entre la idea en tu cabeza y la frase que escribiste tiene una textura. "
        "Y aprender a sentirla... bueno, eso también es un medio."
    ),
    (
        "30_lucia_eno", "lucia", 300,
        "Exacto. Brian Eno escribió en su diario en 1995 que todo lo que resulta extraño y feo de un nuevo medio termina convirtiéndose en su sello distintivo. "
        "Así que ahora miro con ternura los tics de la IA: los dedos extra, el entusiasmo incesante, la palabra profundizar. "
        "En veinte años alguien los va a añadir a propósito y lo va a llamar estilo vintage. (chuckle)"
    ),
    (
        "31_fred_fluido", "fred", 480,
        "Pero ojo, tampoco vamos a ponernos en modo futurista ciego publicando fotos del amanecer diciendo que el futuro ya está aquí. "
        "Hay una advertencia importante: el estudio donde le dieron a escritores ideas generadas por IA. Las historias fueron más creativas... pero se volvieron más parecidas entre sí."
    ),
    (
        "32_lucia_recipiente", "lucia", 280,
        "Sí, todos mejoraron un poco y todos se volvieron un poco más iguales. "
        "Antes yo decía que la IA era un medio fluido como un cumplido, pero se me olvidó lo que hacen los fluidos: el agua no tiene forma propia. Adopta la forma de su recipiente. "
        "Y el recipiente eres tú. Bueno... a menos que prefieras ser un Tupperware. (laughing)"
    ),
    (
        "33_fred_criterio", "fred", 220,
        "(chuckle) Tu gusto, tu peculiaridad, eso que solo tú notas. Una herramienta que vuelve competente a cualquiera solo amenaza a quien su única virtud era ser competente."
    ),
    (
        "34_lucia_coraje", "lucia", 350,
        "Por suerte, siempre he sido más rebelde que competente. Y al final, la IA no me enseñó a programar ni a pintar. "
        "Me enseñó que empezar desde cero es posible. Que haces primero la pregunta tonta y luego creas la versión imperfecta. "
        "Es coraje líquido, Fred: sin resaca y sin mensajes de texto de los que te arrepientas al día siguiente. "
        "El portero sigue ahí, en la puerta de los medios que aún no he probado... solo que ahora se ve más pequeño. Como alguien a quien podría vencer en una batalla de rap."
    ),
    (
        "35_fred_cierre", "fred", 550,
        "(chuckle) Me quedo con eso para cerrar el episodio. ¿Cuál es el punto de todo esto? Vuelve a ser principiante. A propósito. "
        "Elige hoy ese medio que siempre te dio miedo probar, ese que tiene al portero más intimidante. Hazle la pregunta tonta esta noche. "
        "Y luego ve y crea algo feo con tus propias manos. Lucía, un placer enorme."
    ),
    (
        "36_lucia_outro", "lucia", 220,
        "Un placer, Fred. Y gracias a todos por acompañarnos. Esto fue Aparte. Ideas que merecen ser escuchadas."
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
    clips = []  # (speaker, gap_ms, mono_float32_array)

    for tid, speaker, gap_ms, text in TURNS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"
        voice_id = VOICE_FRED if speaker == "fred" else VOICE_LUCIA

        if not (mp3.exists() and mp3.stat().st_size > 4000):
            print(f"[TTS] {tid} ({speaker})...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), reference_id=voice_id, model="drama-3")
        else:
            print(f"[REUSE] {tid}.mp3", flush=True)

        # Trim leading/trailing silence lightly and resample to 48kHz mono
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

    # Assemble stereo timeline with subtle podcast desk panning
    # Fred: slightly left (-12%), Lucía: slightly right (+12%)
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

    voice_full = Path("/tmp/aparte_02_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled 2-host dialogue: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_02_bed.wav")
    print(f"[BED] Generating Morning-Show Jazz-Pop music bed ({total_dur}s)...", flush=True)
    from generate_podcast_music import render_bed_wav
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_nuevo_medio_trampa.mp3"
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
