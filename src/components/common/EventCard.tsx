import React, { useState, useEffect } from 'react';
import { Bookmark, MapPin, Calendar, Clock } from 'lucide-react';
import { CulturalEvent } from '../../types';
import { PriceLabel } from './PriceLabel';
import { SourceBadge } from './SourceBadge';
import { isEventFavorited, toggleFavoriteEvent } from '../../services/favorites';
import { useViewTransition } from '../../context/TransitionContext';

interface EventCardProps {
  event: CulturalEvent;
  onSelect: (event: CulturalEvent) => void;
  userDistanceKm?: number;
  priority?: boolean;
}

const EventCardComponent: React.FC<EventCardProps> = ({
  event,
  onSelect,
  userDistanceKm,
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

  // Format date: "SÁB · 12 SEP"
  const formatDateBadge = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const weekday = d.toLocaleDateString('es-CO', { weekday: 'short' }).toUpperCase().replace('.', '');
    const monthName = d.toLocaleDateString('es-CO', { month: 'short' }).toUpperCase().replace('.', '');
    return `${weekday} · ${day} ${monthName}`;
  };

  return (
    <article
      className="group relative bg-white rounded-3xl overflow-hidden border border-zinc-200/80 shadow-xs hover:shadow-card transition-all duration-300 flex flex-col h-full select-none focus-within:ring-2 focus-within:ring-brand-500 content-visibility-auto"
      aria-label={`Evento: ${event.title}, en ${event.municipality}`}
    >
      {/* 16:9 Image container */}
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-sand-100">
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
          /* Elegant geometric fallback when image fails or is missing */
          <div
            className={`w-full h-full flex flex-col items-center justify-center p-4 bg-gradient-to-br from-sand-200 to-zinc-200 text-zinc-700 ${
              isTransitionTarget ? 'view-transition-hero' : ''
            }`}
          >
            <span className="text-xs uppercase tracking-widest font-bold text-zinc-500 mb-1">{event.category}</span>
            <span className="font-bold text-center text-sm line-clamp-2 px-2">{event.title}</span>
            <span className="text-xs text-zinc-500 mt-2">{event.municipality} · {formatDateBadge(event.start_date)}</span>
          </div>
        )}

        {/* Category Pill Tag on Image */}
        <div className="absolute top-3 left-3 pointer-events-none">
          <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-bold tracking-wide uppercase bg-black/60 backdrop-blur-md text-white border border-white/15">
            {event.category}
          </span>
        </div>

        {/* Favorite Bookmark Button - relative z-20 so it sits above stretched link */}
        <div className="absolute top-3 right-3 z-20">
          <button
            type="button"
            onClick={handleToggleFavorite}
            aria-label={isSaved ? `Quitar ${event.title} de guardados` : `Guardar ${event.title}`}
            className={`p-2 rounded-full backdrop-blur-md transition-all duration-200 active:scale-90 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center ${
              isSaved
                ? 'bg-brand-500 text-white shadow-md'
                : 'bg-black/50 text-white/90 hover:bg-black/70 hover:scale-105'
            }`}
          >
            <Bookmark className={`w-4 h-4 transition-transform duration-200 ${isSaved ? 'fill-current scale-110' : 'scale-100'}`} />
          </button>
        </div>

        {/* "Vale el viaje" badge if applicable */}
        {event.is_worth_the_trip && (
          <div className="absolute bottom-3 left-3 pointer-events-none">
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500 text-white shadow-sm">
              ★ Vale el viaje
            </span>
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="p-4 flex flex-col flex-1 justify-between gap-3">
        <div>
          {/* Date & Time */}
          <div className="flex items-center gap-2 text-xs font-bold text-brand-600 tracking-wide uppercase mb-1.5 pointer-events-none">
            <Calendar className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            <span>{formatDateBadge(event.start_date)}</span>
            <span className="text-zinc-300 font-normal">·</span>
            <span className="text-zinc-600 font-semibold normal-case flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-500" />
              {event.start_time}
            </span>
          </div>

          {/* Event Title with accessible stretched link */}
          <h3 className={`text-base sm:text-lg font-bold text-zinc-900 leading-snug line-clamp-2 ${
            isTransitionTarget ? 'view-transition-title' : ''
          }`}>
            <button
              type="button"
              onClick={() => onSelect(event)}
              className="after:absolute after:inset-0 text-left focus:outline-none focus-visible:underline group-hover:text-brand-600 transition-colors duration-200 cursor-pointer"
            >
              {event.title}
            </button>
          </h3>

          {/* Location: Municipality · Venue */}
          <div className="flex items-center gap-1.5 text-xs text-zinc-600 font-medium mt-1.5 pointer-events-none">
            <MapPin className="w-3.5 h-3.5 text-zinc-500 shrink-0" aria-hidden="true" />
            <span className="truncate">
              <strong className="text-zinc-800 font-semibold">{event.municipality}</strong> · {event.venue_name}
            </span>
            {typeof userDistanceKm === 'number' && (
              <span className="text-zinc-500 shrink-0">({userDistanceKm} km)</span>
            )}
          </div>

          {/* Luma Host / Organizer Info */}
          <div className="flex items-center gap-1.5 text-xs text-zinc-500 mt-1 pointer-events-none truncate">
            <span className="truncate">Por <span className="font-medium text-zinc-700">{event.organizer_name}</span></span>
          </div>
        </div>

        {/* Footer: Price & Source */}
        <div className="relative z-20 pt-2 border-t border-zinc-100 flex items-center justify-between gap-2 mt-auto">
          <PriceLabel priceType={event.price_type} priceFrom={event.price_from} priceTo={event.price_to} />
          <SourceBadge
            sourceName={event.source_name}
            sourceType={event.source_type}
            showIcon={true}
            className="max-w-[170px]"
          />
        </div>
      </div>
    </article>
  );
};

export const EventCard = React.memo(EventCardComponent);
