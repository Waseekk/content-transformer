/**
 * Timeline Component - Visual history of scheduled runs
 */

import React from 'react';
import { format } from 'date-fns';

interface TimelineEntry {
  run_time: string;
  articles_count: number;
  duration_seconds: number;
  status: 'success' | 'failed';
  error?: string;
}

interface TimelineProps {
  history: TimelineEntry[];
}

export const Timeline: React.FC<TimelineProps> = ({ history }) => {
  if (history.length === 0) {
    return (
      <div className="bg-white rounded-xl border-2 border-gray-200 p-12">
        <div className="text-center text-gray-400">
          <p className="text-lg font-medium mb-2">No run history yet</p>
          <p className="text-sm">
            History will appear here after the scheduler runs
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        📊 Run History
      </h3>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Timeline Entries */}
        <div className="space-y-6">
          {history.map((entry, idx) => {
            const isSuccess = entry.status === 'success';
            const runDate = new Date(entry.run_time);

            return (
              <div key={idx} className="relative flex gap-6">
                {/* Timeline Dot */}
                <div
                  className={`
                    relative z-10 flex-shrink-0 w-12 h-12 rounded-full
                    flex items-center justify-center
                    ${
                      isSuccess
                        ? 'bg-green-500 shadow-lg shadow-green-200'
                        : 'bg-red-500 shadow-lg shadow-red-200'
                    }
                  `}
                >
                  <span className="text-white text-lg">
                    {isSuccess ? '✓' : '✗'}
                  </span>
                </div>

                {/* Content Card */}
                <div
                  className={`
                    flex-1 p-4 rounded-lg border-2
                    ${
                      isSuccess
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }
                  `}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">
                        {format(runDate, 'MMM dd, yyyy - hh:mm a')}
                      </p>
                      <p className="text-xs text-gray-600">
                        {format(runDate, 'EEEE')}
                      </p>
                    </div>

                    {isSuccess && (
                      <span className="px-3 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
                        {entry.articles_count} articles
                      </span>
                    )}
                  </div>

                  <div className="flex gap-4 text-sm text-gray-700">
                    <span>
                      ⏱️ Duration: {entry.duration_seconds.toFixed(1)}s
                    </span>
                    {isSuccess ? (
                      <span className="text-green-700 font-medium">
                        ✓ Success
                      </span>
                    ) : (
                      <span className="text-red-700 font-medium">
                        ✗ Failed
                      </span>
                    )}
                  </div>

                  {entry.error && (
                    <div className="mt-2 p-2 bg-red-100 rounded text-xs text-red-700">
                      Error: {entry.error}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
