import React, { useState } from 'react';
import { Search, MapPin, BarChart3, TrendingUp } from 'lucide-react';
import MetricsCard from './MetricsCard';
import RecommendationCard from './RecommendationCard';
import LocationForm from '../Form/LocationForm';
import { useOptimization } from '../../hooks/useOptimization';
import MapView from '../map/MapView';

const Dashboard = () => {
  const [location, setLocation] = useState('');
  const { recommendations, loading, error, optimizeLocation } = useOptimization();

  const handleOptimize = async (formData) => {
    await optimizeLocation(formData);
  };

  const overallMetrics = recommendations.length > 0 ? {
    averageScore: (recommendations.reduce((sum, rec) => sum + rec.scores.overall_score, 0) / recommendations.length).toFixed(1),
    totalLocations: recommendations.length,
    bestLocation: recommendations[0]?.location.name || 'N/A',
    estimatedRevenue: recommendations.reduce((sum, rec) => sum + (rec.insights.estimated_monthly_revenue || 0), 0)
  } : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
   
        <div className="mb-8">
          <LocationForm onSubmit={handleOptimize} loading={loading} />
        </div>

        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        
        {overallMetrics && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricsCard
              title="Average Score"
              value={overallMetrics.averageScore}
              suffix="/10"
              icon={<BarChart3 className="h-6 w-6" />}
              color="green"
            />
            <MetricsCard
              title="Locations Found"
              value={overallMetrics.totalLocations}
              icon={<MapPin className="h-6 w-6" />}
              color="blue"
            />
            <MetricsCard
              title="Best Location"
              value={overallMetrics.bestLocation}
              icon={<TrendingUp className="h-6 w-6" />}
              color="purple"
              truncate
            />
            <MetricsCard
              title="Total Revenue"
              value={`₹${(overallMetrics.estimatedRevenue / 100000).toFixed(1)}L`}
              suffix="/month"
              icon={<TrendingUp className="h-6 w-6" />}
              color="green"
            />
          </div>
        )}

  
        {recommendations.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
    
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <div className="p-4 border-b bg-gray-50">
                <h2 className="text-lg font-semibold text-gray-900">Location Map</h2>
                <p className="text-sm text-gray-600">Optimal charging station locations</p>
              </div>
              <div className="h-96">
                <MapView recommendations={recommendations} />
              </div>
            </div>

         
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recommendations</h2>
                <span className="text-sm text-gray-600">{recommendations.length} locations</span>
              </div>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {recommendations.map((recommendation, index) => (
                  <RecommendationCard
                    key={index}
                    recommendation={recommendation}
                    rank={index + 1}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;