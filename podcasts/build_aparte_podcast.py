#!/usr/bin/env python3
"""
Synthesizes the Aparte podcast episode in natural human-paced chunks using
Fish Audio (drama-3) with the user's official voice, stitches with natural
pauses, and masters to -16 LUFS / -1 dBTP.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/antigravity/frenti88/rockradio")
sys.path.insert(0, str(REPO / "scripts"))
import generate_dj_fred_track as g

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_01"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS = [
    (
        "01_intro",
        0.7,
        "¿Y si la época dorada del diseño no estuviera terminando, sino apenas comenzando? "
        "Últimamente escuchamos mucho que el diseño UX y UI está en crisis. Y, seamos sinceros, hay razones para pensar así. "
        "Diseñadores con años de experiencia tienen dificultades para encontrar trabajo. Las oportunidades para quienes apenas comienzan son cada vez más competitivas. "
        "Algunas empresas están reduciendo sus equipos de diseño, mientras herramientas de inteligencia artificial como Claude pueden construir sitios web e interfaces funcionales en cuestión de minutos."
    ),
    (
        "02_preguntas",
        0.7,
        "Entonces, es inevitable preguntarse: ¿Qué va a pasar con nosotros, los diseñadores? "
        "¿Tiene sentido seguir aprendiendo diseño? ¿Cuánto tiempo pasará antes de que una inteligencia artificial pueda hacer gran parte de nuestro trabajo? "
        "Son preguntas válidas. Pero creo que estamos mirando esta transformación desde una perspectiva incompleta. "
        "Porque quizás lo que está llegando a su fin no es el diseño, sino la manera en la que hemos entendido nuestra profesión durante los últimos años. Y esa diferencia lo cambia todo."
    ),
    (
        "03_distancia",
        0.65,
        "Durante mucho tiempo, los diseñadores hemos tenido una limitación importante: la distancia entre lo que imaginamos y lo que realmente podemos construir. "
        "Podíamos dedicar días enteros a diseñar una experiencia en Figma, perfeccionar una interacción, pensar en una animación y cuidar hasta el más mínimo detalle. "
        "Y después llegaba esa conversación que muchos conocemos. Eso es muy complejo de desarrollar. No tenemos tiempo. No está dentro del alcance. Dejémoslo para una segunda fase. "
        "Y esa segunda fase, muchas veces, nunca llegaba."
    ),
    (
        "04_ia_puente",
        0.65,
        "Hoy, la inteligencia artificial está reduciendo esa distancia. "
        "Si tienes una idea, puedes construir un prototipo funcional. Si quieres experimentar con una interacción, puedes probarla. "
        "Si quieres explorar diferentes maneras de resolver un problema, puedes hacerlo sin depender de semanas de desarrollo. "
        "Eso no significa que los desarrolladores hayan dejado de ser necesarios. Significa que los diseñadores tenemos una capacidad de experimentación que antes era mucho más difícil de alcanzar."
    ),
    (
        "05_criterio",
        0.7,
        "Y aquí aparece una pregunta interesante. Si cualquier persona puede construir una interfaz utilizando inteligencia artificial, ¿por qué seguiríamos necesitando diseñadores? "
        "Imagina que le entregamos exactamente la misma herramienta a dos personas. Una sin experiencia en diseño y otra con años de experiencia comprendiendo usuarios, productos y negocios. "
        "Ambas pueden construir una aplicación. Pero eso no significa que ambas puedan construir una buena experiencia. "
        "Un diseñador experimentado puede identificar problemas que otras personas ni siquiera perciben. Sabe cuándo una interacción genera incertidumbre, cuándo una jerarquía visual no funciona, "
        "cuándo estamos pidiendo información innecesaria o cuándo una decisión aparentemente pequeña puede generar una fricción enorme. "
        "La diferencia ya no está únicamente en la capacidad de ejecutar. Está en el criterio."
    ),
    (
        "06_proposito",
        0.65,
        "Y ese criterio se vuelve especialmente importante cuando producir interfaces es cada vez más fácil. "
        "Porque construir una pantalla es una cosa. Comprender por qué esa pantalla necesita existir es otra completamente diferente. "
        "¿De qué sirve crear un proceso de registro visualmente espectacular si las personas lo abandonan antes de terminarlo? "
        "¿De qué sirve implementar una animación maravillosa si el usuario no entiende qué debe hacer después? "
        "¿De qué sirve construir una aplicación en diez minutos si estamos resolviendo el problema equivocado?"
    ),
    (
        "07_oportunidad",
        0.65,
        "Creo que ahí está una de las mayores oportunidades para nuestra profesión. "
        "Durante años hemos dedicado una cantidad considerable de tiempo a aprender herramientas. A dominar Figma, construir componentes, organizar sistemas de diseño y perfeccionar interfaces. "
        "Todo eso sigue teniendo valor. Pero dominar una herramienta nunca debió ser el objetivo final del diseño. "
        "Lo verdaderamente importante es comprender cómo piensan las personas, cómo toman decisiones, qué les genera confianza, qué les produce incertidumbre y qué necesitan realmente. "
        "También debemos comprender el negocio. Entender cómo nuestras decisiones afectan la conversión, la retención, la eficiencia y los resultados de un producto. "
        "Necesitamos fortalecer nuestro criterio visual. Aprender a reconocer cuándo algo funciona, cuándo no funciona y, sobre todo, por qué. "
        "Y, por supuesto, aprender a trabajar con inteligencia artificial. No solamente para generar pantallas, sino para investigar, contrastar información, explorar hipótesis, construir soluciones y validar ideas."
    ),
    (
        "08_portafolio",
        0.65,
        "Pensemos también en cómo estamos construyendo nuestros portafolios. "
        "Durante mucho tiempo, un portafolio atractivo era una de las principales formas de demostrar nuestras capacidades. "
        "Pero en un mundo donde una inteligencia artificial puede generar interfaces atractivas en segundos, mostrar únicamente el resultado visual empieza a ser insuficiente. "
        "Lo interesante está detrás. ¿Qué problema identificaste? ¿Cómo descubriste que realmente era un problema? ¿Qué alternativas consideraste? "
        "¿Por qué descartaste algunas? ¿Cómo comprobarías que tu solución mejora la experiencia? "
        "Esas preguntas revelan algo que una colección de pantallas difícilmente puede mostrar: tu capacidad de pensar."
    ),
    (
        "09_aprender",
        0.65,
        "Y si queremos prepararnos para esta nueva etapa, también necesitamos cambiar la forma en la que aprendemos diseño. "
        "Menos obsesión por dominar herramientas y más interés por comprender problemas. "
        "Menos preocupación por producir interfaces perfectas y más curiosidad por descubrir si realmente estamos construyendo algo valioso. "
        "Menos tiempo dedicado a demostrar que sabemos diseñar pantallas y más tiempo demostrando que sabemos tomar decisiones. "
        "La inteligencia artificial no elimina la incertidumbre del mercado laboral. Tampoco garantiza que todos los diseñadores tengan las mismas oportunidades. "
        "Hay cambios reales que debemos reconocer y habilidades que necesitamos transformar. Pero también tenemos delante una oportunidad extraordinaria."
    ),
    (
        "10_cierre",
        0.8,
        "Por primera vez, muchos diseñadores podemos investigar, imaginar, construir, experimentar y validar nuestras propias ideas con una autonomía que hace unos años parecía difícil de alcanzar. "
        "Quizás el futuro del diseño consista precisamente en recuperar aquello que siempre debió estar en el centro de nuestra profesión. "
        "Comprender antes de construir. Preguntar antes de responder. Pensar antes de ejecutar. "
        "Porque cuando construir cualquier cosa se vuelve más fácil, decidir qué vale la pena construir se vuelve mucho más importante. "
        "Y quizás, dentro de unos años, cuando miremos hacia atrás, descubramos que este no fue el momento en el que el diseño perdió su valor. "
        "Fue el momento en el que finalmente pudimos demostrar todo su potencial. "
        "La época dorada del diseño no ha terminado. Acaba de empezar. "
        "Esto es Aparte. Ideas que merecen ser escuchadas."
    ),
]


def probe_dur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        text=True,
    ).strip()
    return round(float(out), 2)


def main():
    concat_entries = []
    for name, pause_sec, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{name}.mp3"
        if not (mp3.exists() and mp3.stat().st_size > 5000):
            print(f"[TTS] Synthesizing {name}...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), model="drama-3")
        else:
            print(f"[REUSE] {name}.mp3", flush=True)
        # Pad each chunk with natural breathing silence at the end
        padded = CHUNKS_DIR / f"{name}_pad.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(mp3),
                "-af", f"aresample=48000,apad=pad_dur={pause_sec}",
                str(padded),
            ],
            check=True,
        )
        concat_entries.append(f"file '{padded}'")

    list_file = Path("/tmp/aparte_concat.txt")
    list_file.write_text("\n".join(concat_entries) + "\n", encoding="utf-8")

    out_mp3 = OUT_DIR / "aparte_epoca_dorada_diseno.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-af", "loudnorm=I=-16:TP=-1.0:LRA=11",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(out_mp3),
        ],
        check=True,
    )
    dur = probe_dur(out_mp3)
    print(f"DONE! {out_mp3} -> {dur}s ({out_mp3.stat().st_size} B)", flush=True)


if __name__ == "__main__":
    main()
