import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { CulturalEvent } from '../../types';
import { PriceLabel } from './PriceLabel';
import { MapPin, Calendar, ExternalLink, X } from 'lucide-react';

interface InteractiveMapProps {
  events: CulturalEvent[];
  selectedEvent?: CulturalEvent | null;
  onSelectEvent: (event: CulturalEvent) => void;
  className?: string;
  initialCenter?: [number, number];
  initialZoom?: number;
}

export const InteractiveMap: React.FC<InteractiveMapProps> = ({
  events,
  selectedEvent,
  onSelectEvent,
  className = 'h-[500px] w-full',
  initialCenter = [6.2442, -75.5812], // Center Antioquia / Medellín
  initialZoom = 9,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const [activePopupEvent, setActivePopupEvent] = useState<CulturalEvent | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return; // already initialized

    const map = L.map(mapContainerRef.current, {
      center: initialCenter,
      zoom: initialZoom,
      zoomControl: false,
    });

    // Clean, contemporary map tiles (CartoDB Positron / Voyager)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, OpenStreetMap',
      maxZoom: 18,
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update markers when events change
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    if (!map || !markersLayer) return;

    markersLayer.clearLayers();

    const bounds = L.latLngBounds([]);

    events.forEach((evt) => {
      if (!evt.latitude || !evt.longitude) return;

      const isSelected = selectedEvent?.event_id === evt.event_id;

      // Custom SVG marker pin
      const iconHtml = `
        <div style="
          background-color: ${isSelected ? '#942B12' : '#D94826'};
          color: white;
          padding: 6px 10px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 4px;
          box-shadow: 0 4px 14px rgba(217, 72, 38, 0.45);
          cursor: pointer;
          transform: ${isSelected ? 'scale(1.15)' : 'scale(1)'};
          transition: transform 0.2s ease;
          border: 2px solid white;
          white-space: nowrap;
        ">
          <span>${evt.municipality}</span>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-evenjoy-pin',
        iconSize: [80, 32],
        iconAnchor: [40, 16],
      });

      const marker = L.marker([evt.latitude, evt.longitude], { icon: customIcon });

      marker.on('click', () => {
        setActivePopupEvent(evt);
        onSelectEvent(evt);
      });

      markersLayer.addLayer(marker);
      bounds.extend([evt.latitude, evt.longitude]);
    });

    // Auto-fit bounds if multiple events exist
    if (events.length > 1 && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
    }
  }, [events, selectedEvent]);

  // Focus map when selectedEvent changes
  useEffect(() => {
    if (selectedEvent && mapInstanceRef.current && selectedEvent.latitude) {
      mapInstanceRef.current.setView(
        [selectedEvent.latitude, selectedEvent.longitude],
        13,
        { animate: true }
      );
      setActivePopupEvent(selectedEvent);
    }
  }, [selectedEvent]);

  return (
    <div className={`relative overflow-hidden rounded-2xl border border-zinc-200/80 shadow-card ${className}`}>
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Floating Mini-Card Preview when a pin is clicked (PRD Section 21) */}
      {activePopupEvent && (
        <div className="absolute bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-80 z-20 bg-white rounded-2xl p-3 shadow-sheet border border-zinc-200 animate-in slide-in-from-bottom-2 duration-200">
          <button
            type="button"
            onClick={() => setActivePopupEvent(null)}
            aria-label="Cerrar vista previa de evento"
            className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-zinc-900 text-white flex items-center justify-center shadow-md hover:bg-black cursor-pointer z-30"
          >
            <X className="w-3 h-3" />
          </button>
          <div className="flex gap-3">
            <img
              src={activePopupEvent.image_url}
              alt={activePopupEvent.title}
              className="w-20 h-20 rounded-xl object-cover shrink-0"
            />
            <div className="flex-1 min-w-0 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-1 text-[11px] font-bold text-brand-600 uppercase">
                  <span>{activePopupEvent.start_date}</span>
                  <PriceLabel priceType={activePopupEvent.price_type} priceFrom={activePopupEvent.price_from} className="text-[10px]" />
                </div>
                <h4 className="text-xs font-bold text-zinc-900 line-clamp-2 mt-0.5">
                  {activePopupEvent.title}
                </h4>
                <p className="text-[11px] text-zinc-500 truncate mt-0.5">
                  {activePopupEvent.municipality} · {activePopupEvent.venue_name}
                </p>
              </div>
              <button
                type="button"
                onClick={() => onSelectEvent(activePopupEvent)}
                className="mt-2 text-xs font-bold text-white bg-zinc-900 hover:bg-black py-1.5 px-3 rounded-lg flex items-center justify-center gap-1 cursor-pointer"
              >
                <span>Ver evento</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
