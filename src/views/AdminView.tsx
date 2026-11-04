import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Database, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  GitMerge, 
  ExternalLink,
  Search,
  Filter,
  ArrowLeft,
  Calendar,
  Check,
  X
} from 'lucide-react';
import { CulturalEvent, SourceEntity } from '../types';
import { SOURCES_CATALOG } from '../data/sources';
import { identifyDuplicateGroups } from '../services/deduplication';

interface AdminViewProps {
  events: CulturalEvent[];
  onUpdateEventStatus: (eventId: string, newStatus: CulturalEvent['status']) => void;
  onNavigateHome: () => void;
}

export const AdminView: React.FC<AdminViewProps> = ({
  events,
  onUpdateEventStatus,
  onNavigateHome,
}) => {
  const [sources, setSources] = useState<SourceEntity[]>(SOURCES_CATALOG);
  const [activeTab, setActiveTab] = useState<'sources' | 'deduplication' | 'events'>('sources');
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncFeedback, setSyncFeedback] = useState<string | null>(null);

  const deduplicationGroups = identifyDuplicateGroups(events);
  const mergedGroupsCount = deduplicationGroups.filter(g => g.detected_duplicates.length > 0).length;

  const handleSimulateSync = () => {
    setIsSyncing(true);
    setSyncFeedback(null);
    setTimeout(() => {
      setIsSyncing(false);
      setSyncFeedback('¡Sincronización completada exitosamente! 18 fuentes verificadas.');
      setTimeout(() => setSyncFeedback(null), 4000);
    }, 1200);
  };

  const activeEventsCount = events.filter(e => e.status === 'ACTIVE').length;
  const avgReliability = Math.round(
    sources.reduce((acc, s) => acc + s.reliability_score, 0) / sources.length
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8 pb-20">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-200 pb-4">
        <div>
          <button
            type="button"
            onClick={onNavigateHome}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-zinc-500 hover:text-zinc-900 mb-2 cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Volver a Evenjoy</span>
          </button>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-zinc-900 text-white">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-black text-zinc-900">
              Panel de Fuentes y Verificación
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-zinc-500 mt-1">
            Gestión de fuentes culturales, confiabilidad de datos y motor de deduplicación canónica
          </p>
        </div>

        <button
          type="button"
          onClick={handleSimulateSync}
          disabled={isSyncing}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-900 text-white text-xs font-bold hover:bg-black transition-all cursor-pointer shadow-xs disabled:opacity-60 min-h-[44px]"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>{isSyncing ? 'Sincronizando fuentes...' : 'Sincronizar fuentes ahora'}</span>
        </button>
      </div>

      {syncFeedback && (
        <div className="p-3.5 rounded-2xl bg-forest-50 border border-forest-200 text-forest-700 text-xs font-bold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-forest-700" />
          <span>{syncFeedback}</span>
        </div>
      )}

      {/* KPI Stats (PRD Section 44) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-zinc-200 shadow-xs">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider block">
            Eventos Activos
          </span>
          <span className="text-2xl sm:text-3xl font-black text-zinc-900 mt-1 block tabular-nums">
            {activeEventsCount}
          </span>
          <span className="text-xs text-forest-700 font-semibold mt-1 block">
            100% verificados con fuente
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-zinc-200 shadow-xs">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider block">
            Fuentes Conectadas
          </span>
          <span className="text-2xl sm:text-3xl font-black text-zinc-900 mt-1 block tabular-nums">
            {sources.length}
          </span>
          <span className="text-xs text-zinc-500 font-semibold mt-1 block">
            Alcaldías, Cajas, Museos, Salas
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-zinc-200 shadow-xs">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider block">
            Score Confiabilidad
          </span>
          <span className="text-2xl sm:text-3xl font-black text-brand-600 mt-1 block tabular-nums">
            {avgReliability}%
          </span>
          <span className="text-xs text-zinc-500 font-semibold mt-1 block">
            Promedio de confianza
          </span>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-zinc-200 shadow-xs">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider block">
            Grupos Deduplicados
          </span>
          <span className="text-2xl sm:text-3xl font-black text-amber-600 mt-1 block tabular-nums">
            {mergedGroupsCount}
          </span>
          <span className="text-xs text-zinc-500 font-semibold mt-1 block">
            Multi-fuente unificada
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-zinc-200 gap-4">
        <button
          type="button"
          onClick={() => setActiveTab('sources')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all cursor-pointer min-h-[44px] ${
            activeTab === 'sources'
              ? 'border-brand-500 text-brand-600'
              : 'border-transparent text-zinc-500 hover:text-zinc-800'
          }`}
        >
          Fuentes Oficiales ({sources.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('deduplication')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all cursor-pointer min-h-[44px] ${
            activeTab === 'deduplication'
              ? 'border-brand-500 text-brand-600'
              : 'border-transparent text-zinc-500 hover:text-zinc-800'
          }`}
        >
          Inspector de Deduplicación ({mergedGroupsCount})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('events')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all cursor-pointer min-h-[44px] ${
            activeTab === 'events'
              ? 'border-brand-500 text-brand-600'
              : 'border-transparent text-zinc-500 hover:text-zinc-800'
          }`}
        >
          Moderación de Eventos ({events.length})
        </button>
      </div>

      {/* Tab 1: Sources Monitor */}
      {activeTab === 'sources' && (
        <div className="bg-white rounded-2xl border border-zinc-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-sand-50 border-b border-zinc-200 text-zinc-500 font-bold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="p-3.5">Fuente</th>
                  <th className="p-3.5">Tipo</th>
                  <th className="p-3.5">Método</th>
                  <th className="p-3.5">Última Sync</th>
                  <th className="p-3.5 text-center">Confiabilidad</th>
                  <th className="p-3.5 text-center">Activos</th>
                  <th className="p-3.5 text-right">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {sources.map((s) => (
                  <tr key={s.id} className="hover:bg-sand-50/60 transition-colors">
                    <td className="p-3.5 font-bold text-zinc-900">
                      <div>{s.name}</div>
                      {s.municipality && (
                        <span className="text-[11px] font-normal text-zinc-500">
                          {s.municipality} ({s.subregion})
                        </span>
                      )}
                    </td>
                    <td className="p-3.5 capitalize text-zinc-600">
                      {s.type.replace('_', ' ')}
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded-md font-bold uppercase text-[10px] bg-zinc-100 text-zinc-700">
                        {s.ingestion_method}
                      </span>
                    </td>
                    <td className="p-3.5 text-zinc-500 text-xs">
                      {s.last_successful_sync.split('T')[0]} {s.last_successful_sync.split('T')[1]?.slice(0, 5)}
                    </td>
                    <td className="p-3.5 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-xs ${
                        s.reliability_score >= 95
                          ? 'bg-forest-100 text-forest-700'
                          : s.reliability_score >= 90
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {s.reliability_score}%
                      </span>
                    </td>
                    <td className="p-3.5 text-center font-bold text-zinc-800">
                      {s.active_events_count}
                    </td>
                    <td className="p-3.5 text-right">
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-bold text-brand-600 hover:underline"
                      >
                        <span>Visitar</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Deduplication Inspector */}
      {activeTab === 'deduplication' && (
        <div className="space-y-4">
          <p className="text-xs text-zinc-600 leading-relaxed bg-sand-50 p-4 rounded-2xl border border-zinc-200">
            <strong>Arquitectura de Deduplicación (Sección 5):</strong> Compara títulos, fechas, municipios, recintos y organizadores mediante ponderación Jaro-Winkler y Levenshtein. Cuando la similitud supera 0.78, se unifica en un <em>Evento Canónico</em> preservando las fuentes secundarias para total transparencia.
          </p>

          <div className="space-y-4">
            {deduplicationGroups.map((group, idx) => {
              const hasDuplicates = group.detected_duplicates.length > 0;
              return (
                <div
                  key={idx}
                  className={`p-5 rounded-2xl border transition-all ${
                    hasDuplicates ? 'bg-white border-amber-300 shadow-sm' : 'bg-white border-zinc-200'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-100 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-zinc-900 text-white">
                          Evento Canónico
                        </span>
                        {hasDuplicates && (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-800 flex items-center gap-1">
                            <GitMerge className="w-3 h-3" />
                            {group.detected_duplicates.length} Fuentes unificadas
                          </span>
                        )}
                      </div>
                      <h3 className="font-bold text-base text-zinc-900 mt-1">
                        {group.canonical_event.title}
                      </h3>
                      <p className="text-xs text-zinc-500">
                        {group.canonical_event.municipality} · {group.canonical_event.venue_name} · {group.canonical_event.start_date}
                      </p>
                    </div>

                    <div className="text-xs text-zinc-500">
                      Fuente primaria: <strong className="text-zinc-800 font-bold">{group.canonical_event.source_name}</strong>
                    </div>
                  </div>

                  {/* Secondary duplicates detected */}
                  {hasDuplicates && (
                    <div className="mt-3 pt-2 text-xs space-y-2">
                      <span className="font-bold text-zinc-600 block text-[11px] uppercase tracking-wider">
                        Fuentes secundarias fusionadas en el canónico:
                      </span>
                      {group.detected_duplicates.map((dup, dIdx) => (
                        <div
                          key={dIdx}
                          className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 p-2.5 rounded-xl bg-sand-50 border border-zinc-200/80 text-zinc-700"
                        >
                          <div>
                            <span className="font-semibold text-zinc-900">{dup.detected_title}</span>
                            <span className="text-zinc-500 block text-[11px]">
                              Fuente: {dup.source_name} ({dup.source_type})
                            </span>
                          </div>
                          <div className="flex items-center gap-3 shrink-0">
                            <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-900 font-bold text-[11px]">
                              Similitud: {Math.round(dup.similarity_score * 100)}%
                            </span>
                            <a
                              href={dup.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-brand-600 font-bold hover:underline inline-flex items-center gap-0.5"
                            >
                              <span>Ver</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Events Moderation & Status */}
      {activeTab === 'events' && (
        <div className="bg-white rounded-2xl border border-zinc-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-sand-50 border-b border-zinc-200 text-zinc-500 font-bold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="p-3.5">Título & Municipio</th>
                  <th className="p-3.5">Fecha</th>
                  <th className="p-3.5">Categoría</th>
                  <th className="p-3.5">Estado</th>
                  <th className="p-3.5 text-right">Cambiar Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {events.map((evt) => (
                  <tr key={evt.event_id} className="hover:bg-sand-50/60 transition-colors">
                    <td className="p-3.5">
                      <span className="font-bold text-zinc-900 block">{evt.title}</span>
                      <span className="text-xs text-zinc-600 font-medium">
                        {evt.municipality} · {evt.venue_name}
                      </span>
                    </td>
                    <td className="p-3.5 text-zinc-600 text-xs whitespace-nowrap">
                      {evt.start_date}
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded-md font-bold text-[11px] bg-sand-100 text-zinc-700">
                        {evt.category}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-xs ${
                        evt.status === 'ACTIVE'
                          ? 'bg-forest-100 text-forest-700'
                          : evt.status === 'CANCELLED'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {evt.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right space-x-1">
                      {evt.status === 'ACTIVE' ? (
                        <button
                          type="button"
                          onClick={() => onUpdateEventStatus(evt.event_id, 'CANCELLED')}
                          className="px-2.5 py-1 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 text-xs font-bold cursor-pointer"
                        >
                          Cancelar
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => onUpdateEventStatus(evt.event_id, 'ACTIVE')}
                          className="px-2.5 py-1 rounded-lg border border-forest-200 text-forest-700 hover:bg-forest-50 text-xs font-bold cursor-pointer"
                        >
                          Activar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
