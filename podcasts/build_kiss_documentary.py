#!/usr/bin/env python3
"""
Produces all 25 independent narration tracks for:
"KISS: MÁS ALLÁ DEL MAQUILLAJE" (1972–2026)

Uses Fred's Fish Audio voice model (96e5d63e023a4fd5b7926226ed8db011) on drama-3,
with clean natural text (no forced paragraph-start bracket prefixes), subtle
cinematic background music bed (-20 dB under voice with soft sidechain ducking),
and independent mastering per track (-16 LUFS, 192 kbps stereo MP3).
"""
import json
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

OUT_DIR = REPO / "podcasts" / "kiss_doc"
RAW_DIR = OUT_DIR / "raw_voice"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

FISH_VOICE_ID = "96e5d63e023a4fd5b7926226ed8db011"
FISH_MODEL_ID = "drama-3"

# (slug, title, album, year, song_after, bed_vol, tail_sec, paragraphs)
TRACKS = [
    (
        "01_introduccion",
        "Introducción: Antes de que se encendieran las luces",
        "—", "1972–1973", None, 0.11, 3.5,
        [
            "Imagínate Nueva York, principios de los años setenta. Cuatro tipos que todavía no eran nadie, con una ambición descomunal y una idea que, para muchos, resultaba completamente absurda: ¿y si una banda de rock pudiera convertirse en algo mucho más grande que su propia música?",
            "Maquillaje, fuego, sangre, guitarras que parecían cobrar vida… y cuatro personajes que terminarían siendo reconocidos incluso por personas que jamás habían escuchado uno de sus discos. Pero antes de llenar estadios, antes de vender millones de álbumes y antes de tener un ejército de fanáticos, KISS estuvo peligrosamente cerca de desaparecer. Y ahí comienza nuestra historia.",
            "A ver, pongámonos un poquito en contexto. Todo arrancó con dos neoyorquinos tercos y ambiciosos: Gene Simmons y Paul Stanley. Venían de una banda llamada Wicked Lester que incluso alcanzó a grabar un álbum para Epic Records, pero el disco nunca salió porque ellos mismos sentían que no tenía dirección ni identidad. Querían otra cosa. Querían el gancho melódico de The Beatles, la teatralidad provocadora de Alice Cooper, la actitud callejera de los New York Dolls y la fantasía de los cómics que leían de niños.",
            "Para lograrlo necesitaban dos piezas más. Primero llegó Peter Criss, un baterista de Brooklyn con alma de jazz y rock clásico que había puesto un anuncio en Rolling Stone diciendo que estaba dispuesto a hacer cualquier cosa por triunfar. Y luego apareció Ace Frehley, un guitarrista del Bronx que llegó a la audición con un zapato rojo y otro naranja… pero apenas conectó su guitarra, todos supieron que era el indicado.",
            "Así nacieron cuatro personajes con identidad propia: The Demon, The Starchild, The Spaceman y The Catman. Cuatro desconocidos pintándose la cara frente a un espejo en Manhattan, listos para retar a toda la industria."
        ],
    ),
    (
        "02_kiss_1974",
        "Cap. I — KISS (1974)",
        "KISS", "1974", "Strutter", 0.11, 3.2,
        [
            "Arrancamos en 1973 y 1974. KISS tocaba en clubes pequeños de Nueva York, gastando lo poco que tenía en plataformas, vestuario y efectos caseros. El punto de quiebre llegó cuando Bill Aucoin, un productor de televisión que vio el potencial visual de inmediato, se convirtió en su mánager y los conectó con Neil Bogart, el visionario y temerario fundador de Casablanca Records.",
            "El álbum debut, simplemente titulado KISS, se grabó en los estudios Bell Sound de Nueva York a finales de 1973, con Kenny Kerner y Richie Wise en la producción. Fue un disco rápido, crudo y con presupuesto apretado. Pero imagínate por un momento esa situación: no tenían dinero para grandes lujos de estudio, así que metieron las canciones que ya tenían fogueadas en vivo.",
            "Y aunque el sonido en estudio se quedó un poco seco frente a lo que hacían en tarima, ahí ya estaban los cimientos de su repertorio clásico: Deuce, Black Diamond, Cold Gin… y un tema que captura como pocos esa energía callejera de Nueva York, escrito por Paul Stanley sobre una melodía de Gene Simmons. Escuchemos Strutter."
        ],
    ),
    (
        "03_hotter_than_hell_1974",
        "Hotter Than Hell (1974)",
        "Hotter Than Hell", "1974", "Parasite", 0.11, 3.2,
        [
            "El primer disco no explotó en ventas, pero Casablanca Records sabía que tenía que mantener a la banda en movimiento. Así que en agosto de 1974 mandaron a KISS a Los Ángeles para grabar su segundo álbum, Hotter Than Hell, nuevamente con Kerner y Wise.",
            "Y aquí es donde la historia se pone interesante. Los Ángeles fue un choque total para cuatro muchachos de Nueva York. A Paul Stanley incluso le robaron su guitarra el primer día. El estudio tenía un sonido más denso, más fangoso y más pesado que el debut, algo que con el tiempo muchos fanáticos terminaron adorando por su crudeza.",
            "La sesión de fotos de la portada también se volvió legendaria: según contaron posteriormente los integrantes, hubo tanto alcohol en el estudio que Ace Frehley terminó con media cara maquillada y tuvieron que retocarle el rostro con fotografía, mientras Peter Criss se quedó dormido en plena sesión. Comercialmente, el disco volvió a quedarse corto. Pero musicalmente nos dejó una de las guitarras más feroces de Ace Frehley en los setenta, cantada por Gene Simmons. Esto es Parasite."
        ],
    ),
    (
        "04_dressed_to_kill_1975",
        "Dressed to Kill (1975)",
        "Dressed to Kill", "1975", "C'mon and Love Me", 0.11, 3.2,
        [
            "Principios de 1975. La situación era crítica. Casablanca Records estaba al borde de la quiebra y KISS seguía sin tener un éxito real en la radio. No había dinero ni para contratar a un productor externo, así que el propio Neil Bogart se sentó en la consola para producir Dressed to Kill.",
            "Se grabó en tiempo récord en Electric Lady Studios, en Nueva York. Incluso la portada refleja esa urgencia: los cuatro vestidos con trajes prestados —algunos ni siquiera eran de su talla— posando en una esquina de Manhattan.",
            "De esas sesiones nació un himno pensado específicamente para cerrar los conciertos, Rock and Roll All Nite, aunque en su versión de estudio todavía no lograba reflejar el estallido que provocaba en vivo. Y en medio de esa presión financiera, Paul Stanley también entregó una de las canciones más directas y contagiosas del primer ciclo de la banda. Vamos con C'mon and Love Me."
        ],
    ),
    (
        "05_alive_1975",
        "Cap. II — Alive! (1975) y la KISS Army",
        "Alive!", "1975", "Rock and Roll All Nite (Alive!)", 0.12, 3.5,
        [
            "Llegamos al punto de inflexión. Mediados de 1975. Casablanca estaba contra las cuerdas y KISS llevaba tres discos de estudio sin despegar de verdad. Todo el mundo que los veía en vivo salía fascinado, pero los álbumes no lograban atrapar ese sudor, ese volumen ni ese caos eléctrico.",
            "¿La apuesta desesperada? Sacar un álbum doble en vivo. En aquella época, muchos en la industria pensaban que un disco en directo era un suicidio comercial para una banda que todavía no era masiva. Pero Bill Aucoin y Neil Bogart apostaron todo, y trajeron a Eddie Kramer para mezclar y darle forma a Alive!",
            "Y lo curioso de todo esto es que, años después, el propio Eddie Kramer y los integrantes reconocieron que el disco tuvo retoques y sobregrabaciones en estudio para que sonara como el público recordaba haberlo vivido, no necesariamente como una grabación cruda de consola. Más allá del debate, el resultado fue un terremoto. Alive! vendió millones, salvó a Casablanca Records y convirtió a KISS en gigantes de la noche a la mañana.",
            "En ese mismo impulso nació la KISS Army, cuando dos jóvenes de Terre Haute, Indiana —Bill Starkey y Jay Evans— presionaron a una emisora local hasta lograr que pusieran a KISS al aire. Y poco después la banda visitó Cadillac, Michigan, para apoyar a un equipo de fútbol americano escolar que escuchaba su música antes de cada partido. KISS había entendido algo que casi nadie más veía: los fanáticos no eran espectadores, eran parte del show. ¿Quién hubiera pensado que ese disco terminaría salvándoles la carrera? Aquí suena la versión que lo cambió todo: Rock and Roll All Nite, de Alive!"
        ],
    ),
    (
        "06_destroyer_1976",
        "Destroyer (1976)",
        "Destroyer", "1976", "Detroit Rock City", 0.11, 3.2,
        [
            "Con el éxito arrollador de Alive!, KISS tenía un reto enorme: demostrar que también podían hacer una obra grande en estudio. Para eso llamaron a Bob Ezrin, el productor detrás de los discos clásicos de Alice Cooper.",
            "Y Ezrin los puso en cintura. Literalmente les daba clases de teoría musical, les exigía disciplina y los empujó a experimentar con coros infantiles, arreglos orquestales, efectos de sonido y estructuras mucho más ambiciosas.",
            "De Destroyer nacieron piezas fundamentales: God of Thunder, que Paul Stanley escribió originalmente para sí mismo hasta que Ezrin la ralentizó y se la entregó a Gene Simmons para convertirla en el himno definitivo del Demonio; y Beth, una balada con piano y cuerdas cantada por Peter Criss que nadie esperaba que fuera el sencillo más exitoso de la banda en Estados Unidos hasta ese momento. Pero el disco abre con una tragedia convertida en gloria del rock: la historia de un fanático que murió en un accidente automovilístico camino a un concierto de KISS. Escuchemos Detroit Rock City."
        ],
    ),
    (
        "07_rock_and_roll_over_1976",
        "Rock and Roll Over (1976)",
        "Rock and Roll Over", "1976", "Calling Dr. Love", 0.11, 3.2,
        [
            "Destroyer fue un triunfo, pero parte del núcleo más duro de seguidores extrañaba la energía cruda y directa de los comienzos. Y KISS escuchó.",
            "A finales de 1976 regresaron con Eddie Kramer, pero en lugar de encerrarse en un estudio tradicional, alquilaron el teatro vacío Star Theatre en Nanuet, Nueva York. Peter Criss grabó su batería dentro de uno de los baños del teatro para conseguir una reverberación natural y explosiva, comunicándose con el resto por video.",
            "El contraste frente a Destroyer era evidente: nada de orquestas, nada de adornos cinematográficos. Solo cuatro músicos golpeando fuerte, con canciones pensadas para hacer temblar arenas enteras. Entre ellas, uno de los clásicos más infecciosos de Gene Simmons. Esto es Calling Dr. Love."
        ],
    ),
    (
        "08_love_gun_1977",
        "Love Gun (1977)",
        "Love Gun", "1977", "Love Gun", 0.12, 3.2,
        [
            "1977 fue el año en que KISS estuvo literalmente en todas partes. Encuestas de la época los situaban como la banda más popular entre los jóvenes estadounidenses, y Love Gun fue la banda sonora de ese momento.",
            "Grabado nuevamente con Eddie Kramer, el disco consolidó la fórmula de estadios y marcó un hito muy especial: por primera vez, Ace Frehley tomó el micrófono como cantante principal en Shock Me, inspirada en una descarga eléctrica real que casi lo mata en el escenario en Lakeland, Florida.",
            "Pero el corazón del álbum es la canción que le da título, una de las composiciones favoritas del propio Paul Stanley, donde además grabó el bajo y una guitarra rítmica que empuja la canción sin descanso. Vamos con Love Gun."
        ],
    ),
    (
        "09_alive_ii_1977",
        "Alive II (1977)",
        "Alive II", "1977", "I Stole Your Love (Alive II)", 0.11, 3.2,
        [
            "Para cerrar 1977, KISS publicó Alive II, el retrato definitivo de su apogeo como fenómeno de masas. Los escenarios eran cada vez más gigantescos, la pirotecnia más intensa y la devoción del público rozaba la locura.",
            "El álbum combinó tres lados grabados en directo —principalmente en el Forum de Los Ángeles— con un cuarto lado de canciones nuevas de estudio, en una época en la que ya empezaban a notarse las primeras grietas internas, con sesiones donde Ace Frehley no siempre participaba en todos los temas.",
            "Aun así, la fuerza de la banda en tarima seguía siendo arrolladora. Escuchemos esa descarga inicial: I Stole Your Love, en su versión de Alive II."
        ],
    ),
    (
        "10_solistas_1978",
        "Cap. III — El imperio y los cuatro álbumes solistas (1978)",
        "Solo Albums", "1978", "New York Groove (Ace Frehley)", 0.11, 3.5,
        [
            "Y aquí es donde el éxito comenzó a romperlo todo por dentro. Para 1978, KISS ya no era solo una banda de rock: era una maquinaria de entretenimiento. Había muñecos, loncheras, máquinas de pinball, disfraces y un cómic de Marvel cuya campaña promocional incluyó una famosa sesión en la que los integrantes donaron pequeñas cantidades de sangre para mezclarlas con la tinta roja de la imprenta. Existen distintas versiones sobre cuánto de eso fue real y cuánto pura genialidad publicitaria, pero logró exactamente lo que buscaban: que todo el mundo hablara de ellos.",
            "También llegó la película para televisión KISS Meets the Phantom of the Park. Bueno… estamos hablando de KISS. Evidentemente, nada podía ser demasiado exagerado. La producción fue un caos, los músicos apenas soportaban el rodaje y el resultado hoy se recuerda con una mezcla de cariño y mucha risa.",
            "En medio de esas tensiones, y para evitar que la banda se separara, Bill Aucoin ideó una jugada sin precedentes: lanzar cuatro álbumes solistas el mismo día, el 18 de septiembre de 1978. Cada disco mostraba quién era realmente cada integrante. Paul Stanley entregó rock melódico muy cercano al sonido clásico de KISS; Gene Simmons armó un desfile ecléctico lleno de invitados famosos; Peter Criss se volcó hacia el R&B y el soul; y Ace Frehley, para sorpresa de muchos, grabó el disco más rockero y exitoso comercialmente de los cuatro. Para representar ese cruce de caminos, escuchemos el gran hit de The Spaceman: New York Groove, de Ace Frehley."
        ],
    ),
    (
        "11_dynasty_1979",
        "Dynasty (1979)",
        "Dynasty", "1979", "I Was Made for Lovin' You", 0.11, 3.2,
        [
            "1979. La fiebre de la música disco dominaba las listas y las tensiones internas de KISS estaban al límite. Peter Criss había sufrido un accidente automovilístico y, según los registros de las sesiones, apenas tocó en una canción de todo el álbum; el baterista de sesión Anton Fig se encargó del resto.",
            "Bajo la producción de Vini Poncia, Dynasty mezcló el rock de KISS con el pulso bailable de la época. Muchos fanáticos tradicionales sintieron que la banda los estaba traicionando. Pero Paul Stanley, junto a Desmond Child y Vini Poncia, escribió un tema casi como un reto para demostrar que podía hacer un éxito disco en minutos.",
            "Lo irónico es que aquella canción tan criticada en su momento terminó convirtiéndose en uno de los mayores himnos globales de toda la historia de KISS. Aquí suena I Was Made for Lovin' You."
        ],
    ),
    (
        "12_unmasked_1980",
        "Unmasked (1980)",
        "Unmasked", "1980", "Shandi", 0.10, 3.2,
        [
            "Si Dynasty había dividido opiniones, Unmasked en 1980 llevó el giro aún más lejos hacia el pop rock y el power pop. Otra vez con Vini Poncia y Anton Fig en la batería, Peter Criss todavía apareció en la portada y en el video promocional, pero en la práctica ya estaba fuera de la banda.",
            "En Estados Unidos el disco se desplomó comercialmente; el público rockero se había alejado. Sin embargo, en países como Australia, Nueva Zelanda y partes de Europa, KISS seguía llenando estadios y el álbum fue un éxito rotundo.",
            "De ese contraste quedó una joya melódica y nostálgica de Paul Stanley, muy distinta al rugido de los setenta, pero imposible de olvidar. Escuchemos Shandi."
        ],
    ),
    (
        "13_the_elder_1981",
        "Music from “The Elder” (1981)",
        "Music from “The Elder”", "1981", "A World Without Heroes", 0.10, 3.5,
        [
            "Bueno… llegamos a uno de los momentos más extraños, pero también más fascinantes, de toda la historia de KISS.",
            "Estamos en 1981. Eric Carr ya había llegado a la batería con una energía descomunal, la banda estaba perdiendo popularidad en Estados Unidos, Ace Frehley no estaba nada contento con el rumbo musical… y Gene Simmons y Paul Stanley querían demostrarle al mundo que podían hacer algo mucho más sofisticado.",
            "¿Y qué se les ocurre? Hacer un álbum conceptual de fantasía medieval, basado en una historia sobre un joven héroe destinado a enfrentar las fuerzas del mal. Una apuesta bastante arriesgada para una banda que, unos años antes, nos estaba invitando a rockear toda la noche.",
            "Con Bob Ezrin nuevamente en la producción y la colaboración de nada menos que Lou Reed en varias letras, el disco sumó arreglos orquestales, aires progresivos y una sensibilidad completamente distinta. Ace Frehley, frustrado, grabó gran parte de sus guitarras desde su estudio casero. Comercialmente fue un desastre. Pero escúchalo hoy, sin esperar que suene como Love Gun, y quizás encuentres algo extraordinario. Esta canción, coescrita con Lou Reed, demuestra que detrás de todo ese maquillaje también había espacio para la fragilidad. Esto es A World Without Heroes."
        ],
    ),
    (
        "14_creatures_of_the_night_1982",
        "Creatures of the Night (1982)",
        "Creatures of the Night", "1982", "I Love It Loud", 0.11, 3.2,
        [
            "Después del golpe de The Elder, KISS sabía que tenía que volver a golpear fuerte. En 1982 grabaron Creatures of the Night, uno de los discos más pesados y oscuros de toda su carrera.",
            "El sonido de la batería de Eric Carr era sencillamente descomunal, como truenos en medio de la tormenta. Ace Frehley todavía figuraba en la portada por cuestiones contractuales, pero ya estaba prácticamente fuera de la banda, así que varios guitarristas pasaron por el estudio, incluido un joven Vinnie Vincent, cuyo aporte compositivo fue decisivo.",
            "Curiosamente, cuando salió en 1982, el disco no vendió bien en Estados Unidos; el público todavía no les perdonaba el desvío anterior. Pero con los años, Creatures of the Night fue reivindicado como una obra maestra del hard rock ochentero. Escuchemos su himno de resistencia: I Love It Loud."
        ],
    ),
    (
        "15_lick_it_up_1983",
        "Cap. IV — Lick It Up (1983)",
        "Lick It Up", "1983", "Lick It Up", 0.11, 3.2,
        [
            "Septiembre de 1983. KISS tomó la decisión más arriesgada de su carrera: presentarse en MTV sin una sola gota de maquillaje.",
            "Imagínate lo que significaba eso. Durante diez años, sus rostros reales habían sido un secreto celosamente guardado. Pero el mundo estaba cambiando, una nueva generación de bandas jóvenes dominaba la escena y KISS necesitaba demostrar que podía sobrevivir solo con sus canciones.",
            "Lick It Up, con Vinnie Vincent ya como guitarrista oficial, fue el renacimiento. Sonaba fresco, afilado, directo y hambriento. El público respondió, el disco devolvió a la banda al disco de platino y abrió oficialmente la era sin maquillaje. Vamos con Lick It Up."
        ],
    ),
    (
        "16_animalize_1984",
        "Animalize (1984)",
        "Animalize", "1984", "Heaven's on Fire", 0.11, 3.2,
        [
            "Para 1984, la relación con Vinnie Vincent ya se había roto, así que KISS incorporó a un virtuoso de la guitarra llamado Mark St. John. Su paso por la banda fue brevísimo debido a una condición médica en sus manos que le impidió continuar la gira, pero dejó su huella en Animalize.",
            "En esta etapa, Gene Simmons estaba cada vez más distraído con el cine y otros negocios, así que Paul Stanley se echó la banda al hombro y asumió el liderazgo creativo. El resultado fue un álbum vibrante, adaptado de lleno al hard rock de MTV en los ochenta, y uno de los mayores éxitos comerciales de la década para KISS. Aquí suena Heaven's on Fire."
        ],
    ),
    (
        "17_asylum_1985",
        "Asylum (1985)",
        "Asylum", "1985", "Tears Are Falling", 0.11, 3.2,
        [
            "Tras la salida de Mark St. John, llegó alguien que traería algo rarísimo en la historia de KISS: estabilidad. Bruce Kulick tomó la guitarra líder en 1985 y se quedaría más de una década, aportando técnica, elegancia y profesionalismo.",
            "Asylum reflejaba por completo la estética colorida, brillante y exagerada de mediados de los ochenta. Los videos en MTV eran parte esencial del juego, y Paul Stanley volvió a entregar un sencillo lleno de ganchos melódicos y coros pensados para la radio. Escuchemos Tears Are Falling."
        ],
    ),
    (
        "18_crazy_nights_1987",
        "Crazy Nights (1987)",
        "Crazy Nights", "1987", "Crazy Crazy Nights", 0.11, 3.2,
        [
            "En 1987, el glam metal reinaba en el planeta. Bandas como Bon Jovi o Def Leppard —que habían crecido admirando a KISS— estaban vendiendo millones con producciones pulidas y teclados brillantes.",
            "KISS decidió competir en ese mismo terreno y contrató al productor Ron Nevison para grabar Crazy Nights. El disco incorporó sintetizadores prominentes y un enfoque abiertamente comercial. Aunque dividió a los seguidores más puristas, en el Reino Unido y Europa fue un fenómeno enorme y nos dejó uno de los coros más optimistas de la banda. Esto es Crazy Crazy Nights."
        ],
    ),
    (
        "19_hot_in_the_shade_1989",
        "Hot in the Shade (1989)",
        "Hot in the Shade", "1989", "Forever", 0.10, 3.5,
        [
            "Cerrando los ochenta, KISS buscó un sonido más crudo y menos pulido en Hot in the Shade, un álbum largo grabado casi sobre maquetas en estudio.",
            "Y aquí apareció una combinación inesperada: Paul Stanley se sentó a componer con Michael Bolton, y juntos crearon una balada acústica que devolvió a KISS al Top 10 de Estados Unidos por primera vez desde 1976.",
            "Pero este disco también guarda un matiz melancólico: sería el último álbum de estudio completo con Eric Carr en la batería, un músico querido por todos que pronto enfrentaría la batalla más difícil de su vida. Escuchemos Forever."
        ],
    ),
    (
        "20_revenge_1992",
        "Cap. V — Eric Carr y Revenge (1992)",
        "Revenge", "1992", "Unholy", 0.09, 3.5,
        [
            "Al comenzar los años noventa, KISS vivió el golpe más duro de su historia. A principios de 1991, a Eric Carr le diagnosticaron un tipo muy raro de cáncer de corazón. Luchó con una valentía admirable, pero falleció el 24 de noviembre de 1991, con apenas 41 años. Su pérdida dejó un vacío enorme, tanto en lo musical como en lo humano.",
            "Con el corazón golpeado, la banda reclutó a Eric Singer en la batería, volvió a llamar a Bob Ezrin y hasta retomó la colaboración compositiva con Vinnie Vincent. Así nació Revenge en 1992: un disco oscuro, pesado, rabioso y maduro, dedicado a la memoria de Eric Carr.",
            "Para muchos seguidores, Revenge es el mejor álbum de KISS fuera de los años setenta. Y abre con un rugido inolvidable de Gene Simmons. Escuchemos Unholy."
        ],
    ),
    (
        "21_carnival_of_souls_1997",
        "Carnival of Souls: The Final Sessions (1997)",
        "Carnival of Souls: The Final Sessions", "1997", "Hate", 0.10, 3.2,
        [
            "Después de Revenge llegaron Alive III, las convenciones oficiales de fanáticos y, en 1995, un concierto que lo sacudió todo: el MTV Unplugged, donde Ace Frehley y Peter Criss subieron como invitados especiales. La química fue tan fuerte que disparó el camino hacia la reunión original.",
            "Pero antes de que esa reunión se concretara, la formación de Simmons, Stanley, Kulick y Singer ya había grabado un disco completo entre finales de 1995 y principios de 1996, profundamente influenciado por el grunge y los sonidos oscuros de Seattle.",
            "Con la reunión en marcha, el álbum quedó guardado en el cajón hasta que las copias piratas obligaron a publicarlo oficialmente en 1997 bajo el título Carnival of Souls: The Final Sessions. Un disco denso, arriesgado y muy diferente a todo lo demás en su catálogo. Vamos con Hate."
        ],
    ),
    (
        "22_psycho_circus_1998",
        "Cap. VI — La reunión y Psycho Circus (1998)",
        "Psycho Circus", "1998", "Psycho Circus", 0.11, 3.2,
        [
            "En 1996 ocurrió lo que millones creían imposible: Gene Simmons, Paul Stanley, Ace Frehley y Peter Criss volvieron a maquillarse y salieron de gira mundial. El regreso fue apoteósico; generaciones enteras que solo habían visto a KISS en discos y pósteres por fin los tenían enfrente.",
            "La expectativa por un nuevo álbum de estudio de los cuatro originales era gigantesca. Pero cuando llegó Psycho Circus en 1998, la realidad detrás de escena era mucho más compleja que la foto de portada. Las viejas tensiones habían regresado y, según los créditos y testimonios de la época, los cuatro integrantes originales solo tocaron juntos en una canción del disco, mientras músicos como Tommy Thayer y Kevin Valentine cubrieron gran parte de las sesiones.",
            "Aun con esa contradicción, la canción titular capturó con fuerza el espíritu teatral del regreso. Escuchemos Psycho Circus."
        ],
    ),
    (
        "23_sonic_boom_2009",
        "Sonic Boom (2009)",
        "Sonic Boom", "2009", "Modern Day Delilah", 0.11, 3.2,
        [
            "El nuevo milenio trajo una primera gira de despedida, las salidas definitivas de Ace Frehley y Peter Criss, y la llegada de Tommy Thayer en la guitarra junto al regreso de Eric Singer en la batería.",
            "El hecho de que Thayer y Singer adoptaran el maquillaje de The Spaceman y The Catman abrió uno de los debates más encendidos entre los seguidores: para muchos era una falta de respeto a los creadores originales; para la banda, los personajes pertenecían a KISS y debían seguir vivos en el escenario.",
            "Durante once años no hubo música nueva, hasta que en 2009 Paul Stanley tomó las riendas de la producción y grabaron Sonic Boom, un álbum directo, pensado para recuperar el espíritu clásico de los setenta sin artificios modernos. Escuchemos Modern Day Delilah."
        ],
    ),
    (
        "24_monster_2012",
        "Monster (2012)",
        "Monster", "2012", "Hell or Hallelujah", 0.11, 3.2,
        [
            "En 2012, con esa misma formación consolidada, KISS regresó al estudio para grabar Monster. Apostaron por equipo analógico, amplificadores clásicos y un sonido orgánico, sin trucos digitales ni baladas de relleno.",
            "Nadie lo sabía con certeza en aquel momento, pero con el paso de los años Monster terminó convirtiéndose, hasta hoy, en el último álbum de estudio de toda la discografía de KISS. Un cierre rockero, orgulloso y sin disculpas. Escuchemos Hell or Hallelujah."
        ],
    ),
    (
        "25_epilogo_el_maquillaje_es_eterno",
        "Cap. VII y Epílogo — El maquillaje es eterno (2013–2026)",
        "—", "2013–2026", None, 0.11, 8.0,
        [
            "La última etapa de KISS fue tan grandiosa y polémica como toda su historia. En 2014 ingresaron finalmente al Rock & Roll Hall of Fame, en una ceremonia marcada por las diferencias públicas sobre qué formaciones debían ser reconocidas y por la decisión de no tocar en vivo esa noche.",
            "Luego vino la gira End of the Road, que culminó el 2 de diciembre de 2023 en el Madison Square Garden de Nueva York, la misma ciudad donde todo había comenzado cincuenta años atrás. Esa noche anunciaron el siguiente paso: los avatares digitales, seguidos en 2024 por la adquisición de su catálogo, marca y propiedad intelectual por parte de la compañía sueca Pophouse.",
            "Y en medio de esa transición hacia el futuro, en octubre de 2025 el mundo del rock recibió una noticia que dolió hondo: el fallecimiento de Ace Frehley, a los 74 años. El hombre del Bronx que llegó con un zapato de cada color y terminó inspirando a generaciones enteras de guitarristas que aprendieron a tocar escuchando sus solos.",
            "Sin embargo, el vínculo con la KISS Army nunca se apagó. En noviembre de 2025 y nuevamente en noviembre de 2026, KISS se reencontró con miles de fanáticos en Las Vegas para los eventos especiales de KISS Kruise: Land-Locked In Vegas, ofreciendo conciertos íntimos y sin maquillaje que demostraron que la historia sigue viva.",
            "Quizás nunca fueron la banda más virtuosa del mundo. Quizás tomaron decisiones que muchos de sus propios seguidores jamás entendieron. Y sí… seguramente vendieron más cosas de las que cualquiera habría imaginado. Pero hicieron algo que muy pocas bandas consiguieron. Crearon un universo al que millones de personas sintieron que pertenecían.",
            "Porque escuchar a KISS no era solamente escuchar rock. Era elegir un personaje, coleccionar discos, aprender a tocar guitarra, pintarse la cara frente al espejo y sentir, aunque fuera durante unos minutos, que uno también podía ser extraordinario. Y tal vez por eso, cuando se apagan las luces, desaparece el humo y cae el último confeti… KISS sigue existiendo. En sus discos. En sus historias. Y en quienes todavía suben el volumen cuando escuchan esa primera guitarra."
        ],
    ),
]


def load_wav_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            arr = arr.reshape(-1, 2).mean(axis=1)
        return arr


def build_track(slug, title, album, year, song_after, bed_vol, tail_sec, paragraphs):
    sr = 48000
    out_mp3 = OUT_DIR / f"{slug}.mp3"
    if out_mp3.exists() and out_mp3.stat().st_size > 10000:
        dur = probe_dur(out_mp3)
        print(f"[REUSE TRACK] {slug}.mp3 ({dur:.2f}s)", flush=True)
        return dur

    clips = []
    for idx, text in enumerate(paragraphs):
        raw_mp3 = RAW_DIR / f"{slug}_p{idx+1:02d}.mp3"
        raw_wav = RAW_DIR / f"{slug}_p{idx+1:02d}.wav"
        if not (raw_mp3.exists() and raw_mp3.stat().st_size > 2000):
            print(f"[TTS] {slug} p{idx+1:02d}/{len(paragraphs)}...", flush=True)
            g._fish_audio_tts_sync(
                text,
                str(raw_mp3),
                reference_id=FISH_VOICE_ID,
                model=FISH_MODEL_ID,
                temperature=0.60,
                top_p=0.76,
            )
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(raw_mp3),
                "-af", "aresample=48000,silenceremove=start_periods=1:start_silence=0.04:start_threshold=-45dB",
                "-ac", "1", "-ar", str(sr),
                str(raw_wav),
            ],
            check=True,
        )
        clips.append(load_wav_mono(raw_wav))

    lead_in = int(2.0 * sr)
    gap_between = int(0.9 * sr)
    tail = int(tail_sec * sr)

    cursor = lead_in
    placements = []
    for i, audio in enumerate(clips):
        if i > 0:
            cursor += gap_between
        placements.append((cursor, audio))
        cursor += len(audio)

    total_samples = cursor + tail
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for start, audio in placements:
        end = start + len(audio)
        stereo[start:end, 0] += audio
        stereo[start:end, 1] += audio

    peak = np.max(np.abs(stereo)) + 1e-9
    if peak > 0.95:
        stereo *= 0.95 / peak

    voice_wav = Path(f"/tmp/kiss_doc_{slug}_voice.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_wav)
    bed_wav = Path(f"/tmp/kiss_doc_{slug}_bed.wav")
    render_bed_wav(bed_wav, total_dur + 1.0)

    fade_out_dur = 4.5 if slug == "25_epilogo_el_maquillaje_es_eterno" else 2.6
    fade_start = max(0.0, total_dur - fade_out_dur)

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(voice_wav),
            "-i", str(bed_wav),
            "-filter_complex",
            f"[0:a]asplit=2[v_mix][v_sc];"
            f"[1:a]aresample=48000,aecho=0.8:0.88:28|42:0.16|0.10,lowpass=f=4200,volume={bed_vol},"
            f"afade=t=in:st=0:d=1.8,afade=t=out:st={fade_start:.2f}:d={fade_out_dur:.2f}[b_raw];"
            f"[b_raw][v_sc]sidechaincompress=threshold=0.012:ratio=4.0:attack=50:release=480:makeup=1[b_duck];"
            f"[v_mix][b_duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=2,"
            f"loudnorm=I=-16:TP=-1.0:LRA=11[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
            str(out_mp3),
        ],
        check=True,
    )
    dur = probe_dur(out_mp3)
    print(f"[DONE] {slug}.mp3 -> {dur:.2f}s ({out_mp3.stat().st_size} B)", flush=True)
    return dur


def main():
    manifest = []
    total_narration_sec = 0.0
    for item in TRACKS:
        slug, title, album, year, song_after, bed_vol, tail_sec, paragraphs = item
        dur = build_track(slug, title, album, year, song_after, bed_vol, tail_sec, paragraphs)
        total_narration_sec += dur
        manifest.append({
            "slug": slug,
            "title": title,
            "album": album,
            "year": year,
            "song_after": song_after,
            "audio": f"podcasts/kiss_doc/{slug}.mp3",
            "duration_sec": round(dur, 2),
        })

    (OUT_DIR / "playlist.json").write_text(
        json.dumps(
            {
                "title": "KISS: MÁS ALLÁ DEL MAQUILLAJE",
                "total_tracks": len(manifest),
                "total_narration_sec": round(total_narration_sec, 2),
                "tracks": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nALL 25 TRACKS COMPLETE! Total narration: {total_narration_sec:.1f}s ({total_narration_sec/60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
