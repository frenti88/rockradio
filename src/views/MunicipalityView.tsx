import React, { useState } from 'react';
import { 
  ArrowLeft, 
  MapPin, 
  Navigation, 
  Mountain, 
  Calendar, 
  Sparkles,
  ChevronRight,
  Filter
} from 'lucide-react';
import { MunicipalityData, CulturalEvent } from '../types';
import { EventCard } from '../components/common/EventCard';
import { LazyMap } from '../components/common/LazyMap';
import { MUNICIPALITIES } from '../data/municipalities';

interface MunicipalityViewProps {
  municipality: MunicipalityData;
  events: CulturalEvent[];
  onBack: () => void;
  onSelectEvent: (event: CulturalEvent) => void;
  onSelectOtherMunicipality: (muni: MunicipalityData) => void;
}

export const MunicipalityView: React.FC<MunicipalityViewProps> = ({
  municipality,
  events,
  onBack,
  onSelectEvent,
  onSelectOtherMunicipality,
}) => {
  const [filterMode, setFilterMode] = useState<'all' | 'weekend' | 'free'>('all');
  const [imageError, setImageError] = useState(false);

  const muniEvents = events.filter(
    e => e.municipality.toLowerCase() === municipality.name.toLowerCase()
  );

  const displayedEvents = muniEvents.filter(e => {
    if (filterMode === 'weekend') {
      return e.start_date <= '2026-09-13' && e.end_date >= '2026-09-12';
    }
    if (filterMode === 'free') {
      return e.price_type === 'free';
    }
    return true;
  });

  const nearbyMunicipalities = MUNICIPALITIES.filter(
    m => m.subregion === municipality.subregion && m.slug !== municipality.slug
  );

  return (
    <div className="pb-16 space-y-8">
      {/* Back button */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-6">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-bold text-zinc-600 hover:text-zinc-900 transition-colors py-2 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Volver al inicio</span>
        </button>
      </div>

      {/* Hero Header */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="relative rounded-3xl overflow-hidden shadow-card border border-zinc-200/80 bg-zinc-900 text-white min-h-[260px] sm:min-h-[320px] flex flex-col justify-end p-6 sm:p-10">
          {!imageError ? (
            <img
              src={municipality.hero_image}
              alt={municipality.name}
              onError={() => setImageError(true)}
              className="absolute inset-0 w-full h-full object-cover"
            />
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-forest-800 to-zinc-950" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />

          <div className="relative z-10 max-w-3xl space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-brand-500 text-white shadow-sm">
                {municipality.subregion}
              </span>
              <span className="text-xs text-white/80 font-medium">
                Antioquia, Colombia
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
              Qué hacer en {municipality.name}
            </h1>

            <p className="text-sm sm:text-base text-white/90 leading-relaxed max-w-2xl font-normal">
              {municipality.description}
            </p>

            {/* Quick travel facts */}
            <div className="pt-2 flex flex-wrap items-center gap-4 text-xs font-semibold text-white/80 tabular-nums">
              <span className="flex items-center gap-1">
                <Navigation className="w-3.5 h-3.5 text-brand-400" />
                {municipality.distance_from_medellin_km} km desde Medellín ({municipality.travel_time_approx})
              </span>
              <span className="flex items-center gap-1">
                <Mountain className="w-3.5 h-3.5 text-brand-400" />
                {municipality.altitude_m} msnm
              </span>
              {municipality.climate && (
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                  {municipality.climate}
                </span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Main Agenda Section (PRD Section 11: El evento sigue siendo el protagonista) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-200 pb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-zinc-900">
              Agenda Cultural Próxima en {municipality.name}
            </h2>
            <p className="text-xs text-zinc-500">
              {muniEvents.length} {muniEvents.length === 1 ? 'actividad confirmada' : 'actividades confirmadas'} con fuentes oficiales
            </p>
          </div>

          {/* Subfilters for town agenda */}
          <div className="flex items-center gap-2 bg-sand-200/80 p-1 rounded-2xl border border-zinc-200 shrink-0">
            <button
              type="button"
              onClick={() => setFilterMode('all')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterMode === 'all'
                  ? 'bg-white text-zinc-900 shadow-xs'
                  : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              Todos los eventos ({muniEvents.length})
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('weekend')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterMode === 'weekend'
                  ? 'bg-white text-zinc-900 shadow-xs'
                  : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              Este fin de semana
            </button>
            <button
              type="button"
              onClick={() => setFilterMode('free')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterMode === 'free'
                  ? 'bg-white text-zinc-900 shadow-xs'
                  : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              Entrada libre
            </button>
          </div>
        </div>

        {displayedEvents.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayedEvents.map((evt) => (
              <EventCard
                key={evt.event_id}
                event={evt}
                onSelect={onSelectEvent}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-3xl border border-zinc-200 p-6 space-y-2">
            <p className="text-sm font-bold text-zinc-800">
              No encontramos actividades con este filtro en {municipality.name}.
            </p>
            <p className="text-xs text-zinc-500">
              Prueba consultando las actividades de toda la semana o eventos en pueblos cercanos.
            </p>
            <button
              type="button"
              onClick={() => setFilterMode('all')}
              className="mt-2 text-xs font-bold text-brand-600 hover:text-brand-700 underline cursor-pointer"
            >
              Restablecer y ver toda la agenda de {municipality.name}
            </button>
          </div>
        )}
      </section>

      {/* Town Location Map */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 space-y-3">
        <h3 className="text-lg font-bold text-zinc-900">
          Ubicación y recintos en {municipality.name}
        </h3>
        <LazyMap
          events={muniEvents}
          onSelectEvent={onSelectEvent}
          className="h-80 w-full"
          initialCenter={[municipality.latitude, municipality.longitude]}
          initialZoom={13}
        />
      </section>

      {/* Nearby Municipalities in same subregion */}
      {nearbyMunicipalities.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 space-y-4 pt-6 border-t border-zinc-200">
          <h3 className="text-lg font-bold text-zinc-900">
            Otros pueblos cercanos en el {municipality.subregion}
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {nearbyMunicipalities.map((nearby) => (
              <button
                key={nearby.slug}
                type="button"
                onClick={() => onSelectOtherMunicipality(nearby)}
                className="p-4 rounded-2xl bg-white border border-zinc-200/80 hover:border-brand-500 hover:shadow-card text-left transition-all cursor-pointer group"
              >
                <span className="block font-bold text-sm text-zinc-900 group-hover:text-brand-600">
                  {nearby.name}
                </span>
                <span className="text-xs text-zinc-500">
                  {nearby.distance_from_medellin_km} km · {nearby.travel_time_approx}
                </span>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
