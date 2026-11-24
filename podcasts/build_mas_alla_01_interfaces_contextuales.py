#!/usr/bin/env python3
"""
Builds Podcast: "Más allá de la interfaz — ¿Y si las interfaces aprendieran a entendernos?"
Co-hosts:
  - Fred  (g.DEFAULT_FISH_VOICE)
  - María (1cb68a6f33be463ebb0902d4aa4740af)

Follows the user's exact script with laughter, pauses, brief voice overlap,
subtle stereo panning, and the custom Drive background music bed.
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
CHUNKS_DIR = OUT_DIR / "chunks_mas_alla_01"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_MARIA = "1cb68a6f33be463ebb0902d4aa4740af"

# (id, speaker, gap_ms_before, text)
TURNS = [
    ("01_fred", "fred", 0, "María, te voy a hacer una pregunta. ¿Cuántas veces has entrado a una aplicación para hacer algo relativamente sencillo y has terminado pensando: ¿por qué me están haciendo la vida tan difícil?"),
    ("02_maria", "maria", 200, "(chuckle) ¿Hoy o durante toda mi existencia?"),
    ("03_fred", "fred", 180, "(laughing) Bueno, hoy."),
    ("04_maria", "maria", 160, "Es que pasa muchísimo. Te piden información que ya tienen, te muestran mensajes que no entiendes, te ofrecen cosas que no necesitas... Uno termina trabajando para la aplicación, en lugar de que la aplicación trabaje para uno."),
    ("05_fred", "fred", 180, "¡Exactamente! Y ahí comienza el proyecto del que queremos hablar hoy: las interfaces contextuales."),
    ("06_maria", "maria", 200, "Que suena como un término sofisticadísimo, pero tiene que ver con algo muy humano: entender qué necesita una persona en un momento determinado."),
    ("07_fred", "fred", 220, "Y este proyecto nace de una pregunta mucho más grande. ¿Cómo podemos diseñar experiencias digitales que ayuden a que las personas se sientan exitosas en cada interacción?"),
    ("08_maria", "maria", 200, "Ojo con esa palabra: exitosas. Porque no es simplemente que la persona termine un formulario."),
    ("09_fred", "fred", 140, "Claro."),
    ("10_maria", "maria", 140, "Es que entienda lo que está haciendo, tenga confianza y pueda resolver aquello por lo que realmente entró."),

    # El problema de diseñar para todo el mundo
    ("11_fred", "fred", 500, "Imagínate que entras a una cafetería todos los días. Siempre pides el mismo café. Después de seis meses, la persona que te atiende te sigue preguntando si sabes qué es un cappuccino."),
    ("12_maria", "maria", 180, "(laughing) Y te entrega un tutorial de cinco pasos para tomarte el café."),
    ("13_fred", "fred", 160, "¡Eso! Y adicionalmente te ofrece una tarjeta de crédito antes de entregártelo."),
    ("14_maria", "maria", 160, "(laughing) Ya me quiero ir de esa cafetería."),
    ("15_fred", "fred", 260, "(chuckle) Pues, de alguna manera, eso es lo que hacemos cuando diseñamos experiencias digitales que no tienen en cuenta el contexto. Tratamos igual a personas que tienen necesidades diferentes, conocimientos diferentes y momentos de vida completamente distintos."),
    ("16_maria", "maria", 220, "Y las organizaciones tienen cantidades enormes de información sobre sus clientes. Saben qué productos tienen, qué operaciones realizan, qué procesos han comenzado..."),
    ("17_fred", "fred", 180, "Pero esa información no siempre se convierte en una mejor experiencia."),
    ("18_maria", "maria", 160, "Exacto. Tener información no significa entender a alguien."),
    ("19_fred", "fred", 200, "Esa es una de las premisas centrales del proyecto. El valor no está necesariamente en tener más datos, sino en saber qué decisiones tomar con ellos."),

    # ¿Qué es una interfaz contextual?
    ("20_maria", "maria", 500, "Bueno, pongámoslo en palabras sencillas, porque tampoco queremos que alguien termine este podcast pensando que necesita un doctorado en inteligencia artificial."),
    ("21_fred", "fred", 200, "Una interfaz contextual es una experiencia que utiliza información relevante sobre la persona, su situación y el momento de interacción para adaptar la ayuda, el contenido o las acciones que presenta."),
    ("22_maria", "maria", 220, "Por ejemplo, si estoy solicitando un crédito por primera vez, probablemente necesito explicaciones, orientación y acompañamiento. Pero si ya he realizado ese proceso anteriormente, posiblemente necesito rapidez y claridad para avanzar."),
    ("23_fred", "fred", 180, "Mismo producto. Mismo objetivo general. Diferente contexto."),
    ("24_maria", "maria", 120, "Diferente experiencia."),
    ("25_fred", "fred", -200, "Exactamente."),
    ("26_maria", "maria", 220, "Aunque aquí tengo una inquietud. ¿Eso no es simplemente personalización? Porque llevamos años hablando de personalizar experiencias."),
    ("27_fred", "fred", 200, "La personalización tradicional puede estar relacionada con preferencias, recomendaciones o características relativamente estables de una persona. La contextualización pone especial atención en lo que está ocurriendo ahora."),
    ("28_maria", "maria", 180, "O sea, no solamente quién soy, sino qué estoy tratando de resolver en este momento."),
    ("29_fred", "fred", 180, "Tal cual. Incluso una misma persona puede necesitar dos experiencias diferentes dependiendo de la situación."),

    # Cuando la interfaz debería darse cuenta de que algo pasa
    ("30_maria", "maria", 500, "Pensemos en un ejemplo bancario. Supongamos que una persona está solicitando un producto financiero y llega al momento de cargar unos documentos. Intenta subir un archivo. Falla. Lo vuelve a intentar. Falla. Y finalmente abandona."),
    ("31_fred", "fred", 240, "El enfoque tradicional podría ser mejorar el mensaje de error, cambiar el color del botón o reorganizar el formulario."),
    ("32_maria", "maria", 160, "Y eso puede ayudar."),
    ("33_fred", "fred", 160, "Sí, por supuesto. Pero desde un enfoque contextual nos preguntaríamos algo adicional: ¿qué podemos entender de lo que está sucediendo? ¿El archivo tiene un formato incorrecto? ¿La persona no sabe qué documento necesita? ¿Está intentando realizar el proceso desde el celular? ¿Tiene problemas de conexión?"),
    ("34_maria", "maria", 200, "Porque dependiendo de la causa, la respuesta debería ser completamente distinta."),
    ("35_fred", "fred", 180, "Exactamente. Si el problema es el peso del archivo, podemos orientar sobre cómo reducirlo. Si no tiene el documento disponible, podríamos permitirle continuar más tarde sin perder el progreso, siempre que el proceso lo permita."),
    ("36_maria", "maria", 200, "Y si simplemente no entiende qué documento le están pidiendo, probablemente no necesita un mensaje de error. Necesita una explicación."),
    ("37_fred", "fred", 650, "Ahí está la diferencia entre reaccionar a un evento y comprender una situación."),
    ("38_maria", "maria", 180, "Y también entre diseñar una pantalla y diseñar una decisión."),

    # El proyecto de Interfaces Contextuales
    ("39_fred", "fred", 500, "Precisamente, el proyecto busca construir una metodología práctica que permita a los equipos de diseño identificar estas oportunidades dentro de los journeys bancarios. No pretende reinventar toda la disciplina del diseño ni agregar veinte reuniones al calendario."),
    ("40_maria", "maria", 180, "(chuckle) Menos mal, porque si la solución era otra reunión semanal, yo ya estaba renunciando al proyecto."),
    ("41_fred", "fred", 220, "(laughing) La intención es todo lo contrario. Crear una herramienta sencilla que permita conectar problemas reales de experiencia con posibles decisiones contextuales."),
    ("42_maria", "maria", 180, "Y que cualquier diseñador pueda utilizar sin tener que convertirse en científico de datos."),
    ("43_fred", "fred", 180, "Correcto. Pero para que esto funcione, necesitamos partir de algo fundamental: la evidencia. No deberíamos contextualizar una experiencia simplemente porque tenemos la capacidad tecnológica de hacerlo."),
    ("44_maria", "maria", 180, "Sí. Porque a veces aparece una tecnología nueva y salimos desesperados a buscarle un problema."),
    ("45_fred", "fred", -180, "¡Exactamente!"),
    ("46_maria", "maria", 160, "Tenemos inteligencia artificial. Pongámosle inteligencia artificial al botón. Pongámosle inteligencia artificial al menú. Pongámosle inteligencia artificial hasta al mensaje de bienvenida."),
    ("47_fred", "fred", 180, "(laughing) Y después descubrimos que lo único que necesitaba el usuario era encontrar el botón de continuar."),

    # Los datos como punto de partida
    ("48_fred", "fred", 520, "Uno de los aspectos importantes del proyecto es aprovechar las fuentes de información que ya existen dentro de la organización. Las mediciones de experiencia, los comentarios de clientes, los estudios de investigación, Insights Hub, los indicadores de satisfacción y recomendación, y las métricas de comportamiento."),
    ("49_maria", "maria", 220, "Porque ahí hay una oportunidad enorme. Muchas veces los equipos investigan un problema desde cero, cuando posiblemente ya existen conversaciones, comentarios o mediciones que permiten entender parte de lo que ocurre."),
    ("50_fred", "fred", 200, "Y no se trata únicamente de encontrar un indicador que esté bajo. Se trata de comprender qué está pasando detrás de ese indicador."),
    ("51_maria", "maria", 180, "Claro. Un NPS bajo nos puede indicar que existe un problema de percepción o recomendación. Pero no necesariamente nos dice cómo resolverlo."),
    ("52_fred", "fred", 200, "Para eso necesitamos conectar distintas fuentes. Identificar momentos de fricción, comprender necesidades, encontrar comportamientos recurrentes y formular hipótesis."),
    ("53_maria", "maria", 200, "Y también reconocer cuándo no tenemos suficiente información. Porque sería muy peligroso asumir que conocemos al cliente solamente porque tenemos muchos datos sobre él."),

    # De la señal a la decisión
    ("54_fred", "fred", 500, "Para organizar este proceso, el proyecto plantea un framework compuesto por seis elementos: señal, contexto, intención, decisión, respuesta y evidencia."),
    ("55_maria", "maria", 180, "Espérate, Fred. Eso suena a que estamos a punto de abrir una presentación de cuarenta diapositivas."),
    ("56_fred", "fred", 160, "(chuckle) No, no, tranquila. Hagámoslo con un ejemplo."),
    ("57_maria", "maria", 140, "Bueno, te escucho."),
    ("58_fred", "fred", 180, "Imagina nuevamente a la persona que está intentando cargar sus documentos. La señal es aquello que podemos observar: ha intentado cargar el archivo varias veces sin éxito."),
    ("59_maria", "maria", 180, "Hasta ahí sabemos qué ocurrió, pero todavía no sabemos por qué."),
    ("60_fred", "fred", 180, "Exactamente. Entonces aparece el contexto. Sabemos, por ejemplo, que está utilizando un dispositivo móvil y que el archivo supera el tamaño permitido. Después viene la intención. ¿Qué quiere realmente esa persona? No quiere cargar un PDF por diversión."),
    ("61_maria", "maria", 160, "(laughing) Aunque nunca se sabe. Hay gente para todo."),
    ("62_fred", "fred", 180, "Quiere completar su solicitud. La decisión consiste en determinar qué debería hacer la experiencia frente a esa situación."),
    ("63_maria", "maria", 160, "Por ejemplo, ofrecerle una alternativa válida para continuar."),
    ("64_fred", "fred", 160, "Sí. Y la respuesta es cómo materializamos esa decisión en la interfaz: una explicación, una ayuda contextual, una acción alternativa o una opción para retomar el proceso."),
    ("65_maria", "maria", 160, "Y falta la evidencia."),
    ("66_fred", "fred", 160, "Que nos permite comprobar si realmente funcionó. ¿Disminuyeron los intentos fallidos? ¿Más personas completaron el proceso? ¿Necesitaron menos asistencia? ¿Comprendieron mejor lo que tenían que hacer?"),
    ("67_maria", "maria", 180, "Me gusta porque la decisión no termina cuando el diseñador entrega el prototipo."),
    ("68_fred", "fred", 180, "Termina, provisionalmente, cuando tenemos evidencia para evaluar su impacto."),

    # ¿Dónde entra la inteligencia artificial?
    ("69_maria", "maria", 520, "Aquí viene la pregunta obligatoria. ¿Todo esto necesita inteligencia artificial?"),
    ("70_fred", "fred", 240, "No."),
    ("71_maria", "maria", 700, "(chuckle) Bueno, muchas gracias por acompañarnos en este episodio."),
    ("72_fred", "fred", 240, "(laughing) No, pero es importante aclararlo. Una interfaz contextual puede funcionar mediante reglas de negocio, estados del sistema, información transaccional o condiciones previamente definidas. La inteligencia artificial puede ampliar estas capacidades, ayudando a interpretar grandes volúmenes de información, identificar patrones, comprender lenguaje natural o sugerir respuestas."),
    ("73_maria", "maria", 200, "Pero no debería convertirse en un requisito para solucionar problemas que se pueden resolver de manera mucho más sencilla."),
    ("74_fred", "fred", 180, "Exactamente. La tecnología debe responder a la necesidad, no al revés."),
    ("75_maria", "maria", 180, "Y además estamos hablando de experiencias financieras. No podemos permitir que un sistema improvise decisiones delicadas simplemente porque es capaz de generar una respuesta convincente."),
    ("76_fred", "fred", 180, "Por eso la privacidad, la transparencia, la seguridad y el control de las personas son fundamentales. Las decisiones contextuales deben tener límites claros."),
    ("77_maria", "maria", 180, "Entender al usuario no significa vigilarlo. Y anticiparse a una necesidad tampoco significa decidir todo por él."),

    # Cuatro formas de hacer sentir mejor al cliente
    ("78_fred", "fred", 520, "El proyecto también busca contribuir a experiencias que se perciban como fluidas, empáticas, que impulsen al cliente y que lo acompañen de manera incondicional."),
    ("79_maria", "maria", 200, "Traduzcamos eso a situaciones concretas. Una experiencia fluida evita que tenga que repetir información innecesariamente. Una experiencia empática reconoce que puedo estar confundida y me ayuda sin hacerme sentir culpable. Una experiencia que me impulsa me entrega información para tomar mejores decisiones. Y una experiencia que me acompaña de manera incondicional no me abandona cuando algo sale mal."),
    ("80_fred", "fred", 220, "Eso último me parece especialmente importante. Es relativamente fácil diseñar cuando todo funciona perfectamente."),
    ("81_maria", "maria", 140, "El famoso camino feliz."),
    ("82_fred", "fred", 160, "Exacto. Pero la verdadera calidad de una experiencia muchas veces aparece cuando las cosas no salen como estaban previstas."),
    ("83_maria", "maria", 180, "Cuando falla una transferencia, cuando no entiendo un cobro, cuando pierdo la conexión o cuando necesito resolver algo urgente. Ahí es donde realmente quiero sentir que la organización está de mi lado."),

    # ¿Cómo se lleva todo esto a la práctica?
    ("84_fred", "fred", 520, "Para que el proyecto no se quede únicamente en una guía conceptual, estamos explorando una herramienta digital llamada Contextual."),
    ("85_maria", "maria", 160, "Bueno, ¿y qué hace?"),
    ("86_fred", "fred", 180, "Su propósito es acompañar al diseñador desde la identificación de un problema hasta la formulación de una posible solución contextual. La persona describe la situación que quiere resolver, incorpora la evidencia disponible y analiza qué señales, contextos e intenciones podrían estar involucrados."),
    ("87_maria", "maria", 180, "O sea, ayuda a estructurar el pensamiento."),
    ("88_fred", "fred", 180, "Exactamente. También busca facilitar la exploración de patrones contextuales y referencias externas. Identificar cómo otras organizaciones resuelven problemas similares, contrastar esos aprendizajes con la información interna y encontrar nuevas oportunidades."),
    ("89_maria", "maria", 180, "Pero no se trata de copiar lo que hizo otra aplicación."),
    ("90_fred", "fred", 180, "No. Las referencias sirven para ampliar el panorama, no para sustituir la investigación ni el criterio del diseñador."),
    ("91_maria", "maria", 180, "Y al final deberíamos obtener algo más útil que un documento lleno de definiciones."),
    ("92_fred", "fred", 180, "Una hipótesis de solución concreta. Qué problema queremos resolver, qué información necesitamos, qué decisión debería tomar la experiencia, cómo podríamos prototiparla y cómo evaluaríamos su impacto."),

    # ¿Y cómo sabemos si funciona?
    ("93_maria", "maria", 520, "Bueno, todo esto suena interesante. Pero imagínate que llega alguien de negocio y pregunta: ¿y esto qué impacto tiene?"),
    ("94_fred", "fred", 200, "Una pregunta completamente válida. El proyecto busca contribuir al fortalecimiento de la experiencia del cliente, incluyendo el ICX y otros indicadores relevantes. Pero no podemos prometer que implementar una interfaz contextual automáticamente aumentará esos resultados."),
    ("95_maria", "maria", 180, "Porque existen muchísimas variables que influyen en la percepción de una experiencia."),
    ("96_fred", "fred", 180, "Claro. Por eso debemos comenzar midiendo aquello sobre lo que la intervención tiene una relación más directa. Si estamos resolviendo un problema de abandono, midamos abandono y finalización. Si estamos resolviendo incertidumbre, evaluemos comprensión y confianza. Si queremos reducir el esfuerzo, observemos el tiempo, los errores o la necesidad de solicitar ayuda."),
    ("97_maria", "maria", 180, "Y posteriormente contrastamos estos resultados con indicadores de percepción más amplios, como la satisfacción o el NPS."),
    ("98_fred", "fred", 180, "Exactamente. Así podemos construir una relación más sólida entre las decisiones de diseño y los resultados de experiencia."),
    ("99_maria", "maria", 180, "Y dejar de defender nuestras soluciones únicamente diciendo que se ven más bonitas o que son más intuitivas."),
    ("100_fred", "fred", 180, "Que es una conversación que también tenemos que empezar a cambiar como diseñadores."),

    # El futuro del rol del diseñador
    ("101_maria", "maria", 520, "Fred, a mí este proyecto me deja pensando en algo. Si cada vez tenemos herramientas más rápidas para construir interfaces, ¿dónde estará realmente nuestro valor como diseñadores?"),
    ("102_fred", "fred", 220, "Creo que estará cada vez más en comprender problemas, conectar información, identificar oportunidades y formular mejores decisiones."),
    ("103_maria", "maria", 180, "Porque generar una pantalla es una cosa. Saber por qué esa pantalla debería existir es otra completamente diferente."),
    ("104_fred", "fred", 160, "Y saber cuándo no debería existir también."),
    ("105_maria", "maria", 180, "¡Totalmente! Quizás la mejor interfaz contextual es esa que evita que tengas que pasar por una interfaz innecesaria."),
    ("106_fred", "fred", 750, "El proyecto también representa una oportunidad para recuperar esa dimensión estratégica del diseño. Para dejar de estar únicamente al final del proceso, resolviendo solicitudes de interfaz, y participar desde el momento en que se está intentando comprender el problema."),
    ("107_maria", "maria", 200, "No esperar a que alguien nos diga qué construir, sino ayudar a descubrir qué vale la pena construir."),

    # Una última reflexión
    ("108_fred", "fred", 600, "María, si tuviéramos que resumir todo este proyecto en una sola idea, ¿cuál sería?"),
    ("109_maria", "maria", 220, "Para mí sería dejar de diseñar experiencias que esperan que las personas se adapten a ellas, y empezar a diseñar experiencias que sepan adaptarse a las necesidades de las personas."),
    ("110_fred", "fred", 200, "Me gusta. Y agregaría algo: no se trata de que una interfaz parezca inteligente. Se trata de que la persona se sienta comprendida, acompañada y capaz de lograr aquello que necesita."),
    ("111_maria", "maria", 180, "Porque probablemente un cliente nunca va a salir diciendo: ¡Qué espectacular decisión contextual acaba de tomar este banco!"),
    ("112_fred", "fred", 160, "(laughing) Ojalá no."),
    ("113_maria", "maria", 180, "Va a decir algo mucho más sencillo: Qué fácil fue. Encontré lo que necesitaba. Pude hacerlo. No tuve que pedir ayuda."),
    ("114_fred", "fred", 200, "Y quizás ahí está el verdadero éxito de este proyecto. Que la complejidad esté del lado del sistema y la simplicidad del lado de las personas."),
    ("115_maria", "maria", 700, "Bueno, Fred, después de todo esto, ¿vamos por ese café?"),
    ("116_fred", "fred", 180, "(chuckle) Sí. Pero espero que esta vez no me pidan actualizar mis datos para comprarlo."),
    ("117_maria", "maria", 260, "(laughing) Esto fue Más allá de la interfaz."),
    ("118_fred", "fred", 180, "Un espacio para cuestionar cómo diseñamos y descubrir cómo podríamos hacerlo mejor."),
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

        if not (mp3.exists() and mp3.stat().st_size > 2000):
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

    lead_in_samples = int(2.6 * sr)
    tail_samples = int(4.5 * sr)

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

    voice_full = Path("/tmp/mas_alla_01_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled Mas alla de la interfaz dialogue: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/mas_alla_01_bed.wav")
    print(f"[BED] Rendering custom Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "mas_alla_interfaces_contextuales.mp3"
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
