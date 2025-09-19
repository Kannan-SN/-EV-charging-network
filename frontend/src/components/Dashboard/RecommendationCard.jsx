
import React from 'react';
import { TrendingUp, Zap, MapPin, DollarSign, Users } from 'lucide-react';

const RecommendationCard = ({ recommendation, rank }) => {
  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-blue-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 8) return 'bg-green-100';
    if (score >= 6) return 'bg-blue-100';
    if (score >= 4) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow p-4">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded-full">
              #{rank}
            </span>
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {recommendation.location.name}
            </h3>
          </div>
          <p className="text-xs text-gray-600 truncate">{recommendation.location.address}</p>
        </div>
        <div className="text-right ml-2">
          <div className={`text-lg font-bold ${getScoreColor(recommendation.scores.overall_score)}`}>
            {recommendation.scores.overall_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">Score</div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div className="flex items-center space-x-1">
          <TrendingUp className="h-3 w-3 text-blue-500" />
          <span className="text-gray-600">Traffic:</span>
          <span className="font-medium">{recommendation.scores.traffic_score.toFixed(1)}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Zap className="h-3 w-3 text-yellow-500" />
          <span className="text-gray-600">Grid:</span>
          <span className="font-medium">{recommendation.scores.grid_capacity.toFixed(1)}</span>
        </div>
        <div className="flex items-center space-x-1">
          <MapPin className="h-3 w-3 text-red-500" />
          <span className="text-gray-600">Competition:</span>
          <span className="font-medium">{recommendation.scores.competition_gap.toFixed(1)}</span>
        </div>
        <div className="flex items-center space-x-1">
          <DollarSign className="h-3 w-3 text-green-500" />
          <span className="text-gray-600">ROI:</span>
          <span className="font-medium">{recommendation.scores.roi_potential.toFixed(1)}</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="border-t pt-2 space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-gray-600">Monthly Revenue:</span>
          <span className="font-medium text-green-600">
            ₹{(recommendation.insights.estimated_monthly_revenue / 100000).toFixed(1)}L
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Payback:</span>
          <span className="font-medium">
            {recommendation.insights.payback_period_months} months
          </span>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;