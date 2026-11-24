#!/usr/bin/env python3
"""
Builds Aparte Podcast Episode 7 (Solo Fred):
"La dura rutina de George Orwell: escribir 1984 en una isla remota"
Intimate solo monologue narrated by Fred (g.DEFAULT_FISH_VOICE) in Fish Audio drama-3,
with expressive natural variations, thoughts out loud, short anecdotes, soft laughs,
sighs, reflective pauses, and the custom Drive background music bed.
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
CHUNKS_DIR = OUT_DIR / "chunks_aparte_07"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

VOICE_FRED = g.DEFAULT_FISH_VOICE

# (id, gap_ms_before, text)
CHUNKS = [
    (
        "01_intro", 0,
        "Hola… ¿qué tal? Bienvenido a Aparte. Hoy estoy solo frente al micrófono, con un café en la mano y una historia que, te soy sincero, "
        "me dejó pensando toda la semana. En 1947, George Orwell se estaba muriendo. Y él lo sabía. Era plenamente consciente de su final."
    ),
    (
        "02_barnhill", 450,
        "Aun así, ¿qué hizo? Se marchó a una granja remota en la isla escocesa de Jura. Instaló su vieja máquina de escribir en la sala principal "
        "y allí pasó los dos años siguientes escribiendo 1984, refugiado prácticamente como un ermitaño. "
        "La casa se llamaba Barnhill. Imagínate esto: sin electricidad, con un suministro de agua poco fiable y el hospital más cercano a un viaje durísimo de distancia. "
        "Cuando se sentía bien, escribía en la sala. Cuando la enfermedad no le dejaba levantarse… trabajaba desde la cama."
    ),
    (
        "03_manuscrito_muerte", 500,
        "Vivía rodeado de cuadernos, herramientas de granja, manuscritos y una máquina de escribir que era casi una reliquia y se averiaba a cada rato. "
        "En octubre de 1948, a punto de terminar 1984, calculaba que el manuscrito llegaría a las ciento veinticinco mil palabras… y ni siquiera estaba satisfecho. "
        "1984 se publicó el ocho de junio de 1949. Y Orwell murió el veintiuno de enero de 1950, con apenas cuarenta y seis años, sin llegar a ver el legado gigantesco de su obra."
    ),
    (
        "04_reflexion_excusas", 550,
        "(sigh) A mí esto me dejó bastante pensativo… ¿Cuántas veces evitamos una tarea con la excusa más mínima? "
        "Que si hace frío, que si no tengo la silla ergonómica, que si el primer borrador me salió feo… (chuckle) "
        "Mientras tanto, un hombre enfermo de tuberculosis, en una granja remota sin luz, creó una de las novelas más influyentes de la historia. "
        "No hay que tenerlo todo a favor. Y, seamos honestos, jamás lo tendrás por mucho que esperes."
    ),
    (
        "05_rutina_ritual", 550,
        "Miremos su rutina con lupa, porque tiene detalles buenísimos. No tenía un horario rígido de esos de gurú de productividad, pero en Jura se levantaba con el sol "
        "para aprovechar la luz natural, ya que solo tenía velas. Escribía a mano en cuadernos o a máquina según el día. Era flexible, sí, pero obsesivamente perfeccionista: "
        "en su diario de 1940 confesó que prácticamente todo lo había escrito al menos dos veces, sus libros completos tres veces, y algunos fragmentos… ¡hasta diez!"
    ),
    (
        "06_el_te", 450,
        "Y tenía su ritual sagrado: el té. Se lo tomaba tan en serio que en 1946 publicó un ensayo entero llamado A Nice Cup of Tea, "
        "con once reglas exactas para prepararlo, incluyendo el orden correcto de añadir el té y la leche. (laughing) ¡Once reglas para un té! "
        "Pero fíjate en lo importante: era su señal del entorno. Ese pequeño ritual que le decía a su cerebro: ya empezamos. "
        "¿Cuál es el tuyo? Un café, abrir un cuaderno, una ducha previa, poner música… el ser humano es rutinario, y un buen ritual te ahorra media batalla."
    ),
    (
        "07_eric_blair", 550,
        "Ahora, quizá no lo sepas, pero él ni siquiera se llamaba George Orwell. Su nombre real era Eric Arthur Blair. "
        "Venía de una familia acomodada y estudió en el prestigioso Eton College, pero siempre sintió que no encajaba. "
        "Fue policía colonial en Birmania, vivió en la pobreza en París y Londres, fue profesor, librero, miliciano en la Guerra Civil española, y en Jura cultivaba verduras y criaba animales. "
        "Toda esa vida variopinta le mostró de primera mano las desigualdades y los abusos de poder."
    ),
    (
        "08_corryvreckan_hospital", 500,
        "Y en Barnhill la vida era sencilla, pero durísima. Sin teléfono, con caminos que se volvían intransitables con el mal tiempo. "
        "En agosto de 1947 casi muere ahogado en un accidente de barca cerca del peligroso remolino de Corryvreckan, junto a su hijo adoptado Richard y otros familiares. Salió vivo por los pelos. "
        "Meses después, la tuberculosis lo mandó siete meses al hospital de Hairmyres. Y ahí, tumbado en la camilla, seguía escribiendo. "
        "En su diario anotó algo que me dolió leer: que solo cuando intentaba escribir se daba cuenta del deterioro dentro de su cabeza."
    ),
    (
        "09_mecanografiar", 500,
        "Aun así, regresó a Jura en julio de 1948. En octubre le escribió a su editor, Fredric Warburg, preocupado por el esfuerzo físico de pasar a máquina la copia final de ciento veinticinco mil palabras. "
        "Intentó buscar un mecanógrafo… pero claro, ¿quién iba a irse hasta esa granja perdida? Nadie se ofreció. "
        "Así que volvió a mecanografiar la novela entera él mismo, con dolores, a un ritmo de unas cuatro mil palabras diarias en diciembre de 1948. "
        "Cuando terminó estaba exhausto. En enero de 1949 dejó Jura para entrar de nuevo a un sanatorio, sabiendo que probablemente no volvería."
    ),
    (
        "10_por_que_escribo", 550,
        "Uno podría pensar que Orwell era simplemente un ermitaño obsesionado. Pero no. En su ensayo Por qué escribo explicó sus cuatro motivos: "
        "el puro egoísmo, el impulso histórico, el entusiasmo estético y el propósito político. Y después de la Guerra Civil española, el propósito político pasó al centro. "
        "Quería dejar un legado literario advirtiendo sobre el totalitarismo, la propaganda y la censura. "
        "No estaba esperando el momento ideal. Empieza con las condiciones que tienes y adapta el trabajo a tus posibilidades."
    ),
    (
        "11_diarios_caoticos", 500,
        "Otro detalle que me encanta: sus diarios personales, de 1938 a 1949. No eran esos cuadernos estéticos y perfectos que uno ve hoy en redes sociales para fingir. (chuckle) "
        "Eran hojas caóticas donde convivían semillas plantadas en la granja, conteo de huevos recogidos, dibujos, cálculos de un monumento megalítico, recortes de prensa y reflexiones políticas. "
        "Así se ve de verdad la cabeza de un creador."
    ),
    (
        "12_cuatro_ideas", 550,
        "Entonces, ¿qué podemos robar de la historia de George Orwell para escribir cada día, incluso con pereza? Cuatro ideas concretas. "
        "Primera: escribe un diario. Anota lo que observas, el clima, lo que piensas cuando consumes contenido en vez de seguir haciendo scroll. El noventa y nueve por ciento consume ideas ajenas; recuerda pensar las tuyas. "
        "Segunda: reescribe. El primer borrador es solo material bruto; la calidad real aparece en la refinación. "
        "Tercera: sé minimalista. Orwell solo necesitaba una máquina de escribir, un cuaderno y un rato sin interrupción. No necesitas un estudio de película."
    ),
    (
        "13_proposito_cierre", 550,
        "Y cuarta: encuentra un propósito para escribir. Orwell creía que sus experiencias y preocupaciones políticas daban sentido a su obra. "
        "Tener una intención para escribir te hará volver; es lo que te empujará incluso en tu peor día. Como todo en la vida, sin rumbo es difícil llegar a algún lugar. La mayoría deambula; asegúrate de tener rumbo. "
        "En cuatro líneas, para que no se te escape: observa lo que te rodea. Reescribe con esmero. Sé minimalista. Ten una meta. "
        "Hasta aquí por hoy. Esto fue Aparte. Ideas que merecen ser escuchadas."
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

    for tid, gap_ms, text in CHUNKS:
        mp3 = CHUNKS_DIR / f"{tid}.mp3"
        wav = CHUNKS_DIR / f"{tid}.wav"

        if not (mp3.exists() and mp3.stat().st_size > 2000):
            print(f"[TTS] {tid} (fred)...", flush=True)
            g._fish_audio_tts_sync(text, str(mp3), reference_id=VOICE_FRED, model="drama-3")
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
        clips.append((gap_ms, load_wav_mono(wav)))

    lead_in_samples = int(2.4 * sr)
    tail_samples = int(5.5 * sr)

    cursor = lead_in_samples
    placements = []
    max_end = lead_in_samples
    for gap_ms, audio in clips:
        start = max(lead_in_samples, cursor + int(gap_ms * sr / 1000.0))
        end = start + len(audio)
        placements.append((start, audio))
        cursor = end
        if end > max_end:
            max_end = end

    total_samples = max_end + tail_samples
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for start, audio in placements:
        end = start + len(audio)
        stereo[start:end, 0] += audio
        stereo[start:end, 1] += audio

    peak = np.max(np.abs(stereo)) + 1e-9
    if peak > 0.95:
        stereo *= 0.95 / peak

    voice_full = Path("/tmp/aparte_07_voice_full.wav")
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(voice_full), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    total_dur = probe_dur(voice_full)
    print(f"[TIMELINE] Assembled Solo Fred Orwell episode: {total_dur}s", flush=True)

    bed_wav = Path("/tmp/aparte_07_bed.wav")
    print(f"[BED] Rendering custom Drive music bed ({total_dur}s)...", flush=True)
    render_bed_wav(bed_wav, total_dur + 1.0)

    out_mp3 = OUT_DIR / "aparte_proposito_escribir.mp3"
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
