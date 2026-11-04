import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Calendar, 
  Clock, 
  MapPin, 
  Share2, 
  Bookmark, 
  ExternalLink, 
  ShieldCheck, 
  CalendarPlus, 
  Download, 
  AlertTriangle,
  Sparkles,
  Check,
  Building2,
  Navigation,
  Compass,
  Mountain
} from 'lucide-react';
import { CulturalEvent } from '../types';
import { MUNICIPALITIES } from '../data/municipalities';
import { PriceLabel } from '../components/common/PriceLabel';
import { SourceBadge } from '../components/common/SourceBadge';
import { EventCard } from '../components/common/EventCard';
import { LazyMap } from '../components/common/LazyMap';
import { isEventFavorited, toggleFavoriteEvent } from '../services/favorites';
import { generateGoogleCalendarUrl, downloadIcsFile } from '../services/calendar';

interface EventDetailViewProps {
  event: CulturalEvent;
  allEvents: CulturalEvent[];
  onBack: () => void;
  onSelectEvent: (event: CulturalEvent) => void;
  onSelectMunicipality: (muniSlug: string) => void;
}

export const EventDetailView: React.FC<EventDetailViewProps> = ({
  event,
  allEvents,
  onBack,
  onSelectEvent,
  onSelectMunicipality,
}) => {
  const [isSaved, setIsSaved] = useState(false);
  const [copiedToast, setCopiedToast] = useState(false);
  const [showCalendarMenu, setShowCalendarMenu] = useState(false);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    setIsSaved(isEventFavorited(event.event_id));
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Inject Schema.org / Event JSON-LD (PRD Section 34)
    const jsonLdData = {
      "@context": "https://schema.org",
      "@type": "Event",
      "name": event.title,
      "description": event.description,
      "startDate": `${event.start_date}T${event.start_time}:00-05:00`,
      "endDate": `${event.end_date || event.start_date}T${event.end_time || '23:00'}:00-05:00`,
      "eventStatus": event.status === 'ACTIVE' 
        ? "https://schema.org/EventScheduled" 
        : event.status === 'CANCELLED' 
        ? "https://schema.org/EventCancelled" 
        : "https://schema.org/EventPostponed",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "location": {
        "@type": "Place",
        "name": event.venue_name,
        "address": {
          "@type": "PostalAddress",
          "streetAddress": event.address,
          "addressLocality": event.municipality,
          "addressRegion": "Antioquia",
          "addressCountry": "CO"
        },
        "geo": {
          "@type": "GeoCoordinates",
          "latitude": event.latitude,
          "longitude": event.longitude
        }
      },
      "image": [event.image_url],
      "organizer": {
        "@type": "Organization",
        "name": event.organizer_name,
        "url": event.organizer_url || event.source_url
      },
      "offers": {
        "@type": "Offer",
        "price": event.price_from,
        "priceCurrency": "COP",
        "availability": "https://schema.org/InStock",
        "url": event.source_url
      }
    };

    let script = document.getElementById('json-ld-event') as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement('script');
      script.id = 'json-ld-event';
      script.type = 'application/ld+json';
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(jsonLdData);

    return () => {
      const el = document.getElementById('json-ld-event');
      if (el) el.remove();
    };
  }, [event]);

  const handleToggleFavorite = () => {
    const next = toggleFavoriteEvent(event.event_id);
    setIsSaved(next);
  };

  const handleShare = async () => {
    const shareData = {
      title: `${event.title} en ${event.municipality} | EVENJOY`,
      text: `¡Pilas a este plan en ${event.municipality}! ${event.title} (${event.start_date}). Conoce los detalles en Evenjoy:`,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        // user cancelled or share failed
      }
    } else {
      // Clipboard fallback
      navigator.clipboard.writeText(window.location.href);
      setCopiedToast(true);
      setTimeout(() => setCopiedToast(false), 3000);
    }
  };

  // Determine CTA label based on source and registration requirement (PRD Section 16)
  const getCtaLabel = () => {
    if (event.source_type === 'compensation_box') {
      return `Reservar en ${event.source_name.split('—')[0].trim()}`;
    }
    if (event.price_type === 'paid') {
      return 'Comprar entradas';
    }
    if (event.registration_required) {
      return 'Inscribirme en fuente oficial';
    }
    return 'Ver información oficial';
  };

  // Format full date in Colombian Spanish
  const formatFullDate = (dateStr: string) => {
    const [y, m, d] = dateStr.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString('es-CO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Related events algorithm (PRD Section 18)
  const relatedEvents = allEvents
    .filter(e => e.event_id !== event.event_id)
    .sort((a, b) => {
      let scoreA = 0;
      let scoreB = 0;
      if (a.municipality === event.municipality) scoreA += 4;
      if (b.municipality === event.municipality) scoreB += 4;
      if (a.category === event.category) scoreA += 3;
      if (b.category === event.category) scoreB += 3;
      if (a.subregion === event.subregion) scoreA += 2;
      if (b.subregion === event.subregion) scoreB += 2;
      return scoreB - scoreA;
    })
    .slice(0, 3);

  const muniData = MUNICIPALITIES.find(
    m => m.name.toLowerCase() === event.municipality.toLowerCase() || m.slug === event.municipality.toLowerCase()
  );

  return (
    <div className="pb-28">
      {/* Toast notification */}
      {copiedToast && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-zinc-900 text-white px-4 py-2 rounded-full text-xs font-bold shadow-lg flex items-center gap-1.5 animate-in fade-in">
          <Check className="w-3.5 h-3.5 text-forest-200" />
          <span>¡Enlace copiado! Compártelo con quien quieras viajar.</span>
        </div>
      )}

      {/* Breadcrumb & Navigation */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 px-safe pt-6 pb-4 no-print">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-bold text-zinc-600 hover:text-zinc-900 transition-colors py-2 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Volver a la cartelera</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => window.print()}
              className="p-2 rounded-full border border-zinc-200 bg-white hover:bg-zinc-50 text-zinc-700 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center shadow-xs transition-colors"
              aria-label="Imprimir ficha de ruta o guardar como PDF"
              title="Imprimir o guardar en PDF para viajar sin señal"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="6 9 6 2 18 2 18 9"></polyline>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                <rect x="6" y="14" width="12" height="8"></rect>
              </svg>
            </button>
            <button
              type="button"
              onClick={handleShare}
              className="p-2 rounded-full border border-zinc-200 bg-white hover:bg-zinc-50 text-zinc-700 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center shadow-xs"
              aria-label="Compartir este evento"
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleToggleFavorite}
              className={`p-2 rounded-full border border-zinc-200 bg-white hover:bg-zinc-50 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center shadow-xs transition-colors ${
                isSaved ? 'text-brand-500 fill-brand-500' : 'text-zinc-700'
              }`}
              aria-label={isSaved ? 'Quitar de guardados' : 'Guardar evento'}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Container - Luma Style Simplicity */}
      <article className="max-w-4xl mx-auto px-4 sm:px-6 px-safe space-y-8 print:space-y-4">
        {/* Printable Itinerary Header - Visible ONLY when printing (Zero Cellular Dead Zones) */}
        <div className="hidden print:block border-b-2 border-zinc-900 pb-4 mb-4">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black text-xl tracking-tight text-zinc-900">EVENJOY ANTIOQUIA</span>
                <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 bg-zinc-100 rounded text-zinc-700 border border-zinc-300">
                  Ficha de Ruta Cultural
                </span>
              </div>
              <p className="text-xs text-zinc-500 mt-1">
                Itinerario impreso para viaje de campo sin señal celular · Generado el {new Date().toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })}
              </p>
            </div>
            <div className="text-right">
              <span className="text-sm font-black text-brand-700 uppercase block">{event.municipality}</span>
              <span className="text-xs text-zinc-600 block">Subregión {event.subregion}</span>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-3 gap-3 p-3 bg-zinc-50 border border-zinc-200 rounded-lg text-xs">
            <div>
              <span className="text-zinc-500 block font-semibold">📍 Recinto & Dirección:</span>
              <span className="font-bold text-zinc-900 block">{event.venue_name}</span>
              <span className="block text-zinc-600">{event.address}</span>
            </div>
            <div>
              <span className="text-zinc-500 block font-semibold">🗓️ Fecha y Horario:</span>
              <span className="font-bold text-zinc-900 block">{formatFullDate(event.start_date)}</span>
              <span className="block text-zinc-600">{event.start_time} {event.end_time ? `a ${event.end_time}` : ''}</span>
            </div>
            <div>
              <span className="text-zinc-500 block font-semibold">🌐 Coordenadas GPS:</span>
              <span className="font-mono text-zinc-900 block">{event.latitude.toFixed(4)}, {event.longitude.toFixed(4)}</span>
              <span className="block text-zinc-600 font-semibold">{muniData?.distance_from_medellin_km ? `${muniData.distance_from_medellin_km} km de Medellín (~${muniData.travel_time_approx})` : 'Antioquia'}</span>
            </div>
          </div>
        </div>

        {/* Hero Poster */}
        <div className="relative rounded-3xl overflow-hidden aspect-[16/9] shadow-md border border-zinc-200/80 bg-zinc-900">
          {!imageError ? (
            <img
              src={event.image_url}
              alt={event.title}
              onError={() => setImageError(true)}
              className="w-full h-full object-cover view-transition-hero"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-6 bg-gradient-to-br from-sand-200 via-zinc-200 to-sand-100 text-zinc-700 text-center view-transition-hero">
              <span className="text-xs uppercase tracking-widest font-bold text-zinc-500 mb-2">{event.category}</span>
              <span className="text-xl sm:text-2xl font-black max-w-lg">{event.title}</span>
              <span className="text-xs sm:text-sm text-zinc-600 mt-2 font-medium">{event.municipality}, Antioquia</span>
            </div>
          )}
          {/* Top badges overlay */}
          <div className="absolute top-4 left-4 flex gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-black/60 backdrop-blur-md text-white border border-white/20">
              {event.category}
            </span>
            {event.status === 'CANCELLED' && (
              <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-red-600 text-white">
                Cancelado
              </span>
            )}
          </div>
        </div>

        {/* Title and High-Level Context */}
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => onSelectMunicipality(event.municipality.toLowerCase())}
              className="text-xs sm:text-sm font-bold text-brand-600 hover:underline uppercase tracking-wide cursor-pointer"
            >
              {event.municipality}, Antioquia
            </button>
            <span className="text-zinc-300">·</span>
            <span className="text-xs text-zinc-500 font-semibold">{event.subregion}</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-zinc-900 tracking-tight leading-tight view-transition-title">
            {event.title}
          </h1>

          <p className="text-base sm:text-lg text-zinc-600 leading-relaxed font-normal">
            {event.short_description}
          </p>
        </div>

        {/* Metadata Cards Grid (Luma style clean block cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Card 1: Fecha y Hora */}
          <div className="bg-white rounded-2xl p-5 border border-zinc-200/80 shadow-xs flex flex-col justify-between space-y-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-brand-50 text-brand-600 shrink-0">
                <Calendar className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <span className="block text-xs font-bold text-zinc-500 uppercase tracking-wider">
                  Cuándo
                </span>
                <span className="block text-sm sm:text-base font-bold text-zinc-900 capitalize mt-0.5">
                  {formatFullDate(event.start_date)}
                </span>
                <span className="block text-xs text-zinc-600 font-medium mt-0.5">
                  {event.start_time} {event.end_time ? `a ${event.end_time}` : ''} (Hora Colombia)
                </span>
              </div>
            </div>

            {/* Calendar actions */}
            <div className="pt-3 border-t border-zinc-100 flex items-center gap-2">
              <a
                href={generateGoogleCalendarUrl(event)}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Agregar este evento a Google Calendar"
                className="flex-1 text-center py-2 px-3 rounded-xl border border-zinc-200 text-xs font-bold text-zinc-700 hover:bg-zinc-50 transition-colors flex items-center justify-center gap-1.5 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              >
                <CalendarPlus className="w-3.5 h-3.5 text-zinc-500" />
                <span>Google Calendar</span>
              </a>
              <button
                type="button"
                onClick={() => downloadIcsFile(event)}
                className="py-2 px-3 rounded-xl border border-zinc-200 text-xs font-bold text-zinc-700 hover:bg-zinc-50 transition-colors flex items-center justify-center gap-1.5 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                title="Descargar archivo de calendario (.ics) para Apple Calendar u Outlook"
                aria-label="Descargar archivo de calendario (.ics) para Apple Calendar u Outlook"
              >
                <Download className="w-3.5 h-3.5 text-zinc-500" />
                <span>Apple / Outlook</span>
              </button>
            </div>
          </div>

          {/* Card 2: Ubicación y Recinto */}
          <div className="bg-white rounded-2xl p-5 border border-zinc-200/80 shadow-xs flex flex-col justify-between space-y-4">
            <div className="flex items-start gap-3.5">
              <div className="p-2.5 rounded-xl bg-forest-50 text-forest-700 shrink-0">
                <MapPin className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <span className="block text-xs font-bold text-zinc-500 uppercase tracking-wider">
                  Dónde
                </span>
                <span className="block text-sm sm:text-base font-bold text-zinc-900 mt-0.5">
                  {event.venue_name}
                </span>
                <span className="block text-xs text-zinc-500 font-medium truncate mt-0.5">
                  {event.address}
                </span>
                <span className="block text-xs text-brand-600 font-semibold mt-0.5">
                  {event.municipality} ({event.subregion})
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-zinc-100 flex items-center justify-between text-xs">
              <PriceLabel priceType={event.price_type} priceFrom={event.price_from} priceTo={event.price_to} />
              <span className="text-zinc-500 font-medium">
                {event.event_format === 'outdoor' ? 'Al aire libre' : 'Recinto cerrado'}
              </span>
            </div>
          </div>
        </div>

        {/* Considered Local Travel & Heritage Tip */}
        {muniData && (
          <div className="p-4 sm:p-5 rounded-2xl bg-white border border-zinc-200/80 shadow-xs flex items-start gap-3.5">
            <div className="p-2.5 rounded-xl bg-forest-50 text-forest-700 shrink-0 mt-0.5">
              <Compass className="w-5 h-5" />
            </div>
            <div className="min-w-0 space-y-1 text-left">
              <span className="block text-xs font-bold uppercase tracking-wider text-zinc-500">
                Viajar a {muniData.name} ({muniData.subregion})
              </span>
              <p className="text-xs sm:text-sm text-zinc-700 leading-relaxed font-medium tabular-nums">
                {muniData.distance_from_medellin_km} km desde Medellín · Aprox. {muniData.travel_time_approx} en carretera · {muniData.altitude_m} msnm · {muniData.climate}
              </p>
              <p className="text-xs text-zinc-500 italic">
                Identidad local: {muniData.signature_tradition}.
              </p>
            </div>
          </div>
        )}

        {/* Outbound Official CTA Block (Distilled Luma style) */}
        <div className="p-6 sm:p-7 rounded-3xl bg-sand-100/80 border border-zinc-200/80 text-center space-y-3">
          <a
            href={event.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white text-base font-bold shadow-sm transition-all cursor-pointer min-h-[48px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          >
            <span>{getCtaLabel()}</span>
            <ExternalLink className="w-4 h-4" />
          </a>

          <p className="text-xs text-zinc-500 flex items-center justify-center gap-1.5 font-medium">
            <ShieldCheck className="w-4 h-4 text-forest-700 shrink-0" />
            <span>Enlace directo al sitio oficial de <strong>{event.source_name}</strong> · Sin intermediarios</span>
          </p>
        </div>

        {/* Description and Editorial Details */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-zinc-200/80 shadow-xs space-y-6">
          <div>
            <h2 className="text-lg font-bold text-zinc-900 mb-3">
              Acerca de esta actividad
            </h2>
            <div className="prose max-w-prose text-sm sm:text-base text-zinc-700 leading-relaxed space-y-4">
              {event.description.split('\n\n').map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          </div>

          {/* Tags */}
          {event.tags && event.tags.length > 0 && (
            <div className="pt-4 border-t border-zinc-100">
              <span className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2">
                Temas y Etiquetas
              </span>
              <div className="flex flex-wrap gap-1.5">
                {event.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-sand-100 text-zinc-700"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Host / Organizer profile */}
          <div className="pt-4 border-t border-zinc-100 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-sand-200 flex items-center justify-center text-zinc-700 font-bold text-sm">
                <Building2 className="w-5 h-5 text-zinc-600" />
              </div>
              <div>
                <span className="block text-xs text-zinc-500 font-bold uppercase">Organiza</span>
                <span className="block text-sm font-bold text-zinc-900">{event.organizer_name}</span>
              </div>
            </div>
            {event.organizer_url && (
              <a
                href={event.organizer_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-bold text-brand-600 hover:underline"
              >
                Sitio web
              </a>
            )}
          </div>
        </div>

        {/* Mini Venue Map */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-zinc-900">Ubicación en el mapa</h3>
              <p className="text-xs text-zinc-500">{event.venue_name}, {event.municipality}</p>
            </div>
          </div>
          <LazyMap
            events={[event]}
            selectedEvent={event}
            onSelectEvent={() => {}}
            className="h-64 w-full"
            initialCenter={[event.latitude, event.longitude]}
            initialZoom={14}
          />
        </div>

        {/* Verification Metadata & Secondary Sources (PRD Section 4 & 5) */}
        <div className="bg-sand-50 rounded-2xl p-4 border border-zinc-200/80 text-xs text-zinc-500 space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="flex items-center gap-1.5 font-medium text-zinc-700">
              <ShieldCheck className="w-4 h-4 text-forest-700" />
              Información verificada por Evenjoy el {event.last_verified_at.split('T')[0]}
            </span>
            <span className="text-zinc-500">ID: {event.event_id}</span>
          </div>

          {event.secondary_sources && event.secondary_sources.length > 0 && (
            <div className="pt-2 border-t border-zinc-200/60 text-[11px]">
              <span className="font-semibold text-zinc-600">Otras fuentes detectadas para este evento:</span>
              <ul className="mt-1 space-y-0.5">
                {event.secondary_sources.map((s, idx) => (
                  <li key={idx} className="flex items-center gap-1">
                    <span>· {s.source_name}</span>
                    <a
                      href={s.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:underline inline-flex items-center gap-0.5"
                    >
                      (enlace) <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* PRD Section 18: Related Events */}
        {relatedEvents.length > 0 && (
          <div className="pt-8 border-t border-zinc-200 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-brand-600">
                  Descubre más
                </span>
                <h3 className="text-xl font-black text-zinc-900">
                  También podría gustarte
                </h3>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {relatedEvents.map((rel) => (
                <EventCard
                  key={rel.event_id}
                  event={rel}
                  onSelect={onSelectEvent}
                />
              ))}
            </div>
          </div>
        )}
      </article>

      {/* PRD Section 17: Mobile Sticky CTA with safe-area support */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-zinc-200/90 px-4 px-safe py-3 pb-safe shadow-sheet flex items-center justify-between gap-3 no-print">
        <div>
          <span className="text-[10px] font-bold text-zinc-500 uppercase block">Precio</span>
          <PriceLabel priceType={event.price_type} priceFrom={event.price_from} priceTo={event.price_to} />
        </div>
        <a
          href={event.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 py-3 px-5 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-bold text-center shadow-md flex items-center justify-center gap-1.5 cursor-pointer min-h-[48px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-500"
        >
          <span>{getCtaLabel()}</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
