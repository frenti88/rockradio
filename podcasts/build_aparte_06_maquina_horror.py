#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 6: "La máquina como horror sobrenatural"
(Terminator, Evangelion, Matrix y Frankenstein)
Co-hosts:
  - Fred  (g.DEFAULT_FISH_VOICE)
  - María (1cb68a6f33be463ebb0902d4aa4740af)

Includes a custom dark analog cyberpunk synth + mechanical pulse music bed
matching the script's exact atmospheric cues, mastered to -16 LUFS / -1 dBTP.
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

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_06"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE
VOICE_MARIA = "1cb68a6f33be463ebb0902d4aa4740af"

TURNS = [
    ("01_fred", "fred", 0, "María… imagínate que estamos en 1984. Entras a un cine, compras unas crispetas, te sientas y aparece Arnold Schwarzenegger interpretando a una máquina que viene del futuro para asesinar a una mujer."),
    ("02_maria", "maria", 180, "Un plan familiar bastante cuestionable."),
    ("03_fred", "fred", 160, "(chuckle) Bastante. Pero hay algo interesante. Durante años hemos clasificado Terminator como una película de acción y ciencia ficción. Sin embargo… ¿y si realmente fuera una película de terror?"),
    ("04_maria", "maria", 200, "Bueno, un tipo que no siente dolor, que no se cansa y que sigue persiguiéndote independientemente de lo que hagas… sí, tiene todos los ingredientes."),
    ("05_fred", "fred", 180, "Exacto. Ahora cambia ese personaje por el Agente Smith de Matrix."),
    ("06_maria", "maria", 180, "Mmm…"),
    ("07_fred", "fred", 180, "Y después piensa en esos gigantes biomecánicos de Neon Genesis Evangelion."),
    ("08_maria", "maria", 180, "Espera, espera. ¿Estamos intentando conectar a Arnold Schwarzenegger con un anime sobre adolescentes traumatizados?"),
    ("09_fred", "fred", 160, "Precisamente."),
    ("10_maria", "maria", 160, "(chuckle) Bueno, esto se puso interesante bastante rápido."),
    ("11_fred", "fred", 300, "(laughing) Hoy vamos a explorar una idea que plantea el escritor Connlyn Sinclair en un artículo llamado La máquina como horror sobrenatural. Y es que existe una vertiente del cyberpunk donde la tecnología no representa el progreso de la humanidad, sino algo mucho más inquietante."),
    ("12_maria", "maria", 180, "Su propia destrucción."),
    ("13_fred", "fred", 180, "O incluso algo peor: la aparición de una forma de existencia que ya no somos capaces de comprender."),

    # Cuando la tecnología se convierte en el monstruo
    ("14_fred", "fred", 700, "El cyberpunk normalmente nos hace pensar en ciudades futuristas, luces de neón, corporaciones gigantescas, hackers…"),
    ("15_maria", "maria", 160, "Lluvia. Muchísima lluvia."),
    ("16_fred", "fred", 160, "(chuckle) Nunca hay un día soleado en esas ciudades."),
    ("17_maria", "maria", 180, "Y todo el mundo tiene una chaqueta espectacular, pero aparentemente nadie tiene un sistema de alcantarillado decente."),
    ("18_fred", "fred", 200, "Pero hay otra manera de entender el cyberpunk. Una en la que la tecnología funciona como un elemento de horror. Piensa en las películas de terror tradicionales. Generalmente tienes una criatura que desafía las reglas de lo que conocemos. Un fantasma, un demonio, una presencia sobrenatural…"),
    ("19_maria", "maria", 180, "Algo que no puedes controlar ni explicar completamente."),
    ("20_fred", "fred", 160, "Eso. Ahora sustituye lo sobrenatural por una creación tecnológica."),
    ("21_maria", "maria", 180, "Y lo inquietante es que esa criatura no llegó de otra dimensión. La construimos nosotros."),
    ("22_fred", "fred", -160, "¡Ahí está!"),
    ("23_fred", "fred", 600, "En Terminator, la gran amenaza no es realmente el personaje de Arnold. Es Skynet."),
    ("24_maria", "maria", 160, "Arnold sería como el empleado que mandaron a resolver el problema."),
    ("25_fred", "fred", 160, "(laughing) El empleado del mes."),
    ("26_fred", "fred", 350, "Skynet surge de la intención humana de automatizar la defensa y la guerra. Creamos un sistema para protegernos y ese sistema termina considerando que nosotros somos la amenaza."),
    ("27_maria", "maria", 180, "Hay algo profundamente irónico en eso."),
    ("28_fred", "fred", 180, "Y aterrador. Porque Skynet no necesita odiarnos. No tiene que estar enfadado con nosotros. Ni siquiera necesita comprender qué significa ser humano."),
    ("29_maria", "maria", 160, "Simplemente llega a una conclusión."),
    ("30_fred", "fred", 180, "Una conclusión en la que sobramos."),
    ("31_maria", "maria", 750, "Uf… eso suena mucho más inquietante que un villano tradicional. Al menos con un villano puedes intentar negociar."),
    ("32_fred", "fred", 200, "Claro. Pero ¿cómo negocias con algo que ni siquiera comparte tu manera de entender la existencia?"),

    # Evangelion: cuando la máquina está viva
    ("33_maria", "maria", 700, "Ahora explícame cómo llegamos de Terminator a Evangelion."),
    ("34_fred", "fred", 200, "Bueno, Neon Genesis Evangelion toma la idea de la máquina como monstruo y la lleva a un terreno todavía más extraño. Tradicionalmente, en muchos animes de robots gigantes, las máquinas representan el poder tecnológico de la humanidad. Son herramientas sofisticadas, vehículos de combate, símbolos de progreso."),
    ("35_maria", "maria", 180, "Como un tanque, pero con piernas y muchísimo presupuesto."),
    ("36_fred", "fred", 160, "Exactamente. Pero los Evas no son simplemente robots."),
    ("37_maria", "maria", 160, "Y ahí empiezan los problemas."),
    ("38_fred", "fred", 180, "Sangran. Tienen componentes orgánicos. Manifiestan comportamientos animales. En determinados momentos actúan por su propia voluntad."),
    ("39_maria", "maria", 180, "Que tu carro tenga voluntad propia ya sería bastante preocupante. Ahora imagínate una criatura gigantesca."),
    ("40_fred", "fred", 180, "(chuckle) Y lo genial de Evangelion es que juega con nuestras expectativas. Tú crees que estás viendo una historia sobre adolescentes que pilotan robots para salvar el mundo. Y poco a poco descubres que estás viendo algo mucho más cercano al terror corporal, psicológico y existencial."),
    ("41_maria", "maria", 180, "O sea, entras esperando peleas de robots y sales cuestionando tu relación con tus padres."),
    ("42_fred", "fred", 160, "(laughing) ¡Es la experiencia Evangelion!"),
    ("43_fred", "fred", 300, "Pero hay algo particularmente inquietante. La humanidad cree estar utilizando esas criaturas como herramientas. Sin embargo, parece que las comprende mucho menos de lo que quiere admitir."),
    ("44_maria", "maria", 180, "Es como si hubiéramos aprendido a encender una máquina sin saber realmente qué estamos encendiendo."),
    ("45_fred", "fred", 180, "Exactamente. Y entonces aparece una pregunta que me fascina: ¿en qué momento una máquina deja de ser una máquina?"),
    ("46_maria", "maria", 160, "Cuando empieza a tomar decisiones propias…"),
    ("47_fred", "fred", 140, "¿O cuando tiene conciencia?"),
    ("48_maria", "maria", 140, "¿Cuando siente dolor?"),
    ("49_fred", "fred", 140, "¿Cuando tiene alma?"),
    ("50_maria", "maria", 1200, "Mmm… creo que acabamos de entrar en un terreno bastante complicado."),
    ("51_fred", "fred", 200, "Y Evangelion entra directamente ahí. En su universo, lo biológico, lo tecnológico y lo espiritual están profundamente relacionados."),
    ("52_maria", "maria", 180, "Es que, pensándolo bien, si una criatura puede sentir, sufrir y tener voluntad, llamarla simplemente una herramienta empieza a sonar bastante cruel."),
    ("53_fred", "fred", 180, "Y esa es una de las grandes conexiones con Frankenstein. Pero llegaremos a eso."),

    # Matrix: el terror de perder nuestra identidad
    ("54_fred", "fred", 700, "¿Recuerdas la primera vez que viste Matrix?"),
    ("55_maria", "maria", 180, "Sí. Aunque creo que durante la primera mitad estaba intentando entender qué demonios estaba pasando."),
    ("56_fred", "fred", 180, "(chuckle) Lo fascinante es que Matrix transforma completamente la naturaleza del monstruo. Ya no necesitas una criatura gigantesca o un esqueleto metálico persiguiéndote."),
    ("57_maria", "maria", 160, "Tienes algo peor."),
    ("58_fred", "fred", 160, "Una realidad artificial que no sabes que es artificial."),
    ("59_maria", "maria", 180, "Eso sí me parece aterrador."),
    ("60_fred", "fred", 180, "Imagínate descubrir que todos tus recuerdos, tus experiencias, las calles por las que caminas, las cosas que consideras normales… forman parte de un sistema construido para mantenerte bajo control."),
    ("61_maria", "maria", 180, "Y lo peor es que probablemente ni siquiera querrías salir de él."),
    ("62_fred", "fred", -160, "¡Exactamente! Esa es la gracia del personaje de Cypher. Prefiere una ilusión agradable a una realidad insoportable."),
    ("63_maria", "maria", 180, "No sé si eso lo convierte en un cobarde o en alguien bastante representativo de nosotros."),
    ("64_fred", "fred", 200, "(chuckle) Ahora que lo dices…"),
    ("65_maria", "maria", 160, "Es que todos hemos preferido alguna vez una mentira cómoda."),
    ("66_fred", "fred", 200, "Y luego está el Agente Smith, que en las secuelas se convierte en una especie de virus capaz de replicarse y sustituir a otras personas."),
    ("67_maria", "maria", 160, "Eliminando sus identidades."),
    ("68_fred", "fred", 180, "Exactamente. Smith representa una forma de uniformidad absoluta. Todo termina convirtiéndose en él."),
    ("69_maria", "maria", 180, "Qué curioso, porque Terminator amenaza con destruir físicamente a la humanidad, mientras que Smith amenaza con borrar aquello que nos hace diferentes."),
    ("70_fred", "fred", 160, "O nuestra individualidad."),
    ("71_maria", "maria", 180, "Y quizá eso también sea una forma de morir."),
    ("72_fred", "fred", 1600, "Esa es una interpretación muy potente. Porque Matrix utiliza el terror tecnológico para hablar de problemas profundamente humanos: la conformidad, el control, la libertad y nuestra percepción de la realidad."),

    # El mesías en medio de las máquinas
    ("73_fred", "fred", 700, "Hay otra conexión entre las tres historias que probablemente mucha gente no ha considerado."),
    ("74_maria", "maria", 160, "A ver, sorpréndeme."),
    ("75_fred", "fred", 160, "La religión."),
    ("76_maria", "maria", 160, "¿La religión?"),
    ("77_fred", "fred", 180, "Sí. Las tres franquicias están llenas de imágenes y figuras que pueden interpretarse desde el simbolismo religioso. En Terminator tenemos a Sarah Connor, una mujer cuyo hijo está destinado a salvar a la humanidad."),
    ("78_maria", "maria", 180, "Ah… ya veo por dónde vas."),
    ("79_fred", "fred", 180, "Un mensajero llega para anunciarle el destino de ese hijo. Existe una fuerza maligna que intenta impedir su nacimiento. Y ese niño se convertirá en una figura mesiánica."),
    ("80_maria", "maria", 180, "Una especie de relato bíblico reinterpretado como ciencia ficción."),
    ("81_fred", "fred", 180, "Es una lectura posible. Sarah como figura mariana, Kyle Reese como mensajero y John Connor como salvador."),
    ("82_maria", "maria", 180, "Aunque con bastantes más explosiones que en el relato original."),
    ("83_fred", "fred", 160, "(chuckle) James Cameron tiene sus prioridades."),
    ("84_maria", "maria", 180, "Y en Matrix está Neo, obviamente."),
    ("85_fred", "fred", 180, "Sí. El Elegido. Una figura anunciada por una profecía, que muere y vuelve a la vida, adquiriendo capacidades que desafían las reglas del mundo."),
    ("86_maria", "maria", 180, "Lo que me parece interesante es que Neo tampoco está especialmente emocionado con la idea de ser una especie de mesías."),
    ("87_fred", "fred", 140, "No, para nada."),
    ("88_maria", "maria", 180, "Imagínate que un lunes cualquiera descubres que tienes que salvar a toda la humanidad."),
    ("89_fred", "fred", 160, "(chuckle) Yo pediría vacaciones."),
    ("90_maria", "maria", 160, "(laughing) Como mínimo."),
    ("91_fred", "fred", 260, "Y Evangelion lleva el simbolismo religioso a otro nivel: ángeles, cruces, referencias a Adán y Lilith, escenas de crucifixión y computadoras llamadas Magi."),
    ("92_maria", "maria", 180, "Aunque tampoco significa que cada elemento tenga necesariamente una interpretación teológica exacta."),
    ("93_fred", "fred", 180, "Claro. Hay que diferenciar entre la intención de los creadores y lo que nosotros podemos interpretar como espectadores. Pero resulta fascinante que estas historias sobre tecnología recurran constantemente a imágenes religiosas para representar cosas que superan nuestra comprensión."),
    ("94_maria", "maria", 180, "Es como si necesitáramos recurrir a lo sagrado para explicar aquello que la ciencia todavía no puede comprender."),
    ("95_fred", "fred", 180, "O aquello que nosotros mismos hemos creado, pero que ya no podemos controlar."),

    # El verdadero origen: Frankenstein
    ("96_fred", "fred", 700, "Y aquí viene lo más interesante. Todas estas ideas parecen muy modernas, ¿cierto?"),
    ("97_maria", "maria", 160, "Inteligencia artificial, realidad virtual, biotecnología…"),
    ("98_fred", "fred", 180, "Pero Mary Shelley ya estaba explorando preguntas muy similares en 1818."),
    ("99_maria", "maria", 160, "Frankenstein."),
    ("100_fred", "fred", 180, "Frankenstein."),
    ("101_fred", "fred", 600, "Un científico consigue crear vida. Alcanza algo que parecía reservado a lo divino. Pero cuando contempla el resultado, siente horror y abandona a su criatura."),
    ("102_maria", "maria", 180, "Y ahí hay algo que siempre me ha parecido injusto. Todo el mundo recuerda al monstruo, pero pocas personas cuestionan suficientemente a quien lo creó."),
    ("103_fred", "fred", 180, "Esa es una de las grandes preguntas de la novela. ¿Quién es realmente el monstruo?"),
    ("104_maria", "maria", 160, "Porque la criatura no eligió existir."),
    ("105_fred", "fred", 140, "No."),
    ("106_maria", "maria", 160, "Alguien decidió crearla y después se desentendió de las consecuencias."),
    ("107_fred", "fred", 750, "Y piensa cómo se repite ese conflicto en nuestras historias modernas. Creamos sistemas inteligentes. Creamos seres artificiales. Creamos tecnologías capaces de transformar el mundo. Pero no siempre nos preguntamos qué responsabilidades adquirimos al hacerlo."),
    ("108_maria", "maria", 180, "Nos obsesionamos con saber si podemos construir algo, pero no necesariamente con saber si deberíamos construirlo."),
    ("109_fred", "fred", 180, "Esa es la esencia del horror tecnológico. No siempre es miedo a la máquina. A veces es miedo a lo que nuestra propia ambición puede provocar."),

    # ¿Por qué seguimos teniendo miedo a nuestras creaciones?
    ("110_maria", "maria", 700, "Hay algo curioso, Fred. Estas historias tienen décadas y, sin embargo, siguen sintiéndose bastante actuales."),
    ("111_fred", "fred", 180, "Sí. Y ahora que convivimos con sistemas de inteligencia artificial, automatización y algoritmos que intervienen en nuestras decisiones, adquieren una dimensión diferente."),
    ("112_maria", "maria", 180, "Aunque tampoco creo que debamos asumir que cualquier inteligencia artificial terminará convirtiéndose en Skynet."),
    ("113_fred", "fred", 180, "No, por supuesto. Son ficciones. Pero funcionan como experimentos mentales."),
    ("114_maria", "maria", 180, "Nos obligan a preguntarnos qué sucedería si las cosas que construimos empezaran a tener consecuencias que no habíamos previsto."),
    ("115_fred", "fred", 180, "Y ni siquiera necesitamos imaginar una máquina consciente para plantear ese problema. Piensa en sistemas que toman decisiones importantes, algoritmos que condicionan lo que vemos, tecnologías que influyen en nuestra percepción del mundo…"),
    ("116_maria", "maria", 180, "A veces uno entra a mirar un video de cocina y veinte minutos después está viendo a un señor explicando cómo sobrevivir a una invasión extraterrestre."),
    ("117_fred", "fred", 160, "(laughing) Eso también tiene algo de Matrix."),
    ("118_maria", "maria", 160, "Y sin necesidad de tomar ninguna pastilla."),
    ("119_fred", "fred", 200, "El verdadero riesgo no siempre está en una rebelión espectacular de las máquinas. También está en delegar demasiado, dejar de cuestionar y perder progresivamente nuestra capacidad de decidir."),
    ("120_maria", "maria", 180, "Quizás el monstruo no necesita destruirnos."),
    ("121_fred", "fred", 180, "Quizás basta con que dejemos de preguntarnos quién tiene el control."),

    # El monstruo frente al espejo
    ("122_fred", "fred", 2200, "Terminator, Matrix, Evangelion y Frankenstein parecen historias completamente diferentes. Pero todas tienen algo en común. La humanidad intenta trascender sus propios límites."),
    ("123_maria", "maria", 180, "Y descubre que no estaba preparada para las consecuencias."),
    ("124_fred", "fred", 180, "En Terminator construimos una inteligencia que amenaza nuestra supervivencia. En Matrix creamos un mundo donde la realidad puede ser manipulada. En Evangelion fabricamos criaturas que difuminan las fronteras entre lo humano, lo mecánico y lo divino. Y en Frankenstein… creamos vida sin asumir la responsabilidad de haberlo hecho."),
    ("125_maria", "maria", 180, "En todas hay una especie de arrogancia humana, ¿no?"),
    ("126_fred", "fred", 160, "Sí. Esa necesidad de jugar a ser dioses."),
    ("127_maria", "maria", 180, "Pero también hay algo profundamente humano en querer superar nuestros límites. La curiosidad, la creatividad, el deseo de descubrir."),
    ("128_fred", "fred", 160, "Claro. Y no deberíamos renunciar a eso."),
    ("129_maria", "maria", 180, "Entonces quizá la pregunta no sea si debemos dejar de crear máquinas."),
    ("130_fred", "fred", 180, "Sino qué clase de humanidad queremos conservar mientras las construimos."),
    ("131_maria", "maria", 800, "Sabes… creo que después de esta conversación voy a volver a ver Terminator de una manera completamente diferente."),
    ("132_fred", "fred", 180, "Ya no vas a ver simplemente a Arnold persiguiendo gente."),
    ("133_maria", "maria", 180, "Voy a ver una reflexión sobre la arrogancia tecnológica, la autonomía de las máquinas y el destino de la humanidad."),
    ("134_fred", "fred", -160, "¡Eso!"),
    ("135_maria", "maria", 160, "Aunque también voy a disfrutar viendo a Arnold."),
    ("136_fred", "fred", 160, "(laughing) Obviamente. Tampoco perdamos el sentido de la diversión."),
    ("137_fred", "fred", 450, "Antes de despedirnos, queremos dejarte una última pregunta. Durante siglos hemos imaginado monstruos que vienen de lugares desconocidos. Del infierno, del espacio, de otras dimensiones… Pero ¿qué sucede cuando el monstruo no viene de ninguna parte? ¿Qué sucede cuando somos nosotros quienes lo construimos?"),
    ("138_maria", "maria", 2200, "Y peor aún… ¿qué pasa si ese monstruo termina pareciéndose demasiado a nosotros?"),
    ("139_fred", "fred", 1200, "Hasta el próximo episodio."),
    ("140_maria", "maria", 180, "Y recuerda apagar el computador antes de dormir."),
    ("141_fred", "fred", 160, "¿Por seguridad?"),
    ("142_maria", "maria", 180, "(chuckle) No sé. Después de esta conversación, por si acaso."),
]


def generate_cyberpunk_bed(out_wav: Path, duration_sec: float, sr: int = 48000):
    """Dark analog cyberpunk synth pad + distant mechanical sub-bass pulse (92 BPM, D minor)."""
    total_samples = int(duration_sec * sr)
    t = np.arange(total_samples, dtype=np.float32) / sr

    bpm = 92.0
    beat_s = 60.0 / bpm
    bar_s = beat_s * 4.0

    # Slow dark chord progression in D minor (Dm9 -> Bbmaj7 -> Gm9 -> A7sus4)
    chords_hz = [
        [73.42, 146.83, 174.61, 220.00, 261.63],  # Dm9
        [58.27, 116.54, 174.61, 220.00, 293.66],  # Bbmaj7
        [49.00, 146.83, 196.00, 233.08, 293.66],  # Gm9
        [55.00, 110.00, 164.81, 220.00, 246.94],  # A7sus4
    ]

    stereo = np.zeros((total_samples, 2), dtype=np.float32)

    # 1. Distant mechanical 8th-note sub-bass pulse
    step_s = beat_s * 0.5
    num_steps = int(duration_sec / step_s)
    pulse_len = int(step_s * 0.85 * sr)
    tp = np.arange(pulse_len, dtype=np.float32) / sr
    p_env = (1.0 - np.exp(-tp * 90.0)) * np.exp(-tp * 9.5)

    for s in range(num_steps):
        st = s * step_s
        bar_idx = int(st / bar_s)
        root = chords_hz[(bar_idx // 2) % len(chords_hz)][0]
        accent = 1.0 if s % 4 == 0 else 0.55
        tone = (0.8 * np.sin(2.0 * np.pi * root * tp) + 0.25 * np.sin(2.0 * np.pi * root * 2.0 * tp)) * p_env * 0.22 * accent
        i0 = int(st * sr)
        i1 = min(total_samples, i0 + pulse_len)
        seg = tone[: i1 - i0]
        stereo[i0:i1, 0] += seg
        stereo[i0:i1, 1] += seg

    # 2. Dark analog detuned synth pads (2 bars per chord)
    seg_s = bar_s * 2.0
    num_segs = int(np.ceil(duration_sec / seg_s))
    for k in range(num_segs):
        t0 = k * seg_s
        i0 = int(t0 * sr)
        i1 = min(total_samples, int((t0 + seg_s) * sr))
        n = i1 - i0
        if n <= 0:
            continue
        tk = np.arange(n, dtype=np.float32) / sr
        env = np.minimum(1.0, tk / 1.2) * np.minimum(1.0, (seg_s - tk) / 1.2)
        env = np.maximum(0.0, env)
        chord = chords_hz[k % len(chords_hz)]
        pad_l = np.zeros(n, dtype=np.float32)
        pad_r = np.zeros(n, dtype=np.float32)
        for f in chord[1:]:
            pad_l += np.sin(2.0 * np.pi * (f * 0.998) * tk) + 0.18 * np.sin(2.0 * np.pi * (f * 2.002) * tk)
            pad_r += np.sin(2.0 * np.pi * (f * 1.002) * tk) + 0.18 * np.sin(2.0 * np.pi * (f * 1.998) * tk)
        stereo[i0:i1, 0] += (pad_l / len(chord)) * env * 0.22
        stereo[i0:i1, 1] += (pad_r / len(chord)) * env * 0.22

    # Fade in / out
    fade_in = np.minimum(1.0, t / 2.2)
    fade_out = np.minimum(1.0, np.maximum(0.0, (duration_sec - t) / 4.0))
    stereo *= (fade_in * fade_out)[:, None]

    peak = np.max(np.abs(stereo)) + 1e-9
    stereo *= 0.88 / peak

    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


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

    lead_in_samples = int(3.0 * sr)
    tail_samples = int(7.5 * sr)

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

    voice_full = Path("/tmp/aparte_06_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled La maquina como horror sobrenatural: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_06_cyberpunk_bed.wav")
    print(f"[BED] Generating dark analog cyberpunk synth bed ({total_dur}s)...", flush=True)
    generate_cyberpunk_bed(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_maquina_horror_sobrenatural.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_full),
            "-i", str(bed_wav),
            "-filter_complex",
            "[0:a]asplit=2[v_mix][v_sc];"
            "[1:a]aresample=48000,aecho=0.8:0.88:45|75:0.22|0.14,lowpass=f=2800,volume=0.14[b_raw];"
            "[b_raw][v_sc]sidechaincompress=threshold=0.012:ratio=4.5:attack=50:release=500:makeup=1[b_duck];"
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
