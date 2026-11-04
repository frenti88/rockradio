import React, { useState, useEffect } from 'react';
import { Bookmark, MapPin, Calendar } from 'lucide-react';
import { CulturalEvent } from '../../types';
import { PriceLabel } from './PriceLabel';
import { SourceBadge } from './SourceBadge';
import { isEventFavorited, toggleFavoriteEvent } from '../../services/favorites';
import { useViewTransition } from '../../context/TransitionContext';

interface EventCardCompactProps {
  event: CulturalEvent;
  onSelect: (event: CulturalEvent) => void;
  isHovered?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

const EventCardCompactComponent: React.FC<EventCardCompactProps> = ({
  event,
  onSelect,
  isHovered = false,
  onMouseEnter,
  onMouseLeave,
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

  const formatDateShort = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const weekday = d.toLocaleDateString('es-CO', { weekday: 'short' }).toUpperCase().replace('.', '');
    const monthName = d.toLocaleDateString('es-CO', { month: 'short' }).toUpperCase().replace('.', '');
    return `${weekday} ${day} ${monthName}`;
  };

  return (
    <article
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={`group relative bg-white rounded-xl p-3 border transition-all duration-200 flex gap-3.5 items-center select-none focus-within:ring-2 focus-within:ring-brand-500 content-visibility-auto ${
        isHovered
          ? 'border-brand-500 shadow-md ring-1 ring-brand-500'
          : 'border-zinc-200/80 hover:border-zinc-300 hover:shadow-card'
      }`}
      aria-label={`Evento: ${event.title}, en ${event.municipality}`}
    >
      {/* Thumbnail 1:1 or 4:3 with error fallback */}
      <div className="relative w-24 h-24 sm:w-28 sm:h-28 rounded-lg overflow-hidden shrink-0 bg-sand-100 pointer-events-none">
        {!imageError ? (
          <img
            src={event.image_url}
            alt={event.title}
            loading="lazy"
            decoding="async"
            onError={() => setImageError(true)}
            className={`w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 ${
              isTransitionTarget ? 'view-transition-hero' : ''
            }`}
          />
        ) : (
          <div
            className={`w-full h-full flex flex-col items-center justify-center p-2 bg-gradient-to-br from-sand-200 to-zinc-200 text-zinc-600 text-center ${
              isTransitionTarget ? 'view-transition-hero' : ''
            }`}
          >
            <span className="text-[10px] uppercase tracking-wider font-bold text-zinc-500">{event.category}</span>
            <span className="text-[11px] font-bold line-clamp-2 mt-0.5">{event.title}</span>
          </div>
        )}
        <div className="absolute top-1.5 left-1.5">
          <span className="inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-black/60 text-white">
            {event.category}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 flex flex-col justify-between h-full py-0.5">
        <div>
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-bold text-brand-600 uppercase flex items-center gap-1 pointer-events-none">
              <Calendar className="w-3 h-3" />
              {formatDateShort(event.start_date)} · {event.start_time}
            </span>
            <div className="relative z-20">
              <button
                type="button"
                onClick={handleToggleFavorite}
                aria-label={isSaved ? `Quitar ${event.title} de guardados` : `Guardar ${event.title}`}
                className="min-h-[44px] min-w-[44px] -mr-2 -mt-1 flex items-center justify-center text-zinc-500 hover:text-brand-500 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-full"
              >
                <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-brand-500 text-brand-500' : ''}`} />
              </button>
            </div>
          </div>

          <h4 className={`text-sm font-bold text-zinc-900 line-clamp-2 mt-1 ${
            isTransitionTarget ? 'view-transition-title' : ''
          }`}>
            <button
              type="button"
              onClick={() => onSelect(event)}
              className="after:absolute after:inset-0 text-left focus:outline-none focus-visible:underline group-hover:text-brand-600 transition-colors cursor-pointer"
            >
              {event.title}
            </button>
          </h4>

          <div className="flex items-center gap-1 text-xs text-zinc-600 mt-1 truncate pointer-events-none">
            <MapPin className="w-3 h-3 shrink-0 text-zinc-500" />
            <span className="truncate"><strong className="text-zinc-800">{event.municipality}</strong> · {event.venue_name}</span>
          </div>
        </div>

        <div className="relative z-20 flex items-center justify-between gap-2 mt-2 pt-2 border-t border-zinc-100">
          <PriceLabel priceType={event.price_type} priceFrom={event.price_from} priceTo={event.price_to} />
          <SourceBadge
            sourceName={event.source_name}
            sourceType={event.source_type}
            showIcon={false}
            className="text-[11px] max-w-[140px]"
          />
        </div>
      </div>
    </article>
  );
};

export const EventCardCompact = React.memo(EventCardCompactComponent);
