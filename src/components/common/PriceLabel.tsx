import React from 'react';
import { PriceType } from '../../types';

interface PriceLabelProps {
  priceType: PriceType;
  priceFrom: number;
  priceTo?: number;
  currency?: string;
  className?: string;
}

export const PriceLabel: React.FC<PriceLabelProps> = ({
  priceType,
  priceFrom,
  priceTo,
  currency = 'COP',
  className = '',
}) => {
  const formatCOP = (num: number) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(num);

  if (priceType === 'free' || priceFrom === 0) {
    return (
      <span
        aria-label="Entrada libre y gratuita"
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-forest-100 text-forest-700 tracking-wide ${className}`}
      >
        Entrada libre
      </span>
    );
  }

  if (priceType === 'donation') {
    return (
      <span
        aria-label="Entrada con aporte voluntario sugerido"
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 ${className}`}
      >
        Aporte voluntario
      </span>
    );
  }

  const priceText = priceTo && priceTo > priceFrom
    ? `${formatCOP(priceFrom)} – ${formatCOP(priceTo)}`
    : `Desde ${formatCOP(priceFrom)}`;

  const ariaLabel = priceTo && priceTo > priceFrom
    ? `Boletería de ${formatCOP(priceFrom)} a ${formatCOP(priceTo)} pesos colombianos`
    : `Boletería desde ${formatCOP(priceFrom)} pesos colombianos`;

  return (
    <span
      aria-label={ariaLabel}
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 tabular-nums ${className}`}
    >
      {priceText}
    </span>
  );
};
