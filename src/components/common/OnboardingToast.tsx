import React, { useEffect } from 'react';
import { Bookmark, Sparkles, X, Check } from 'lucide-react';

interface OnboardingToastProps {
  message: string;
  subtext?: string;
  isOpen: boolean;
  onClose: () => void;
  actionLabel?: string;
  onAction?: () => void;
  durationMs?: number;
}

export const OnboardingToast: React.FC<OnboardingToastProps> = ({
  message,
  subtext,
  isOpen,
  onClose,
  actionLabel,
  onAction,
  durationMs = 6000,
}) => {
  useEffect(() => {
    if (!isOpen) return;
    const timer = setTimeout(() => {
      onClose();
    }, durationMs);
    return () => clearTimeout(timer);
  }, [isOpen, durationMs, onClose]);

  if (!isOpen) return null;

  return (
    <aside
      aria-label="Notificación del sistema"
      className="fixed bottom-20 sm:bottom-6 right-4 left-4 sm:left-auto sm:max-w-md z-40 bg-zinc-900 text-white p-4 rounded-2xl shadow-xl border border-zinc-700/80 flex items-start gap-3.5 animate-in slide-in-from-bottom-5 fade-in duration-300"
    >
      <div className="p-2 rounded-xl bg-brand-500 text-white shrink-0">
        <Bookmark className="w-4 h-4 fill-white" />
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-sm font-bold text-white flex items-center gap-1.5">
          <span>{message}</span>
        </p>
        {subtext && (
          <p className="text-xs text-zinc-300 mt-0.5 leading-relaxed">
            {subtext}
          </p>
        )}
        {actionLabel && onAction && (
          <button
            type="button"
            onClick={() => {
              onAction();
              onClose();
            }}
            className="mt-2 text-xs font-bold text-brand-300 hover:text-brand-200 underline cursor-pointer"
          >
            {actionLabel}
          </button>
        )}
      </div>

      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar aviso"
        className="p-1 rounded-lg text-zinc-400 hover:text-white transition-colors cursor-pointer shrink-0"
      >
        <X className="w-4 h-4" />
      </button>
    </aside>
  );
};
