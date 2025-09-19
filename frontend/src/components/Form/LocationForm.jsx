// frontend/src/components/Form/LocationForm.jsx
import React, { useState } from 'react';
import { MapPin, Search, Settings } from 'lucide-react';
import Button from '../UI/Button';
import FilterPanel from './FilterPanel';

const LocationForm = ({ onSubmit, loading = false }) => {
  const [location, setLocation] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    radius_km: 50,
    budget: 5000000,
    station_type: 'fast',
    max_recommendations: 5
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!location.trim()) {
      alert('Please enter a location');
      return;
    }

    onSubmit({
      location: location.trim(),
      ...filters
    });
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Find Optimal Locations</h2>
        <p className="text-sm text-gray-600">Enter a location in Tamil Nadu to find the best EV charging station sites</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Location Input */}
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
            Target Location
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Chennai, Tamil Nadu"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
            />
          </div>
        </div>

        {/* Filter Toggle */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <Settings className="h-4 w-4" />
            <span>{showFilters ? 'Hide' : 'Show'} Advanced Options</span>
          </button>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <FilterPanel
            filters={filters}
            onChange={handleFilterChange}
            disabled={loading}
          />
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          loading={loading}
          className="w-full"
          icon={<Search className="h-4 w-4" />}
        >
          {loading ? 'Finding Locations...' : 'Find Optimal Locations'}
        </Button>
      </form>
    </div>
  );
};

export default LocationForm;





