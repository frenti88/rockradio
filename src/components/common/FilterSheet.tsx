import React from 'react';
import { X, RotateCcw, SlidersHorizontal, Check } from 'lucide-react';
import { FilterState, EventCategory, Subregion, AudienceType, EventFormat } from '../../types';
import { MUNICIPALITIES, SUBREGIONS } from '../../data/municipalities';

interface FilterSheetProps {
  isOpen: boolean;
  onClose: () => void;
  filters: FilterState;
  onChange: (newFilters: FilterState) => void;
  totalMatchingEvents: number;
}

const CATEGORIES: EventCategory[] = [
  'Música', 'Fiestas', 'Arte', 'Teatro', 'Cine', 
  'Gastronomía', 'Ferias', 'Talleres', 'Literatura', 
  'Patrimonio', 'Familia', 'Naturaleza'
];

const AUDIENCES: Array<{ id: AudienceType; label: string }> = [
  { id: 'all_ages', label: 'Todo público' },
  { id: 'family', label: 'Familiar con niños' },
  { id: 'adults', label: 'Adultos' },
  { id: 'youth', label: 'Jóvenes' },
];

const FORMATS: Array<{ id: EventFormat; label: string }> = [
  { id: 'outdoor', label: 'Al aire libre' },
  { id: 'in_person', label: 'Recinto cerrado' },
  { id: 'hybrid', label: 'Híbrido' },
];

export const FilterSheet: React.FC<FilterSheetProps> = ({
  isOpen,
  onClose,
  filters,
  onChange,
  totalMatchingEvents,
}) => {
  if (!isOpen) return null;

  const handleReset = () => {
    onChange({
      ...filters,
      dateRange: 'all',
      municipality: 'all',
      subregion: 'all',
      category: 'all',
      priceType: 'all',
      audience: 'all',
      format: 'all',
      onlyVerified: false,
      nearMe: false,
    });
  };

  const activeFiltersCount = [
    filters.dateRange !== 'all',
    filters.municipality !== 'all',
    filters.subregion !== 'all',
    filters.category !== 'all',
    filters.priceType !== 'all',
    filters.audience !== 'all',
    filters.format !== 'all',
    filters.onlyVerified,
    filters.nearMe,
  ].filter(Boolean).length;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="bg-white w-full sm:max-w-xl rounded-t-3xl sm:rounded-3xl shadow-sheet sm:shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in slide-in-from-bottom duration-300 ease-natural"
        role="dialog"
        aria-modal="true"
        aria-labelledby="filter-sheet-title"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-zinc-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-zinc-100 text-zinc-800">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <div>
              <h2 id="filter-sheet-title" className="text-lg font-bold text-zinc-900">
                Filtros {activeFiltersCount > 0 && `(${activeFiltersCount})`}
              </h2>
              <p className="text-xs text-zinc-500">Ajusta tu búsqueda a tu medida</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {activeFiltersCount > 0 && (
              <button
                type="button"
                onClick={handleReset}
                className="text-xs font-bold text-brand-600 hover:text-brand-700 flex items-center gap-1 px-2.5 py-1.5 rounded-lg hover:bg-brand-50 cursor-pointer min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Limpiar
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Cerrar filtros"
              className="p-2 text-zinc-500 hover:text-zinc-700 rounded-full hover:bg-zinc-100 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Filters Body */}
        <div className="p-4 sm:p-6 overflow-y-auto flex-1 space-y-6">
          {/* 1. Precio */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
              Precio
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'all', label: 'Cualquier precio' },
                { id: 'free', label: 'Entrada libre' },
                { id: 'paid', label: 'Con boletería' },
              ].map((p) => {
                const isSelected = filters.priceType === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => onChange({ ...filters, priceType: p.id as any })}
                    className={`py-2.5 px-3 rounded-xl text-xs font-bold border transition-all cursor-pointer min-h-[44px] ${
                      isSelected
                        ? 'bg-zinc-900 text-white border-zinc-900'
                        : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                    }`}
                  >
                    {p.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Fechas rápidas */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
              Cuándo
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'all', label: 'Cualquier fecha' },
                { id: 'today', label: 'Hoy' },
                { id: 'tomorrow', label: 'Mañana' },
                { id: 'this_weekend', label: 'Este fin de semana' },
                { id: 'this_week', label: 'Esta semana' },
                { id: 'next_weekend', label: 'Próximo finde' },
              ].map((d) => {
                const isSelected = filters.dateRange === d.id;
                return (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => onChange({ ...filters, dateRange: d.id as any })}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all cursor-pointer min-h-[44px] ${
                      isSelected
                        ? 'bg-brand-500 text-white border-brand-500 shadow-sm'
                        : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                    }`}
                  >
                    {d.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 3. Subregiones */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
              Subregión de Antioquia
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => onChange({ ...filters, subregion: 'all' })}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all cursor-pointer min-h-[44px] ${
                  filters.subregion === 'all'
                    ? 'bg-zinc-900 text-white border-zinc-900'
                    : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                }`}
              >
                Todas las subregiones
              </button>
              {SUBREGIONS.map((s) => {
                const isSelected = filters.subregion === s.name;
                return (
                  <button
                    key={s.slug}
                    type="button"
                    onClick={() => onChange({ ...filters, subregion: s.name as Subregion, municipality: 'all' })}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all cursor-pointer min-h-[44px] ${
                      isSelected
                        ? 'bg-zinc-900 text-white border-zinc-900'
                        : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                    }`}
                  >
                    {s.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 4. Categoría */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
              Categoría Cultural
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => onChange({ ...filters, category: 'all' })}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all cursor-pointer min-h-[44px] ${
                  filters.category === 'all'
                    ? 'bg-brand-500 text-white border-brand-500'
                    : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                }`}
              >
                Todas
              </button>
              {CATEGORIES.map((c) => {
                const isSelected = filters.category === c;
                return (
                  <button
                    key={c}
                    type="button"
                    onClick={() => onChange({ ...filters, category: c })}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all cursor-pointer min-h-[44px] ${
                      isSelected
                        ? 'bg-brand-500 text-white border-brand-500'
                        : 'bg-sand-50 text-zinc-700 border-zinc-200/80 hover:bg-white'
                    }`}
                  >
                    {c}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 5. Público y Formato */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
                Público
              </label>
              <select
                value={filters.audience}
                onChange={(e) => onChange({ ...filters, audience: e.target.value as any })}
                className="w-full p-2.5 rounded-xl border border-zinc-200 bg-sand-50 text-sm font-medium focus:ring-2 focus:ring-brand-500 min-h-[44px]"
              >
                <option value="all">Cualquier público</option>
                {AUDIENCES.map(a => (
                  <option key={a.id} value={a.id}>{a.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-zinc-500 mb-2.5">
                Formato
              </label>
              <select
                value={filters.format}
                onChange={(e) => onChange({ ...filters, format: e.target.value as any })}
                className="w-full p-2.5 rounded-xl border border-zinc-200 bg-sand-50 text-sm font-medium focus:ring-2 focus:ring-brand-500 min-h-[44px]"
              >
                <option value="all">Cualquier formato</option>
                {FORMATS.map(f => (
                  <option key={f.id} value={f.id}>{f.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Bottom CTA sticky */}
        <div className="p-4 sm:p-5 border-t border-zinc-100 bg-white">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-3.5 px-6 rounded-2xl bg-zinc-900 hover:bg-black text-white font-bold text-sm shadow-md transition-all cursor-pointer min-h-[48px] flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
          >
            {totalMatchingEvents > 0 ? (
              <span>Ver {totalMatchingEvents} {totalMatchingEvents === 1 ? 'evento disponible' : 'eventos disponibles'}</span>
            ) : (
              <span>Ver resultados (0 eventos encontrados)</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
