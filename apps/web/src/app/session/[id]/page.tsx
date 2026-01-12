'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DecisionBrief from '@/components/DecisionBrief';
import { apiClient } from '@/lib/api';
import { DecisionSessionResponse } from '@/lib/types';
import { formatDate, getStressLevelColor } from '@/lib/utils';

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const [session, setSession] = useState<DecisionSessionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const sessionId = params.id as string;
        const data = await apiClient.getDecisionSession(sessionId);
        setSession(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load session');
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-calm-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Ładowanie analizy decyzji...</p>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Sesja nie została znaleziona'}</p>
          <button onClick={() => router.push('/')} className="btn-primary">
            Utwórz Nową Sesję
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Session Header */}
        <div className="mb-8 animate-fade-in">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Analiza Decyzji
              </h1>
              <p className="text-gray-600">{formatDate(session.created_at)}</p>
            </div>
            <span className={`badge ${getStressLevelColor(session.stress_level)} border`}>
              Stres: {session.stress_level}/10
            </span>
          </div>

          {/* Original Context */}
          <div className="card bg-gray-50">
            <h3 className="font-semibold text-gray-700 mb-2">Kontekst Twojej Decyzji:</h3>
            <p className="text-gray-600 mb-3">{session.input.context}</p>
            <h3 className="font-semibold text-gray-700 mb-2">Rozważane Opcje:</h3>
            <p className="text-gray-600">{session.input.options}</p>
          </div>
        </div>

        {/* Decision Brief */}
        <DecisionBrief brief={session.output} />

        {/* Actions */}
        <div className="mt-8 flex gap-4 justify-center">
          <button onClick={() => router.push('/')} className="btn-primary">
            Utwórz Nową Sesję
          </button>
          <button onClick={() => router.push('/history')} className="btn-secondary">
            Zobacz Historię
          </button>
        </div>
      </div>
    </div>
  );
}
