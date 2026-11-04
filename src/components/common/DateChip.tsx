import React from 'react';

interface DateChipProps {
  label: string;
  count?: number;
  isSelected: boolean;
  onClick: () => void;
}

export const DateChip: React.FC<DateChipProps> = ({
  label,
  count,
  isSelected,
  onClick,
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 cursor-pointer select-none flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:outline-none min-h-[44px] ${
        isSelected
          ? 'bg-zinc-900 text-white shadow-sm'
          : 'bg-white text-zinc-700 border border-zinc-200/80 hover:border-zinc-300 hover:bg-zinc-50 active:scale-95'
      }`}
      aria-pressed={isSelected}
    >
      <span>{label}</span>
      {typeof count === 'number' && (
        <span
          className={`text-xs px-1.5 py-0.5 rounded-full font-bold tabular-nums ${
            isSelected ? 'bg-zinc-800 text-zinc-300' : 'bg-zinc-100 text-zinc-500'
          }`}
        >
          {count}
        </span>
      )}
    </button>
  );
};
