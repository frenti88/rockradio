import React from 'react';
import { Compass, Sparkles, Heart } from 'lucide-react';
import { MUNICIPALITIES, SUBREGIONS } from '../../data/municipalities';

interface FooterProps {
  onSelectMunicipality: (muniSlug: string) => void;
  onSelectSubregion: (subregionSlug: string) => void;
  onOpenAdmin: () => void;
  onOpenOnboarding?: () => void;
}

export const Footer: React.FC<FooterProps> = ({
  onSelectMunicipality,
  onSelectSubregion,
  onOpenAdmin,
  onOpenOnboarding,
}) => {
  return (
    <footer className="bg-sand-100 border-t border-zinc-200/80 mt-16 text-zinc-700 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Column 1: Brand & Purpose */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-brand-500 flex items-center justify-center text-white font-black text-lg">
                E
              </div>
              <span className="font-black text-xl tracking-tight text-zinc-900">
                EVENJOY
              </span>
            </div>
            <p className="text-xs sm:text-sm text-zinc-600 leading-relaxed">
              "Todo lo que está pasando en Antioquia."
            </p>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Descubridor cultural abierto de los pueblos y municipios de Antioquia. Conectamos la oferta cultural viva directamente con sus fuentes oficiales sin intermediación transaccional.
            </p>
          </div>

          {/* Column 2: Municipios Destacados */}
          <div>
            <h4 className="font-bold text-zinc-900 text-xs uppercase tracking-wider mb-3">
              Pueblos de Antioquia
            </h4>
            <ul className="space-y-1.5 text-xs">
              {MUNICIPALITIES.slice(0, 6).map((m) => (
                <li key={m.slug}>
                  <button
                    type="button"
                    onClick={() => onSelectMunicipality(m.slug)}
                    className="text-zinc-600 hover:text-brand-600 transition-colors cursor-pointer py-1"
                  >
                    Qué hacer en {m.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 3: Subregiones */}
          <div>
            <h4 className="font-bold text-zinc-900 text-xs uppercase tracking-wider mb-3">
              Subregiones
            </h4>
            <ul className="space-y-1.5 text-xs">
              {SUBREGIONS.slice(0, 6).map((s) => (
                <li key={s.slug}>
                  <button
                    type="button"
                    onClick={() => onSelectSubregion(s.slug)}
                    className="text-zinc-600 hover:text-brand-600 transition-colors cursor-pointer py-1"
                  >
                    Cultura en {s.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 4: Principios & Fuentes */}
          <div className="space-y-3">
            <h4 className="font-bold text-zinc-900 text-xs uppercase tracking-wider mb-1">
              Transparencia y Datos
            </h4>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Evenjoy no organiza ni vende boletas. Toda la información conserva explícitamente su procedencia: alcaldías, casas de la cultura, museos, Comfama, Comfenalco y colectivos independientes.
            </p>
            <div className="pt-2 flex flex-col gap-2">
              {onOpenOnboarding && (
                <button
                  type="button"
                  onClick={onOpenOnboarding}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-zinc-700 hover:text-brand-600 transition-colors cursor-pointer py-1"
                >
                  <Compass className="w-3.5 h-3.5 text-brand-500" />
                  ¿Cómo funciona? (Guía interactiva)
                </button>
              )}
              <button
                type="button"
                onClick={onOpenAdmin}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-zinc-700 hover:text-brand-600 transition-colors cursor-pointer py-1"
              >
                <Sparkles className="w-3.5 h-3.5 text-brand-500" />
                Panel de fuentes y verificación
              </button>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-zinc-200/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-zinc-500">
          <p>© {new Date().getFullYear()} EVENJOY · Plataforma Cultural de Antioquia, Colombia.</p>
          <p className="flex items-center gap-1">
            Diseñado para descubrir cultura local con <Heart className="w-3.5 h-3.5 text-brand-500 fill-brand-500" /> en las montañas de Antioquia.
          </p>
        </div>
      </div>
    </footer>
  );
};
