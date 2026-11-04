import React, { useEffect } from 'react';
import { 
  X, 
  Compass, 
  MapPin, 
  Sparkles, 
  Ticket, 
  Mountain, 
  Map as MapIcon, 
  Lock, 
  ArrowRight,
  Search
} from 'lucide-react';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onActionNearMe: () => void;
  onActionFreeEvents: () => void;
  onActionHeritageTowns: () => void;
  onActionOpenMap: () => void;
  onActionSearch: () => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onActionNearMe,
  onActionFreeEvents,
  onActionHeritageTowns,
  onActionOpenMap,
  onActionSearch,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
    >
      <div 
        className="bg-white w-full sm:max-w-xl rounded-t-3xl sm:rounded-3xl shadow-2xl border border-zinc-200/80 overflow-hidden flex flex-col max-h-[90vh] animate-in slide-in-from-bottom duration-300 ease-natural"
      >
        {/* Header with Visual Banner */}
        <div className="relative bg-gradient-to-br from-brand-600 via-brand-500 to-amber-700 text-white p-6 sm:p-8">
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar guía de bienvenida"
            className="absolute top-4 right-4 p-2 rounded-full bg-black/20 hover:bg-black/40 text-white/90 transition-colors cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-bold tracking-wider uppercase mb-3 border border-white/20">
            <Sparkles className="w-3.5 h-3.5 text-amber-200" />
            <span>Bienvenido a Evenjoy Antioquia</span>
          </div>

          <h2 id="onboarding-title" className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white leading-tight">
            Descubre qué hacer hoy en las montañas de Antioquia
          </h2>

          <p className="text-sm text-white/90 mt-2 max-w-md leading-relaxed">
            La cartelera cultural abierta de los 125 municipios. Festivales, teatro, música y patrimonio sin algoritmos ni registros obligatorios.
          </p>
        </div>

        {/* Interactive Quick Starters (Time to Value: 10s) */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-5">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-zinc-500 mb-3">
              Elige cómo prefieres comenzar:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {/* Option 1: Near Me */}
              <button
                type="button"
                onClick={() => {
                  onActionNearMe();
                  onClose();
                }}
                className="flex items-start gap-3 p-3.5 rounded-2xl border border-zinc-200 bg-sand-50/50 hover:bg-brand-50/40 hover:border-brand-300 text-left transition-all group cursor-pointer"
              >
                <div className="p-2 rounded-xl bg-brand-100 text-brand-700 group-hover:scale-105 transition-transform shrink-0">
                  <MapPin className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="block font-bold text-sm text-zinc-900 group-hover:text-brand-700">
                    Ver eventos cerca de mí
                  </span>
                  <span className="block text-xs text-zinc-500 mt-0.5 leading-snug">
                    Usa tu ubicación actual para ver eventos a tu alrededor.
                  </span>
                </div>
              </button>

              {/* Option 2: Free Events */}
              <button
                type="button"
                onClick={() => {
                  onActionFreeEvents();
                  onClose();
                }}
                className="flex items-start gap-3 p-3.5 rounded-2xl border border-zinc-200 bg-sand-50/50 hover:bg-forest-50/40 hover:border-forest-300 text-left transition-all group cursor-pointer"
              >
                <div className="p-2 rounded-xl bg-forest-100 text-forest-700 group-hover:scale-105 transition-transform shrink-0">
                  <Ticket className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="block font-bold text-sm text-zinc-900 group-hover:text-forest-700">
                    Ver eventos con entrada libre
                  </span>
                  <span className="block text-xs text-zinc-500 mt-0.5 leading-snug">
                    Plazas, casas de la cultura y conciertos abiertos.
                  </span>
                </div>
              </button>

              {/* Option 3: Heritage Towns */}
              <button
                type="button"
                onClick={() => {
                  onActionHeritageTowns();
                  onClose();
                }}
                className="flex items-start gap-3 p-3.5 rounded-2xl border border-zinc-200 bg-sand-50/50 hover:bg-amber-50/40 hover:border-amber-300 text-left transition-all group cursor-pointer"
              >
                <div className="p-2 rounded-xl bg-amber-100 text-amber-700 group-hover:scale-105 transition-transform shrink-0">
                  <Mountain className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="block font-bold text-sm text-zinc-900 group-hover:text-amber-800">
                    Explorar pueblos patrimoniales
                  </span>
                  <span className="block text-xs text-zinc-500 mt-0.5 leading-snug">
                    Jardín, Jericó, Guatapé, El Retiro y Sonsón.
                  </span>
                </div>
              </button>

              {/* Option 4: Interactive Map */}
              <button
                type="button"
                onClick={() => {
                  onActionOpenMap();
                  onClose();
                }}
                className="flex items-start gap-3 p-3.5 rounded-2xl border border-zinc-200 bg-sand-50/50 hover:bg-sky-50/40 hover:border-sky-300 text-left transition-all group cursor-pointer"
              >
                <div className="p-2 rounded-xl bg-sky-100 text-sky-700 group-hover:scale-105 transition-transform shrink-0">
                  <MapIcon className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="block font-bold text-sm text-zinc-900 group-hover:text-sky-700">
                    Ver mapa interactivo
                  </span>
                  <span className="block text-xs text-zinc-500 mt-0.5 leading-snug">
                    Ver todos los pines de eventos en el mapa de Antioquia.
                  </span>
                </div>
              </button>
            </div>
          </div>

          {/* Core Principles & Superpowers */}
          <div className="pt-2 border-t border-zinc-100 grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
            <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-sand-100/60">
              <Lock className="w-4 h-4 text-brand-600 mt-0.5 shrink-0" />
              <div>
                <span className="block text-xs font-bold text-zinc-900">Sin registros</span>
                <span className="block text-[11px] text-zinc-500 leading-tight">Guarda planes de forma 100% privada en tu navegador.</span>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-sand-100/60">
              <Compass className="w-4 h-4 text-brand-600 mt-0.5 shrink-0" />
              <div>
                <span className="block text-xs font-bold text-zinc-900">Fuentes oficiales</span>
                <span className="block text-[11px] text-zinc-500 leading-tight">Conectado a alcaldías, colectivos y casas de cultura.</span>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-sand-100/60">
              <Search className="w-4 h-4 text-brand-600 mt-0.5 shrink-0" />
              <div>
                <span className="block text-xs font-bold text-zinc-900">Tecla rápida</span>
                <span className="block text-[11px] text-zinc-500 leading-tight">Presiona <kbd className="px-1 py-0.5 bg-white rounded border text-[10px] font-mono">/</kbd> para buscar en cualquier pantalla.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 sm:p-5 bg-sand-50/80 border-t border-zinc-100 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onClose}
            className="text-xs font-semibold text-zinc-500 hover:text-zinc-800 transition-colors cursor-pointer py-2 px-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-lg"
          >
            Cerrar y explorar
          </button>

          <button
            type="button"
            onClick={() => {
              onActionSearch();
              onClose();
            }}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-zinc-900 hover:bg-black text-white text-xs font-bold transition-all shadow-sm cursor-pointer min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          >
            <span>Ir a la cartelera completa</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
