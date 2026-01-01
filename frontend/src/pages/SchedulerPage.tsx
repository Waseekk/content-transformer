/**
 * Scheduler Page - Automated scraping scheduler
 */

import React, { useState } from 'react';
import {
  useSchedulerStatus,
  useStartScheduler,
  useStopScheduler,
  useSchedulerHistory,
} from '../hooks/useScheduler';
import { IntervalSelector } from '../components/scheduler/IntervalSelector';
import { Timeline } from '../components/scheduler/Timeline';
import toast from 'react-hot-toast';

export const SchedulerPage = () => {
  const { data: status, isLoading: statusLoading } = useSchedulerStatus();
  const { data: history } = useSchedulerHistory(20);
  const startScheduler = useStartScheduler();
  const stopScheduler = useStopScheduler();

  const [selectedInterval, setSelectedInterval] = useState(6);

  const isRunning = status?.is_running || false;

  const handleStart = () => {
    startScheduler.mutate(selectedInterval);
  };

  const handleStop = () => {
    stopScheduler.mutate();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ⏰ Automated Scheduler
        </h1>
        <p className="text-gray-600">
          Configure automated scraping to run at regular intervals
        </p>
      </div>

      {/* Status Banner */}
      {!statusLoading && (
        <div
          className={`
            mb-6 rounded-xl p-6 border-2
            ${
              isRunning
                ? 'bg-green-50 border-green-300'
                : 'bg-gray-50 border-gray-200'
            }
          `}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span
                  className={`
                    w-3 h-3 rounded-full animate-pulse
                    ${isRunning ? 'bg-green-500' : 'bg-gray-400'}
                  `}
                ></span>
                <h3 className="text-xl font-bold text-gray-900">
                  {isRunning ? 'Scheduler Active' : 'Scheduler Inactive'}
                </h3>
              </div>

              {isRunning && status && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Interval</p>
                    <p className="text-lg font-semibold text-gray-900">
                      Every {status.interval_hours} hours
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-600 mb-1">Next Run</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {status.time_until_next || 'Calculating...'}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-600 mb-1">Total Runs</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {status.run_count}
                    </p>
                  </div>
                </div>
              )}

              {!isRunning && (
                <p className="text-gray-600">
                  Select an interval below and click "Start Scheduler" to begin automated scraping
                </p>
              )}
            </div>

            {/* Start/Stop Button */}
            <button
              onClick={isRunning ? handleStop : handleStart}
              disabled={startScheduler.isPending || stopScheduler.isPending}
              className={`
                px-8 py-4 rounded-lg font-bold transition-all
                ${
                  isRunning
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-teal-500 hover:bg-teal-600 text-white hover:shadow-xl transform hover:scale-105'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {startScheduler.isPending || stopScheduler.isPending ? (
                <span className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  {isRunning ? 'Stopping...' : 'Starting...'}
                </span>
              ) : isRunning ? (
                '⏹️ Stop Scheduler'
              ) : (
                '▶️ Start Scheduler'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Interval Selection */}
      {!isRunning && (
        <div className="mb-8 bg-white rounded-xl p-6 border-2 border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Select Scraping Interval
          </h3>
          <IntervalSelector
            value={selectedInterval}
            onChange={setSelectedInterval}
            disabled={isRunning}
          />
        </div>
      )}

      {/* Timeline */}
      {history && history.length > 0 && (
        <div className="mb-8">
          <Timeline history={history} />
        </div>
      )}

      {/* Help Section */}
      <div className="bg-blue-50 rounded-xl p-6 border-2 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          💡 How the Scheduler Works
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start gap-2">
            <span className="font-bold">•</span>
            <span>
              The scheduler automatically runs the scraper at your selected interval
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold">•</span>
            <span>
              All scraped articles are saved to your database and viewable on the Articles page
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold">•</span>
            <span>
              You can start/stop the scheduler at any time without losing your settings
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold">•</span>
            <span>
              The timeline below shows the history of past runs with success/failure status
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};
