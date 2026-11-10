// Vercel Serverless Function: Fred Rewind Native AI Story Generation
// Generates authentic DJ Fredd classic rock radio stories using OpenAI gpt-4o-mini

const APERTURA_OBLIGATORIA = "Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.";

module.exports = async (req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const data = (typeof req.body === 'string' ? JSON.parse(req.body) : req.body) || {};
    const songTitle = data.song_title || data.songTitle || 'Canción de Rock';
    const bandName = data.band_name || data.bandName || 'Artista';
    const albumName = data.album || '';
    const year = data.year || '';
    const angle = parseInt(data.angle || 1, 10);

    const apiKey = process.env.OPENAI_API_KEY;
    const cierre = `¡Sube el volumen y escuchemos a ${songTitle} aquí en Fred Rewind, de regreso al pasado!`;

    if (!apiKey) {
      // Return structured fallback if API key is not configured in environment
      const fallbackDesarrollo = `En ${year || 'su época cumbre'}, para ${albumName ? 'el álbum ' + albumName : 'uno de los momentos más inspirados de su carrera'}, ${bandName} grabó una obra inolvidable. La música tiene memoria, y esta pieza capturó toda la energía, potencia y química en vivo del grupo, convirtiéndose en un himno esencial que definió el sonido de una generación entera en las ondas de radio.`;
      const fullScript = `${APERTURA_OBLIGATORIA} ${fallbackDesarrollo} ${cierre}`;
      return res.status(200).json({
        success: true,
        full_script: fullScript,
        apertura: APERTURA_OBLIGATORIA,
        desarrollo: fallbackDesarrollo,
        cierre: cierre,
        source: 'curated_fallback',
        words: fallbackDesarrollo.split(/\s+/).length,
        duration_est_sec: 38
      });
    }

    const systemPrompt = `Eres DJ Fredd, el respetado locutor de radio de rock clásico de la emisora "Fred Rewind".
Tu frase insignia es "La música tiene memoria" y el concepto del programa es "De regreso al pasado".
Hablas con tono cálido, medio-grave, melómano, apasionado por las historias musicales de los 60s, 70s, 80s y 90s, con estilo de radio clásica FM en español latinoamericano.
Tu tarea es escribir el guion oficial para narrar la historia real detrás de una canción.`;

    const userPrompt = `Escribe la historia oficial para la canción "${songTitle}" de "${bandName}" (Álbum: "${albumName || 'Clásico'}", Año: "${year || 'Época Dorada'}").

ESTRUCTURA OBLIGATORIA:
1. APERTURA EXACTA:
"${APERTURA_OBLIGATORIA}"

2. DESARROLLO (Anécdota musical auténtica):
- Narra una historia real, interesante y verificable sobre la composición, grabación en el estudio, anécdotas de los músicos o el impacto histórico que la convirtió en un clásico.
- Duración mínima narrada: al menos 30 a 45 segundos de locución real (entre 90 y 130 palabras en el desarrollo).
- No inventes fechas ni acontecimientos falsos. Si no tienes datos exactos, enfócate en hechos documentados.
- Incorpora de forma natural y elegante la frase insignia: "La música tiene memoria".
- Puntuación cuidada con comas y puntos para pausas orgánicas de locución. No uses etiquetas técnicas ni acotaciones entre paréntesis.

3. CIERRE EXACTO:
"${cierre}"`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 380
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`OpenAI API error: ${response.status} ${errText}`);
    }

    const json = await response.json();
    const rawText = (json.choices && json.choices[0] && json.choices[0].message && json.choices[0].message.content) ? json.choices[0].message.content.trim() : '';

    // Clean and isolate the desarrollo
    let desarrollo = rawText;
    desarrollo = desarrollo.replace(/^(?:"?Estás escuchando Fred Rewind, de regreso al pasado\.\s*Soy DJ Fredd\.?"?)\s*/i, '');
    desarrollo = desarrollo.replace(/(?:"?¡?Sube el volumen y escuchemos a .*? aquí en Fred Rewind, de regreso al pasado!?\"?)\s*$/i, '');
    desarrollo = desarrollo.replace(/^["'\s]+|["'\s]+$/g, '').trim();

    const fullScript = `${APERTURA_OBLIGATORIA} ${desarrollo} ${cierre}`;
    const wordCount = desarrollo.split(/\s+/).filter(Boolean).length;
    const durEstSec = Math.round(wordCount / 2.3);

    return res.status(200).json({
      success: true,
      full_script: fullScript,
      apertura: APERTURA_OBLIGATORIA,
      desarrollo: desarrollo,
      cierre: cierre,
      source: 'openai_gpt_4o_mini',
      words: wordCount,
      duration_est_sec: durEstSec
    });

  } catch (error) {
    console.error('Error in /api/generate_story_text:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Error generating story script'
    });
  }
};
