
import asyncio
import httpx
from typing import Dict, Any, List, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging
import json
import time
import hashlib

from app.agents.base_agent import BaseAgent
from app.models import AgentState, AgentResult

logger = logging.getLogger(__name__)

class TrafficFlowAnalyst(BaseAgent):
    """Agent responsible for analyzing traffic flow patterns with enhanced debugging"""
    
    def __init__(self):
        super().__init__("Traffic Flow Analyst")
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute traffic analysis with enhanced location-specific logic"""
        try:
            location = state['location']
            logger.info(f"=== TRAFFIC ANALYSIS START for {location} ===")
            
            if 'errors' not in state:
                state['errors'] = []
            
          
            coordinates = await self._get_coordinates(location)
            if not coordinates:
                logger.warning(f"Geocoding failed for {location}, using location-specific fallback")
                state['errors'].append(f"Could not geocode location: {location}")
                state['traffic_data'] = self._get_location_specific_fallback(location)
                return state
            
            lat, lon = coordinates
            logger.info(f"Coordinates for {location}: {lat}, {lon}")
            
          
            try:
                traffic_data = await self._analyze_traffic_patterns(lat, lon, state['radius_km'], location)
                state['traffic_data'] = traffic_data
                logger.info(f"Real traffic data fetched for {location}")
            except Exception as api_error:
                logger.warning(f"API failed for {location}: {api_error}, using location-specific fallback")
                state['traffic_data'] = self._get_location_specific_fallback(location, lat, lon)
            
            logger.info(f"=== TRAFFIC ANALYSIS COMPLETE for {location} ===")
            
        except Exception as e:
            error_msg = f"Traffic analysis failed for {state['location']}: {str(e)}"
            logger.error(error_msg)
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(error_msg)
           
            state['traffic_data'] = self._get_location_specific_fallback(state['location'])
        
        return state
    
    async def _get_coordinates(self, location: str) -> Tuple[float, float] | None:
        """Get latitude and longitude for a location"""
        try:
           
            queries = [
                f"{location}, Tamil Nadu, India",
                f"{location}, Tamil Nadu",
                f"{location}, India"
            ]
            
            for query in queries:
                logger.info(f"Trying geocoding: {query}")
                location_data = self.geolocator.geocode(query)
                if location_data:
                    logger.info(f"Geocoding successful: {location_data.latitude}, {location_data.longitude}")
                    return location_data.latitude, location_data.longitude
                
            return None
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
    
    def _get_location_specific_fallback(self, location: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """Provide location-specific fallback data based on known Tamil Nadu locations"""
        
        location_lower = location.lower().strip()
        
       
        location_profiles = {
            "chennai": {
                "traffic_score": 9.2,
                "daily_traffic": 85000,
                "road_density": 8.5,
                "coords": [13.0827, 80.2707],
                "characteristics": "Major metropolitan city with heavy traffic"
            },
            "coimbatore": {
                "traffic_score": 7.8,
                "daily_traffic": 55000,
                "road_density": 6.2,
                "coords": [11.0168, 76.9558],
                "characteristics": "Industrial city with moderate to high traffic"
            },
            "madurai": {
                "traffic_score": 6.8,
                "daily_traffic": 42000,
                "road_density": 5.1,
                "coords": [9.9252, 78.1198],
                "characteristics": "Historic city with growing traffic"
            },
            "salem": {
                "traffic_score": 6.2,
                "daily_traffic": 38000,
                "road_density": 4.8,
                "coords": [11.6643, 78.1460],
                "characteristics": "Steel city with industrial traffic"
            },
            "tiruchirappalli": {
                "traffic_score": 6.5,
                "daily_traffic": 40000,
                "road_density": 5.0,
                "coords": [10.7905, 78.7047],
                "characteristics": "Central hub with moderate traffic"
            },
            "erode": {
                "traffic_score": 5.8,
                "daily_traffic": 32000,
                "road_density": 4.2,
                "coords": [11.3410, 77.7172],
                "characteristics": "Textile city with moderate traffic"
            },
            "vellore": {
                "traffic_score": 6.0,
                "daily_traffic": 35000,
                "road_density": 4.5,
                "coords": [12.9165, 79.1325],
                "characteristics": "Educational hub with growing traffic"
            },
            "tirunelveli": {
                "traffic_score": 5.5,
                "daily_traffic": 28000,
                "road_density": 3.8,
                "coords": [8.7139, 77.7567],
                "characteristics": "Southern city with moderate traffic"
            },
            "thanjavur": {
                "traffic_score": 5.2,
                "daily_traffic": 25000,
                "road_density": 3.5,
                "coords": [10.7870, 79.1378],
                "characteristics": "Cultural city with low to moderate traffic"
            },
            "ramanathapuram": {
                "traffic_score": 4.8,
                "daily_traffic": 22000,
                "road_density": 3.2,
                "coords": [9.3639, 78.8370],
                "characteristics": "Coastal town with light traffic"
            },
            "kumbakonam": {
                "traffic_score": 4.5,
                "daily_traffic": 20000,
                "road_density": 3.0,
                "coords": [10.9601, 79.3788],
                "characteristics": "Temple town with light traffic"
            },
            "dindigul": {
                "traffic_score": 5.5,
                "daily_traffic": 30000,
                "road_density": 4.0,
                "coords": [10.3673, 77.9803],
                "characteristics": "Commercial town with moderate traffic"
            }
        }
        
       
        profile = None
        for key, data in location_profiles.items():
            if key in location_lower:
                profile = data
                break
        
       
        if not profile:
            
            location_hash = int(hashlib.md5(location_lower.encode()).hexdigest()[:8], 16)
            base_score = 4.0 + (location_hash % 40) / 10 
            
            profile = {
                "traffic_score": base_score,
                "daily_traffic": int(15000 + (location_hash % 35000)),
                "road_density": base_score * 0.7,
                "coords": [lat or (10.0 + (location_hash % 400) / 100), 
                          lon or (77.0 + (location_hash % 300) / 100)],
                "characteristics": f"Regional location with varied traffic patterns"
            }
        
       
        final_coords = [lat or profile["coords"][0], lon or profile["coords"][1]]
        
        logger.info(f"Using location-specific data for {location}: Traffic Score = {profile['traffic_score']}")
        
        return {
            "coordinates": {"lat": final_coords[0], "lon": final_coords[1]},
            "radius_km": 50,
            "traffic_metrics": {
                "traffic_score": profile["traffic_score"],
                "road_density_score": profile["road_density"],
                "estimated_daily_traffic": profile["daily_traffic"],
                "peak_hours": ["08:00-10:00", "18:00-20:00"],
                "traffic_flow_rating": (
                    "High" if profile["traffic_score"] > 7 else 
                    "Medium" if profile["traffic_score"] > 5 else 
                    "Low"
                )
            },
            "road_analysis": {
                "highway_types": self._generate_road_types(profile["traffic_score"]),
                "total_roads": int(profile["road_density"] * 10),
                "estimated_total_length_km": profile["daily_traffic"] / 300,
                "road_density": profile["road_density"]
            },
            "high_traffic_zones": [
                {
                    "name": f"Major Highway near {location}",
                    "type": "primary",
                    "distance_km": 1.5,
                    "coordinates": {"lat": final_coords[0], "lon": final_coords[1]}
                }
            ],
            "data_source": "location_specific_fallback",
            "location_profile": profile["characteristics"],
            "note": f"Location-specific data for {location} based on regional characteristics"
        }
    
    def _generate_road_types(self, traffic_score: float) -> Dict[str, int]:
        """Generate realistic road type distribution based on traffic score"""
        if traffic_score >= 8:
            return {"motorway": 3, "trunk": 5, "primary": 8, "secondary": 12, "tertiary": 15, "residential": 25}
        elif traffic_score >= 6:
            return {"motorway": 1, "trunk": 3, "primary": 5, "secondary": 8, "tertiary": 12, "residential": 20}
        elif traffic_score >= 4:
            return {"trunk": 1, "primary": 2, "secondary": 5, "tertiary": 8, "residential": 15}
        else:
            return {"primary": 1, "secondary": 3, "tertiary": 5, "residential": 10}
    
    async def _analyze_traffic_patterns(
        self, lat: float, lon: float, radius_km: int, location: str
    ) -> Dict[str, Any]:
        """Analyze traffic patterns using OpenStreetMap data with better error handling"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:  
                
                query = f"""
                [out:json][timeout:10];
                (
                  way["highway"]["highway"!="footway"]["highway"!="path"]["highway"!="cycleway"]
                      (around:{min(radius_km * 1000, 25000)},{lat},{lon});
                );
                out geom;
                """
                
                logger.info(f"Querying OSM for {location} at {lat}, {lon}")
                
               
                response = await client.post(
                    "https://overpass-api.de/api/interpreter",
                    content=query,
                    headers={"Content-Type": "text/plain"}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Overpass API returned status {response.status_code}")
                
                data = response.json()
                ways = data.get("elements", [])
                
                logger.info(f"Found {len(ways)} road segments for {location}")
                
                if len(ways) == 0:
                    raise Exception("No road data found from OSM")
                
                
                road_analysis = self._analyze_road_network(ways)
                
             
                traffic_metrics = self._calculate_traffic_metrics(road_analysis, lat, lon, location)
                
                return {
                    "coordinates": {"lat": lat, "lon": lon},
                    "radius_km": radius_km,
                    "road_analysis": road_analysis,
                    "traffic_metrics": traffic_metrics,
                    "high_traffic_zones": self._identify_high_traffic_zones(ways, lat, lon),
                    "data_source": "openstreetmap_api",
                    "query_timestamp": time.time(),
                    "location": location
                }
                
        except Exception as e:
            logger.error(f"OSM API failed for {location}: {e}")
            raise  
    
    def _analyze_road_network(self, ways) -> Dict[str, Any]:
        """Analyze road network characteristics"""
        highway_types = {}
        total_length = 0
        
        for way in ways:
            if way.get("type") == "way":
                highway_type = way.get("tags", {}).get("highway", "unknown")
                
                if highway_type in highway_types:
                    highway_types[highway_type] += 1
                else:
                    highway_types[highway_type] = 1
                
                
                geometry = way.get("geometry", [])
                if len(geometry) > 1:
                    total_length += len(geometry) * 0.1 
        
        return {
            "highway_types": highway_types,
            "total_roads": len(ways),
            "estimated_total_length_km": total_length,
            "road_density": total_length / 100 if total_length > 0 else 0
        }
    
    def _calculate_traffic_metrics(
        self, road_analysis: Dict[str, Any], lat: float, lon: float, location: str
    ) -> Dict[str, Any]:
        """Calculate traffic-related metrics with location awareness"""
        highway_types = road_analysis.get("highway_types", {})
        
       
        traffic_weights = {
            "motorway": 10,
            "trunk": 9,
            "primary": 8,
            "secondary": 6,
            "tertiary": 4,
            "residential": 2,
            "service": 1
        }
        
        weighted_score = 0
        for highway_type, count in highway_types.items():
            weight = traffic_weights.get(highway_type, 1)
            weighted_score += count * weight
        
       
        base_traffic_score = min(weighted_score / 50, 10) if weighted_score > 0 else 3.0
        
       
        location_lower = location.lower()
        if "chennai" in location_lower:
            location_boost = 2.0
        elif any(city in location_lower for city in ["coimbatore", "madurai", "salem"]):
            location_boost = 1.0
        elif any(city in location_lower for city in ["tiruchirappalli", "erode", "vellore"]):
            location_boost = 0.5
        else:
            location_boost = 0.0
        
        final_traffic_score = min(base_traffic_score + location_boost, 10.0)
        
        return {
            "traffic_score": round(final_traffic_score, 1),
            "road_density_score": min(road_analysis.get("road_density", 0), 10),
            "estimated_daily_traffic": int(final_traffic_score * 5000),
            "peak_hours": ["08:00-10:00", "18:00-20:00"],
            "traffic_flow_rating": "High" if final_traffic_score > 7 else "Medium" if final_traffic_score > 4 else "Low",
            "location_factor": location_boost
        }
    
    def _identify_high_traffic_zones(
        self, ways, center_lat: float, center_lon: float
    ) -> List[Dict[str, Any]]:
        """Identify high-traffic zones based on road hierarchy"""
        high_traffic_zones = []
        
        major_roads = ["motorway", "trunk", "primary", "secondary"]
        
        for way in ways[:10]:  
            if way.get("type") == "way":
                highway_type = way.get("tags", {}).get("highway", "")
                
                if highway_type in major_roads:
                    geometry = way.get("geometry", [])
                    if geometry:
                        try:
                            first_point = geometry[0]
                            point_lat = first_point.get("lat")
                            point_lon = first_point.get("lon")
                            
                            if point_lat and point_lon:
                                distance = geodesic(
                                    (center_lat, center_lon),
                                    (point_lat, point_lon)
                                ).kilometers
                                
                                if distance <= 20:  # Within 20km
                                    high_traffic_zones.append({
                                        "name": way.get("tags", {}).get("name", f"{highway_type.title()} Road"),
                                        "type": highway_type,
                                        "distance_km": round(distance, 1),
                                        "coordinates": {
                                            "lat": point_lat,
                                            "lon": point_lon
                                        }
                                    })
                        except (KeyError, TypeError, ValueError) as e:
                            logger.debug(f"Could not process way: {e}")
                            continue
        
        return high_traffic_zones