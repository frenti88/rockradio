import { CulturalEvent, DeduplicationGroup, SourceType } from '../types';

// Normalized Levenshtein similarity [0, 1]
export function stringSimilarity(a: string, b: string): number {
  const s1 = a.toLowerCase().trim();
  const s2 = b.toLowerCase().trim();
  if (s1 === s2) return 1.0;
  if (s1.length === 0 || s2.length === 0) return 0.0;

  const track = Array(s2.length + 1).fill(null).map(() =>
    Array(s1.length + 1).fill(null)
  );
  for (let i = 0; i <= s1.length; i += 1) track[0][i] = i;
  for (let j = 0; j <= s2.length; j += 1) track[j][0] = j;

  for (let j = 1; j <= s2.length; j += 1) {
    for (let i = 1; i <= s1.length; i += 1) {
      const indicator = s1[i - 1] === s2[j - 1] ? 0 : 1;
      track[j][i] = Math.min(
        track[j][i - 1] + 1, // deletion
        track[j - 1][i] + 1, // insertion
        track[j - 1][i - 1] + indicator // substitution
      );
    }
  }

  const distance = track[s2.length][s1.length];
  const maxLength = Math.max(s1.length, s2.length);
  return Math.max(0, 1 - distance / maxLength);
}

// Token Jaccard similarity for unordered titles
export function tokenSimilarity(a: string, b: string): number {
  const clean = (s: string) =>
    s.toLowerCase().replace(/[^a-záéíóúñ0-9\s]/gi, '').split(/\s+/).filter(Boolean);
  const setA = new Set(clean(a));
  const setB = new Set(clean(b));
  if (setA.size === 0 && setB.size === 0) return 1;
  if (setA.size === 0 || setB.size === 0) return 0;

  let intersection = 0;
  for (const item of setA) {
    if (setB.has(item)) intersection++;
  }
  const union = new Set([...setA, ...setB]).size;
  return intersection / union;
}

// Priority rank for choosing the canonical source (lower number = higher authority)
const SOURCE_TYPE_PRIORITY: Record<SourceType, number> = {
  independent: 1, // Official festival/artist organizer
  government: 2,  // Alcaldía / Secretaría de Cultura / ICPA
  cultural_center: 3, // Casa de la cultura / Museo
  compensation_box: 4, // Comfama / Comfenalco
  university: 5,
  ticketing: 6, // Eventbrite / Tuboleta
  community: 7,
};

export function calculateEventMatchScore(evtA: CulturalEvent, evtB: CulturalEvent): number {
  // Same event ID
  if (evtA.event_id === evtB.event_id) return 1.0;

  // Title similarity (blend of Levenshtein and token Jaccard)
  const titleScore = (stringSimilarity(evtA.title, evtB.title) + tokenSimilarity(evtA.title, evtB.title)) / 2;

  // Municipality match
  const muniMatch = evtA.municipality.toLowerCase() === evtB.municipality.toLowerCase() ? 1.0 : 0.0;
  if (muniMatch === 0) return 0; // Different towns cannot be the same event

  // Venue match
  const venueScore = stringSimilarity(evtA.venue_name, evtB.venue_name);

  // Date match
  const dateMatch = evtA.start_date === evtB.start_date ? 1.0 : 0.0;
  if (dateMatch === 0) return 0; // Different dates

  // Weighted score according to PRD section 5
  // Title: 35%, Venue & Municipality: 30%, Date: 25%, Organizer: 10%
  const organizerScore = stringSimilarity(evtA.organizer_name, evtB.organizer_name);
  
  return (titleScore * 0.35) + (venueScore * 0.30) + (dateMatch * 0.25) + (organizerScore * 0.10);
}

// Detect and group duplicates into canonical events
export function identifyDuplicateGroups(events: CulturalEvent[]): DeduplicationGroup[] {
  const groups: DeduplicationGroup[] = [];
  const visited = new Set<string>();

  for (let i = 0; i < events.length; i++) {
    const current = events[i];
    if (visited.has(current.event_id)) continue;

    const matchedDuplicates: Array<{
      source_name: string;
      source_url: string;
      source_type: SourceType;
      similarity_score: number;
      detected_title: string;
      detected_venue: string;
      detected_at: string;
    }> = [];

    let canonical = current;

    for (let j = i + 1; j < events.length; j++) {
      const candidate = events[j];
      if (visited.has(candidate.event_id)) continue;

      const score = calculateEventMatchScore(canonical, candidate);
      if (score >= 0.78) { // 78% threshold for canonical match
        visited.add(candidate.event_id);

        // Decide if candidate should replace current as canonical
        const currentRank = SOURCE_TYPE_PRIORITY[canonical.source_type] ?? 99;
        const candidateRank = SOURCE_TYPE_PRIORITY[candidate.source_type] ?? 99;

        if (candidateRank < currentRank) {
          // Candidate becomes canonical
          matchedDuplicates.push({
            source_name: canonical.source_name,
            source_url: canonical.source_url,
            source_type: canonical.source_type,
            similarity_score: Number(score.toFixed(2)),
            detected_title: canonical.title,
            detected_venue: canonical.venue_name,
            detected_at: canonical.first_detected_at,
          });
          canonical = candidate;
        } else {
          matchedDuplicates.push({
            source_name: candidate.source_name,
            source_url: candidate.source_url,
            source_type: candidate.source_type,
            similarity_score: Number(score.toFixed(2)),
            detected_title: candidate.title,
            detected_venue: candidate.venue_name,
            detected_at: candidate.first_detected_at,
          });
        }
      }
    }

    visited.add(canonical.event_id);

    // If duplicates were merged, attach secondary sources
    if (matchedDuplicates.length > 0) {
      canonical = {
        ...canonical,
        secondary_sources: [
          ...(canonical.secondary_sources || []),
          ...matchedDuplicates.map(d => ({
            source_name: d.source_name,
            source_url: d.source_url,
            source_type: d.source_type,
            detected_at: d.detected_at,
          }))
        ]
      };
    }

    groups.push({
      canonical_event: canonical,
      detected_duplicates: matchedDuplicates,
    });
  }

  return groups;
}
