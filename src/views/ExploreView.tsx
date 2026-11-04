import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Search, 
  SlidersHorizontal, 
  X, 
  Map as MapIcon, 
  List, 
  LayoutGrid,
  RotateCcw, 
  Calendar,
  Sparkles,
  MapPin,
  Clock
} from 'lucide-react';
import { CulturalEvent, FilterState, EventCategory } from '../types';
import { EventCard } from '../components/common/EventCard';
import { EventCardCompact } from '../components/common/EventCardCompact';
import { LumaEventRow } from '../components/common/LumaEventRow';
import { FilterSheet } from '../components/common/FilterSheet';
import { LazyMap } from '../components/common/LazyMap';
import { filterEvents } from '../services/searchEngine';

interface ExploreViewProps {
  events: CulturalEvent[];
  filters: FilterState;
  onUpdateFilters: (newFilters: FilterState) => void;
  onSelectEvent: (event: CulturalEvent) => void;
  onClearFilters: () => void;
  initialViewMode?: 'list' | 'grid' | 'map';
}

const LUMA_CATEGORIES: Array<{ id: EventCategory | 'all'; label: string }> = [
  { id: 'all', label: 'Todos' },
  { id: 'Música', label: 'Música' },
  { id: 'Fiestas', label: 'Fiestas y Tradición' },
  { id: 'Arte', label: 'Arte' },
  { id: 'Teatro', label: 'Teatro y Danza' },
  { id: 'Cine', label: 'Cine' },
  { id: 'Gastronomía', label: 'Gastronomía' },
  { id: 'Ferias', label: 'Ferias' },
  { id: 'Talleres', label: 'Talleres' },
  { id: 'Literatura', label: 'Literatura' },
  { id: 'Patrimonio', label: 'Patrimonio' },
  { id: 'Familia', label: 'Familia' },
  { id: 'Naturaleza', label: 'Naturaleza' },
];

const QUICK_DATES: Array<{ id: FilterState['dateRange']; label: string }> = [
  { id: 'all', label: 'Cualquier fecha' },
  { id: 'today', label: 'Hoy' },
  { id: 'tomorrow', label: 'Mañana' },
  { id: 'this_weekend', label: 'Este finde' },
];

interface DateGroup {
  id: string;
  title: string;
  subtitle?: string;
  events: CulturalEvent[];
}

function groupEventsChronologically(events: CulturalEvent[]): DateGroup[] {
  // Sort events chronologically: start_date ascending, then start_time ascending
  const sorted = [...events].sort((a, b) => {
    if (a.start_date !== b.start_date) {
      return a.start_date.localeCompare(b.start_date);
    }
    return (a.start_time || '').localeCompare(b.start_time || '');
  });

  const groups: Record<string, DateGroup> = {
    today: {
      id: 'today',
      title: 'Hoy',
      subtitle: 'Martes, 8 de septiembre',
      events: [],
    },
    tomorrow: {
      id: 'tomorrow',
      title: 'Mañana',
      subtitle: 'Miércoles, 9 de septiembre',
      events: [],
    },
    this_week: {
      id: 'this_week',
      title: 'Esta semana',
      subtitle: 'Jueves 10 y Viernes 11 de septiembre',
      events: [],
    },
    this_weekend: {
      id: 'this_weekend',
      title: 'Este fin de semana',
      subtitle: 'Sábado 12 y Domingo 13 de septiembre',
      events: [],
    },
    upcoming: {
      id: 'upcoming',
      title: 'Próximas semanas',
      subtitle: 'A partir del 14 de septiembre',
      events: [],
    },
    other: {
      id: 'other',
      title: 'Otros eventos',
      events: [],
    },
  };

  for (const evt of sorted) {
    if (evt.start_date === '2026-09-08') {
      groups.today.events.push(evt);
    } else if (evt.start_date === '2026-09-09') {
      groups.tomorrow.events.push(evt);
    } else if (evt.start_date === '2026-09-10' || evt.start_date === '2026-09-11') {
      groups.this_week.events.push(evt);
    } else if (evt.start_date === '2026-09-12' || evt.start_date === '2026-09-13') {
      groups.this_weekend.events.push(evt);
    } else if (evt.start_date > '2026-09-13') {
      groups.upcoming.events.push(evt);
    } else {
      groups.other.events.push(evt);
    }
  }

  return Object.values(groups).filter(g => g.events.length > 0);
}

export const ExploreView: React.FC<ExploreViewProps> = ({
  events,
  filters,
  onUpdateFilters,
  onSelectEvent,
  onClearFilters,
  initialViewMode = 'list',
}) => {
  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'map'>(initialViewMode);
  const [isFilterSheetOpen, setIsFilterSheetOpen] = useState(false);
  const [hoveredEventId, setHoveredEventId] = useState<string | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialViewMode) {
      setViewMode(initialViewMode);
    }
  }, [initialViewMode]);

  // Keyboard shortcut: '/' focuses search input
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === '/' && 
        document.activeElement?.tagName !== 'INPUT' && 
        document.activeElement?.tagName !== 'TEXTAREA'
      ) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filtered = useMemo(() => filterEvents(events, filters), [events, filters]);

  // Group events chronologically (Luma Discover pattern)
  const dateGroups = useMemo(() => groupEventsChronologically(filtered), [filtered]);

  const activeFilterChips: Array<{ id: string; label: string; onRemove: () => void }> = [];

  if (filters.searchQuery.trim()) {
    activeFilterChips.push({
      id: 'query',
      label: `"${filters.searchQuery}"`,
      onRemove: () => onUpdateFilters({ ...filters, searchQuery: '' }),
    });
  }

  if (filters.dateRange !== 'all') {
    const labels: Record<string, string> = {
      today: 'Hoy',
      tomorrow: 'Mañana',
      this_weekend: 'Este finde',
      this_week: 'Esta semana',
      next_weekend: 'Próximo finde',
      custom: 'Fecha elegida',
    };
    activeFilterChips.push({
      id: 'date',
      label: labels[filters.dateRange] || 'Fecha',
      onRemove: () => onUpdateFilters({ ...filters, dateRange: 'all', customDate: undefined }),
    });
  }

  if (filters.municipality !== 'all') {
    activeFilterChips.push({
      id: 'municipality',
      label: filters.municipality,
      onRemove: () => onUpdateFilters({ ...filters, municipality: 'all' }),
    });
  }

  if (filters.subregion !== 'all') {
    activeFilterChips.push({
      id: 'subregion',
      label: filters.subregion,
      onRemove: () => onUpdateFilters({ ...filters, subregion: 'all' }),
    });
  }

  if (filters.category !== 'all') {
    activeFilterChips.push({
      id: 'category',
      label: filters.category,
      onRemove: () => onUpdateFilters({ ...filters, category: 'all' }),
    });
  }

  if (filters.priceType !== 'all') {
    activeFilterChips.push({
      id: 'price',
      label: filters.priceType === 'free' ? 'Gratis' : 'Con boleta',
      onRemove: () => onUpdateFilters({ ...filters, priceType: 'all' }),
    });
  }

  if (filters.audience !== 'all') {
    const audienceLabels: Record<string, string> = {
      all_ages: 'Todo público',
      family: 'Familiar',
      adults: 'Adultos',
      youth: 'Jóvenes',
    };
    activeFilterChips.push({
      id: 'audience',
      label: audienceLabels[filters.audience] || filters.audience,
      onRemove: () => onUpdateFilters({ ...filters, audience: 'all' }),
    });
  }

  if (filters.format !== 'all') {
    const formatLabels: Record<string, string> = {
      outdoor: 'Al aire libre',
      in_person: 'Recinto cerrado',
      hybrid: 'Híbrido',
    };
    activeFilterChips.push({
      id: 'format',
      label: formatLabels[filters.format] || filters.format,
      onRemove: () => onUpdateFilters({ ...filters, format: 'all' }),
    });
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Header Section with Luma discovery flair */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-zinc-200/60">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-brand-50 text-brand-700 border border-brand-200/70 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Directorio Cultural · Antioquia</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-zinc-900 tracking-tight">
            Descubre eventos y experiencias
          </h1>
          <p className="text-sm text-zinc-500 mt-1 max-w-2xl">
            Explora ferias, conciertos, exposiciones y talleres a lo largo de los 125 municipios de Antioquia.
          </p>
        </div>

        {/* View Toggle: [Lista | Cuadrícula | Mapa] (Luma 3-way layout switcher) */}
        <div className="flex items-center self-start md:self-auto bg-sand-200/80 p-1 rounded-2xl border border-zinc-200 shrink-0 shadow-2xs">
          <button
            type="button"
            onClick={() => setViewMode('list')}
            aria-label="Vista en lista"
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[38px] ${
              viewMode === 'list'
                ? 'bg-white text-zinc-900 shadow-xs'
                : 'text-zinc-600 hover:text-zinc-900'
            }`}
          >
            <List className="w-4 h-4" />
            <span className="hidden sm:inline">Lista</span>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('grid')}
            aria-label="Vista en cuadrícula"
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[38px] ${
              viewMode === 'grid'
                ? 'bg-white text-zinc-900 shadow-xs'
                : 'text-zinc-600 hover:text-zinc-900'
            }`}
          >
            <LayoutGrid className="w-4 h-4" />
            <span className="hidden sm:inline">Cuadrícula</span>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('map')}
            aria-label="Vista en mapa"
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[38px] ${
              viewMode === 'map'
                ? 'bg-white text-zinc-900 shadow-xs'
                : 'text-zinc-600 hover:text-zinc-900'
            }`}
          >
            <MapIcon className="w-4 h-4" />
            <span className="hidden sm:inline">Mapa</span>
          </button>
        </div>
      </div>

      {/* Luma Category Pill Carousel (Horizontal scrolling pills) */}
      <div className="relative">
        <div 
          className="flex items-center gap-2 overflow-x-auto no-scrollbar py-1 scroll-smooth"
          role="tablist"
          aria-label="Categorías de eventos"
        >
          {LUMA_CATEGORIES.map((cat) => {
            const isSelected = filters.category === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                role="tab"
                aria-selected={isSelected}
                onClick={() => onUpdateFilters({ ...filters, category: cat.id })}
                className={`px-4 py-2 rounded-full text-xs font-bold whitespace-nowrap transition-all duration-200 cursor-pointer min-h-[38px] flex items-center shrink-0 select-none ${
                  isSelected
                    ? 'bg-zinc-900 text-white shadow-sm border border-zinc-900 scale-[1.02]'
                    : 'bg-white text-zinc-700 hover:text-zinc-950 hover:bg-zinc-100/80 border border-zinc-200/90'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Search & Secondary Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        {/* Search input with live query + keyboard shortcut */}
        <div className="relative flex-1">
          <Search className="w-5 h-5 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            ref={searchInputRef}
            type="text"
            value={filters.searchQuery}
            onChange={(e) => onUpdateFilters({ ...filters, searchQuery: e.target.value })}
            placeholder="Buscar por evento, artista, municipio, recinto o género..."
            aria-label="Buscar eventos por nombre, artista, municipio o recinto"
            className="w-full pl-10 pr-10 py-3 rounded-2xl border border-zinc-200/90 bg-white text-base sm:text-sm font-medium focus:ring-2 focus:ring-brand-500 focus:outline-none shadow-xs"
          />
          {!filters.searchQuery && (
            <kbd className="hidden sm:inline-flex items-center justify-center px-1.5 py-0.5 text-[11px] font-mono font-medium text-zinc-400 bg-sand-100/80 rounded border border-zinc-200 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none select-none">
              /
            </kbd>
          )}
          {filters.searchQuery && (
            <button
              type="button"
              onClick={() => onUpdateFilters({ ...filters, searchQuery: '' })}
              aria-label="Borrar búsqueda"
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-zinc-500 hover:text-zinc-700 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-full"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Quick Date Switcher Pills + Filter Sheet trigger button */}
        <div className="flex items-center gap-2 shrink-0 flex-wrap sm:flex-nowrap">
          {/* Quick Dates */}
          <div className="hidden md:flex items-center gap-1 bg-white p-1 rounded-2xl border border-zinc-200/90 shadow-2xs">
            {QUICK_DATES.map((qd) => {
              const isSelected = filters.dateRange === qd.id;
              return (
                <button
                  key={qd.id}
                  type="button"
                  onClick={() => onUpdateFilters({ ...filters, dateRange: qd.id, customDate: undefined })}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-sand-200/90 text-zinc-900 font-bold'
                      : 'text-zinc-500 hover:text-zinc-900 hover:bg-sand-100/60'
                  }`}
                >
                  {qd.label}
                </button>
              );
            })}
          </div>

          {/* Full Filters Bottom Sheet Trigger */}
          <button
            type="button"
            onClick={() => setIsFilterSheetOpen(true)}
            className={`flex items-center gap-2 px-4 py-3 rounded-2xl border text-sm font-bold transition-all cursor-pointer min-h-[44px] ${
              activeFilterChips.length > 0
                ? 'bg-zinc-900 text-white border-zinc-900 shadow-sm'
                : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filtros</span>
            {activeFilterChips.length > 0 && (
              <span className="w-5 h-5 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-bold">
                {activeFilterChips.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Active Filter Chips (Removable tags) */}
      {activeFilterChips.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap pt-0.5">
          <span className="text-xs font-semibold text-zinc-500">Filtros activos:</span>
          {activeFilterChips.map((chip) => (
            <span
              key={chip.id}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-zinc-100 text-zinc-800 border border-zinc-200/80 shadow-2xs"
            >
              <span>{chip.label}</span>
              <button
                type="button"
                onClick={chip.onRemove}
                className="hover:text-brand-600 cursor-pointer p-0.5"
                aria-label={`Quitar filtro ${chip.label}`}
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}

          <button
            type="button"
            onClick={onClearFilters}
            className="text-xs font-bold text-brand-600 hover:text-brand-700 underline cursor-pointer ml-1"
          >
            Limpiar todos
          </button>
        </div>
      )}

      {/* Results Header Counter */}
      <div className="flex items-center justify-between text-xs text-zinc-500 font-medium">
        <p>
          Mostrando <strong className="text-zinc-900 font-bold">{filtered.length}</strong>{' '}
          {filtered.length === 1 ? 'evento cultural' : 'eventos culturales'}{' '}
          {filters.municipality !== 'all'
            ? `en ${filters.municipality}`
            : filters.subregion !== 'all'
            ? `en el ${filters.subregion} antioqueño`
            : filters.nearMe
            ? 'cerca de tu ubicación'
            : 'en Antioquia'}
        </p>
      </div>

      {/* Zero results state */}
      {filtered.length === 0 && (
        <div className="text-center py-16 px-4 bg-white rounded-3xl border border-zinc-200/80 shadow-xs max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-full bg-sand-100 text-zinc-400 mx-auto flex items-center justify-center mb-4">
            <Search className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-zinc-900">
            No encontramos planes con estos filtros
          </h3>
          <p className="text-sm text-zinc-500 mt-1 max-w-sm mx-auto">
            Prueba quitando algunos filtros o ampliando la fecha o el municipio seleccionado.
          </p>
          <button
            type="button"
            onClick={onClearFilters}
            className="mt-5 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-zinc-900 text-white font-bold text-xs hover:bg-black transition-all cursor-pointer shadow-xs"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restablecer todos los filtros</span>
          </button>
        </div>
      )}

      {/* Content Rendering depending on viewMode (Luma Lista, Cuadrícula, or Mapa) */}
      {filtered.length > 0 && (
        <>
          {viewMode === 'list' && (
            /* Luma Chronological Timeline List View */
            <div className="space-y-8">
              {dateGroups.map((group, groupIdx) => (
                <section key={group.id} aria-label={group.title} className="space-y-3">
                  {/* Sticky Section Date Header with subtle glassmorphism */}
                  <div className="sticky top-16 z-10 py-2.5 px-4 bg-sand-50/95 backdrop-blur-md rounded-2xl border border-zinc-200/70 flex items-center justify-between shadow-2xs">
                    <div className="flex items-baseline gap-2 truncate">
                      <h2 className="text-base sm:text-lg font-black text-zinc-900 tracking-tight">
                        {group.title}
                      </h2>
                      {group.subtitle && (
                        <span className="text-xs sm:text-sm font-medium text-zinc-500 truncate">
                          · {group.subtitle}
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-bold text-zinc-500 px-2.5 py-0.5 rounded-full bg-white border border-zinc-200/80 shrink-0">
                      {group.events.length} {group.events.length === 1 ? 'evento' : 'eventos'}
                    </span>
                  </div>

                  {/* Luma Event Rows */}
                  <div className="space-y-3">
                    {group.events.map((evt, idx) => (
                      <LumaEventRow
                        key={evt.event_id}
                        event={evt}
                        priority={groupIdx === 0 && idx < 3}
                        onSelect={onSelectEvent}
                      />
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}

          {viewMode === 'grid' && (
            /* Luma 3-Column Grid View */
            <div className="space-y-8">
              {dateGroups.map((group, groupIdx) => (
                <section key={group.id} aria-label={group.title} className="space-y-4">
                  {/* Sticky Section Date Header */}
                  <div className="sticky top-16 z-10 py-2.5 px-4 bg-sand-50/95 backdrop-blur-md rounded-2xl border border-zinc-200/70 flex items-center justify-between shadow-2xs">
                    <div className="flex items-baseline gap-2 truncate">
                      <h2 className="text-base sm:text-lg font-black text-zinc-900 tracking-tight">
                        {group.title}
                      </h2>
                      {group.subtitle && (
                        <span className="text-xs sm:text-sm font-medium text-zinc-500 truncate">
                          · {group.subtitle}
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-bold text-zinc-500 px-2.5 py-0.5 rounded-full bg-white border border-zinc-200/80 shrink-0">
                      {group.events.length} {group.events.length === 1 ? 'evento' : 'eventos'}
                    </span>
                  </div>

                  {/* 3-Column Event Card Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {group.events.map((evt, idx) => (
                      <EventCard
                        key={evt.event_id}
                        event={evt}
                        priority={groupIdx === 0 && idx < 6}
                        onSelect={onSelectEvent}
                      />
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}

          {viewMode === 'map' && (
            /* Map View with Leaflet */
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-5 space-y-3 max-h-[750px] overflow-y-auto pr-1">
                {filtered.map((evt) => (
                  <EventCardCompact
                    key={evt.event_id}
                    event={evt}
                    onSelect={onSelectEvent}
                    isHovered={hoveredEventId === evt.event_id}
                    onMouseEnter={() => setHoveredEventId(evt.event_id)}
                    onMouseLeave={() => setHoveredEventId(null)}
                  />
                ))}
              </div>
              <div className="lg:col-span-7 sticky top-24">
                <LazyMap
                  events={filtered}
                  selectedEvent={filtered.find(e => e.event_id === hoveredEventId) || null}
                  onSelectEvent={onSelectEvent}
                  className="h-[500px] lg:h-[750px] w-full"
                />
              </div>
            </div>
          )}
        </>
      )}

      {/* Filter Sheet Modal */}
      <FilterSheet
        isOpen={isFilterSheetOpen}
        onClose={() => setIsFilterSheetOpen(false)}
        filters={filters}
        onChange={onUpdateFilters}
        totalMatchingEvents={filtered.length}
      />
    </div>
  );
};
