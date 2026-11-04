import React, { useState, useMemo } from 'react';
import { 
  Search, 
  MapPin, 
  Sparkles, 
  ArrowRight, 
  Compass, 
  Calendar, 
  Clock,
  Tag, 
  Navigation,
  ChevronRight
} from 'lucide-react';
import { CulturalEvent, MunicipalityData, EventCategory, Subregion, FilterState } from '../types';
import { EventCard } from '../components/common/EventCard';
import { CategoryChip } from '../components/common/CategoryChip';
import { DateChip } from '../components/common/DateChip';
import { MunicipalityCard } from '../components/common/MunicipalityCard';
import { PriceLabel } from '../components/common/PriceLabel';
import { SourceBadge } from '../components/common/SourceBadge';
import { MUNICIPALITIES } from '../data/municipalities';
import { balanceTerritorialDiversity } from '../services/territorialDiversity';

const formatDateBadge = (dateStr: string) => {
  const [year, month, day] = dateStr.split('-').map(Number);
  const d = new Date(year, month - 1, day);
  const weekday = d.toLocaleDateString('es-CO', { weekday: 'short' }).toUpperCase().replace('.', '');
  const monthName = d.toLocaleDateString('es-CO', { month: 'short' }).toUpperCase().replace('.', '');
  return `${weekday} · ${day} ${monthName}`;
};

interface HomeViewProps {
  events: CulturalEvent[];
  onSelectEvent: (event: CulturalEvent) => void;
  onSelectMunicipality: (muni: MunicipalityData) => void;
  onApplyQuickFilter: (filters: Partial<FilterState>) => void;
  onOpenLocationModal: () => void;
  currentMunicipality: string | 'all';
  currentSubregion: Subregion | 'all';
  onNavigateExplore: (initialQuery?: string) => void;
}

const CATEGORIES: EventCategory[] = [
  'Música', 'Fiestas', 'Arte', 'Teatro', 'Cine', 
  'Gastronomía', 'Ferias', 'Talleres', 'Literatura', 
  'Patrimonio', 'Familia', 'Naturaleza'
];

export const HomeView: React.FC<HomeViewProps> = ({
  events,
  onSelectEvent,
  onSelectMunicipality,
  onApplyQuickFilter,
  onOpenLocationModal,
  currentMunicipality,
  currentSubregion,
  onNavigateExplore,
}) => {
  const [searchInput, setSearchInput] = useState('');
  const [selectedDateQuick, setSelectedDateQuick] = useState<'all' | 'today' | 'tomorrow' | 'this_weekend' | 'this_week'>('all');
  const [regionalTab, setRegionalTab] = useState<'Suroeste' | 'Oriente'>('Suroeste');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onNavigateExplore(searchInput.trim());
    } else {
      onNavigateExplore();
    }
  };

  // Section 57: Editorial Curated modules with Territorial Diversity algorithm
  const weekendEvents = useMemo(() => balanceTerritorialDiversity(
    events.filter(e => e.start_date <= '2026-09-13' && e.end_date >= '2026-09-12'),
    6,
    0.25
  ), [events]);

  const spotlightEvent = useMemo(() => (weekendEvents.length > 0 ? weekendEvents[0] : null), [weekendEvents]);
  const otherWeekendEvents = useMemo(() => weekendEvents.slice(1), [weekendEvents]);

  const freeEvents = useMemo(() => balanceTerritorialDiversity(
    events.filter(e => e.price_type === 'free'),
    6,
    0.25
  ), [events]);

  const suroesteEvents = useMemo(() => events.filter(e => e.subregion === 'Suroeste'), [events]);
  const orienteEvents = useMemo(() => events.filter(e => e.subregion === 'Oriente'), [events]);
  const worthTheTripEvents = useMemo(() => events.filter(e => e.is_worth_the_trip), [events]);

  const handleSurpriseMe = () => {
    if (events.length === 0) return;
    const randomIndex = Math.floor(Math.random() * events.length);
    onSelectEvent(events[randomIndex]);
  };

  return (
    <div className="space-y-12 pb-16">
      {/* PRD Section 7: Discovery Hero - Refined, Quieter Editorial Presentation */}
      <section className="bg-sand-50/70 pt-8 sm:pt-12 pb-7 border-b border-zinc-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="max-w-3xl mx-auto text-center flex flex-col items-center space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-sand-100 text-zinc-600 border border-zinc-200/70">
              <span className="w-1.5 h-1.5 rounded-full bg-forest-600" aria-hidden="true" />
              <span>Cartelera cultural verificada · 125 municipios</span>
            </div>
            
            <h1 className="text-3xl sm:text-4xl md:text-[44px] font-bold text-zinc-900 tracking-tight leading-[1.15] text-center">
              Descubre qué hacer en los pueblos de Antioquia
            </h1>

            <p className="text-zinc-600 text-sm sm:text-base leading-relaxed font-normal max-w-2xl text-center">
              Conciertos, fiestas tradicionales, teatro, ferias y patrimonio en los municipios antioqueños. Conexión directa a fuentes oficiales, sin venta de boletas ni intermediarios.
            </p>

            {/* Architectural, Clean Search Bar */}
            <form onSubmit={handleSearchSubmit} className="pt-2 w-full max-w-2xl">
              <div className="relative flex items-center rounded-2xl bg-white border border-zinc-200/90 shadow-xs p-1.5 sm:p-2 focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:border-brand-500 transition-all text-left">
                <Search className="w-4 h-4 text-zinc-400 ml-3 shrink-0" aria-hidden="true" />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Busca eventos, pueblos o planes (ej. 'Jardín', 'Fiestas', 'Gratis')..."
                  aria-label="Buscar eventos, pueblos o planes culturales en Antioquia"
                  className="w-full px-3 py-2 text-base sm:text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none bg-transparent"
                />
                <kbd className="hidden sm:inline-flex items-center justify-center px-1.5 py-0.5 text-[11px] font-mono font-medium text-zinc-500 bg-sand-100/80 rounded border border-zinc-200 mr-2 shrink-0 select-none">
                  /
                </kbd>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white font-semibold text-xs sm:text-sm transition-colors shrink-0 cursor-pointer min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                >
                  Buscar
                </button>
              </div>
            </form>

            {/* Understated Territorial Metadata Line with Serendipity Plan al azar */}
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1.5 pt-1 text-xs text-zinc-500">
              <span className="flex items-center gap-1.5">
                <span className="font-semibold text-zinc-700">{events.length}</span> planes activos
              </span>
              <span className="text-zinc-300">·</span>
              <span className="flex items-center gap-1.5">
                <span className="font-semibold text-zinc-700">9</span> subregiones
              </span>
              <span className="text-zinc-300">·</span>
              <button
                type="button"
                onClick={onOpenLocationModal}
                className="font-medium text-zinc-600 hover:text-brand-600 transition-colors inline-flex items-center gap-1 cursor-pointer underline underline-offset-2"
              >
                <MapPin className="w-3 h-3 text-zinc-400" />
                <span>
                  {currentMunicipality === 'all'
                    ? 'Toda Antioquia'
                    : currentMunicipality}
                </span>
              </button>
              <span className="text-zinc-300">·</span>
              <button
                type="button"
                onClick={handleSurpriseMe}
                className="inline-flex items-center gap-1 font-semibold text-brand-600 hover:text-brand-700 transition-colors cursor-pointer hover:underline"
                aria-label="Descubrir un plan cultural al azar en Antioquia"
                title="Elegir un plan al azar por los caminos de Antioquia"
              >
                <Sparkles className="w-3.5 h-3.5 text-brand-500" />
                <span>Plan al azar</span>
              </button>
            </div>
          </div>

          {/* Quick Date Chips with calm spacing */}
          <div className="relative mt-7 pt-5 border-t border-zinc-200/50 after:pointer-events-none after:absolute after:right-0 after:top-5 after:bottom-2 after:w-8 after:bg-gradient-to-l after:from-sand-50/70 after:to-transparent sm:after:hidden">
            <div className="flex items-center justify-start sm:justify-center gap-2 overflow-x-auto pb-1 no-scrollbar">
              <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider shrink-0 mr-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-zinc-400" />
                Cuándo:
              </span>
              <DateChip
                label="Todos los planes"
                isSelected={selectedDateQuick === 'all'}
                onClick={() => {
                  setSelectedDateQuick('all');
                  onApplyQuickFilter({ dateRange: 'all' });
                }}
              />
              <DateChip
                label="Hoy martes"
                isSelected={selectedDateQuick === 'today'}
                onClick={() => {
                  setSelectedDateQuick('today');
                  onApplyQuickFilter({ dateRange: 'today' });
                  onNavigateExplore();
                }}
              />
              <DateChip
                label="Mañana miércoles"
                isSelected={selectedDateQuick === 'tomorrow'}
                onClick={() => {
                  setSelectedDateQuick('tomorrow');
                  onApplyQuickFilter({ dateRange: 'tomorrow' });
                  onNavigateExplore();
                }}
              />
              <DateChip
                label="Este fin de semana"
                isSelected={selectedDateQuick === 'this_weekend'}
                onClick={() => {
                  setSelectedDateQuick('this_weekend');
                  onApplyQuickFilter({ dateRange: 'this_weekend' });
                  onNavigateExplore();
                }}
              />
              <DateChip
                label="Esta semana"
                isSelected={selectedDateQuick === 'this_week'}
                onClick={() => {
                  setSelectedDateQuick('this_week');
                  onApplyQuickFilter({ dateRange: 'this_week' });
                  onNavigateExplore();
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base sm:text-lg font-bold text-zinc-900 tracking-tight">
            Explora por categoría
          </h2>
        </div>
        <div className="relative after:pointer-events-none after:absolute after:right-0 after:top-0 after:bottom-2 after:w-10 after:bg-gradient-to-l after:from-sand-50/70 after:to-transparent sm:after:hidden">
          <div className="flex items-center gap-2.5 overflow-x-auto pb-2 no-scrollbar">
            {CATEGORIES.map((cat) => (
              <CategoryChip
                key={cat}
                category={cat}
                onClick={(c) => {
                  onApplyQuickFilter({ category: c });
                  onNavigateExplore();
                }}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Editorial Block 1: "Este fin de semana" */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight">
            Este fin de semana
          </h2>
          <button
            type="button"
            onClick={() => {
              onApplyQuickFilter({ dateRange: 'this_weekend' });
              onNavigateExplore();
            }}
            className="text-xs sm:text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1 cursor-pointer"
          >
            <span>Ver cartelera del fin de semana</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Editorial Spotlight Card for #1 Weekend Event */}
        {spotlightEvent && (
          <article className="group relative bg-white rounded-3xl overflow-hidden border border-zinc-200/80 shadow-xs hover:shadow-card transition-all duration-300 mb-6 focus-within:ring-2 focus-within:ring-brand-500 select-none">
            <div className="grid grid-cols-1 md:grid-cols-12">
              {/* Image Container */}
              <div className="md:col-span-7 relative aspect-[16/10] md:aspect-auto overflow-hidden bg-sand-100 min-h-[240px] md:min-h-[320px]">
                <img
                  src={spotlightEvent.image_url}
                  alt={spotlightEvent.title}
                  loading="eager"
                  decoding="async"
                  fetchPriority="high"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent md:hidden" />
                
                {/* Category Badge */}
                <div className="absolute top-4 left-4 flex items-center gap-2 pointer-events-none">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-black/60 backdrop-blur-md text-white border border-white/20">
                    {spotlightEvent.category}
                  </span>
                </div>

                {spotlightEvent.is_worth_the_trip && (
                  <div className="absolute bottom-4 left-4 pointer-events-none">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500 text-white shadow-sm">
                      ★ Vale el viaje
                    </span>
                  </div>
                )}
              </div>

              {/* Editorial Content */}
              <div className="md:col-span-5 p-6 sm:p-7 flex flex-col justify-between bg-white">
                <div>
                  <div className="flex items-center gap-2 text-xs font-bold text-brand-600 uppercase tracking-wider mb-2 pointer-events-none">
                    <Calendar className="w-3.5 h-3.5 shrink-0" />
                    <span>{formatDateBadge(spotlightEvent.start_date)}</span>
                    <span className="text-zinc-300">·</span>
                    <span className="text-zinc-600 normal-case flex items-center gap-1 font-semibold">
                      <Clock className="w-3.5 h-3.5 text-zinc-500" />
                      {spotlightEvent.start_time}
                    </span>
                  </div>

                  <h3 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight leading-tight group-hover:text-brand-600 transition-colors">
                    <button
                      type="button"
                      onClick={() => onSelectEvent(spotlightEvent)}
                      className="after:absolute after:inset-0 text-left focus:outline-none focus-visible:underline cursor-pointer"
                    >
                      {spotlightEvent.title}
                    </button>
                  </h3>

                  <div className="flex items-center gap-1.5 text-xs sm:text-sm text-zinc-600 font-medium mt-2 pointer-events-none">
                    <MapPin className="w-4 h-4 text-zinc-500 shrink-0" />
                    <span>
                      <strong className="text-zinc-900 font-bold">{spotlightEvent.municipality}</strong> ({spotlightEvent.subregion}) · {spotlightEvent.venue_name}
                    </span>
                  </div>

                  <p className="text-zinc-600 text-sm mt-3 line-clamp-2 leading-relaxed pointer-events-none font-normal">
                    {spotlightEvent.short_description}
                  </p>
                </div>

                <div className="relative z-20 pt-4 mt-4 border-t border-zinc-100 flex items-center justify-between gap-3">
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Entrada</span>
                    <PriceLabel priceType={spotlightEvent.price_type} priceFrom={spotlightEvent.price_from} priceTo={spotlightEvent.price_to} />
                  </div>
                  <div className="flex items-center gap-2">
                    <SourceBadge
                      sourceName={spotlightEvent.source_name}
                      sourceType={spotlightEvent.source_type}
                      showIcon={true}
                      className="max-w-[150px]"
                    />
                    <div className="w-8 h-8 rounded-full bg-sand-100 text-zinc-700 group-hover:bg-brand-500 group-hover:text-white transition-colors flex items-center justify-center shrink-0 pointer-events-none">
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </article>
        )}

        {/* Remaining Weekend Events Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {otherWeekendEvents.map((evt) => (
            <EventCard
              key={evt.event_id}
              event={evt}
              onSelect={onSelectEvent}
              priority={true}
            />
          ))}
        </div>
      </section>

      {/* Editorial Block 2: Pueblos de Antioquia */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight">
              Pueblos de Antioquia
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 mt-0.5">
              Patrimonio, valles cafeteros y tradición cultural
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
          {MUNICIPALITIES.filter(m => m.slug !== 'medellin').slice(0, 4).map((muni) => {
            const count = events.filter(e => e.municipality.toLowerCase() === muni.name.toLowerCase()).length;
            return (
              <MunicipalityCard
                key={muni.slug}
                municipality={muni}
                eventCount={count}
                onSelect={onSelectMunicipality}
              />
            );
          })}
        </div>
      </section>

      {/* Editorial Block 3: Planes gratuitos (Flattened, no nested card) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight">
              Planes con entrada libre
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 mt-0.5">
              Conciertos en plazas, festivales comunitarios y exposiciones abiertas
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              onApplyQuickFilter({ priceType: 'free' });
              onNavigateExplore();
            }}
            className="text-xs sm:text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1 cursor-pointer"
          >
            <span>Ver planes de entrada libre</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {freeEvents.slice(0, 3).map((evt) => (
            <EventCard
              key={evt.event_id}
              event={evt}
              onSelect={onSelectEvent}
            />
          ))}
        </div>
      </section>

      {/* Editorial Block 4: Consolidated Subregional Showcase (Suroeste / Oriente) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight">
              Descubre por subregión
            </h2>
            <p className="text-xs sm:text-sm text-zinc-500 mt-0.5">
              Oferta cultural viva en las provincias de Antioquia
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="inline-flex p-1 rounded-xl bg-sand-200/70 border border-zinc-200/80 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setRegionalTab('Suroeste')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  regionalTab === 'Suroeste'
                    ? 'bg-white text-zinc-900 shadow-xs font-bold'
                    : 'text-zinc-600 hover:text-zinc-900'
                }`}
              >
                Suroeste ({suroesteEvents.length})
              </button>
              <button
                type="button"
                onClick={() => setRegionalTab('Oriente')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  regionalTab === 'Oriente'
                    ? 'bg-white text-zinc-900 shadow-xs font-bold'
                    : 'text-zinc-600 hover:text-zinc-900'
                }`}
              >
                Oriente ({orienteEvents.length})
              </button>
            </div>

            <button
              type="button"
              onClick={() => {
                onApplyQuickFilter({ subregion: regionalTab });
                onNavigateExplore();
              }}
              className="text-xs sm:text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1 cursor-pointer ml-1"
            >
              <span>Ver planes en el {regionalTab}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div 
          key={regionalTab}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-300 ease-natural"
        >
          {(regionalTab === 'Suroeste' ? suroesteEvents : orienteEvents).slice(0, 3).map((evt) => (
            <EventCard
              key={evt.event_id}
              event={evt}
              onSelect={onSelectEvent}
            />
          ))}
        </div>
      </section>

      {/* Editorial Block 5: "Imperdibles / Vale el Viaje" */}
      {worthTheTripEvents.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="border-t border-zinc-200/80 pt-8">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-xl sm:text-2xl font-bold text-zinc-900 tracking-tight">
                  Eventos que valen el viaje
                </h2>
                <p className="text-xs sm:text-sm text-zinc-500 mt-0.5">
                  Celebraciones y festivales tradicionales de gran arraigo
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {worthTheTripEvents.slice(0, 3).map((evt) => (
                <EventCard
                  key={evt.event_id}
                  event={evt}
                  onSelect={onSelectEvent}
                />
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
