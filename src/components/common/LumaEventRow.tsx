import React, { useState, useEffect } from 'react';
import { Bookmark, MapPin, Calendar, Clock, ChevronRight, ShieldCheck, Sparkles, Building2 } from 'lucide-react';
import { CulturalEvent } from '../../types';
import { PriceLabel } from './PriceLabel';
import { isEventFavorited, toggleFavoriteEvent } from '../../services/favorites';
import { useViewTransition } from '../../context/TransitionContext';

interface LumaEventRowProps {
  event: CulturalEvent;
  onSelect: (event: CulturalEvent) => void;
  priority?: boolean;
}

const LumaEventRowComponent: React.FC<LumaEventRowProps> = ({
  event,
  onSelect,
  priority = false,
}) => {
  const [isSaved, setIsSaved] = useState(false);
  const [imageError, setImageError] = useState(false);
  const { activeTransitionSlug } = useViewTransition();
  const isTransitionTarget = activeTransitionSlug === event.slug;

  useEffect(() => {
    setIsSaved(isEventFavorited(event.event_id));

    const handleFavChange = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail && customEvent.detail.eventId === event.event_id) {
        setIsSaved(customEvent.detail.added);
      }
    };

    window.addEventListener('evenjoy-favorites-changed', handleFavChange);
    return () => window.removeEventListener('evenjoy-favorites-changed', handleFavChange);
  }, [event.event_id]);

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    const state = toggleFavoriteEvent(event.event_id);
    setIsSaved(state);
  };

  // Format date: "SÁB, 12 SEP"
  const formatDateBadge = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const weekday = d.toLocaleDateString('es-CO', { weekday: 'short' }).toUpperCase().replace('.', '');
    const monthName = d.toLocaleDateString('es-CO', { month: 'short' }).toUpperCase().replace('.', '');
    return `${weekday}, ${day} ${monthName}`;
  };

  return (
    <article
      className="group relative bg-white hover:bg-zinc-50/80 rounded-2xl sm:rounded-3xl p-3 sm:p-4 border border-zinc-200/80 hover:border-zinc-300 shadow-2xs hover:shadow-xs transition-all duration-300 flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 sm:gap-5 select-none focus-within:ring-2 focus-within:ring-brand-500 content-visibility-auto"
      aria-label={`Evento: ${event.title}, en ${event.municipality}`}
    >
      {/* Thumbnail Poster (16:10 aspect, Luma rounded frame) */}
      <div className="relative w-full sm:w-44 md:w-52 aspect-[16/10] sm:aspect-[16/10] rounded-xl sm:rounded-2xl overflow-hidden shrink-0 bg-sand-100 border border-zinc-200/60 pointer-events-none">
        {!imageError ? (
          <img
            src={event.image_url}
            alt={`Afiche de ${event.title}`}
            loading={priority ? 'eager' : 'lazy'}
            decoding="async"
            fetchPriority={priority ? 'high' : 'auto'}
            onError={() => setImageError(true)}
            className={`w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out ${
              isTransitionTarget ? 'view-transition-hero' : ''
            }`}
          />
        ) : (
          <div
            className={`w-full h-full flex flex-col items-center justify-center p-3 bg-gradient-to-br from-sand-200 to-zinc-200 text-zinc-700 text-center ${
              isTransitionTarget ? 'view-transition-hero' : ''
            }`}
          >
            <span className="text-[10px] uppercase tracking-widest font-bold text-zinc-500">{event.category}</span>
            <span className="font-bold text-xs line-clamp-1 mt-1">{event.title}</span>
            <span className="text-[10px] text-zinc-500 mt-1">{event.municipality}</span>
          </div>
        )}

        {/* Category Pill Tag floating on poster */}
        <div className="absolute top-2.5 left-2.5">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-black/60 backdrop-blur-md text-white border border-white/15">
            {event.category}
          </span>
        </div>

        {/* "Vale el viaje" pill if applicable */}
        {event.is_worth_the_trip && (
          <div className="absolute bottom-2.5 left-2.5">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500 text-white shadow-xs">
              <Sparkles className="w-2.5 h-2.5" />
              <span>Vale el viaje</span>
            </span>
          </div>
        )}
      </div>

      {/* Main Content Area (Luma typography & metadata hierarchy) */}
      <div className="flex-1 min-w-0 flex flex-col justify-between h-full py-0.5">
        <div>
          {/* Top Line: Date, Time & Status */}
          <div className="flex items-center gap-2 text-xs font-bold text-brand-600 tracking-wide uppercase mb-1 pointer-events-none">
            <Calendar className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            <span>{formatDateBadge(event.start_date)}</span>
            <span className="text-zinc-300 font-normal">·</span>
            <span className="text-zinc-600 font-semibold normal-case flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-400" />
              {event.start_time}
            </span>
            {event.price_type === 'free' && (
              <span className="hidden sm:inline-flex px-2 py-0.2 rounded-full text-[10px] font-bold bg-forest-50 text-forest-700 border border-forest-200">
                Entrada libre
              </span>
            )}
          </div>

          {/* Event Title with accessible stretched link */}
          <h3
            className={`text-base sm:text-lg font-bold text-zinc-900 leading-snug line-clamp-1 sm:line-clamp-2 ${
              isTransitionTarget ? 'view-transition-title' : ''
            }`}
          >
            <button
              type="button"
              onClick={() => onSelect(event)}
              className="after:absolute after:inset-0 text-left focus:outline-none focus-visible:underline group-hover:text-brand-600 transition-colors cursor-pointer"
            >
              {event.title}
            </button>
          </h3>

          {/* Location & Territory */}
          <div className="flex items-center gap-1.5 text-xs text-zinc-500 mt-1 truncate pointer-events-none">
            <MapPin className="w-3.5 h-3.5 shrink-0 text-zinc-400" />
            <span className="font-semibold text-zinc-800">{event.venue_name}</span>
            <span className="text-zinc-300">·</span>
            <span>{event.municipality}, Antioquia ({event.subregion})</span>
          </div>

          {/* Organizer / Host info (Luma's signature "Hosted by" line) */}
          <div className="flex items-center gap-2 mt-2.5 pt-2 border-t border-zinc-100 text-xs text-zinc-600 pointer-events-none">
            <div className="w-5 h-5 rounded-full bg-sand-200 text-zinc-700 flex items-center justify-center shrink-0">
              <Building2 className="w-3 h-3" />
            </div>
            <span className="truncate">
              Por <strong className="font-semibold text-zinc-800">{event.organizer_name}</strong>
            </span>
            {event.source_type === 'government' && (
              <span className="hidden md:inline-flex items-center gap-0.5 text-[11px] text-forest-700 font-semibold shrink-0">
                <ShieldCheck className="w-3 h-3 text-forest-600" />
                Oficial
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right Side: Price, Save Button & Arrow CTA */}
      <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-3 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-zinc-100 relative z-20">
        <PriceLabel priceType={event.price_type} priceFrom={event.price_from} priceTo={event.price_to} />

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={handleToggleFavorite}
            aria-label={isSaved ? `Quitar ${event.title} de guardados` : `Guardar ${event.title}`}
            className={`p-2.5 rounded-full transition-all duration-200 active:scale-90 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center ${
              isSaved
                ? 'bg-brand-50 text-brand-600 border border-brand-200'
                : 'bg-zinc-100 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200/70'
            }`}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>

          <div
            className="w-9 h-9 rounded-full bg-zinc-100 group-hover:bg-zinc-900 group-hover:text-white text-zinc-500 flex items-center justify-center transition-all duration-200 pointer-events-none hidden sm:flex shrink-0"
            aria-hidden="true"
          >
            <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </div>
        </div>
      </div>
    </article>
  );
};

export const LumaEventRow = React.memo(LumaEventRowComponent);
