import React from 'react';
import { ShieldCheck, ExternalLink } from 'lucide-react';
import { SourceType } from '../../types';

interface SourceBadgeProps {
  sourceName: string;
  sourceType: SourceType;
  lastVerified?: string;
  url?: string;
  showIcon?: boolean;
  className?: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  sourceName,
  sourceType,
  lastVerified,
  url,
  showIcon = true,
  className = '',
}) => {
  // Truncate long source names for clean card layout if needed
  const cleanName = sourceName.split('—')[0].trim();

  return (
    <div className={`inline-flex items-center gap-1.5 text-xs text-zinc-500 font-medium ${className}`}>
      {showIcon && (
        <span
          title="Fuente oficial verificada"
          aria-label="Fuente oficial verificada"
          className="text-forest-700 inline-flex items-center"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
        </span>
      )}
      <span className="truncate">
        Fuente: <strong className="font-semibold text-zinc-800">{cleanName}</strong>
      </span>
      {lastVerified && (
        <span className="text-zinc-500 hidden sm:inline">
          · Verificado recientemente
        </span>
      )}
      {url && (
        <ExternalLink className="w-3 h-3 text-zinc-500 shrink-0" aria-hidden="true" />
      )}
    </div>
  );
};
