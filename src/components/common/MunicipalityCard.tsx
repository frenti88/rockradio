import React, { useState } from 'react';
import { MapPin, Navigation, ArrowUpRight } from 'lucide-react';
import { MunicipalityData } from '../../types';

interface MunicipalityCardProps {
  municipality: MunicipalityData;
  eventCount?: number;
  onSelect: (muni: MunicipalityData) => void;
}

const MunicipalityCardComponent: React.FC<MunicipalityCardProps> = ({
  municipality,
  eventCount,
  onSelect,
}) => {
  const [imageError, setImageError] = useState(false);

  return (
    <article
      className="group relative rounded-2xl overflow-hidden shadow-card hover:shadow-card-hover transition-all duration-300 aspect-[4/5] sm:aspect-[3/4] flex flex-col justify-end p-5 select-none focus-within:ring-2 focus-within:ring-brand-500 focus-within:outline-none bg-forest-900 content-visibility-auto"
      aria-label={`Municipio de ${municipality.name}, ${municipality.subregion}`}
    >
      {/* Background Hero Image with fallback */}
      {!imageError ? (
        <img
          src={municipality.hero_image}
          alt={`Paisaje de ${municipality.name}`}
          loading="lazy"
          decoding="async"
          onError={() => setImageError(true)}
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-b from-forest-800 to-forest-950" />
      )}

      {/* Dark gradient overlay for optimal text legibility */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent" />

      {/* Top Badge: Subregion */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between z-10">
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-white/20 backdrop-blur-md text-white border border-white/20">
          <MapPin className="w-3 h-3" />
          {municipality.subregion}
        </span>
        <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white group-hover:bg-brand-500 transition-colors">
          <ArrowUpRight className="w-4 h-4" />
        </div>
      </div>

      {/* Bottom Content */}
      <div className="relative z-10 text-white">
        <h3 className="text-xl sm:text-2xl font-black tracking-tight leading-tight group-hover:text-brand-200 transition-colors">
          <button
            type="button"
            onClick={() => onSelect(municipality)}
            className="after:absolute after:inset-0 text-left focus:outline-none focus-visible:underline cursor-pointer"
          >
            {municipality.name}
          </button>
        </h3>
        <p className="text-xs text-white/80 line-clamp-2 mt-1 pointer-events-none">
          {municipality.signature_tradition}
        </p>

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/20 text-xs text-white/90 pointer-events-none">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="flex items-center gap-1 font-medium">
              <Navigation className="w-3 h-3" />
              {municipality.travel_time_approx}
            </span>
            {municipality.climate && (
              <>
                <span className="text-white/40">·</span>
                <span className="text-white/80">{municipality.climate}</span>
              </>
            )}
          </div>
          {typeof eventCount === 'number' && (
            <span className="px-2 py-0.5 rounded-md bg-brand-500/90 text-white font-bold shrink-0 ml-2">
              {eventCount} {eventCount === 1 ? 'evento' : 'eventos'}
            </span>
          )}
        </div>
      </div>
    </article>
  );
};

export const MunicipalityCard = React.memo(MunicipalityCardComponent);
