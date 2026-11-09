import asyncio
import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath('scripts'))
import generate_dj_eddie_track as gen

TRACKS_TO_REGENERATE = [
    {
        "id": "intro_kiss_detroit_rock_city",
        "pairId": "kiss_detroit_rock_city",
        "bandName": "KISS",
        "songTitle": "Detroit Rock City",
        "albumName": "Destroyer",
        "year": "1976",
        "out_file": "audio/eddie_intro_kiss_detroit_rock_city.mp3"
    },
    {
        "id": "intro_kiss_forever",
        "pairId": "kiss_forever",
        "bandName": "KISS",
        "songTitle": "Forever",
        "albumName": "Hot in the Shade",
        "year": "1989",
        "out_file": "audio/eddie_intro_kiss_forever.mp3"
    },
    {
        "id": "intro_alice_cooper_poison",
        "pairId": "alice_cooper_poison",
        "bandName": "Alice Cooper",
        "songTitle": "Poison",
        "albumName": "Trash",
        "year": "1989",
        "out_file": "audio/eddie_intro_alice_cooper_poison.mp3"
    },
    {
        "id": "intro_metallica_master_of_puppets",
        "pairId": "metallica_master_of_puppets",
        "bandName": "Metallica",
        "songTitle": "Master of Puppets",
        "albumName": "Master of Puppets",
        "year": "1986",
        "out_file": "audio/eddie_intro_metallica_master_of_puppets.mp3"
    },
    {
        "id": "intro_metallica_enter_sandman",
        "pairId": "metallica_enter_sandman",
        "bandName": "Metallica",
        "songTitle": "Enter Sandman",
        "albumName": "Metallica (The Black Album)",
        "year": "1991",
        "out_file": "audio/eddie_intro_metallica_enter_sandman.mp3"
    },
    {
        "id": "intro_metallica_one",
        "pairId": "metallica_one",
        "bandName": "Metallica",
        "songTitle": "One",
        "albumName": "...And Justice for All",
        "year": "1988",
        "out_file": "audio/eddie_intro_metallica_one.mp3"
    },
    {
        "id": "intro_eagles_hotel_california",
        "pairId": "eagles_hotel_california",
        "bandName": "Eagles",
        "songTitle": "Hotel California",
        "albumName": "Hotel California",
        "year": "1976",
        "out_file": "audio/eddie_intro_eagles_hotel_california.mp3"
    },
    {
        "id": "intro_acdc_highway_to_hell",
        "pairId": "acdc_highway_to_hell",
        "bandName": "AC/DC",
        "songTitle": "Highway to Hell",
        "albumName": "Highway to Hell",
        "year": "1979",
        "out_file": "audio/eddie_intro_acdc_highway_to_hell.mp3"
    },
    {
        "id": "intro_acdc_back_in_black",
        "pairId": "acdc_back_in_black",
        "bandName": "AC/DC",
        "songTitle": "Back in Black",
        "albumName": "Back in Black",
        "year": "1980",
        "out_file": "audio/eddie_intro_acdc_back_in_black.mp3"
    },
    {
        "id": "intro_guns_n_roses_sweet_child_o_mine",
        "pairId": "guns_n_roses_sweet_child_o_mine",
        "bandName": "Guns N' Roses",
        "songTitle": "Sweet Child O' Mine",
        "albumName": "Appetite for Destruction",
        "year": "1987",
        "out_file": "audio/eddie_intro_guns_n_roses_sweet_child_o_mine.mp3"
    },
    {
        "id": "intro_toto_africa",
        "pairId": "toto_africa",
        "bandName": "Toto",
        "songTitle": "Africa",
        "albumName": "Toto IV",
        "year": "1982",
        "out_file": "audio/eddie_intro_toto_africa.mp3"
    },
    {
        "id": "intro_alphaville_forever_young",
        "pairId": "alphaville_forever_young",
        "bandName": "Alphaville",
        "songTitle": "Forever Young",
        "albumName": "Forever Young",
        "year": "1984",
        "out_file": "audio/eddie_intro_alphaville_forever_young.mp3"
    },
    {
        "id": "intro_rush_subdivisions",
        "pairId": "rush_subdivisions",
        "bandName": "Rush",
        "songTitle": "Subdivisions",
        "albumName": "Signals",
        "year": "1982",
        "out_file": "audio/eddie_intro_rush_subdivisions.mp3"
    },
    {
        "id": "intro_mtley_cre_shout_at_the_devil",
        "pairId": "mtley_cre_shout_at_the_devil",
        "bandName": "Mötley Crüe",
        "songTitle": "Shout at the Devil",
        "albumName": "Shout at the Devil",
        "year": "1983",
        "out_file": "audio/eddie_intro_mtley_cre_shout_at_the_devil.mp3"
    },
    {
        "id": "intro_led_zeppelin_stairway_to_heaven",
        "pairId": "led_zeppelin_stairway_to_heaven",
        "bandName": "Led Zeppelin",
        "songTitle": "Stairway to Heaven",
        "albumName": "Led Zeppelin IV",
        "year": "1971",
        "out_file": "audio/eddie_intro_led_zeppelin_stairway_to_heaven.mp3"
    },
    {
        "id": "intro_def_leppard_hysteria",
        "pairId": "def_leppard_hysteria",
        "bandName": "Def Leppard",
        "songTitle": "Hysteria",
        "albumName": "Hysteria",
        "year": "1987",
        "out_file": "audio/eddie_intro_def_leppard_hysteria.mp3"
    },
    {
        "id": "intro_tears_for_fears_everybody_wants_to_rule_the_w",
        "pairId": "tears_for_fears_everybody_wants_to_rule_the_w",
        "bandName": "Tears for Fears",
        "songTitle": "Everybody Wants to Rule the World",
        "albumName": "Songs from the Big Chair",
        "year": "1985",
        "out_file": "audio/eddie_intro_tears_for_fears_everybody_wants_to_rule_the_w.mp3"
    }
]

async def process_all():
    results = []
    print(f"================================================================================")
    print(f"🎸 INICIANDO REGENERACIÓN MAESTRA DE LAS {len(TRACKS_TO_REGENERATE)} HISTORIAS DE DJ EDDIE")
    print(f"================================================================================\n")
    
    total_start = time.time()
    success_count = 0
    fail_count = 0
    
    for idx, t in enumerate(TRACKS_TO_REGENERATE):
        song = t["songTitle"]
        band = t["bandName"]
        album = t["albumName"]
        year = t["year"]
        out_f = t["out_file"]
        
        print(f"[{idx+1}/{len(TRACKS_TO_REGENERATE)}] Procesando: '{song}' - {band} ({year}) ...")
        
        # Get the standard master script
        ap, dev, ci, full_script = gen.get_master_eddie_script(song, band, album, year)
        
        try:
            out_path, duration, elapsed, intro_timings, intro_end, final_script = await gen.build_eddie_radio_narration(
                full_script, song, band, out_f
            )
            
            # Verify file exists and is valid size
            file_size = os.path.getsize(out_path)
            if file_size < 100000:
                raise ValueError(f"Archivo generado demasiado pequeño ({file_size} bytes)")
                
            print(f"   ✓ Generado exitosamente: {out_path}")
            print(f"   ⏱ Duración real: {duration:.2f}s | Intro end: {intro_end:.2f}s | Tiempo proceso: {elapsed:.2f}s")
            print(f"   📝 Timings generados: {len(intro_timings)} marcas de letra sincronizada\n")
            
            success_count += 1
            results.append({
                "id": t["id"],
                "pairId": t["pairId"],
                "songTitle": song,
                "bandName": band,
                "albumName": album,
                "year": year,
                "audioUrl": out_f,
                "fileUrl": out_f,
                "duration": int(round(duration)),
                "durationSec": round(duration, 2),
                "introSec": f"{int(round(duration))}s",
                "summary": final_script,
                "lyrics": intro_timings,
                "success": True,
                "sizeBytes": file_size
            })
        except Exception as e:
            print(f"   ❌ ERROR al generar '{song}': {e}\n")
            fail_count += 1
            results.append({
                "id": t["id"],
                "pairId": t["pairId"],
                "songTitle": song,
                "bandName": band,
                "error": str(e),
                "success": False
            })
            
    total_elapsed = time.time() - total_start
    print(f"================================================================================")
    print(f"🏁 RESUMEN DEL PROCESO DE REGENERACIÓN MAESTRA:")
    print(f"   - Total procesadas: {len(TRACKS_TO_REGENERATE)}")
    print(f"   - Exitosas: {success_count}")
    print(f"   - Fallidas: {fail_count}")
    print(f"   - Tiempo total: {total_elapsed:.2f}s")
    print(f"================================================================================")
    
    with open("master_regeneration_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Guardado reporte detallado en master_regeneration_results.json")

if __name__ == "__main__":
    asyncio.run(process_all())
