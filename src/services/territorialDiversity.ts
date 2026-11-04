import { CulturalEvent } from '../types';

/**
 * Ensures territorial diversity in discovery modules (PRD Sections 55 & 57).
 * Prevents Medellín from occupying more than maxUrbanRatio (e.g. 25-30%) of a section,
 * ensuring rich representation of Oriente, Suroeste, Occidente, Norte, Urabá, etc.
 */
export function balanceTerritorialDiversity(
  events: CulturalEvent[],
  maxLimit: number = 10,
  maxMedellinRatio: number = 0.25
): CulturalEvent[] {
  if (events.length <= maxLimit) return events;

  const maxMedellinCount = Math.max(1, Math.floor(maxLimit * maxMedellinRatio));
  const medellinEvents: CulturalEvent[] = [];
  const regionalEvents: CulturalEvent[] = [];

  for (const evt of events) {
    if (evt.municipality.toLowerCase() === 'medellín' || evt.subregion === 'Valle de Aburrá') {
      medellinEvents.push(evt);
    } else {
      regionalEvents.push(evt);
    }
  }

  // Interleave regional events with a controlled number of urban events
  const selected: CulturalEvent[] = [];
  const subregionBuckets: Record<string, CulturalEvent[]> = {};

  // Group regionals by subregion to maximize variety across Antioquia
  for (const evt of regionalEvents) {
    if (!subregionBuckets[evt.subregion]) subregionBuckets[evt.subregion] = [];
    subregionBuckets[evt.subregion].push(evt);
  }

  const subregionKeys = Object.keys(subregionBuckets);
  let round = 0;
  let addedRegional = 0;

  // Round-robin selection across subregions
  while (addedRegional < maxLimit - maxMedellinCount && addedRegional < regionalEvents.length) {
    let madeProgress = false;
    for (const key of subregionKeys) {
      const bucket = subregionBuckets[key];
      if (bucket && round < bucket.length) {
        selected.push(bucket[round]);
        addedRegional++;
        madeProgress = true;
        if (addedRegional >= maxLimit - maxMedellinCount) break;
      }
    }
    if (!madeProgress) break;
    round++;
  }

  // Add the allowed quota of Medellín events
  const medellinSlice = medellinEvents.slice(0, maxMedellinCount);
  for (const m of medellinSlice) {
    selected.push(m);
  }

  // Fill up if there's still room
  if (selected.length < maxLimit) {
    for (const r of regionalEvents) {
      if (!selected.includes(r) && selected.length < maxLimit) {
        selected.push(r);
      }
    }
    for (const m of medellinEvents) {
      if (!selected.includes(m) && selected.length < maxLimit) {
        selected.push(m);
      }
    }
  }

  return selected.slice(0, maxLimit);
}
