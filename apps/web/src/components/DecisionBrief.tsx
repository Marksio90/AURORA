'use client';

import { DecisionBrief as DecisionBriefType } from '@/lib/types';
import { getEmotionalRiskColor } from '@/lib/utils';

interface DecisionBriefProps {
  brief: DecisionBriefType;
}

export default function DecisionBrief({ brief }: DecisionBriefProps) {
  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-fade-in">
      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
        ⚠️ {brief.disclaimer}
      </div>

      {/* Calm Step */}
      <div className="card bg-calm-50 border-calm-200">
        <h2 className="text-2xl font-bold text-calm-900 mb-4">
          🧘 First, Take a Moment
        </h2>
        <div className="space-y-3">
          <h3 className="text-xl font-semibold text-calm-800">{brief.calm_step.title}</h3>
          <p className="text-gray-700">{brief.calm_step.description}</p>
          <p className="text-sm text-calm-600">
            ⏱️ Duration: {brief.calm_step.duration_minutes} minute
            {brief.calm_step.duration_minutes !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Decision Options */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          💡 Your Options
        </h2>
        <div className="space-y-6">
          {brief.options.map((option, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-5 hover:border-calm-400 transition-colors"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">
                  {index + 1}. {option.title}
                </h3>
                <span
                  className={`badge ${getEmotionalRiskColor(option.emotional_risk)}
                             bg-opacity-10 border`}
                >
                  {option.emotional_risk} Risk
                </span>
              </div>

              <p className="text-gray-700 mb-4">{option.description}</p>

              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-2">
                  Possible Consequences:
                </h4>
                <ul className="space-y-1">
                  {option.consequences.map((consequence, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-calm-500">•</span>
                      <span>{consequence}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Control Question */}
      <div className="card bg-purple-50 border-purple-200">
        <h2 className="text-xl font-bold text-purple-900 mb-3">
          🤔 Reflect on This
        </h2>
        <p className="text-lg text-purple-800">{brief.control_question}</p>
      </div>

      {/* Next Check-in */}
      <div className="card bg-indigo-50 border-indigo-200">
        <h2 className="text-xl font-bold text-indigo-900 mb-3">
          ⏰ When to Return
        </h2>
        <p className="text-lg text-indigo-800 mb-2">
          {brief.next_check_in.suggestion}
        </p>
        <p className="text-sm text-indigo-600">{brief.next_check_in.reasoning}</p>
      </div>
    </div>
  );
}
