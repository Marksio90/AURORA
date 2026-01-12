'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DecisionForm from '@/components/DecisionForm';
import { apiClient } from '@/lib/api';
import { CreateDecisionSessionRequest } from '@/lib/types';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (request: CreateDecisionSessionRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const session = await apiClient.createDecisionSession(request);
      router.push(`/session/${session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nie udało się utworzyć sesji');
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Podejmuj spokojniejsze decyzje
            <br />
            <span className="text-calm-600">w 60 sekund</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Odpowiedz na 3 pytania. Otrzymaj jasną Analizę Decyzji: możliwe kierunki,
            konsekwencje i spokojny następny krok.
          </p>
        </div>

        {/* Wyświetlanie błędów */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 animate-slide-up">
            <p className="text-red-800">
              <strong>Błąd:</strong> {error}
            </p>
          </div>
        )}

        {/* Decision Form */}
        <DecisionForm onSubmit={handleSubmit} isLoading={isLoading} />

        {/* Jak to działa */}
        <div className="mt-16 grid md:grid-cols-3 gap-8 animate-slide-up">
          <div className="text-center">
            <div className="bg-calm-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">📝</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">3 pytania</h3>
            <p className="text-sm text-gray-600">
              Opisz swoją decyzję, opcje i poziom stresu
            </p>
          </div>

          <div className="text-center">
            <div className="bg-calm-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🤖</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">5 agentów AI</h3>
            <p className="text-sm text-gray-600">
              Wyspecjalizowani agenci analizują kontekst, opcje i stan emocjonalny
            </p>
          </div>

          <div className="text-center">
            <div className="bg-calm-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">✨</span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Analiza Decyzji</h3>
            <p className="text-sm text-gray-600">
              Jasne ścieżki, konsekwencje, krok uspokajający i przypomnienie
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
