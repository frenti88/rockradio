import React, { Suspense, lazy } from 'react';
import { CulturalEvent } from '../../types';
import { MapPin } from 'lucide-react';

// Code-split Leaflet and InteractiveMap so they don't block initial page load
const InteractiveMapComponent = lazy(() =>
  import('./InteractiveMap').then((m) => ({ default: m.InteractiveMap }))
);

interface LazyMapProps {
  events: CulturalEvent[];
  selectedEvent?: CulturalEvent | null;
  onSelectEvent: (event: CulturalEvent) => void;
  className?: string;
  initialCenter?: [number, number];
  initialZoom?: number;
}

export const LazyMap: React.FC<LazyMapProps> = (props) => {
  return (
    <Suspense
      fallback={
        <div
          className={`flex flex-col items-center justify-center bg-sand-100/70 border border-zinc-200/80 rounded-2xl animate-pulse text-zinc-500 gap-3 ${
            props.className || 'h-[500px] w-full'
          }`}
          aria-label="Cargando mapa interactivo de eventos en Antioquia..."
          role="status"
        >
          <div className="w-10 h-10 rounded-full bg-sand-200 flex items-center justify-center text-brand-600">
            <MapPin className="w-5 h-5 animate-bounce" />
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-zinc-600">
            Cargando mapa interactivo...
          </span>
        </div>
      }
    >
      <InteractiveMapComponent {...props} />
    </Suspense>
  );
};
