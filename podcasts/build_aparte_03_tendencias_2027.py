#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 3: "10 tendencias de diseño UI/UX para 2027"
Morning-radio style conversational 2-host podcast featuring:
  - Fred  (g.DEFAULT_FISH_VOICE)
  - María (43536a5ca1a34eee8ca1cd737af551c1)

Alternates all 10 UI/UX trends for 2027 with lively debate, agreement/disagreement,
practical additions, humor, laughter, varied intonations, natural interruption
overlaps, subtle stereo desk panning, and the 112 BPM morning-news Music Bed.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_03"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_MARIA = "1cb68a6f33be463ebb0902d4aa4740af"

# (id, speaker, gap_ms_before, text)
TURNS = [
    (
        "01_fred_intro", "fred", 0,
        "¡Muy buenos días y bienvenidos a Aparte! Ideas que merecen ser escuchadas. "
        "Hoy tenemos café recién hecho, energía de programa matutino y una invitada de lujo en el micrófono: mi coanfitriona María. ¿Cómo amaneciste hoy, María?"
    ),
    (
        "02_maria_saludo", "maria", 200,
        "¡Hola, Fred! Feliz de estar aquí, con mi café doble en mano y lista para debatir. "
        "Porque hoy traemos un temazo: las diez tendencias de diseño UI y UX a tener en cuenta en 2027. Y ya te aviso que en varias vamos a chocar un poquito. (chuckle)"
    ),
    (
        "03_fred_setup", "fred", 180,
        "(laughing) ¡Así me gusta! Porque 2027 pinta distinto: ya no basta con hacer pantallas bonitas. "
        "Vamos a hacer esto dinámico: uno lanza una tendencia y el otro responde, debate, contradice o suma. Arranco yo con la número uno: experiencias impulsadas por IA y con agentes."
    ),
    (
        "04_fred_t1", "fred", 220,
        "La IA está dejando atrás los chatbots simples. Imagina abrir una app de viajes y decir: quiero ir a Singapur el mes que viene, búscame vuelos baratos y hotel céntrico. "
        "El agente compara, arma todo y casi que te reserva. El reto para nosotros ya no es el buscador, sino diseñar indicadores de progreso, confirmaciones claras y botones fáciles para deshacer."
    ),
    (
        "05_maria_t1_debate", "maria", -220,
        "A ver, estoy de acuerdo... ¡pero con un asterisco gigante! Porque me da pánico que un agente reserve el vuelo equivocado mientras yo pestañeo. (laughing) "
        "El botón de deshacer y la confirmación antes de pagar no son un extra, son supervivencia. El objetivo nunca puede ser sacar al usuario del control."
    ),
    (
        "06_maria_t2", "maria", 350,
        "Bueno, paso yo a la número dos, que está pegadita a la tuya: interfaz de usuario generativa. "
        "En lugar de mostrarle el mismo dashboard aburrido a todo el mundo, la interfaz cambia según lo que pidas. Si un dueño de negocio pregunta por ingresos mensuales, le aparece un gráfico limpio; si otro pide detalle, le sale una tabla con filtros y exportación."
    ),
    (
        "07_fred_t2_debate", "fred", 200,
        "Uff, aquí voy a hacer de abogado del diablo, María. ¿No te parece que si la pantalla cambia cada vez que entras, el usuario se pierde? "
        "A la gente le gusta saber dónde está el botón de siempre. Si no diseñamos componentes flexibles con reglas muy estrictas, eso se vuelve un carnaval."
    ),
    (
        "08_maria_t2_reply", "maria", -240,
        "¡Totalmente! Por eso no desaparecemos los diseñadores: dejamos de dibujar pantallas sueltas para diseñar los límites y las reglas del juego."
    ),
    (
        "09_fred_t3", "fred", 380,
        "Y eso me da el pase perfecto para la tendencia número tres: sistemas de diseño preparados para la IA. "
        "Antes un design system era para que humanos no pusieran cinco tonos distintos de azul. Ahora tus tokens, tu tipografía, tus espaciados y tu documentación son el contexto que lee la IA para construir pantallas coherentes."
    ),
    (
        "10_maria_t3_debate", "maria", 220,
        "(chuckle) Qué risa, porque todos esos equipos que decían: luego documentamos el sistema de diseño... ahora están corriendo en círculos. "
        "Estoy cien por ciento de acuerdo contigo: si tus convenciones de nombres son un desastre, la IA te va a multiplicar el desastre a velocidad luz. Diseño y código tienen que hablar el mismo idioma."
    ),
    (
        "11_maria_t4", "maria", 380,
        "Vamos con la número cuatro: experiencias multimodales, más allá del tacto y el clic. "
        "Imagina estar en una app de compras: subes la foto de una chaqueta, preguntas por voz si hay talla mediana en negro y navegas las recomendaciones en pantalla. Voz, texto, imagen y gestos trabajando juntos."
    ),
    (
        "12_fred_t4_debate", "fred", 220,
        "Me encanta cuando tiene sentido, pero ojo con el síndrome de meterle voz a todo. "
        "Nadie quiere estar en el bus a las siete de la mañana gritándole a su celular: ¡transfiere cincuenta dólares a mi primo! (laughing) "
        "La clave está en transiciones fluidas y dar siempre alternativas accesibles."
    ),
    (
        "13_maria_t4_reply", "maria", -200,
        "(laughing) ¡Por favor, no en el bus! Totalmente, la multimodalidad debe sumar naturalidad, no vergüenza ajena."
    ),
    (
        "14_fred_t5", "fred", 380,
        "Tendencia número cinco, me toca: experiencias hiperpersonalizadas y adaptativas. "
        "Un novato y un experto abren la misma app pero buscan cosas distintas. Una app financiera puede destacarte alertas de gasto según tus hábitos, o una plataforma de cursos recomendarte la lección exacta según tu progreso."
    ),
    (
        "15_maria_t5_debate", "maria", 240,
        "Mmm... aquí tengo sentimientos encontrados, Fred. Me gusta que la app sea inteligente, pero odio cuando un algoritmo me esconde funciones que yo usaba ayer solo porque decidió que ya no las necesito. "
        "La personalización tiene que sentirse relevante, nunca extraña ni invasiva. Y el usuario siempre debe poder apagarla."
    ),
    (
        "16_maria_t6", "maria", 380,
        "Y hablando de pensar en todos, lanzo la número seis: diseño que prioriza la accesibilidad. "
        "No es nueva, pero en 2027 deja de ser un checklist al final del proyecto. Contraste de color, botones táctiles decentes, navegación por teclado, mensajes de error claros y pautas WCAG desde el día uno."
    ),
    (
        "17_fred_t6_debate", "fred", 200,
        "Aquí cero debate, cien por ciento de acuerdo, y sumo un dato práctico: la accesibilidad no es solo para personas con discapacidad. "
        "Si alguna vez intentaste leer un texto gris clarito sobre fondo blanco bajo el sol del mediodía... ¡felicidades, necesitabas accesibilidad! (chuckle) Beneficia a absolutamente todos."
    ),
    (
        "18_fred_t7", "fred", 380,
        "Me toca la siete, que va directo a la confianza: experiencia de usuario centrada en la privacidad. "
        "Si una app financiera con IA te recomienda qué hacer con tu dinero, pero no tienes idea de qué hace con tus datos, ¿confiarías en ella? Obvio no. "
        "Necesitamos permisos claros, configuraciones simples y explicaciones transparentes de por qué la IA recomienda algo."
    ),
    (
        "19_maria_t7_debate", "maria", 220,
        "(sigh) ¡Qué necesario! Porque hoy en día los ajustes de privacidad parecen un laberinto diseñado para que te rindas y le des a aceptar todo. "
        "Si escondes controles en cinco submenús, pierdes al usuario. La transparencia bien diseñada hoy es una ventaja competitiva enorme."
    ),
    (
        "20_maria_t8", "maria", 380,
        "Paso a la número ocho, que es música para mis oídos: interfaces tranquilas y minimalistas. "
        "Estamos saturados de notificaciones, pop-ups y banners peleando por nuestra atención. Imagina un gestor de proyectos que en vez de quince gráficos te muestre solo tres cosas: qué requiere tu atención, qué está pasando ahora y qué sigue."
    ),
    (
        "21_fred_t8_debate", "fred", -220,
        "¡Amén a eso! Aunque, ojo, no confundamos minimalismo con dejar la pantalla vacía y sin pistas. "
        "El minimalismo reflexivo usa jerarquía visual, espacio en blanco y divulgación progresiva: te muestro lo importante primero y el detalle solo cuando lo pides."
    ),
    (
        "22_fred_t9", "fred", 380,
        "Vamos entrando en la recta final con la número nueve: experiencias fluidas y multidispositivo. "
        "Nadie vive en una sola pantalla. Empiezas un documento en el celular camino al trabajo, lo sigues en la laptop y lo terminas en la tableta. "
        "El usuario espera continuidad total, progreso sincronizado y no tener que repetir nada."
    ),
    (
        "23_maria_t9_debate", "maria", 220,
        "¡Me pasa todos los días! Y qué rabia da cuando cambias del celular a la computadora y la app te pregunta: ¿quién eres y qué estabas haciendo? (laughing) "
        "Ya no basta con que sea responsivo; hay que preservar el contexto entre dispositivos."
    ),
    (
        "24_maria_t10", "maria", 380,
        "Y cierro la lista con la número diez, que me encanta: diseño visual más expresivo y movimiento con propósito. "
        "Como la IA hace facilísimo sacar plantillas genéricas, las marcas necesitan personalidad real: tipografía audaz, colores distintivos, ilustraciones propias, texturas sutiles y microinteracciones que comuniquen qué acaba de pasar."
    ),
    (
        "25_fred_t10_debate", "fred", 220,
        "Qué buen cierre, María. Porque veníamos hablando de minimalismo y de IA, y alguien podría pensar que todo en 2027 va a ser aburrido e igualito. "
        "Pero ojo: expresión sí, decoración gratuita no. Si una animación tarda tres segundos y me bloquea el botón, la voy a odiar por más bonita que sea. (chuckle) Personalidad y claridad tienen que ir de la mano."
    ),
    (
        "26_maria_habilidades", "maria", 450,
        "Totalmente. Y para quienes nos escuchan tomando café y se preguntan en qué enfocarse para 2027, el resumen es clarísimo: "
        "fundamentos sólidos de UX, alfabetización en IA, sistemas de diseño escalables, pensamiento de producto y negocio, accesibilidad diaria y buena comunicación visual."
    ),
    (
        "27_fred_cierre", "fred", 280,
        "No hace falta perseguir cada moda ni instalar veinte herramientas nuevas por semana. "
        "Lo único que nunca cambia es quién está al centro: las personas. "
        "Me quedo con esta frase para cerrar la mañana: no te limites a aprender a usar la próxima herramienta de diseño. Aprende a pensar como un diseñador. "
        "María, ¡qué gran conversación!"
    ),
    (
        "28_maria_outro", "maria", 200,
        "¡La pasé increíble, Fred! Cuéntennos cuál de estas diez tendencias creen que tendrá más impacto en 2027. "
        "Esto fue Aparte. Ideas que merecen ser escuchadas. ¡Hasta la próxima!"
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

    voice_full = Path("/tmp/aparte_03_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled 2-host morning-show dialogue: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_03_bed.wav")
    print(f"[BED] Generating Morning-Show Jazz-Pop music bed ({total_dur}s)...", flush=True)
    from generate_podcast_music import render_bed_wav
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_tendencias_uiux_2027.mp3"
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
