import React, { useState, useEffect, useRef, Suspense, lazy } from 'react';
import { CulturalEvent, MunicipalityData, FilterState, Subregion } from './types';
import { INITIAL_EVENTS } from './data/events';
import { MUNICIPALITIES, SUBREGIONS } from './data/municipalities';
import { Header } from './components/common/Header';
import { BottomNav, TabType } from './components/common/BottomNav';
import { Footer } from './components/common/Footer';
import { LocationModal } from './components/common/LocationModal';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { OnboardingModal } from './components/common/OnboardingModal';
import { OnboardingToast } from './components/common/OnboardingToast';
import { HomeView } from './views/HomeView';
import { ExploreView } from './views/ExploreView';
import { EventDetailView } from './views/EventDetailView';
import { MunicipalityView } from './views/MunicipalityView';
import { SavedEventsView } from './views/SavedEventsView';
import { getFavoriteEventIds } from './services/favorites';
import { useViewTransition } from './context/TransitionContext';

// Code-splitting for Admin View (core web vitals optimization)
const AdminView = lazy(() => import('./views/AdminView').then(m => ({ default: m.AdminView })));

export function App() {
  const { navigateWithTransition } = useViewTransition();
  const isInitialLoad = useRef(true);

  const [events, setEvents] = useState<CulturalEvent[]>(INITIAL_EVENTS);
  const [currentView, setCurrentView] = useState<'home' | 'explore' | 'detail' | 'municipality' | 'saved' | 'admin'>('home');
  const [previousView, setPreviousView] = useState<'home' | 'explore' | 'detail' | 'municipality' | 'saved' | 'admin'>('home');
  const [selectedEvent, setSelectedEvent] = useState<CulturalEvent | null>(null);
  const [selectedMunicipality, setSelectedMunicipality] = useState<MunicipalityData | null>(null);
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);
  const [isNearMeActive, setIsNearMeActive] = useState(false);
  const [savedCount, setSavedCount] = useState<number>(() => getFavoriteEventIds().length);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState<boolean>(() => {
    try {
      return localStorage.getItem('evenjoy_onboarded_v1') !== 'true';
    } catch {
      return false;
    }
  });
  const [isFavToastOpen, setIsFavToastOpen] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
    dateRange: 'all',
    municipality: 'all',
    subregion: 'all',
    category: 'all',
    priceType: 'all',
    audience: 'all',
    format: 'all',
    searchQuery: '',
    onlyVerified: false,
    nearMe: false,
    maxDistanceKm: 50,
  });

  const [exploreInitialViewMode, setExploreInitialViewMode] = useState<'list' | 'grid' | 'map'>('list');

  // Browser History & URL Router sync
  useEffect(() => {
    const syncRouteFromPath = () => {
      const path = window.location.pathname;
      if (path.startsWith('/evento/')) {
        const slug = path.replace('/evento/', '');
        const evt = events.find(e => e.slug === slug);
        if (evt) {
          setSelectedEvent(evt);
          setCurrentView('detail');
          return;
        }
      }
      if (path.startsWith('/antioquia/')) {
        const muniSlug = path.replace('/antioquia/', '');
        const muni = MUNICIPALITIES.find(m => m.slug === muniSlug);
        if (muni) {
          setSelectedMunicipality(muni);
          setCurrentView('municipality');
          return;
        }
      }
      if (path === '/mapa') {
        setExploreInitialViewMode('map');
        setCurrentView('explore');
        return;
      }
      if (path === '/eventos' || path === '/buscar') {
        setExploreInitialViewMode('list');
        setCurrentView('explore');
        return;
      }
      if (path === '/guardados') {
        setCurrentView('saved');
        return;
      }
      if (path === '/admin') {
        setCurrentView('admin');
        return;
      }
      setCurrentView('home');
    };

    const handlePopState = () => {
      navigateWithTransition(syncRouteFromPath);
    };

    // Keyboard Shortcuts (Alex persona & accessibility)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsLocationModalOpen(false);
      }
      if (e.key === '/' && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) {
        e.preventDefault();
        setExploreInitialViewMode('list');
        navigateTo('explore', '/buscar');
      }
    };

    const handleFavoritesChanged = () => {
      const count = getFavoriteEventIds().length;
      setSavedCount(count);
      try {
        if (count > 0 && localStorage.getItem('evenjoy_fav_onboarded_v1') !== 'true') {
          setIsFavToastOpen(true);
          localStorage.setItem('evenjoy_fav_onboarded_v1', 'true');
        }
      } catch {
        // safe ignore in private browsing
      }
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('evenjoy-favorites-changed', handleFavoritesChanged);

    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      syncRouteFromPath();
    }

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('evenjoy-favorites-changed', handleFavoritesChanged);
    };
  }, [events, navigateWithTransition]);

  const navigateTo = (view: typeof currentView, url: string = '/') => {
    navigateWithTransition(() => {
      setPreviousView(currentView);
      setCurrentView(view);
      window.history.pushState({}, '', url);
      window.scrollTo({ top: 0, behavior: 'instant' });
    });
  };

  const handleSelectEvent = (evt: CulturalEvent) => {
    setPreviousView(currentView);
    navigateWithTransition(
      () => {
        setSelectedEvent(evt);
        setCurrentView('detail');
        window.history.pushState({}, '', `/evento/${evt.slug}`);
        window.scrollTo({ top: 0, behavior: 'instant' });
      },
      evt.slug,
      false
    );
  };

  const handleBackFromDetail = () => {
    const slug = selectedEvent?.slug || null;
    const targetView = previousView === 'detail' ? 'explore' : previousView;
    const targetUrl =
      targetView === 'home'
        ? '/'
        : targetView === 'saved'
        ? '/guardados'
        : targetView === 'municipality' && selectedMunicipality
        ? `/antioquia/${selectedMunicipality.slug}`
        : '/buscar';

    navigateWithTransition(
      () => {
        setCurrentView(targetView);
        window.history.pushState({}, '', targetUrl);
      },
      slug,
      true
    );
  };

  const handleSelectMunicipality = (muni: MunicipalityData) => {
    setSelectedMunicipality(muni);
    navigateTo('municipality', `/antioquia/${muni.slug}`);
  };

  const handleSelectMunicipalityBySlug = (slug: string) => {
    const muni = MUNICIPALITIES.find(m => m.slug === slug || m.name.toLowerCase() === slug.toLowerCase());
    if (muni) {
      handleSelectMunicipality(muni);
    } else {
      setFilters(prev => ({ ...prev, municipality: slug }));
      navigateTo('explore', '/buscar');
    }
  };

  const handleSelectSubregion = (subregionSlugOrName: string) => {
    const matched = SUBREGIONS.find(s => s.slug === subregionSlugOrName || s.name.toLowerCase() === subregionSlugOrName.toLowerCase());
    const sub = (matched ? matched.name : subregionSlugOrName) as Subregion;
    setFilters(prev => ({ ...prev, subregion: sub, municipality: 'all' }));
    navigateTo('explore', '/buscar');
  };

  const handleActivateNearMe = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setIsNearMeActive(true);
          setFilters(prev => ({
            ...prev,
            nearMe: true,
            userCoords: {
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
            },
          }));
          navigateTo('explore', '/buscar');
        },
        () => {
          // Fallback location: Medellín center
          setIsNearMeActive(true);
          setFilters(prev => ({
            ...prev,
            nearMe: true,
            userCoords: { latitude: 6.2442, longitude: -75.5812 },
          }));
          navigateTo('explore', '/buscar');
        }
      );
    } else {
      setIsNearMeActive(true);
      setFilters(prev => ({
        ...prev,
        nearMe: true,
        userCoords: { latitude: 6.2442, longitude: -75.5812 },
      }));
      navigateTo('explore', '/buscar');
    }
  };

  const handleCloseOnboarding = () => {
    setIsOnboardingOpen(false);
    try {
      localStorage.setItem('evenjoy_onboarded_v1', 'true');
    } catch {
      // safe ignore
    }
  };

  const handleOnboardingNearMe = () => {
    handleCloseOnboarding();
    handleActivateNearMe();
  };

  const handleOnboardingFreeEvents = () => {
    handleCloseOnboarding();
    setFilters(prev => ({ ...prev, priceType: 'free' }));
    setExploreInitialViewMode('list');
    navigateTo('explore', '/buscar');
  };

  const handleOnboardingHeritageTowns = () => {
    handleCloseOnboarding();
    setFilters(prev => ({ ...prev, subregion: 'Suroeste', municipality: 'all' }));
    setExploreInitialViewMode('list');
    navigateTo('explore', '/buscar');
  };

  const handleOnboardingOpenMap = () => {
    handleCloseOnboarding();
    setExploreInitialViewMode('map');
    navigateTo('explore', '/mapa');
  };

  const handleOnboardingSearch = () => {
    handleCloseOnboarding();
    setExploreInitialViewMode('list');
    navigateTo('explore', '/buscar');
  };

  const handleUpdateEventStatus = (eventId: string, newStatus: CulturalEvent['status']) => {
    setEvents(prev =>
      prev.map(e => e.event_id === eventId ? { ...e, status: newStatus } : e)
    );
  };

  // Compute active tab for bottom navigation
  const getActiveTab = (): TabType => {
    if (currentView === 'home') return 'explorar';
    if (currentView === 'explore') {
      return exploreInitialViewMode === 'map' ? 'mapa' : 'buscar';
    }
    if (currentView === 'saved') return 'guardados';
    return 'explorar';
  };

  return (
    <div className="min-h-screen flex flex-col bg-sand-50 text-zinc-900 selection:bg-brand-100 selection:text-brand-900">
      {/* Skip to Content for Keyboard Users (WCAG 2.4.1) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 z-50 px-4 py-2 bg-brand-500 text-white rounded-xl font-bold shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500"
      >
        Saltar al contenido principal
      </a>

      {/* Header */}
      <Header
        currentMunicipality={filters.municipality}
        currentSubregion={filters.subregion}
        activeTab={getActiveTab()}
        onOpenLocationModal={() => setIsLocationModalOpen(true)}
        onNavigateSearch={() => {
          setExploreInitialViewMode('list');
          navigateTo('explore', '/buscar');
        }}
        onNavigateHome={() => navigateTo('home', '/')}
        onNavigateSaved={() => navigateTo('saved', '/guardados')}
        onNavigateMap={() => {
          setExploreInitialViewMode('map');
          navigateTo('explore', '/mapa');
        }}
        onOpenOnboarding={() => setIsOnboardingOpen(true)}
        savedCount={savedCount}
      />

      {/* Main Content Area */}
      <main id="main-content" className="flex-1">
        <ErrorBoundary>
          {currentView === 'home' && (
          <HomeView
            events={events}
            onSelectEvent={handleSelectEvent}
            onSelectMunicipality={handleSelectMunicipality}
            onApplyQuickFilter={(newFilters) => {
              setFilters(prev => ({ ...prev, ...newFilters }));
            }}
            onOpenLocationModal={() => setIsLocationModalOpen(true)}
            currentMunicipality={filters.municipality}
            currentSubregion={filters.subregion}
            onNavigateExplore={(query) => {
              if (query) {
                setFilters(prev => ({ ...prev, searchQuery: query }));
              }
              setExploreInitialViewMode('list');
              navigateTo('explore', '/buscar');
            }}
          />
        )}

        {currentView === 'explore' && (
          <ExploreView
            events={events}
            filters={filters}
            initialViewMode={exploreInitialViewMode}
            onUpdateFilters={setFilters}
            onSelectEvent={handleSelectEvent}
            onClearFilters={() => {
              setFilters({
                dateRange: 'all',
                municipality: 'all',
                subregion: 'all',
                category: 'all',
                priceType: 'all',
                audience: 'all',
                format: 'all',
                searchQuery: '',
                onlyVerified: false,
                nearMe: false,
              });
              setIsNearMeActive(false);
            }}
          />
        )}

        {currentView === 'detail' && selectedEvent && (
          <EventDetailView
            event={selectedEvent}
            allEvents={events}
            onBack={handleBackFromDetail}
            onSelectEvent={handleSelectEvent}
            onSelectMunicipality={handleSelectMunicipalityBySlug}
          />
        )}

        {currentView === 'municipality' && selectedMunicipality && (
          <MunicipalityView
            municipality={selectedMunicipality}
            events={events}
            onBack={() => navigateTo('home', '/')}
            onSelectEvent={handleSelectEvent}
            onSelectOtherMunicipality={handleSelectMunicipality}
          />
        )}

        {currentView === 'saved' && (
          <SavedEventsView
            allEvents={events}
            onSelectEvent={handleSelectEvent}
            onNavigateHome={() => navigateTo('home', '/')}
            onNavigateExplore={() => {
              setExploreInitialViewMode('list');
              navigateTo('explore', '/buscar');
            }}
          />
        )}

        {currentView === 'admin' && (
          <Suspense fallback={
            <div className="min-h-[400px] flex items-center justify-center text-zinc-500 font-medium">
              Cargando panel de administración...
            </div>
          }>
            <AdminView
              events={events}
              onUpdateEventStatus={handleUpdateEventStatus}
              onNavigateHome={() => navigateTo('home', '/')}
            />
          </Suspense>
        )}
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <Footer
        onSelectMunicipality={handleSelectMunicipalityBySlug}
        onSelectSubregion={handleSelectSubregion}
        onOpenAdmin={() => navigateTo('admin', '/admin')}
        onOpenOnboarding={() => setIsOnboardingOpen(true)}
      />

      {/* Mobile Bottom Navigation - Hidden on event detail to avoid collision with event sticky CTA */}
      {currentView !== 'detail' && (
        <BottomNav
          currentTab={getActiveTab()}
          savedCount={savedCount}
          onChangeTab={(tab) => {
            if (tab === 'explorar') navigateTo('home', '/');
            if (tab === 'buscar') {
              setExploreInitialViewMode('list');
              navigateTo('explore', '/buscar');
            }
            if (tab === 'mapa') {
              setExploreInitialViewMode('map');
              navigateTo('explore', '/mapa');
            }
            if (tab === 'guardados') navigateTo('saved', '/guardados');
          }}
        />
      )}

      {/* Location Modal */}
      <LocationModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
        selectedMunicipality={filters.municipality}
        onSelectMunicipality={(muni) => setFilters(prev => ({ ...prev, municipality: muni }))}
        selectedSubregion={filters.subregion}
        onSelectSubregion={(sub) => setFilters(prev => ({ ...prev, subregion: sub }))}
        onActivateNearMe={handleActivateNearMe}
        isNearMeActive={isNearMeActive}
      />

      {/* Onboarding Interactive Modal (Time to Value: 10s) */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={handleCloseOnboarding}
        onActionNearMe={handleOnboardingNearMe}
        onActionFreeEvents={handleOnboardingFreeEvents}
        onActionHeritageTowns={handleOnboardingHeritageTowns}
        onActionOpenMap={handleOnboardingOpenMap}
        onActionSearch={handleOnboardingSearch}
      />

      {/* Contextual First-Save Onboarding Toast */}
      <OnboardingToast
        isOpen={isFavToastOpen}
        onClose={() => setIsFavToastOpen(false)}
        message="¡Primer plan guardado!"
        subtext="En Evenjoy tus favoritos se conservan en tu dispositivo sin necesidad de crear cuenta ni contraseñas. Puedes verlos en la pestaña 'Guardados'."
        actionLabel="Ver guardados"
        onAction={() => navigateTo('saved', '/guardados')}
      />
    </div>
  );
}
export default App;
