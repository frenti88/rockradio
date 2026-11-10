import re
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the new rich curated datasets with real album covers
    old_curated_block_re = re.compile(
        r'    // Curated Fallback Collections for Rock\s+const CURATED_ROCK_PLAYLISTS = \[.*?const CURATED_ROCK_TRACKS = \[.*?\];',
        re.DOTALL
    )

    new_curated_block = """    // Curated Fallback Collections for Rock with Real Authentic Album Artwork
    const CURATED_ROCK_PLAYLISTS = [
      {
        id: 'curated_rock_classics',
        name: 'Rock Clásicos 70s y 80s',
        description: 'Los himnos inmortales de Queen, Led Zeppelin, The Beatles, Pink Floyd y las mayores leyendas.',
        images: [{ url: 'img/albums/queen_1975_night_at_opera.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 8 },
        items: [
          { id: 'sp_cur_1', name: 'Bohemian Rhapsody', artists: [{ name: 'Queen' }], album: { name: 'A Night at the Opera (1975)', release_date: '1975', images: [{ url: 'img/albums/queen_1975_night_at_opera.png' }] }, duration_ms: 354000 },
          { id: 'sp_cur_2', name: 'Stairway to Heaven', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Led Zeppelin IV (1971)', release_date: '1971', images: [{ url: 'img/albums/led_zeppelin_1971_iv.png' }] }, duration_ms: 482000 },
          { id: 'sp_cur_3', name: 'Back in Black', artists: [{ name: 'AC/DC' }], album: { name: 'Back in Black (1980)', release_date: '1980', images: [{ url: 'img/albums/acdc_1980_back_in_black.png' }] }, duration_ms: 255000 },
          { id: 'sp_cur_4', name: 'Help!', artists: [{ name: 'The Beatles' }], album: { name: 'Help! (1965)', release_date: '1965', images: [{ url: 'img/albums/the_beatles_1965_help.png' }] }, duration_ms: 139000 },
          { id: 'sp_cur_5', name: 'Enter Sandman', artists: [{ name: 'Metallica' }], album: { name: 'Metallica (1991)', release_date: '1991', images: [{ url: 'img/albums/metallica_1991_black_album.png' }] }, duration_ms: 331000 },
          { id: 'sp_cur_6', name: "Sweet Child O' Mine", artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction (1987)', release_date: '1987', images: [{ url: 'img/albums/guns_n_roses_1987_appetite.png' }] }, duration_ms: 356000 },
          { id: 'sp_cur_7', name: 'Paranoid', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid (1970)', release_date: '1970', images: [{ url: 'img/albums/black_sabbath_1970_paranoid.png' }] }, duration_ms: 168000 },
          { id: 'sp_cur_8', name: 'Rock and Roll All Nite', artists: [{ name: 'KISS' }], album: { name: 'Alive! (1975)', release_date: '1975', images: [{ url: 'img/albums/kiss_1975_alive.png' }] }, duration_ms: 169000 }
        ]
      },
      {
        id: 'curated_hard_rock_stadiums',
        name: 'Hard Rock Stadiums',
        description: 'Riffs demoledores y coros para cantar con el volumen de la radio al 100%.',
        images: [{ url: 'img/albums/acdc_1979_highway_to_hell.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 6 },
        items: [
          { id: 'sp_hr_1', name: 'Highway to Hell', artists: [{ name: 'AC/DC' }], album: { name: 'Highway to Hell', release_date: '1979', images: [{ url: 'img/albums/acdc_1979_highway_to_hell.png' }] }, duration_ms: 208000 },
          { id: 'sp_hr_2', name: 'Paradise City', artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction', release_date: '1987', images: [{ url: 'img/albums/guns_n_roses_1987_appetite.png' }] }, duration_ms: 406000 },
          { id: 'sp_hr_3', name: 'Detroit Rock City', artists: [{ name: 'KISS' }], album: { name: 'Destroyer', release_date: '1976', images: [{ url: 'img/albums/kiss_1976_destroyer.png' }] }, duration_ms: 317000 },
          { id: 'sp_hr_4', name: 'Pour Some Sugar on Me', artists: [{ name: 'Def Leppard' }], album: { name: 'Hysteria', release_date: '1987', images: [{ url: 'img/albums/def_leppard_1987_hysteria.png' }] }, duration_ms: 267000 },
          { id: 'sp_hr_5', name: 'Kickstart My Heart', artists: [{ name: 'Mötley Crüe' }], album: { name: 'Dr. Feelgood', release_date: '1989', images: [{ url: 'img/albums/motley_crue_1989_feelgood.png' }] }, duration_ms: 284000 },
          { id: 'sp_hr_6', name: 'Tom Sawyer', artists: [{ name: 'Rush' }], album: { name: 'Moving Pictures', release_date: '1981', images: [{ url: 'img/albums/rush_1981_moving_pictures.png' }] }, duration_ms: 276000 }
        ]
      },
      {
        id: 'curated_heavy_metal_anthems',
        name: 'Heavy Metal Anthems',
        description: 'La forja del metal: guitarras afinadas en oscuridad y distorsión pura.',
        images: [{ url: 'img/albums/metallica_1986_master_of_puppets.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 5 },
        items: [
          { id: 'sp_hm_1', name: 'Master of Puppets', artists: [{ name: 'Metallica' }], album: { name: 'Master of Puppets', release_date: '1986', images: [{ url: 'img/albums/metallica_1986_master_of_puppets.png' }] }, duration_ms: 515000 },
          { id: 'sp_hm_2', name: 'Iron Man', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/albums/black_sabbath_1970_paranoid.png' }] }, duration_ms: 356000 },
          { id: 'sp_hm_3', name: 'One', artists: [{ name: 'Metallica' }], album: { name: '...And Justice for All', release_date: '1988', images: [{ url: 'img/albums/metallica_1988_and_justice_for_all.png' }] }, duration_ms: 446000 },
          { id: 'sp_hm_4', name: 'War Pigs', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/albums/black_sabbath_1970_paranoid.png' }] }, duration_ms: 474000 },
          { id: 'sp_hm_5', name: 'Kashmir', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Physical Graffiti', release_date: '1975', images: [{ url: 'img/albums/led_zeppelin_1975_physical.png' }] }, duration_ms: 512000 }
        ]
      },
      {
        id: 'curated_rock_ballads',
        name: 'Baladas Inmortales del Rock',
        description: 'Sensibilidad, solos desgarradores y letras que marcaron épocas.',
        images: [{ url: 'img/albums/def_leppard_1987_hysteria.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 5 },
        items: [
          { id: 'sp_rb_1', name: 'Love Bites', artists: [{ name: 'Def Leppard' }], album: { name: 'Hysteria', release_date: '1987', images: [{ url: 'img/albums/def_leppard_1987_hysteria.png' }] }, duration_ms: 346000 },
          { id: 'sp_rb_2', name: 'November Rain', artists: [{ name: "Guns N' Roses" }], album: { name: 'Use Your Illusion I', release_date: '1991', images: [{ url: 'img/albums/guns_n_roses_1991_illusion_1.png' }] }, duration_ms: 537000 },
          { id: 'sp_rb_3', name: 'Africa', artists: [{ name: 'Toto' }], album: { name: 'Toto IV', release_date: '1982', images: [{ url: 'img/albums/toto_1982_toto_iv.png' }] }, duration_ms: 295000 },
          { id: 'sp_rb_4', name: 'Forever Young', artists: [{ name: 'Alphaville' }], album: { name: 'Forever Young', release_date: '1984', images: [{ url: 'img/albums/alphaville_1984_forever_young.png' }] }, duration_ms: 226000 },
          { id: 'sp_rb_5', name: 'Forever', artists: [{ name: 'KISS' }], album: { name: 'Hot in the Shade', release_date: '1989', images: [{ url: 'img/albums/kiss_1975_alive.png' }] }, duration_ms: 233000 }
        ]
      }
    ];

    // Authentic Rock Tracks with Real Album Art for Each Section
    const CURATED_TOP_TRACKS = [
      { id: 'cur_top_1', name: 'Stairway to Heaven', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Led Zeppelin IV', release_date: '1971', images: [{ url: 'img/albums/led_zeppelin_1971_iv.png' }] }, duration_ms: 482000 },
      { id: 'cur_top_2', name: 'Bohemian Rhapsody', artists: [{ name: 'Queen' }], album: { name: 'A Night at the Opera', release_date: '1975', images: [{ url: 'img/albums/queen_1975_night_at_opera.png' }] }, duration_ms: 354000 },
      { id: 'cur_top_3', name: 'Back in Black', artists: [{ name: 'AC/DC' }], album: { name: 'Back in Black', release_date: '1980', images: [{ url: 'img/albums/acdc_1980_back_in_black.png' }] }, duration_ms: 255000 },
      { id: 'cur_top_4', name: 'Help!', artists: [{ name: 'The Beatles' }], album: { name: 'Help!', release_date: '1965', images: [{ url: 'img/albums/the_beatles_1965_help.png' }] }, duration_ms: 139000 },
      { id: 'cur_top_5', name: 'Enter Sandman', artists: [{ name: 'Metallica' }], album: { name: 'Metallica (The Black Album)', release_date: '1991', images: [{ url: 'img/albums/metallica_1991_black_album.png' }] }, duration_ms: 331000 },
      { id: 'cur_top_6', name: "Sweet Child O' Mine", artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction', release_date: '1987', images: [{ url: 'img/albums/guns_n_roses_1987_appetite.png' }] }, duration_ms: 356000 }
    ];

    const CURATED_RECOMMENDED_TRACKS = [
      { id: 'cur_rec_1', name: 'Pour Some Sugar on Me', artists: [{ name: 'Def Leppard' }], album: { name: 'Hysteria', release_date: '1987', images: [{ url: 'img/albums/def_leppard_1987_hysteria.png' }] }, duration_ms: 267000 },
      { id: 'cur_rec_2', name: 'Tom Sawyer', artists: [{ name: 'Rush' }], album: { name: 'Moving Pictures', release_date: '1981', images: [{ url: 'img/albums/rush_1981_moving_pictures.png' }] }, duration_ms: 276000 },
      { id: 'cur_rec_3', name: 'Africa', artists: [{ name: 'Toto' }], album: { name: 'Toto IV', release_date: '1982', images: [{ url: 'img/albums/toto_1982_toto_iv.png' }] }, duration_ms: 295000 },
      { id: 'cur_rec_4', name: 'Forever Young', artists: [{ name: 'Alphaville' }], album: { name: 'Forever Young', release_date: '1984', images: [{ url: 'img/albums/alphaville_1984_forever_young.png' }] }, duration_ms: 226000 },
      { id: 'cur_rec_5', name: 'Kickstart My Heart', artists: [{ name: 'Mötley Crüe' }], album: { name: 'Dr. Feelgood', release_date: '1989', images: [{ url: 'img/albums/motley_crue_1989_feelgood.png' }] }, duration_ms: 284000 },
      { id: 'cur_rec_6', name: 'Detroit Rock City', artists: [{ name: 'KISS' }], album: { name: 'Destroyer', release_date: '1976', images: [{ url: 'img/albums/kiss_1976_destroyer.png' }] }, duration_ms: 317000 }
    ];

    const CURATED_RECENTLY_PLAYED_TRACKS = [
      { id: 'cur_recp_1', name: 'Paranoid', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/albums/black_sabbath_1970_paranoid.png' }] }, duration_ms: 168000 },
      { id: 'cur_recp_2', name: 'Highway to Hell', artists: [{ name: 'AC/DC' }], album: { name: 'Highway to Hell', release_date: '1979', images: [{ url: 'img/albums/acdc_1979_highway_to_hell.png' }] }, duration_ms: 208000 },
      { id: 'cur_recp_3', name: 'Master of Puppets', artists: [{ name: 'Metallica' }], album: { name: 'Master of Puppets', release_date: '1986', images: [{ url: 'img/albums/metallica_1986_master_of_puppets.png' }] }, duration_ms: 515000 },
      { id: 'cur_recp_4', name: 'November Rain', artists: [{ name: "Guns N' Roses" }], album: { name: 'Use Your Illusion I', release_date: '1991', images: [{ url: 'img/albums/guns_n_roses_1991_illusion_1.png' }] }, duration_ms: 537000 },
      { id: 'cur_recp_5', name: 'Rock and Roll All Nite', artists: [{ name: 'KISS' }], album: { name: 'Alive!', release_date: '1975', images: [{ url: 'img/albums/kiss_1975_alive.png' }] }, duration_ms: 169000 },
      { id: 'cur_recp_6', name: 'Kashmir', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Physical Graffiti', release_date: '1975', images: [{ url: 'img/albums/led_zeppelin_1975_physical.png' }] }, duration_ms: 512000 }
    ];

    const CURATED_ROCK_TRACKS = CURATED_TOP_TRACKS;"""

    if old_curated_block_re.search(content):
        content = old_curated_block_re.sub(new_curated_block, content, 1)
        print("✓ Curated datasets updated with real album art")
    else:
        print("✗ old_curated_block_re not found")
        sys.exit(1)

    # Update createSpotifyHomeTrackCard fallback image
    content = content.replace(
        ": 'img/covers/cover_kiss.png';",
        ": 'img/albums/queen_1975_night_at_opera.png';"
    )
    content = content.replace(
        ": 'img/covers/cover_queen.png';",
        ": 'img/albums/queen_1975_night_at_opera.png';"
    )

    # Update shelf references in renderSpotifyHomeShelves
    # For topTracks:
    content = content.replace(
        "topTracks = CURATED_ROCK_TRACKS;",
        "topTracks = CURATED_TOP_TRACKS;"
    )

    # For recommendations:
    content = content.replace(
        "recTracks = CURATED_ROCK_TRACKS.slice().reverse();",
        "recTracks = CURATED_RECOMMENDED_TRACKS;"
    )

    # For recently played:
    content = content.replace(
        "recentTracks = CURATED_ROCK_TRACKS.slice(2, 8);",
        "recentTracks = CURATED_RECENTLY_PLAYED_TRACKS;"
    )

    # For liked songs:
    content = content.replace(
        "likedSongs = CURATED_ROCK_TRACKS.slice(0, 5);",
        "likedSongs = CURATED_TOP_TRACKS.slice(0, 5);"
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done updating real album covers in index.html!")

if __name__ == '__main__':
    main()
