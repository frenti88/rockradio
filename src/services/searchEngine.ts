import { CulturalEvent, FilterState, MunicipalityData } from '../types';

// Simulated current date for Evenjoy runtime: Tuesday, Sept 8, 2026
export const SIMULATED_TODAY = '2026-09-08';
export const SIMULATED_TOMORROW = '2026-09-09';
export const SIMULATED_WEEKEND_START = '2026-09-12'; // Saturday
export const SIMULATED_WEEKEND_END = '2026-09-13';   // Sunday
export const SIMULATED_WEEK_END = '2026-09-14';
export const SIMULATED_NEXT_WEEKEND_START = '2026-09-19';
export const SIMULATED_NEXT_WEEKEND_END = '2026-09-20';

// Haversine distance in km
export function calculateDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

export function estimateTravelTime(distanceKm: number): string {
  if (distanceKm < 15) return '20 min aprox.';
  if (distanceKm < 45) return '45 min aprox.';
  if (distanceKm < 80) return '1 h 30 min aprox.';
  if (distanceKm < 130) return '3 h aprox.';
  return `${Math.round(distanceKm / 45)} h aprox.`;
}

export function normalizeSearchText(text: string): string {
  if (!text) return '';
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

const normalizedIndexCache = new WeakMap<CulturalEvent, string>();

export function getEventSearchIndex(evt: CulturalEvent): string {
  let cached = normalizedIndexCache.get(evt);
  if (!cached) {
    cached = normalizeSearchText(
      `${evt.title} ${evt.municipality} ${evt.subregion} ${evt.venue_name} ${evt.category} ${evt.subcategory || ''} ${evt.organizer_name} ${evt.tags.join(' ')}`
    );
    normalizedIndexCache.set(evt, cached);
  }
  return cached;
}

export function filterEvents(events: CulturalEvent[], filters: FilterState): CulturalEvent[] {
  return events.filter(evt => {
    // 1. Status check: omit cancelled/expired by default unless looking specifically
    if (evt.status === 'EXPIRED' && filters.dateRange !== 'all') return false;

    // 2. Text search (robust diacritic & case-insensitive matching with memoized index)
    if (filters.searchQuery && filters.searchQuery.trim()) {
      const q = normalizeSearchText(filters.searchQuery);
      if (!getEventSearchIndex(evt).includes(q)) return false;
    }

    // 3. Date range
    if (filters.dateRange === 'today') {
      if (evt.start_date > SIMULATED_TODAY || evt.end_date < SIMULATED_TODAY) return false;
    } else if (filters.dateRange === 'tomorrow') {
      if (evt.start_date > SIMULATED_TOMORROW || evt.end_date < SIMULATED_TOMORROW) return false;
    } else if (filters.dateRange === 'this_weekend') {
      const overlapsWeekend = 
        (evt.start_date <= SIMULATED_WEEKEND_END && evt.end_date >= SIMULATED_WEEKEND_START);
      if (!overlapsWeekend) return false;
    } else if (filters.dateRange === 'this_week') {
      const overlapsWeek =
        (evt.start_date <= SIMULATED_WEEK_END && evt.end_date >= SIMULATED_TODAY);
      if (!overlapsWeek) return false;
    } else if (filters.dateRange === 'next_weekend') {
      const overlapsNextWeekend =
        (evt.start_date <= SIMULATED_NEXT_WEEKEND_END && evt.end_date >= SIMULATED_NEXT_WEEKEND_START);
      if (!overlapsNextWeekend) return false;
    } else if (filters.dateRange === 'custom' && filters.customDate) {
      if (evt.start_date > filters.customDate || evt.end_date < filters.customDate) return false;
    }

    // 4. Municipality
    if (filters.municipality && filters.municipality !== 'all') {
      if (evt.municipality.toLowerCase() !== filters.municipality.toLowerCase()) return false;
    }

    // 5. Subregion
    if (filters.subregion && filters.subregion !== 'all') {
      if (evt.subregion !== filters.subregion) return false;
    }

    // 6. Category
    if (filters.category && filters.category !== 'all') {
      if (evt.category !== filters.category) return false;
    }

    // 7. Price
    if (filters.priceType === 'free') {
      if (evt.price_type !== 'free') return false;
    } else if (filters.priceType === 'paid') {
      if (evt.price_type === 'free') return false;
    }

    // 8. Audience
    if (filters.audience && filters.audience !== 'all') {
      if (evt.audience !== filters.audience && evt.audience !== 'all_ages') return false;
    }

    // 9. Format
    if (filters.format && filters.format !== 'all') {
      if (evt.event_format !== filters.format) return false;
    }

    // 10. Verification
    if (filters.onlyVerified) {
      if (evt.status === 'UNVERIFIED') return false;
    }

    // 11. Near me distance
    if (filters.nearMe && filters.userCoords && filters.maxDistanceKm) {
      const dist = calculateDistanceKm(
        filters.userCoords.latitude,
        filters.userCoords.longitude,
        evt.latitude,
        evt.longitude
      );
      if (dist > filters.maxDistanceKm) return false;
    }

    return true;
  });
}

export interface SearchSuggestions {
  events: CulturalEvent[];
  municipalities: MunicipalityData[];
  categories: string[];
}

export function getInstantSuggestions(
  query: string,
  events: CulturalEvent[],
  municipalities: MunicipalityData[]
): SearchSuggestions {
  if (!query || query.trim().length < 2) {
    return { events: [], municipalities: [], categories: [] };
  }

  const q = normalizeSearchText(query);

  const matchedEvents = events
    .filter(e => normalizeSearchText(e.title).includes(q) || e.tags.some(t => normalizeSearchText(t).includes(q)))
    .slice(0, 4);

  const matchedMunicipalities = municipalities
    .filter(m => normalizeSearchText(m.name).includes(q) || normalizeSearchText(m.subregion).includes(q))
    .slice(0, 3);

  const allCategories = ['Música', 'Teatro', 'Arte', 'Fiestas', 'Cine', 'Gastronomía', 'Patrimonio', 'Naturaleza', 'Talleres'];
  const matchedCategories = allCategories
    .filter(c => normalizeSearchText(c).includes(q))
    .slice(0, 3);

  return {
    events: matchedEvents,
    municipalities: matchedMunicipalities,
    categories: matchedCategories,
  };
}
