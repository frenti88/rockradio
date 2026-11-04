import React, { useState, useEffect } from 'react';
import { MapPin, Search, Bookmark, ChevronDown, HelpCircle, Compass, Map } from 'lucide-react';
import { getFavoriteEventIds } from '../../services/favorites';
import { Subregion } from '../../types';

interface HeaderProps {
  currentMunicipality: string | 'all';
  currentSubregion: Subregion | 'all';
  onOpenLocationModal: () => void;
  onNavigateSearch: () => void;
  onNavigateHome: () => void;
  onNavigateSaved: () => void;
  onNavigateMap?: () => void;
  activeTab?: 'explorar' | 'buscar' | 'mapa' | 'guardados';
  onOpenOnboarding?: () => void;
  savedCount?: number;
}

export const Header: React.FC<HeaderProps> = ({
  currentMunicipality,
  currentSubregion,
  onOpenLocationModal,
  onNavigateSearch,
  onNavigateHome,
  onNavigateSaved,
  onNavigateMap,
  activeTab,
  onOpenOnboarding,
  savedCount: propSavedCount,
}) => {
  const [savedCount, setSavedCount] = useState(propSavedCount ?? 0);

  useEffect(() => {
    setSavedCount(getFavoriteEventIds().length);
    const handleFav = () => {
      setSavedCount(getFavoriteEventIds().length);
    };
    window.addEventListener('evenjoy-favorites-changed', handleFav);
    return () => window.removeEventListener('evenjoy-favorites-changed', handleFav);
  }, []);

  const getLocationLabel = () => {
    if (currentMunicipality !== 'all') return currentMunicipality;
    if (currentSubregion !== 'all') return currentSubregion;
    return 'Antioquia';
  };

  return (
    <header className="sticky top-0 z-30 bg-sand-50/90 backdrop-blur-md border-b border-zinc-200/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 px-safe h-16 flex items-center justify-between gap-3">
        {/* Left: Brand Logo & Location Pill */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={onNavigateHome}
            className="flex items-center gap-2 text-left group cursor-pointer select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-lg p-1"
          >
            <div className="w-8 h-8 rounded-xl bg-brand-500 flex items-center justify-center text-white font-black text-lg shadow-sm shadow-brand-500/30 group-hover:scale-105 transition-transform">
              E
            </div>
            <div>
              <span className="font-black text-xl tracking-tight text-zinc-900 block leading-none group-hover:text-brand-600 transition-colors">
                EVENJOY
              </span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-brand-600 block leading-tight">
                Antioquia
              </span>
            </div>
          </button>

          {/* Location Selector Pill (PRD Section 7: "Antioquia ▾") */}
          <button
            type="button"
            onClick={onOpenLocationModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-zinc-200/80 shadow-xs hover:border-zinc-300 hover:bg-zinc-50 active:scale-95 transition-all cursor-pointer min-h-[44px] text-xs sm:text-sm font-bold text-zinc-800 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
            aria-label={`Filtrar por municipio o subregión. Ubicación seleccionada: ${getLocationLabel()}`}
          >
            <MapPin className="w-3.5 h-3.5 text-brand-500 shrink-0" />
            <span className="truncate max-w-[100px] sm:max-w-[160px]">{getLocationLabel()}</span>
            <ChevronDown className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
          </button>
        </div>

        {/* Center: Desktop Navigation Bar (Seamless cross-device adaptation) */}
        <nav aria-label="Navegación principal de escritorio" className="hidden md:flex items-center gap-1 bg-white/80 border border-zinc-200/80 p-1 rounded-full shadow-2xs">
          <button
            type="button"
            onClick={onNavigateHome}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer min-h-[36px] flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
              activeTab === 'explorar'
                ? 'bg-brand-50 text-brand-600 shadow-2xs'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50'
            }`}
            aria-current={activeTab === 'explorar' ? 'page' : undefined}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Explorar</span>
          </button>

          <button
            type="button"
            onClick={onNavigateSearch}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer min-h-[36px] flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
              activeTab === 'buscar'
                ? 'bg-brand-50 text-brand-600 shadow-2xs'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50'
            }`}
            aria-current={activeTab === 'buscar' ? 'page' : undefined}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Buscar</span>
          </button>

          {onNavigateMap && (
            <button
              type="button"
              onClick={onNavigateMap}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer min-h-[36px] flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
                activeTab === 'mapa'
                  ? 'bg-brand-50 text-brand-600 shadow-2xs'
                  : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50'
              }`}
              aria-current={activeTab === 'mapa' ? 'page' : undefined}
            >
              <Map className="w-3.5 h-3.5" />
              <span>Mapa</span>
            </button>
          )}

          <button
            type="button"
            onClick={onNavigateSaved}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer min-h-[36px] flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none ${
              activeTab === 'guardados'
                ? 'bg-brand-50 text-brand-600 shadow-2xs'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50'
            }`}
            aria-current={activeTab === 'guardados' ? 'page' : undefined}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>Guardados</span>
            {savedCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full bg-brand-500 text-white text-[10px] font-black leading-none">
                {savedCount}
              </span>
            )}
          </button>
        </nav>

        {/* Actions (Desktop and Mobile) */}
        <div className="flex items-center gap-2">
          {onOpenOnboarding && (
            <button
              type="button"
              onClick={onOpenOnboarding}
              className="p-2.5 rounded-full bg-white border border-zinc-200/80 text-zinc-600 hover:text-brand-600 hover:border-zinc-300 shadow-xs cursor-pointer min-h-[44px] min-w-[44px] hidden sm:flex items-center justify-center transition-all focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
              aria-label="Guía rápida: cómo explorar planes en Evenjoy"
              title="¿Cómo funciona Evenjoy?"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
          )}

          <button
            type="button"
            onClick={onNavigateSearch}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-zinc-200/80 text-xs sm:text-sm font-semibold text-zinc-600 hover:text-zinc-900 hover:border-zinc-300 shadow-xs cursor-pointer min-h-[44px] transition-all focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
            aria-label="Buscar eventos y planes culturales (presiona / para buscar)"
          >
            <Search className="w-4 h-4 text-zinc-500" />
            <span className="hidden sm:inline">Buscar planes</span>
          </button>

          <button
            type="button"
            onClick={onNavigateSaved}
            className="relative p-2.5 rounded-full bg-white border border-zinc-200/80 text-zinc-700 hover:text-brand-600 hover:border-zinc-300 shadow-xs cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center transition-all focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none"
            aria-label={savedCount === 0 ? 'Ver planes guardados' : savedCount === 1 ? 'Ver 1 plan guardado' : `Ver ${savedCount} planes guardados`}
          >
            <Bookmark className="w-4 h-4" />
            {savedCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-brand-500 text-white text-[10px] font-black flex items-center justify-center shadow-xs">
                {savedCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
