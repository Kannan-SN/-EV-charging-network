
import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import LocationMarker from './LocationMarker';
import 'leaflet/dist/leaflet.css';

const MapView = ({ recommendations, center = [11.1271, 78.6569], zoom = 10 }) => {
  return (
    <div className="h-full w-full">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {recommendations.map((recommendation, index) => (
          <LocationMarker
            key={index}
            recommendation={recommendation}
            rank={index + 1}
          />
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;






