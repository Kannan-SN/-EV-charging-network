// frontend/src/components/Form/FilterPanel.jsx
import React from 'react';

const FilterPanel = ({ filters, onChange, disabled = false }) => {
  const stationTypes = [
    { value: 'fast', label: 'Fast Charging (DC)' },
    { value: 'regular', label: 'Regular Charging (AC)' },
    { value: 'ultra_fast', label: 'Ultra Fast Charging' }
  ];

  const budgetOptions = [
    { value: 2500000, label: '₹25 Lakhs' },
    { value: 5000000, label: '₹50 Lakhs' },
    { value: 7500000, label: '₹75 Lakhs' },
    { value: 10000000, label: '₹1 Crore' }
  ];

  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-4">
      <h3 className="text-sm font-medium text-gray-700">Advanced Options</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Search Radius */}
        <div>
          <label htmlFor="radius" className="block text-sm font-medium text-gray-700 mb-1">
            Search Radius
          </label>
          <div className="relative">
            <input
              id="radius"
              type="range"
              min="10"
              max="200"
              step="10"
              value={filters.radius_km}
              onChange={(e) => onChange('radius_km', parseInt(e.target.value))}
              disabled={disabled}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>10km</span>
              <span className="font-medium">{filters.radius_km}km</span>
              <span>200km</span>
            </div>
          </div>
        </div>

        {/* Budget */}
        <div>
          <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-1">
            Budget
          </label>
          <select
            id="budget"
            value={filters.budget}
            onChange={(e) => onChange('budget', parseInt(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
          >
            {budgetOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Station Type */}
        <div>
          <label htmlFor="stationType" className="block text-sm font-medium text-gray-700 mb-1">
            Station Type
          </label>
          <select
            id="stationType"
            value={filters.station_type}
            onChange={(e) => onChange('station_type', e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
          >
            {stationTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Max Recommendations */}
        <div>
          <label htmlFor="maxRecommendations" className="block text-sm font-medium text-gray-700 mb-1">
            Max Results
          </label>
          <select
            id="maxRecommendations"
            value={filters.max_recommendations}
            onChange={(e) => onChange('max_recommendations', parseInt(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
          >
            {[1, 3, 5, 10, 20].map(num => (
              <option key={num} value={num}>
                {num} location{num !== 1 ? 's' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;