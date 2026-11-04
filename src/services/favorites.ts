const FAVORITES_KEY = 'evenjoy_saved_events_v1';
let memoryFallback: string[] = [];

export function getFavoriteEventIds(): string[] {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return memoryFallback;
    }
    const raw = localStorage.getItem(FAVORITES_KEY);
    return raw ? JSON.parse(raw) : memoryFallback;
  } catch (e) {
    return memoryFallback;
  }
}

export function isEventFavorited(eventId: string): boolean {
  const list = getFavoriteEventIds();
  return list.includes(eventId);
}

export function toggleFavoriteEvent(eventId: string): boolean {
  try {
    const current = getFavoriteEventIds();
    let updated: string[];
    let added = false;

    if (current.includes(eventId)) {
      updated = current.filter(id => id !== eventId);
      added = false;
    } else {
      updated = [eventId, ...current];
      added = true;
    }

    memoryFallback = updated;

    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem(FAVORITES_KEY, JSON.stringify(updated));
      } catch (storageErr) {
        // QuotaExceededError or private browsing mode - in-memory fallback handles it
      }
      window.dispatchEvent(new CustomEvent('evenjoy-favorites-changed', { detail: { updated, eventId, added } }));
    }
    return added;
  } catch (e) {
    return false;
  }
}
