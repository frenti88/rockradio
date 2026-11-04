import React from 'react';
import { 
  Music, 
  Sparkles, 
  Palette, 
  Theater, 
  Film, 
  Utensils, 
  Store, 
  Wrench, 
  BookOpen, 
  Landmark, 
  Users, 
  Trees 
} from 'lucide-react';
import { EventCategory } from '../../types';

interface CategoryChipProps {
  category: EventCategory;
  isSelected?: boolean;
  onClick: (cat: EventCategory) => void;
}

const CATEGORY_ICONS: Record<EventCategory, React.ElementType> = {
  'Música': Music,
  'Fiestas': Sparkles,
  'Arte': Palette,
  'Teatro': Theater,
  'Cine': Film,
  'Gastronomía': Utensils,
  'Ferias': Store,
  'Talleres': Wrench,
  'Literatura': BookOpen,
  'Patrimonio': Landmark,
  'Familia': Users,
  'Naturaleza': Trees,
};

const CATEGORY_COLORS: Record<EventCategory, { bg: string; text: string }> = {
  'Música': { bg: 'bg-brand-50 group-hover:bg-brand-100', text: 'text-brand-700' },
  'Fiestas': { bg: 'bg-amber-50 group-hover:bg-amber-100', text: 'text-amber-800' },
  'Arte': { bg: 'bg-orange-50 group-hover:bg-orange-100', text: 'text-orange-800' },
  'Teatro': { bg: 'bg-rose-50 group-hover:bg-rose-100', text: 'text-rose-800' },
  'Cine': { bg: 'bg-slate-100 group-hover:bg-slate-200', text: 'text-slate-700' },
  'Gastronomía': { bg: 'bg-amber-100/60 group-hover:bg-amber-100', text: 'text-amber-900' },
  'Ferias': { bg: 'bg-amber-50 group-hover:bg-amber-100', text: 'text-amber-800' },
  'Talleres': { bg: 'bg-emerald-50 group-hover:bg-emerald-100', text: 'text-emerald-800' },
  'Literatura': { bg: 'bg-stone-100 group-hover:bg-stone-200', text: 'text-stone-800' },
  'Patrimonio': { bg: 'bg-stone-100 group-hover:bg-stone-200', text: 'text-stone-800' },
  'Familia': { bg: 'bg-brand-50 group-hover:bg-brand-100', text: 'text-brand-700' },
  'Naturaleza': { bg: 'bg-forest-50 group-hover:bg-forest-100', text: 'text-forest-700' },
};

export const CategoryChip: React.FC<CategoryChipProps> = ({
  category,
  isSelected = false,
  onClick,
}) => {
  const IconComponent = CATEGORY_ICONS[category] || Sparkles;
  const colors = CATEGORY_COLORS[category] || { bg: 'bg-zinc-100 group-hover:bg-zinc-200/60', text: 'text-zinc-600' };

  return (
    <button
      type="button"
      onClick={() => onClick(category)}
      className={`group flex items-center gap-2 px-3.5 py-2 rounded-2xl text-xs sm:text-sm font-semibold transition-all duration-200 shrink-0 cursor-pointer select-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none min-h-[44px] ${
        isSelected
          ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
          : 'bg-white text-zinc-700 border border-zinc-200/80 hover:border-zinc-300 hover:bg-sand-100/50'
      }`}
      aria-pressed={isSelected}
    >
      <span className={`p-1.5 rounded-lg transition-colors ${isSelected ? 'bg-white/20 text-white' : `${colors.bg} ${colors.text}`}`}>
        <IconComponent className="w-4 h-4" />
      </span>
      <span className="whitespace-nowrap">{category}</span>
    </button>
  );
};
