'use client';

import Link from 'next/link';
import { DecisionSessionResponse } from '@/lib/types';
import { formatDate, getStressLevelColor, truncate } from '@/lib/utils';

interface HistoryListProps {
  sessions: DecisionSessionResponse[];
}

export default function HistoryList({ sessions }: HistoryListProps) {
  if (sessions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No decision sessions yet.</p>
        <Link href="/" className="text-calm-600 hover:text-calm-700 mt-4 inline-block">
          Create your first decision session →
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sessions.map((session) => (
        <Link
          key={session.id}
          href={`/session/${session.id}`}
          className="card hover:shadow-xl transition-shadow cursor-pointer block"
        >
          <div className="flex items-start justify-between gap-4 mb-3">
            <div className="flex-1">
              <p className="text-gray-700 font-medium mb-1">
                {truncate(session.input.context, 120)}
              </p>
              <p className="text-sm text-gray-500">
                {formatDate(session.created_at)}
              </p>
            </div>
            <span
              className={`badge ${getStressLevelColor(session.stress_level)} border`}
            >
              Stress: {session.stress_level}/10
            </span>
          </div>

          <div className="flex gap-2 text-sm text-gray-600">
            <span className="bg-gray-100 px-2 py-1 rounded">
              {session.output.options.length} options
            </span>
            <span className="bg-calm-100 text-calm-700 px-2 py-1 rounded">
              {session.output.calm_step.type}
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}
