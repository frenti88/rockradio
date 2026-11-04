import React, { useState } from 'react';
import { X, MapPin, Navigation, Check, ChevronRight } from 'lucide-react';
import { MUNICIPALITIES, SUBREGIONS } from '../../data/municipalities';
import { normalizeSearchText } from '../../services/searchEngine';
import { Subregion } from '../../types';

interface LocationModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedMunicipality: string | 'all';
  onSelectMunicipality: (muniName: string | 'all') => void;
  selectedSubregion: Subregion | 'all';
  onSelectSubregion: (subregion: Subregion | 'all') => void;
  onActivateNearMe: () => void;
  isNearMeActive: boolean;
}

export const LocationModal: React.FC<LocationModalProps> = ({
  isOpen,
  onClose,
  selectedMunicipality,
  onSelectMunicipality,
  selectedSubregion,
  onSelectSubregion,
  onActivateNearMe,
  isNearMeActive,
}) => {
  const [activeTab, setActiveTab] = useState<'municipios' | 'subregiones'>('municipios');
  const [searchMuni, setSearchMuni] = useState('');

  if (!isOpen) return null;

  const normalizedQuery = normalizeSearchText(searchMuni);
  const filteredMunis = MUNICIPALITIES.filter(m =>
    normalizeSearchText(m.name).includes(normalizedQuery) ||
    normalizeSearchText(m.subregion).includes(normalizedQuery)
  );

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-3xl shadow-sheet sm:shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in slide-in-from-bottom duration-300 ease-natural"
        role="dialog"
        aria-modal="true"
        aria-labelledby="location-modal-title"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-zinc-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-brand-50 text-brand-600">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h2 id="location-modal-title" className="text-lg font-bold text-zinc-900">
                ¿Dónde buscas planes?
              </h2>
              <p className="text-xs text-zinc-500">Elige un municipio, subregión o usa tu ubicación actual</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar selector de ubicación"
            className="p-2 text-zinc-500 hover:text-zinc-700 rounded-full hover:bg-zinc-100 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Geolocation Button "Cerca de mí" */}
        <div className="p-4 bg-sand-50 border-b border-zinc-100">
          <button
            type="button"
            onClick={() => {
              onActivateNearMe();
              onClose();
            }}
            className={`w-full flex items-center justify-between p-3.5 rounded-2xl border transition-all cursor-pointer min-h-[48px] ${
              isNearMeActive
                ? 'bg-brand-500 text-white border-brand-500 shadow-sm'
                : 'bg-white text-zinc-800 border-zinc-200 hover:border-brand-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-xl ${isNearMeActive ? 'bg-white/20' : 'bg-brand-50 text-brand-600'}`}>
                <Navigation className="w-4 h-4" />
              </div>
              <div className="text-left">
                <span className="block font-bold text-sm">Usar mi ubicación actual</span>
                <span className={`text-xs ${isNearMeActive ? 'text-white/80' : 'text-zinc-500'}`}>
                  Muestra eventos cercanos en Antioquia sin registros ni rastreo
                </span>
              </div>
            </div>
            {isNearMeActive && <Check className="w-5 h-5 text-white" />}
          </button>
        </div>

        {/* All Antioquia Option */}
        <div className="px-4 pt-3">
          <button
            type="button"
            onClick={() => {
              onSelectMunicipality('all');
              onSelectSubregion('all');
              onClose();
            }}
            className={`w-full flex items-center justify-between p-3 rounded-xl border text-sm font-semibold transition-all cursor-pointer min-h-[44px] ${
              selectedMunicipality === 'all' && selectedSubregion === 'all' && !isNearMeActive
                ? 'bg-zinc-900 text-white border-zinc-900'
                : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50'
            }`}
          >
            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-brand-500"></span>
              Toda Antioquia (125 municipios)
            </span>
            {selectedMunicipality === 'all' && selectedSubregion === 'all' && !isNearMeActive && (
              <Check className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Tabs: Municipios vs Subregiones */}
        <div className="flex border-b border-zinc-200 px-4 mt-3">
          <button
            type="button"
            onClick={() => setActiveTab('municipios')}
            className={`pb-2.5 px-3 text-sm font-bold border-b-2 transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'municipios'
                ? 'border-brand-500 text-brand-600'
                : 'border-transparent text-zinc-500 hover:text-zinc-700'
            }`}
          >
            Municipios y Pueblos
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('subregiones')}
            className={`pb-2.5 px-3 text-sm font-bold border-b-2 transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'subregiones'
                ? 'border-brand-500 text-brand-600'
                : 'border-transparent text-zinc-500 hover:text-zinc-700'
            }`}
          >
            Subregiones
          </button>
        </div>

        {/* Content List */}
        <div className="p-4 overflow-y-auto flex-1 max-h-[350px]">
          {activeTab === 'municipios' ? (
            <div className="space-y-3">
              <input
                type="text"
                value={searchMuni}
                onChange={(e) => setSearchMuni(e.target.value)}
                placeholder="Buscar municipio (ej. Jardín, Sonsón)..."
                aria-label="Buscar municipio por nombre o subregión"
                className="w-full px-3.5 py-2.5 rounded-xl border border-zinc-200 text-base sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-sand-50"
              />
              {filteredMunis.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                  {filteredMunis.map((m) => {
                    const isSelected = selectedMunicipality.toLowerCase() === m.name.toLowerCase();
                    return (
                      <button
                        key={m.slug}
                        type="button"
                        onClick={() => {
                          onSelectMunicipality(m.name);
                          onSelectSubregion('all');
                          onClose();
                        }}
                        className={`flex items-center justify-between p-3 rounded-xl border text-left transition-all cursor-pointer min-h-[44px] ${
                          isSelected
                            ? 'bg-brand-50 border-brand-500 text-brand-900 font-bold'
                            : 'bg-white border-zinc-100 hover:border-zinc-300 text-zinc-800'
                        }`}
                      >
                        <div>
                          <span className="block text-sm font-medium">{m.name}</span>
                          <span className="text-[11px] text-zinc-500">{m.subregion}</span>
                        </div>
                        {isSelected ? (
                          <Check className="w-4 h-4 text-brand-600" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-zinc-300" />
                        )}
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 px-4 bg-sand-50 rounded-2xl border border-zinc-200/80 mt-2 space-y-2.5">
                  <p className="text-sm font-bold text-zinc-800">
                    No encontramos municipios que coincidan con "{searchMuni}"
                  </p>
                  <p className="text-xs text-zinc-500 max-w-xs mx-auto leading-relaxed">
                    Evenjoy incluye los 125 municipios de Antioquia. Revisa la ortografía o navega por subregión en la pestaña superior.
                  </p>
                  <button
                    type="button"
                    onClick={() => setSearchMuni('')}
                    className="mt-1 px-4 py-2 rounded-xl bg-zinc-900 text-white text-xs font-bold hover:bg-black transition-colors cursor-pointer min-h-[40px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                  >
                    Restablecer búsqueda
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2">
              {SUBREGIONS.map((sub) => {
                const isSelected = selectedSubregion === sub.name;
                return (
                  <button
                    key={sub.slug}
                    type="button"
                    onClick={() => {
                      onSelectSubregion(sub.name as Subregion);
                      onSelectMunicipality('all');
                      onClose();
                    }}
                    className={`flex items-center justify-between p-3.5 rounded-xl border text-left transition-all cursor-pointer min-h-[44px] ${
                      isSelected
                        ? 'bg-brand-50 border-brand-500 text-brand-900 font-bold'
                        : 'bg-white border-zinc-100 hover:border-zinc-300 text-zinc-800'
                    }`}
                  >
                    <div>
                      <span className="block text-sm font-bold">{sub.name}</span>
                      <span className="text-xs text-zinc-500">{sub.description}</span>
                    </div>
                    {isSelected ? (
                      <Check className="w-4 h-4 text-brand-600" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-zinc-300" />
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
