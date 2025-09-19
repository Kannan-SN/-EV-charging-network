
import React from 'react';

const MetricsCard = ({ title, value, suffix, icon, color = 'blue', truncate = false }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <div className="flex items-baseline">
            <p className={`text-2xl font-bold ${truncate ? 'truncate' : ''} ${
              color === 'green' ? 'text-green-600' : 
              color === 'blue' ? 'text-blue-600' :
              color === 'purple' ? 'text-purple-600' : 'text-gray-900'
            }`}>
              {value}
            </p>
            {suffix && (
              <span className="ml-1 text-sm text-gray-500">{suffix}</span>
            )}
          </div>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default MetricsCard;