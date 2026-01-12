'use client';

import { useState } from 'react';
import { CreateDecisionSessionRequest } from '@/lib/types';

interface DecisionFormProps {
  onSubmit: (request: CreateDecisionSessionRequest) => Promise<void>;
  isLoading: boolean;
}

export default function DecisionForm({ onSubmit, isLoading }: DecisionFormProps) {
  const [context, setContext] = useState('');
  const [options, setOptions] = useState('');
  const [stressLevel, setStressLevel] = useState(5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      context,
      options,
      stress_level: stressLevel,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto">
      {/* Question 1: Context */}
      <div className="animate-slide-up">
        <label htmlFor="context" className="block text-lg font-medium text-gray-700 mb-2">
          1. Przed jaką decyzją stoisz?
        </label>
        <textarea
          id="context"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Opisz decyzję, którą chcesz podjąć..."
          className="input-field min-h-[120px] resize-y"
          required
          minLength={10}
          maxLength={2000}
        />
        <p className="text-sm text-gray-500 mt-1">
          {context.length}/2000 znaków
        </p>
      </div>

      {/* Question 2: Options */}
      <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
        <label htmlFor="options" className="block text-lg font-medium text-gray-700 mb-2">
          2. Jakie opcje rozważasz?
        </label>
        <textarea
          id="options"
          value={options}
          onChange={(e) => setOptions(e.target.value)}
          placeholder="Wymień opcje, które rozważasz..."
          className="input-field min-h-[100px] resize-y"
          required
          minLength={5}
          maxLength={1000}
        />
        <p className="text-sm text-gray-500 mt-1">
          Oddziel opcje przecinkami lub nowymi liniami
        </p>
      </div>

      {/* Question 3: Stress Level */}
      <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <label htmlFor="stress" className="block text-lg font-medium text-gray-700 mb-2">
          3. Jak bardzo jesteś zestresowany? (1 = spokojny, 10 = przytłoczony)
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            id="stress"
            min="1"
            max="10"
            value={stressLevel}
            onChange={(e) => setStressLevel(parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-calm-600"
          />
          <span className="text-2xl font-bold text-calm-700 w-12 text-center">
            {stressLevel}
          </span>
        </div>
        <div className="flex justify-between text-sm text-gray-500 mt-2">
          <span>😌 Spokojny</span>
          <span>😰 Przytłoczony</span>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !context || !options}
        className="btn-primary w-full text-lg py-4 animate-slide-up"
        style={{ animationDelay: '0.3s' }}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Przetwarzanie...
          </span>
        ) : (
          'Otrzymaj Analizę Decyzji'
        )}
      </button>
    </form>
  );
}
