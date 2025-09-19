
import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';


delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const LocationMarker = ({ recommendation, rank }) => {
  const { location, scores, insights } = recommendation;

  const getMarkerIcon = (score) => {
    const color = score >= 8 ? 'green' : score >= 6 ? 'orange' : 'red';
    return new L.Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });
  };

  return (
    <Marker
      position={[location.coordinates.latitude, location.coordinates.longitude]}
      icon={getMarkerIcon(scores.overall_score)}
    >
      <Popup className="custom-popup">
        <div className="p-3 min-w-64">
          <div className="flex items-center justify-between mb-2">
            <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded-full">
              #{rank}
            </span>
            <span className="text-lg font-bold text-green-600">
              {scores.overall_score.toFixed(1)}/10
            </span>
          </div>
          
          <h3 className="font-semibold text-gray-900 mb-1">{location.name}</h3>
          <p className="text-sm text-gray-600 mb-3">{location.address}</p>
          
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Daily Traffic:</span>
              <span className="font-medium">{insights.daily_traffic?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Monthly Revenue:</span>
              <span className="font-medium text-green-600">
                ₹{(insights.estimated_monthly_revenue / 100000).toFixed(1)}L
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Payback:</span>
              <span className="font-medium">{insights.payback_period_months} months</span>
            </div>
          </div>
        </div>
      </Popup>
    </Marker>
  );
};

export default LocationMarker;