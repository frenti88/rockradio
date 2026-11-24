#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 5: "El arte de no hacer nada"
Intimate radio-style conversation between:
  - Fred  (g.DEFAULT_FISH_VOICE)
  - María (1cb68a6f33be463ebb0902d4aa4740af)

Follows the user's exact script with laughter, sighs, reflective 2-3s pauses,
subtle stereo desk panning, custom Drive background music bed, and an 8-second
instrumental outro fade.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_05"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_MARIA = "1cb68a6f33be463ebb0902d4aa4740af"

# (id, speaker, gap_ms_before, text)
TURNS = [
    ("01_fred", "fred", 0, "María, te voy a hacer una pregunta un poquito incómoda. ¿Cuándo fue la última vez que no hiciste absolutamente nada?"),
    ("02_maria", "maria", 200, "¿Nada de nada?"),
    ("03_fred", "fred", 180, "Nada. Sin celular, sin televisión, sin trabajar, sin pensar en qué tienes que hacer mañana."),
    ("04_maria", "maria", 280, "Mmm… ¿Dormir cuenta?"),
    ("05_fred", "fred", 180, "(chuckle) No, no cuenta."),
    ("06_maria", "maria", 180, "Ah, bueno. Entonces estamos en problemas."),
    ("07_fred", "fred", 220, "Y creo que no somos los únicos. Hay algo muy curioso en nuestra forma de vivir. Parece que solamente tenemos dos modos de funcionamiento: estamos produciendo o estamos consumiendo."),
    ("08_maria", "maria", 180, "Trabajamos para tener dinero y después gastamos ese dinero para recuperarnos de haber trabajado."),
    ("09_fred", "fred", -160, "¡Exactamente!"),
    ("10_maria", "maria", 160, "(chuckle) Qué modelo de negocio tan bien pensado, ¿no?"),
    ("11_fred", "fred", 260, "(laughing) Hoy vamos a hablar de una tercera posibilidad. Una que parece sencilla, pero que cada vez nos cuesta más: no hacer nada."),
    ("12_maria", "maria", 180, "Y que conste que no estamos promoviendo la pereza."),
    ("13_fred", "fred", 180, "No, para nada. Estamos hablando de recuperar algo que, aparentemente, hemos ido perdiendo sin darnos cuenta."),

    # El ciclo del que nadie habla
    ("14_fred", "fred", 700, "Imagínate un lunes cualquiera. Suena la alarma, te levantas, te bañas, desayunas si alcanzas…"),
    ("15_maria", "maria", 160, "Si alcanzas. Importante esa aclaración."),
    ("16_fred", "fred", 180, "Sales de casa, te comes un atasco, llegas al trabajo, pasas ocho horas trabajando y después vuelves a casa."),
    ("17_maria", "maria", 160, "Con otro atasco. Porque uno solo no era suficiente."),
    ("18_fred", "fred", 180, "(chuckle) Y cuando llegas, estás esperando esa pequeña recompensa que llamamos tiempo libre."),
    ("19_maria", "maria", 180, "Que normalmente consiste en tirarse en el sofá, pedir algo de comer y mirar una serie."),
    ("20_fred", "fred", 200, "Claro. Y aquí hay un dato bastante inquietante que recoge Álvaro García en un artículo sobre el ocio. Según las cifras de Gallup que cita, menos del veinte por ciento de los empleados del mundo se siente realmente comprometido con su trabajo."),
    ("21_maria", "maria", 200, "Uf… menos del veinte."),
    ("22_fred", "fred", 180, "Sí. Y eso no significa necesariamente que todos los demás odien su trabajo, pero sí que hay muchísimas personas que no sienten una conexión fuerte con lo que hacen."),
    ("23_maria", "maria", 220, "Entonces pasamos buena parte de nuestra vida esperando que llegue el momento en el que, supuestamente, empieza nuestra vida."),
    ("24_fred", "fred", 750, "Oye… eso que acabas de decir es bastante fuerte."),
    ("25_maria", "maria", 200, "Es que piénsalo. Esperamos el viernes, las vacaciones, diciembre, el próximo puente festivo. Siempre estamos esperando algo."),
    ("26_fred", "fred", 180, "Y cuando finalmente llega ese momento, sentimos que tenemos que aprovecharlo."),
    ("27_maria", "maria", 160, "Salir, comprar, viajar, conocer un restaurante nuevo…"),
    ("28_fred", "fred", 180, "De lunes a viernes cambiamos nuestro tiempo por dinero. Y los fines de semana cambiamos nuestro dinero por entretenimiento."),
    ("29_maria", "maria", 200, "(sigh) Y el domingo por la noche volvemos a empezar."),
    ("30_fred", "fred", 220, "Esa es la rueda."),

    # ¿Cuándo descansar se convirtió en un negocio?
    ("31_maria", "maria", 600, "Pero espera. ¿Siempre hemos sido así?"),
    ("32_fred", "fred", 200, "Curiosamente, no. Los antiguos romanos tenían una palabra para el ocio: otium. Y de su oposición viene el término negotium, relacionado con los negocios y las ocupaciones."),
    ("33_maria", "maria", 180, "O sea que el ocio era prácticamente lo contrario del negocio."),
    ("34_fred", "fred", 160, "Exacto. Y ahora el ocio es uno de los grandes negocios."),
    ("35_maria", "maria", 180, "Los romanos estarían bastante confundidos viendo un centro comercial un domingo."),
    ("36_fred", "fred", 180, "(chuckle) Seguramente. Durante buena parte de la historia, especialmente en las sociedades agrícolas, la vida estaba organizada alrededor de las estaciones y las tareas necesarias para sobrevivir."),
    ("37_maria", "maria", 160, "No alrededor de las notificaciones del calendario."),
    ("38_fred", "fred", 180, "No. Cuando ciertas tareas terminaban, había momentos de reunión, descanso y convivencia. Sin idealizar esas épocas, porque también eran durísimas, la relación con el tiempo era diferente."),
    ("39_maria", "maria", 180, "¿Y cuándo cambia eso?"),
    ("40_fred", "fred", 180, "La Revolución Industrial fue un punto de inflexión. El reloj empezó a organizar la vida de las personas. La fábrica determinaba cuándo entrabas, cuándo salías y cuánto tiempo tenías disponible."),
    ("41_maria", "maria", 200, "Qué curioso. El reloj, que supuestamente nos ayuda a organizar el tiempo, terminó organizándonos a nosotros."),
    ("42_fred", "fred", 180, "Totalmente. Y después aparece un sociólogo llamado Thorstein Veblen, que en 1899 plantea una idea fascinante."),
    ("43_maria", "maria", 140, "A ver…"),
    ("44_fred", "fred", 180, "Durante mucho tiempo, demostrar que no necesitabas trabajar era una señal de riqueza. Pero progresivamente, otra manera de demostrar estatus fue exhibir lo que podías comprar. Él lo llamó consumo ostentoso."),
    ("45_maria", "maria", 180, "Ah. O sea, Instagram antes de Instagram."),
    ("46_fred", "fred", 160, "(laughing) ¡Más o menos!"),
    ("47_maria", "maria", 180, "Veblen habría tenido material para investigar durante años con las redes sociales."),
    ("48_fred", "fred", 180, "Lo interesante es que ya no bastaba con tener tiempo libre. También importaba demostrar qué hacías con él."),

    # La industria de las experiencias
    ("49_fred", "fred", 700, "En 1956 abrió en Minnesota uno de los centros comerciales que marcaron un antes y un después: un espacio cerrado y climatizado donde podías comprar, comer y pasar la tarde con tu familia."),
    ("50_maria", "maria", 180, "Un lugar donde uno entra a mirar y sale con tres bolsas, una deuda y sin saber muy bien qué pasó."),
    ("51_fred", "fred", 180, "(chuckle) Lo interesante es cómo se mezclaron dos conceptos: consumir y disfrutar del tiempo libre."),
    ("52_maria", "maria", 180, "Y ahora prácticamente todo tiene que ser una experiencia."),
    ("53_fred", "fred", -160, "¡Esa es la palabra!"),
    ("54_maria", "maria", 160, "Ya no puedes tomarte un café tranquilamente. Tienes que vivir una experiencia sensorial, conocer la finca, la altura, las notas aromáticas…"),
    ("55_fred", "fred", 160, "Bueno, tampoco te metas con el café."),
    ("56_maria", "maria", 160, "(laughing) Perdón, perdón. Sabía que ese tema era delicado."),
    ("57_fred", "fred", 180, "Pero tienes razón en algo. No hay nada malo en disfrutar de un buen café, una buena cena o un viaje. El problema aparece cuando sentimos que necesitamos comprar constantemente nuevas experiencias para sentir que estamos viviendo."),
    ("58_maria", "maria", 180, "Como si una tarde tranquila en casa fuera una tarde desperdiciada."),
    ("59_fred", "fred", 180, "Exactamente. En 1998, Pine y Gilmore hablaron de algo que llamaron la economía de la experiencia. La idea es que las empresas no venden únicamente productos o servicios, sino también experiencias memorables."),
    ("60_maria", "maria", 180, "Y, a veces, más que vivirlas, queremos tener algo interesante que contar después."),
    ("61_fred", "fred", 180, "Ahí está la cuestión. Una cena, un viaje, un concierto… pueden ser maravillosos. Pero ¿qué pasa cuando empezamos a valorarlos por cómo se ven desde afuera?"),
    ("62_maria", "maria", 180, "Que terminas eligiendo el restaurante por la foto que puedes publicar y no por la comida."),
    ("63_fred", "fred", 180, "O visitando un lugar espectacular mientras estás más preocupado por grabarlo que por contemplarlo."),
    ("64_maria", "maria", 200, "Mmm… creo que todos hemos hecho eso alguna vez."),

    # La paradoja de tener más tiempo
    ("65_fred", "fred", 600, "Hay una contradicción fascinante en todo esto. La tecnología nos ha permitido automatizar tareas, producir más y reducir el tiempo necesario para hacer muchas cosas."),
    ("66_maria", "maria", 180, "En teoría deberíamos tener más tiempo para nosotros."),
    ("67_fred", "fred", 160, "En teoría."),
    ("68_maria", "maria", 180, "Pero uno termina el día con la sensación de que no le alcanzó para nada."),
    ("69_fred", "fred", 180, "Porque cada espacio que liberamos parece llenarse inmediatamente con otra obligación, otra distracción o alguna forma de consumo."),
    ("70_maria", "maria", 180, "Incluso descansar se volvió una tarea. Hay que dormir bien, meditar, hacer ejercicio, leer, cumplir los pasos diarios…"),
    ("71_fred", "fred", 160, "Y si no cumples, te sientes culpable."),
    ("72_maria", "maria", 160, "(laughing) ¡Exacto! Uno termina estresado porque no consiguió relajarse correctamente."),
    ("73_fred", "fred", 220, "(chuckle) Es absurdo cuando lo dices en voz alta."),
    ("74_maria", "maria", 180, "Pero es bastante real."),

    # La respuesta que conocíamos a los ocho años
    ("75_fred", "fred", 700, "¿Sabes qué me parece bonito de todo esto? Que posiblemente ya conocíamos la solución cuando éramos niños."),
    ("76_maria", "maria", 180, "¿Salir a jugar?"),
    ("77_fred", "fred", 180, "Sí. ¿Te acuerdas de esas tardes interminables en las que salías a la calle y volvías cuando empezaba a oscurecer?"),
    ("78_maria", "maria", 180, "Claro. Y no necesitábamos absolutamente ningún plan. A veces una pelota, a veces ni siquiera eso."),
    ("79_fred", "fred", 180, "No estabas construyendo una marca personal, ni intentando mejorar tus habilidades sociales, ni generando ingresos adicionales."),
    ("80_maria", "maria", 160, "Ni grabando un tutorial de cómo jugar en la calle."),
    ("81_fred", "fred", 180, "(chuckle) Simplemente jugabas."),
    ("82_maria", "maria", 1600, "Y eras feliz."),
    ("83_fred", "fred", 240, "Eran momentos sin producto, sin propósito y sin público. Hay investigaciones, como las de Peter Gray, que relacionan la disminución del juego libre infantil con dificultades en el bienestar psicológico de niños y jóvenes."),
    ("84_maria", "maria", 200, "Tiene sentido. Aunque seamos adultos, probablemente seguimos necesitando espacios donde no tengamos que demostrar nada."),
    ("85_fred", "fred", 180, "Exactamente. ¿Cuándo fue la última vez que hiciste algo únicamente porque te gustaba?"),
    ("86_maria", "maria", 160, "Sin pensar en monetizarlo."),
    ("87_fred", "fred", 160, "Sin pensar en mejorarlo."),
    ("88_maria", "maria", 160, "Sin publicarlo."),
    ("89_fred", "fred", 160, "Sin convertirlo en un proyecto."),
    ("90_maria", "maria", 1200, "Uf… parece una pregunta sencilla, pero cuesta responderla."),

    # Los tres enemigos del verdadero ocio
    ("91_fred", "fred", 600, "Hay tres comportamientos que pueden terminar afectando nuestra capacidad de disfrutar. El primero es medir."),
    ("92_maria", "maria", 180, "Ay, no. Mi reloj inteligente acaba de sentirse atacado."),
    ("93_fred", "fred", 180, "(chuckle) Hay un estudio de Jordan Etkin donde las personas realizaban actividades como caminar o leer. Al medir su rendimiento, podían hacer más, pero disfrutar menos."),
    ("94_maria", "maria", 180, "Claro, porque ya no estás caminando por caminar. Estás intentando llegar a los diez mil pasos."),
    ("95_fred", "fred", 180, "Y leer deja de ser disfrutar una historia cuando lo importante es llegar a cincuenta libros al año."),
    ("96_maria", "maria", 180, "Espera, pero medir también puede ayudar a construir buenos hábitos."),
    ("97_fred", "fred", 180, "Sí, absolutamente. No se trata de eliminar las métricas. Se trata de entender cuándo están ayudando y cuándo están sustituyendo el placer por la obligación."),
    ("98_maria", "maria", 180, "Esa diferencia es importante."),
    ("99_fred", "fred", 200, "El segundo enemigo es premiar. En un experimento de 1973, unos investigadores estudiaron a niños que disfrutaban dibujando. A algunos les prometieron una recompensa por hacerlo."),
    ("100_maria", "maria", 160, "¿Y qué pasó?"),
    ("101_fred", "fred", 180, "Después, cuando tuvieron libertad para elegir, los niños que habían esperado una recompensa mostraron menos interés por dibujar."),
    ("102_maria", "maria", 180, "Es como cuando alguien te dice que eres bueno haciendo algo y enseguida aparece la frase: Deberías montar un negocio con eso."),
    ("103_fred", "fred", 160, "¡Sí! Te gusta cocinar… abre un restaurante. Te gusta la fotografía… vende tus fotos. Te gusta pintar… crea una tienda."),
    ("104_maria", "maria", 160, "(laughing) Déjame pintar tranquila, por favor."),
    ("105_fred", "fred", 220, "Monetizar una afición puede ser una excelente decisión, pero también puede cambiar nuestra relación con ella."),
    ("106_maria", "maria", 180, "Porque lo que antes hacías para escapar del trabajo termina convirtiéndose en otro trabajo."),
    ("107_fred", "fred", 200, "Y el tercer enemigo es exhibir."),
    ("108_maria", "maria", 160, "Las redes sociales."),
    ("109_fred", "fred", 180, "Entre otras cosas. Un estudio de 2018 encontró que tomar fotografías con la intención de compartirlas podía reducir el disfrute de ciertas experiencias."),
    ("110_maria", "maria", 180, "Porque empiezas a mirar el momento desde la perspectiva de otras personas."),
    ("111_fred", "fred", 180, "Exacto. Ya no solo estás viviendo algo. Estás pensando en cómo será percibido."),
    ("112_maria", "maria", 200, "Y no es lo mismo guardar un recuerdo porque te hace feliz que necesitar demostrar que estás siendo feliz."),
    ("113_fred", "fred", 800, "Esa frase merece quedarse ahí un momento."),

    # Aprender a no hacer nada
    ("114_maria", "maria", 2400, "Bueno, entonces… ¿qué hacemos? ¿Nos sentamos a mirar una pared durante tres horas?"),
    ("115_fred", "fred", 180, "(chuckle) Tampoco hace falta llevarlo tan lejos. No hacer nada, en este contexto, no significa permanecer inmóvil."),
    ("116_maria", "maria", 180, "Significa hacer cosas sin exigirles un resultado."),
    ("117_fred", "fred", 180, "Exacto. Salir a caminar sin medir la distancia. Escuchar un álbum completo sin estar haciendo otras cinco cosas. Prepararte un café y sentarte a disfrutarlo."),
    ("118_maria", "maria", 160, "Visitar a tus padres sin estar mirando el reloj."),
    ("119_fred", "fred", 160, "Conversar con alguien sin sacar el teléfono."),
    ("120_maria", "maria", 160, "Cocinar algo porque te apetece, aunque no quede bonito."),
    ("121_fred", "fred", 160, "Aburrirte un rato."),
    ("122_maria", "maria", 180, "Esa es difícil. A los treinta segundos de aburrimiento uno ya está buscando el celular."),
    ("123_fred", "fred", 180, "Y quizás ahí está parte del ejercicio. Recuperar la capacidad de estar presentes sin necesitar estímulos constantes."),
    ("124_maria", "maria", 180, "Aunque tampoco deberíamos convertir esto en otra tendencia de productividad."),
    ("125_fred", "fred", 160, "(chuckle) El método definitivo para no hacer nada en siete pasos."),
    ("126_maria", "maria", 160, "(laughing) Con un curso premium y una plantilla de seguimiento."),
    ("127_fred", "fred", 240, "Precisamente de eso estamos intentando escapar."),

    # Recuperar el tiempo que es nuestro
    ("128_fred", "fred", 750, "El artículo de Álvaro termina con una imagen que me gusta mucho. Él cuenta que va a pasar el fin de semana acampando con sus amigos en un bosque cercano. Van a caminar, preparar una barbacoa y jugar a las cartas junto a una hoguera."),
    ("129_maria", "maria", 180, "Suena increíble."),
    ("130_fred", "fred", 180, "No porque sea una experiencia exclusiva. No porque tenga que viajar al otro lado del mundo. Sino porque es tiempo compartido con personas que quiere."),
    ("131_maria", "maria", 200, "A veces pienso que los mejores recuerdos de nuestra vida son momentos que, cuando estaban ocurriendo, no parecían especialmente importantes."),
    ("132_fred", "fred", 180, "Una conversación que se alargó hasta la madrugada."),
    ("133_maria", "maria", 160, "Un almuerzo familiar."),
    ("134_fred", "fred", 160, "Una tarde escuchando música."),
    ("135_maria", "maria", 180, "(chuckle) Reírte tanto con alguien que después ni siquiera recuerdas qué era lo que causaba tanta risa."),
    ("136_fred", "fred", 750, "Quizás hemos confundido una vida llena de actividades con una vida bien vivida."),
    ("137_maria", "maria", 200, "Y quizás no necesitamos añadir más cosas a nuestra vida, sino recuperar la capacidad de disfrutar las que ya tenemos."),
    ("138_fred", "fred", 180, "No estamos diciendo que dejes de trabajar, de viajar, de comprar cosas que te gustan o de construir proyectos."),
    ("139_maria", "maria", 180, "Estamos diciendo que no todos los momentos de tu existencia necesitan justificar su valor."),
    ("140_fred", "fred", 160, "Porque tu tiempo no siempre tiene que producir dinero."),
    ("141_maria", "maria", 140, "Ni generar contenido."),
    ("142_fred", "fred", 140, "Ni mejorar tu rendimiento."),
    ("143_maria", "maria", 180, "A veces, simplemente puede ser tuyo."),
    ("144_fred", "fred", 2400, "Y queremos dejarte una pregunta antes de terminar. ¿Cuándo fue la última vez que disfrutaste de algo sin esperar absolutamente nada a cambio?"),
    ("145_maria", "maria", 1100, "No tienes que responderla ahora."),
    ("146_fred", "fred", 200, "De hecho, cuando termine este episodio, quizás podrías quedarte unos minutos sin poner otro."),
    ("147_maria", "maria", 180, "(chuckle) Una estrategia comercial terrible para un podcast."),
    ("148_fred", "fred", 180, "Terrible. Pero bastante coherente con lo que acabamos de hablar."),
    ("149_maria", "maria", 220, "Hasta la próxima."),
    ("150_fred", "fred", 180, "Y disfruta tu tiempo. No tienes que hacer nada extraordinario con él."),
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
    tail_samples = int(8.0 * sr)  # 8-second instrumental outro fade

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

    voice_full = Path("/tmp/aparte_05_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled El arte de no hacer nada dialogue: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_05_bed.wav")
    print(f"[BED] Rendering custom Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_no_hacer_nada.mp3"
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
