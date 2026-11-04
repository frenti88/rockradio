import React, { useState, useEffect } from 'react';
import { Bookmark, ArrowLeft, Trash2, Sparkles, Compass } from 'lucide-react';
import { CulturalEvent } from '../types';
import { EventCard } from '../components/common/EventCard';
import { getFavoriteEventIds } from '../services/favorites';

interface SavedEventsViewProps {
  allEvents: CulturalEvent[];
  onSelectEvent: (event: CulturalEvent) => void;
  onNavigateHome: () => void;
  onNavigateExplore: () => void;
}

export const SavedEventsView: React.FC<SavedEventsViewProps> = ({
  allEvents,
  onSelectEvent,
  onNavigateHome,
  onNavigateExplore,
}) => {
  const [savedIds, setSavedIds] = useState<string[]>([]);

  useEffect(() => {
    setSavedIds(getFavoriteEventIds());

    const handleFavChange = () => {
      setSavedIds(getFavoriteEventIds());
    };
    window.addEventListener('evenjoy-favorites-changed', handleFavChange);
    return () => window.removeEventListener('evenjoy-favorites-changed', handleFavChange);
  }, []);

  const savedEvents = allEvents.filter(e => savedIds.includes(e.event_id));

  const handleClearAll = () => {
    const count = savedEvents.length;
    const confirmMessage = count === 1
      ? '¿Deseas vaciar tu plan cultural guardado? Se quitará de la memoria de tu dispositivo.'
      : `¿Deseas vaciar tus ${count} planes culturales guardados? Se quitarán de la memoria de tu dispositivo.`;

    if (window.confirm(confirmMessage)) {
      localStorage.removeItem('evenjoy_saved_events_v1');
      window.dispatchEvent(new CustomEvent('evenjoy-favorites-changed'));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-200 pb-4">
        <div>
          <button
            type="button"
            onClick={onNavigateHome}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-zinc-500 hover:text-zinc-900 mb-2 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-md py-1 px-1 -ml-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Volver al inicio</span>
          </button>
          <h1 className="text-2xl sm:text-3xl font-black text-zinc-900 flex items-center gap-2.5">
            <Bookmark className="w-7 h-7 text-brand-500 fill-brand-500" />
            <span>Tus Planes Guardados</span>
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500 mt-1">
            Guardados de forma privada en este dispositivo, sin cuentas ni contraseñas.
          </p>
        </div>

        {savedEvents.length > 0 && (
          <button
            type="button"
            onClick={handleClearAll}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-red-700 hover:text-red-800 transition-colors px-3 py-2 rounded-xl bg-red-50/70 hover:bg-red-100 border border-red-200/60 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
          >
            <Trash2 className="w-4 h-4 text-red-600" />
            <span>Vaciar guardados</span>
          </button>
        )}
      </div>

      {/* Content */}
      {savedEvents.length > 0 ? (
        <div className="space-y-6">
          <div className="p-4 rounded-2xl bg-sand-100/70 border border-zinc-200/70 flex items-center justify-between gap-3 text-xs sm:text-sm text-zinc-700">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-forest-500" />
              <span>
                Tienes <strong className="font-bold text-zinc-900">{savedEvents.length}</strong> {savedEvents.length === 1 ? 'plan seleccionado' : 'planes seleccionados'} en tu agenda cultural privada.
              </span>
            </div>
            <span className="text-zinc-500 text-xs hidden sm:inline font-medium">
              ¡Buen viaje por los caminos de Antioquia!
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedEvents.map((evt) => (
              <EventCard
                key={evt.event_id}
                event={evt}
                onSelect={onSelectEvent}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-20 px-4 bg-white rounded-3xl border border-zinc-200/80 max-w-lg mx-auto shadow-xs">
          <div className="w-16 h-16 rounded-full bg-sand-100 text-brand-500/70 mx-auto flex items-center justify-center mb-4">
            <Bookmark className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-zinc-900">
            Tu morral cultural está vacío
          </h2>
          <p className="text-sm text-zinc-500 mt-2 leading-relaxed max-w-sm mx-auto">
            Guarda conciertos, teatro y ferias con un clic. No necesitas cuenta ni contraseñas: tus favoritos se conservan en tu dispositivo para que armes tu escapada de fin de semana.
          </p>
          <button
            type="button"
            onClick={onNavigateExplore}
            className="mt-6 inline-flex items-center gap-2 px-6 py-3 rounded-full bg-zinc-900 text-white text-xs font-bold hover:bg-black transition-all cursor-pointer shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
          >
            <Compass className="w-4 h-4" />
            <span>Explorar planes en Antioquia</span>
          </button>
        </div>
      )}
    </div>
  );
};
