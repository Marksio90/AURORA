'use client';

import { useEffect, useState } from 'react';
import HistoryList from '@/components/HistoryList';
import { apiClient } from '@/lib/api';
import { ListDecisionSessionsResponse } from '@/lib/types';

export default function HistoryPage() {
  const [data, setData] = useState<ListDecisionSessionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await apiClient.listDecisionSessions();
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-calm-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Ładowanie historii...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Spróbuj Ponownie
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Historia Decyzji
          </h1>
          <p className="text-gray-600">
            Przejrzyj swoje poprzednie sesje decyzyjne i analizy.
          </p>
        </div>

        {data && (
          <div className="animate-slide-up">
            <div className="mb-4 text-gray-600">
              Łączna liczba sesji: <strong>{data.total}</strong>
            </div>
            <HistoryList sessions={data.sessions} />
          </div>
        )}
      </div>
    </div>
  );
}
