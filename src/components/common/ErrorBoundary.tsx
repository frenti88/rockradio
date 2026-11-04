import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Evenjoy ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-sand-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-zinc-200/80 shadow-card text-center space-y-5">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 border border-amber-200/60 text-amber-600 mx-auto flex items-center justify-center">
              <AlertTriangle className="w-7 h-7" />
            </div>

            <div className="space-y-2">
              <h1 className="text-xl font-bold text-zinc-900">
                No pudimos cargar esta vista
              </h1>
              <p className="text-sm text-zinc-600 leading-relaxed">
                Ocurrió un problema temporal al renderizar esta sección. Tus planes guardados y el resto de la cartelera cultural de Antioquia siguen a salvo.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-2.5 pt-2">
              <button
                type="button"
                onClick={this.handleReset}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-zinc-900 hover:bg-black text-white text-xs font-bold transition-all cursor-pointer shadow-sm"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Volver al inicio</span>
              </button>
              <button
                type="button"
                onClick={this.handleReload}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-sand-100 hover:bg-sand-200 text-zinc-800 text-xs font-bold transition-all cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reintentar carga</span>
              </button>
            </div>

            {this.state.error && (
              <details className="text-left text-[11px] text-zinc-500 bg-sand-50 p-3 rounded-xl border border-zinc-200/60 mt-4 overflow-x-auto">
                <summary className="cursor-pointer font-semibold text-zinc-600">
                  Detalles técnicos
                </summary>
                <p className="mt-2 font-mono whitespace-pre-wrap text-zinc-700">
                  {this.state.error.message}
                </p>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
