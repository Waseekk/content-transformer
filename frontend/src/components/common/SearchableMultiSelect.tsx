/**
 * SearchableMultiSelect - Dropdown with search and checkboxes
 */

import React, { useState, useRef, useEffect } from 'react';
import { HiChevronDown, HiSearch, HiX } from 'react-icons/hi';

interface Option {
  value: string;
  label: string;
  count?: number;
}

interface SearchableMultiSelectProps {
  options: Option[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  label?: string;
}

export const SearchableMultiSelect: React.FC<SearchableMultiSelectProps> = ({
  options,
  selected,
  onChange,
  placeholder = 'Select...',
  label,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sort options alphabetically
  const sortedOptions = [...options].sort((a, b) =>
    a.label.localeCompare(b.label)
  );

  // Filter options by search
  const filteredOptions = sortedOptions.filter(option =>
    option.label.toLowerCase().includes(search.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleToggle = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter(v => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const handleSelectAll = () => {
    if (selected.length === filteredOptions.length) {
      onChange([]);
    } else {
      onChange(filteredOptions.map(o => o.value));
    }
  };

  const handleClearAll = () => {
    onChange([]);
    setSearch('');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {selected.length > 0 && `(${selected.length} selected)`}
        </label>
      )}

      {/* Dropdown Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2 text-left bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent flex items-center justify-between min-h-[42px]"
      >
        <span className={`flex-1 ${selected.length === 0 ? 'text-gray-400' : 'text-gray-700'}`}>
          {selected.length === 0 ? (
            placeholder
          ) : (
            <span className="flex flex-wrap gap-1">
              {selected.slice(0, 3).map((val, idx) => (
                <span key={val} className="inline-flex items-center px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full">
                  {val}
                </span>
              ))}
              {selected.length > 3 && (
                <span className="inline-flex items-center px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                  +{selected.length - 3} more
                </span>
              )}
            </span>
          )}
        </span>
        <HiChevronDown className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ml-2 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-hidden">
          {/* Search Input */}
          <div className="p-2 border-b border-gray-200">
            <div className="relative">
              <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search sources..."
                className="w-full pl-9 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
              {search && (
                <button
                  onClick={() => setSearch('')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <HiX className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="px-3 py-2 border-b border-gray-200 flex gap-3 text-xs">
            <button
              onClick={handleSelectAll}
              className="text-teal-600 hover:text-teal-700 font-medium"
            >
              {selected.length === filteredOptions.length ? 'Deselect All' : 'Select All'}
            </button>
            {selected.length > 0 && (
              <button
                onClick={handleClearAll}
                className="text-gray-500 hover:text-gray-700"
              >
                Clear
              </button>
            )}
            <span className="ml-auto text-gray-400">
              {filteredOptions.length} sources
            </span>
          </div>

          {/* Options List */}
          <div className="max-h-52 overflow-y-auto">
            {filteredOptions.length === 0 ? (
              <div className="px-4 py-3 text-sm text-gray-500 text-center">
                No sources found
              </div>
            ) : (
              filteredOptions.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selected.includes(option.value)}
                    onChange={() => handleToggle(option.value)}
                    className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                  />
                  <span className="ml-3 text-sm text-gray-700 flex-1 truncate">
                    {option.label}
                  </span>
                  {option.count !== undefined && (
                    <span className="ml-2 text-xs text-gray-400">
                      ({option.count})
                    </span>
                  )}
                </label>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
