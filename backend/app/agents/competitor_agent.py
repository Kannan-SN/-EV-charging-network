
import overpy
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging
import httpx
from typing import Dict, Any, List  

from app.agents.base_agent import BaseAgent
from app.models import AgentState

logger = logging.getLogger(__name__)

class CompetitorMappingAgent(BaseAgent):
    """Agent for mapping existing charging stations using real data"""
    
    def __init__(self):
        super().__init__("Competitor Mapping Agent")
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute competitor analysis using real data"""
        try:
            logger.info(f"Starting competitor analysis for {state['location']}")
            
            if 'errors' not in state:
                state['errors'] = []
            
            location_data = self.geolocator.geocode(f"{state['location']}, Tamil Nadu, India")
            if not location_data:
                state['errors'].append(f"Could not geocode location: {state['location']}")
                state['competitor_data'] = self._get_fallback_competitor_data(state['location'])
                return state
            
            lat, lon = location_data.latitude, location_data.longitude

            competitor_data = await self._find_real_existing_stations(lat, lon, state['radius_km'])
            
            state['competitor_data'] = competitor_data
            logger.info("Competitor analysis completed successfully")
            
        except Exception as e:
            error_msg = f"Competitor analysis failed: {str(e)}"
            logger.error(error_msg)
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(error_msg)
            state['competitor_data'] = self._get_fallback_competitor_data(state['location'])
        
        return state
    
    async def _find_real_existing_stations(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        """Find existing charging stations using OpenStreetMap"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
               
                osm_stations = await self._fetch_osm_charging_stations(client, lat, lon, radius_km)
                
                fuel_stations = await self._fetch_fuel_stations(client, lat, lon, radius_km)
        
                competition_metrics = self._calculate_competition_metrics(
                    osm_stations, fuel_stations, lat, lon, radius_km
                )
                
                return {
                    **competition_metrics,
                    "osm_stations": osm_stations,
                    "fuel_stations_data": fuel_stations,
                    "coordinates": {"lat": lat, "lon": lon},
                    "radius_km": radius_km,
                    "data_source": "real_apis"
                }
                
        except Exception as e:
            logger.error(f"Real competitor data fetch failed: {e}")
            return self._get_fallback_competitor_data("Unknown")
    
    async def _fetch_osm_charging_stations(self, client: httpx.AsyncClient, lat: float, lon: float, radius_km: int) -> List[Dict[str, Any]]:
        """Fetch charging stations from OpenStreetMap"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="charging_station"](around:{radius_km * 1000},{lat},{lon});
              way["amenity"="charging_station"](around:{radius_km * 1000},{lat},{lon});
            );
            out center meta;
            """
            
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                content=query,
                headers={"Content-Type": "text/plain"}
            )
            
            stations = []
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                
                for element in elements:
                    if element.get("type") == "node":
                        station_lat = element.get("lat")
                        station_lon = element.get("lon")
                    elif element.get("type") == "way" and element.get("center"):
                        station_lat = element["center"]["lat"]
                        station_lon = element["center"]["lon"]
                    else:
                        continue
                    
                    tags = element.get("tags", {})
                    distance = geodesic((lat, lon), (station_lat, station_lon)).kilometers
                    
                    # Extract charging station details
                    station_info = {
                        "name": tags.get("name", "Unnamed Charging Station"),
                        "operator": tags.get("operator", "Unknown"),
                        "network": tags.get("network", "Independent"),
                        "capacity": tags.get("capacity", "Unknown"),
                        "access": tags.get("access", "Unknown"),
                        "fee": tags.get("fee", "Unknown"),
                        "distance_km": round(distance, 2),
                        "coordinates": {"lat": station_lat, "lon": station_lon},
                        "osm_id": element.get("id")
                    }
                    stations.append(station_info)
            
  
            stations.sort(key=lambda x: x["distance_km"])
            return stations
            
        except Exception as e:
            logger.error(f"OSM charging stations fetch failed: {e}")
            return []
    
    async def _fetch_fuel_stations(self, client: httpx.AsyncClient, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        """Fetch fuel stations as potential competition/conversion sites"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="fuel"](around:{radius_km * 1000},{lat},{lon});
            );
            out center;
            """
            
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                content=query,
                headers={"Content-Type": "text/plain"}
            )
            
            fuel_stations = []
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                
                for element in elements:
                    tags = element.get("tags", {})
                    distance = geodesic((lat, lon), (element.get("lat"), element.get("lon"))).kilometers
                    
                    fuel_info = {
                        "name": tags.get("name", "Fuel Station"),
                        "brand": tags.get("brand", "Independent"),
                        "distance_km": round(distance, 2)
                    }
                    fuel_stations.append(fuel_info)
            
            return {
                "count": len(fuel_stations),
                "stations": fuel_stations[:10] 
            }
            
        except Exception as e:
            logger.error(f"Fuel stations fetch failed: {e}")
            return {"count": 0, "stations": []}
    
    def _calculate_competition_metrics(
        self, 
        charging_stations: List[Dict[str, Any]], 
        fuel_data: Dict[str, Any], 
        lat: float, 
        lon: float, 
        radius_km: int
    ) -> Dict[str, Any]:
        """Calculate competition metrics from real data"""

        total_ev_stations = len(charging_stations)
        

        nearest_distance = float('inf')
        if charging_stations:
            nearest_distance = min([s["distance_km"] for s in charging_stations])
        
        area_km2 = 3.14159 * (radius_km ** 2)
        ev_station_density = total_ev_stations / area_km2

        if ev_station_density == 0:
            competition_score = 10.0 
        elif ev_station_density < 0.1:
            competition_score = 8.5
        elif ev_station_density < 0.3:
            competition_score = 7.0
        else:
            competition_score = 5.0
    
        if total_ev_stations == 0:
            market_opportunity = "Excellent"
        elif total_ev_stations < 3:
            market_opportunity = "High"
        elif total_ev_stations < 8:
            market_opportunity = "Medium"
        else:
            market_opportunity = "Low"
        
 
        if ev_station_density < 0.2:
            saturation_level = "Low"
        elif ev_station_density < 0.7:
            saturation_level = "Medium"
        else:
            saturation_level = "High"
        
        return {
            "existing_stations": total_ev_stations,
            "nearest_distance_km": round(nearest_distance, 1) if nearest_distance != float('inf') else None,
            "competition_score": round(competition_score, 1),
            "market_saturation": saturation_level,
            "market_opportunity": market_opportunity,
            "fuel_stations_nearby": fuel_data.get("count", 0),
            "stations_list": charging_stations[:5] 
        }
    
    def _get_fallback_competitor_data(self, location: str) -> Dict[str, Any]:
        """Fallback competitor data when APIs fail"""
        return {
            "existing_stations": 3,
            "nearest_distance_km": 5.2,
            "market_saturation": "Medium",
            "competition_score": 6.0,
            "market_opportunity": "Medium",
            "data_source": "fallback",
            "location": location,
            "note": "Using fallback data due to API unavailability"
        }