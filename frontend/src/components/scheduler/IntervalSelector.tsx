/**
 * Interval Selector Component - Select scraping interval
 */

import React from 'react';

interface IntervalSelectorProps {
  value: number;
  onChange: (hours: number) => void;
  disabled?: boolean;
}

export const IntervalSelector: React.FC<IntervalSelectorProps> = ({
  value,
  onChange,
  disabled,
}) => {
  const intervals = [
    { hours: 1, label: 'Every 1 hour', description: 'High frequency' },
    { hours: 2, label: 'Every 2 hours', description: 'Frequent updates' },
    { hours: 4, label: 'Every 4 hours', description: 'Regular updates' },
    { hours: 6, label: 'Every 6 hours', description: '4 times a day' },
    { hours: 8, label: 'Every 8 hours', description: '3 times a day' },
    { hours: 12, label: 'Every 12 hours', description: 'Twice a day' },
    { hours: 24, label: 'Every 24 hours', description: 'Once a day' },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {intervals.map((interval) => (
        <button
          key={interval.hours}
          onClick={() => onChange(interval.hours)}
          disabled={disabled}
          className={`
            p-4 rounded-xl border-2 transition-all text-left
            ${
              value === interval.hours
                ? 'border-teal-500 bg-teal-50 shadow-lg'
                : 'border-gray-200 bg-white hover:border-teal-300'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-2xl font-bold text-teal-600">
              {interval.hours}h
            </span>
            {value === interval.hours && (
              <span className="text-teal-500">✓</span>
            )}
          </div>
          <p className="text-sm font-semibold text-gray-900 mb-1">
            {interval.label}
          </p>
          <p className="text-xs text-gray-600">{interval.description}</p>
        </button>
      ))}
    </div>
  );
};
