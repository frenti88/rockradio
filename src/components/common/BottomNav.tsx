import React from 'react';
import { Compass, Search, Map, Bookmark } from 'lucide-react';

export type TabType = 'explorar' | 'buscar' | 'mapa' | 'guardados';

interface BottomNavProps {
  currentTab: TabType;
  onChangeTab: (tab: TabType) => void;
  savedCount?: number;
}

export const BottomNav: React.FC<BottomNavProps> = ({
  currentTab,
  onChangeTab,
  savedCount = 0,
}) => {
  interface NavTabItem {
    id: TabType;
    label: string;
    icon: React.ElementType;
    badge?: number;
  }

  const tabs: NavTabItem[] = [
    { id: 'explorar', label: 'Explorar', icon: Compass },
    { id: 'buscar', label: 'Buscar', icon: Search },
    { id: 'mapa', label: 'Mapa', icon: Map },
    { id: 'guardados', label: 'Guardados', icon: Bookmark, badge: savedCount },
  ];

  return (
    <nav
      aria-label="Navegación principal móvil"
      className="sm:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-zinc-200/80 px-2 px-safe pt-1 pb-safe shadow-sheet no-print"
    >
      <div className="flex items-center justify-around">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          const ariaLabel = tab.id === 'guardados' && tab.badge && tab.badge > 0
            ? tab.badge === 1
              ? 'Guardados, 1 plan cultural guardado'
              : `Guardados, ${tab.badge} planes culturales guardados`
            : tab.label;

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onChangeTab(tab.id)}
              aria-label={ariaLabel}
              className={`flex flex-col items-center justify-center py-1.5 px-3 min-h-[48px] rounded-xl transition-all cursor-pointer select-none relative ${
                isActive ? 'text-brand-600 font-bold' : 'text-zinc-500 hover:text-zinc-800'
              }`}
              aria-current={isActive ? 'page' : undefined}
            >
              <div className="relative">
                <Icon className={`w-5 h-5 transition-transform ${isActive ? 'scale-110' : ''}`} />
                {Boolean(tab.badge && tab.badge > 0) && (
                  <span className="absolute -top-1.5 -right-2.5 px-1.5 py-0.2 rounded-full bg-brand-500 text-white text-[9px] font-black">
                    {tab.badge}
                  </span>
                )}
              </div>
              <span className="text-[11px] mt-1 tracking-tight">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
