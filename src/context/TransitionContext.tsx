import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { flushSync } from 'react-dom';

interface TransitionContextValue {
  activeTransitionSlug: string | null;
  setActiveTransitionSlug: (slug: string | null) => void;
  navigateWithTransition: (
    callback: () => void,
    targetSlug?: string | null,
    isReturning?: boolean
  ) => void;
  isSupported: boolean;
}

const TransitionContext = createContext<TransitionContextValue>({
  activeTransitionSlug: null,
  setActiveTransitionSlug: () => {},
  navigateWithTransition: (callback) => callback(),
  isSupported: false,
});

export const useViewTransition = () => useContext(TransitionContext);

interface TransitionProviderProps {
  children: React.ReactNode;
}

export const TransitionProvider: React.FC<TransitionProviderProps> = ({ children }) => {
  const [activeTransitionSlug, setActiveTransitionSlug] = useState<string | null>(null);
  const activeSlugRef = useRef<string | null>(null);

  const isSupported = typeof document !== 'undefined' && 'startViewTransition' in document;

  const navigateWithTransition = useCallback(
    (callback: () => void, targetSlug?: string | null, isReturning: boolean = false) => {
      const prefersReducedMotion =
        typeof window !== 'undefined' &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      // Graceful fallback for unsupported browsers or reduced motion preference
      if (!isSupported || prefersReducedMotion) {
        callback();
        return;
      }

      try {
        if (targetSlug && !isReturning) {
          // Forward navigation (Card -> Detail Hero):
          // Immediately flush state so the origin card element receives 'view-transition-name'
          // in the current DOM before the browser captures the initial snapshot.
          flushSync(() => {
            activeSlugRef.current = targetSlug;
            setActiveTransitionSlug(targetSlug);
          });
        }

        const transition = (document as any).startViewTransition(() => {
          flushSync(() => {
            if (targetSlug && isReturning) {
              // Backward navigation (Detail Hero -> Card):
              // In the new DOM, assign 'view-transition-name' to the destination card
              activeSlugRef.current = targetSlug;
              setActiveTransitionSlug(targetSlug);
            }
            callback();
          });
        });

        transition.finished
          .catch(() => {})
          .finally(() => {
            // Clean up transition name after morph completes so regular layout is unhindered
            activeSlugRef.current = null;
            setActiveTransitionSlug(null);
          });
      } catch (err) {
        console.warn('View transition fallback triggered:', err);
        callback();
        activeSlugRef.current = null;
        setActiveTransitionSlug(null);
      }
    },
    [isSupported]
  );

  return (
    <TransitionContext.Provider
      value={{
        activeTransitionSlug,
        setActiveTransitionSlug,
        navigateWithTransition,
        isSupported,
      }}
    >
      {children}
    </TransitionContext.Provider>
  );
};
