#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 17 (Solo Fred — Humanized Narration Engine v2):
"Guía: Cómo crear tu sistema infinito de ideas — Cap. 6/6: Las 7 formas de
convertir cualquier idea corriente en ideas originales"
Inspired by Álvaro García's series (27 de noviembre de 2026).

Uses podcasts/narration_engine.py with Fish Audio drama-3, preserving Fred's
cloned voice identity (96e5d63e023a4fd5b7926226ed8db011) while delivering
natural conversational pacing, semantic pauses, expressive cues, and
dynamic-preserving mastering.
"""
import argparse
import sys
from pathlib import Path

REPO = Path("/home/antigravity/frenti88/rockradio")
sys.path.insert(0, str(REPO / "podcasts"))

from generate_podcast_music import render_bed_wav  # noqa: E402
from narration_engine import (  # noqa: E402
    DEFAULT_MODEL_ID,
    DEFAULT_VOICE_ID,
    NarrativeUnit,
    render_humanized_podcast,
)

OUT_DIR = REPO / "podcasts"
CHUNKS_DIR = OUT_DIR / "chunks_aparte_17_v2"
OUT_MP3 = OUT_DIR / "aparte_siete_formas_ideas.mp3"

UNITS = [
    NarrativeUnit(
        unit_id="01_gancho_reflexivo",
        intent="question",
        pause_before_ms=0,
        pause_after_ms=1050,
        text=(
            "¿Cuántas veces has tenido una idea... la has mirado dos segundos, "
            "y la has tirado a la basura porque te pareció demasiado normal? "
            "[pause] Piénsalo por un momento. "
            "Casi todos hacemos eso, [sigh] y es una trampa enorme. "
            "Porque [thoughtful] casi ninguna idea brillante nace siendo brillante. "
            "Nace corriente... a veces hasta un poco aburrida. "
            "Lo que la vuelve inolvidable no es cómo llega, sino [emphasis] qué haces con ella después."
        ),
    ),
    NarrativeUnit(
        unit_id="02_contexto_serie",
        intent="conversational",
        pause_before_ms=300,
        pause_after_ms=900,
        text=(
            "Con eso llegamos al capítulo seis, el cierre de esta serie inspirada en la guía de Álvaro García, "
            "Cómo crear tu sistema infinito de ideas. "
            "Ya desmontamos el mito del genio solitario, entendimos cómo el cerebro fabrica la inspiración, "
            "jugamos con la supresión conceptual, vimos cómo crear mejor en grupo "
            "y cómo levantar una obra entera partiendo desde su conclusión. "
            "[pause] Y hoy toca el último paso: las siete formas de agarrar cualquier idea común que ya tengas anotada... "
            "y convertirla en algo [emphasis] genuinamente original."
        ),
    ),
    NarrativeUnit(
        unit_id="03_formas_1_y_2",
        intent="discovery",
        pause_before_ms=400,
        pause_after_ms=950,
        text=(
            "Mira, arranquemos con las dos primeras, porque son rapidísimas de aplicar. "
            "La primera es cambiar el contexto o el público. "
            "Una idea que suena súper gastada en un sector... de pronto puede ser revolucionaria en otro que nunca la ha visto. "
            "[pause] Y la segunda me encanta: [curious] ¿qué pasa si inviertes por completo la premisa? "
            "Si todo el mundo está explicando cómo hacer algo más rápido, más barato o más productivo... "
            "¿y si preguntas qué ocurre cuando lo haces [emphasis] deliberadamente más lento? "
            "[chuckle] Solo darle la vuelta al guion ya te saca del ruido."
        ),
    ),
    NarrativeUnit(
        unit_id="04_formas_3_y_4",
        intent="conversational",
        pause_before_ms=300,
        pause_after_ms=1000,
        text=(
            "A ver, vamos con la tercera y la cuarta. "
            "Tercera: llévala al extremo. Hazla diez veces más grande... o diez veces más pequeña. "
            "Cuando exageras la escala, aparecen preguntas que en tamaño normal jamás se te habrían ocurrido. "
            "[pause] Y la cuarta es cruzar tu idea con una disciplina que no tenga nada que ver. "
            "Por ejemplo, mezclar finanzas con narrativa, o diseño con gastronomía. "
            "Es justo en esos cruces raros donde las ideas dejan de sonar predecibles."
        ),
    ),
    NarrativeUnit(
        unit_id="05_formas_5_6_7",
        intent="revelation",
        pause_before_ms=400,
        pause_after_ms=1150,
        text=(
            "Y aquí viene lo interesante... las últimas tres formas son las que de verdad cambian el juego. "
            "Quinta: cambia el formato. Lo que resulta pesadísimo en un informe de veinte páginas "
            "puede cobrar vida en un audio de tres minutos o en una experiencia interactiva. "
            "[pause] Sexta: ponle una restricción creativa. Limitar el tiempo, el presupuesto o las herramientas "
            "te obliga a pensar distinto, porque ya no puedes resolverlo en piloto automático. "
            "[pause] Y séptima... [thoughtful] aterriza la idea en una historia humana concreta. "
            "Una teoría abstracta se olvida en cinco minutos; una escena real, con personas de carne y hueso, "
            "[emphasis] se queda para siempre."
        ),
    ),
    NarrativeUnit(
        unit_id="06_cierre_intimo",
        intent="intimate",
        pause_before_ms=450,
        pause_after_ms=0,
        volume_db=-1.0,
        text=(
            "Si miras hacia atrás, después de estos seis capítulos... te das cuenta de algo bastante liberador. "
            "[pause] El secreto de un sistema infinito de ideas nunca fue tener una mente sobrehumana. "
            "Fue dejar de esperar el rayo de inspiración perfecta, y empezar a jugar con método, con curiosidad... y con constancia. "
            "[pause] [confident] Gracias por acompañarme en todo este recorrido. "
            "Ahora te toca a ti abrir tu cuaderno, elegir una idea corriente... y ver hasta dónde la puedes llevar. "
            "[pause] Esto fue Aparte. Nos escuchamos en la próxima."
        ),
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build humanized Aparte Episode 17 (Cap. 6/6)")
    parser.add_argument(
        "--regen",
        nargs="*",
        default=None,
        help="Optional list of unit_ids to selectively regenerate (e.g. --regen 03_formas_1_y_2)",
    )
    args = parser.parse_args()

    render_humanized_podcast(
        UNITS,
        chunks_dir=CHUNKS_DIR,
        out_mp3=OUT_MP3,
        bed_renderer=render_bed_wav,
        voice_id=DEFAULT_VOICE_ID,
        model=DEFAULT_MODEL_ID,
        force_regen_ids=args.regen,
    )


if __name__ == "__main__":
    main()
