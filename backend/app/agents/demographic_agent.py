# backend/app/agents/demographic_agent.py (Fixed imports)
import httpx
import logging
from typing import Dict, Any, Tuple  # Added missing imports
from geopy.geocoders import Nominatim

from app.agents.base_agent import BaseAgent
from app.models import AgentState

logger = logging.getLogger(__name__)

class DemographicInsightsAgent(BaseAgent):
    """Agent for analyzing demographic using real APIs"""
    
    def __init__(self):
        super().__init__("Demographic Insights Agent")
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute demographic analysis using real data"""
        try:
            logger.info(f"Starting demographic analysis for {state['location']}")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Get coordinates
            coordinates = await self._get_coordinates(state['location'])
            if not coordinates:
                state['errors'].append(f"Could not geocode location for demographics: {state['location']}")
                state['demographic_data'] = self._get_fallback_demographic_data(state['location'])
                return state
            
            lat, lon = coordinates
            
            # Fetch real demographic data
            demographic_data = await self._fetch_real_demographic_data(lat, lon, state['location'])
            
            state['demographic_data'] = demographic_data
            logger.info("Demographic analysis completed successfully")
            
        except Exception as e:
            error_msg = f"Demographic analysis failed: {str(e)}"
            logger.error(error_msg)
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(error_msg)
            state['demographic_data'] = self._get_fallback_demographic_data(state['location'])
        
        return state
    
    async def _get_coordinates(self, location: str) -> Tuple[float, float] | None:
        """Get coordinates for location"""
        try:
            location_data = self.geolocator.geocode(f"{location}, Tamil Nadu, India")
            if location_data:
                return location_data.latitude, location_data.longitude
            return None
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
    
    async def _fetch_real_demographic_data(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Fetch real demographic data from multiple sources"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Get place information from GeoNames
                place_data = await self._fetch_place_data(client, lat, lon)
                
                # 2. Get nearby amenities as indicators of development
                amenities_data = await self._fetch_amenities_data(client, lat, lon)
                
                # 3. Get economic indicators from nearby infrastructure
                economic_data = await self._fetch_economic_indicators(client, lat, lon)
                
                # 4. Calculate dynamic demographic metrics
                demographic_metrics = self._calculate_demographic_metrics(
                    place_data, amenities_data, economic_data, location
                )
                
                return {
                    **demographic_metrics,
                    "place_data": place_data,
                    "amenities_data": amenities_data,
                    "economic_data": economic_data,
                    "coordinates": {"lat": lat, "lon": lon},
                    "data_source": "real_apis",
                    "location": location
                }
                
            except Exception as e:
                logger.error(f"Real demographic data fetch failed: {e}")
                return self._get_fallback_demographic_data(location)
    
    async def _fetch_place_data(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch place data from GeoNames API"""
        try:
            response = await client.get(
                f"http://api.geonames.org/findNearbyPlaceNameJSON",
                params={
                    "lat": lat,
                    "lng": lon,
                    "radius": 30,
                    "maxRows": 10,
                    "username": "demo"  # Replace with your GeoNames username
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("geonames", [])
                
                if places:
                    # Calculate total population in area
                    total_population = sum(place.get("population", 0) for place in places)
                    largest_place = max(places, key=lambda x: x.get("population", 0))
                    
                    return {
                        "total_population": total_population,
                        "largest_city": largest_place.get("name", "Unknown"),
                        "largest_city_population": largest_place.get("population", 0),
                        "admin_division": largest_place.get("adminName1", ""),
                        "place_count": len(places)
                    }
            
            return {"total_population": 50000, "largest_city": "Unknown"}
            
        except Exception as e:
            logger.error(f"Place data fetch failed: {e}")
            return {"total_population": 50000, "error": str(e)}
    
    async def _fetch_amenities_data(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch amenities data from OpenStreetMap as development indicators"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"~"bank|atm|hospital|school|university|shopping_mall|restaurant|hotel"](around:10000,{lat},{lon});
              node["shop"~"car|car_parts|fuel"](around:10000,{lat},{lon});
              way["building"~"residential|commercial|office"](around:5000,{lat},{lon});
            );
            out center;
            """
            
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                content=query,
                headers={"Content-Type": "text/plain"}
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                
                # Count different types of amenities
                banks = len([e for e in elements if e.get("tags", {}).get("amenity") in ["bank", "atm"]])
                healthcare = len([e for e in elements if e.get("tags", {}).get("amenity") in ["hospital", "clinic"]])
                education = len([e for e in elements if e.get("tags", {}).get("amenity") in ["school", "university"]])
                retail = len([e for e in elements if e.get("tags", {}).get("amenity") in ["shopping_mall", "restaurant"]])
                automotive = len([e for e in elements if e.get("tags", {}).get("shop") in ["car", "car_parts", "fuel"]])
                buildings = len([e for e in elements if "building" in e.get("tags", {})])
                
                # Calculate development index
                development_index = (banks * 2 + healthcare * 2 + education * 1.5 + retail + automotive * 1.5) / 10
                
                return {
                    "banks_atms": banks,
                    "healthcare_facilities": healthcare,
                    "education_facilities": education,
                    "retail_facilities": retail,
                    "automotive_facilities": automotive,
                    "buildings_count": buildings,
                    "development_index": round(development_index, 1)
                }
            
            return {"development_index": 5.0}
            
        except Exception as e:
            logger.error(f"Amenities data fetch failed: {e}")
            return {"development_index": 5.0, "error": str(e)}
    
    async def _fetch_economic_indicators(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch economic indicators from infrastructure data"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              way["highway"~"motorway|trunk|primary|secondary"](around:15000,{lat},{lon});
              node["public_transport"~"station"](around:10000,{lat},{lon});
              way["landuse"~"commercial|industrial|residential"](around:10000,{lat},{lon});
              node["amenity"~"fuel|charging_station"](around:10000,{lat},{lon});
            );
            out center;
            """
            
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                content=query,
                headers={"Content-Type": "text/plain"}
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                
                major_roads = len([e for e in elements if e.get("tags", {}).get("highway") in ["motorway", "trunk", "primary"]])
                public_transport = len([e for e in elements if e.get("tags", {}).get("public_transport") == "station"])
                commercial_areas = len([e for e in elements if e.get("tags", {}).get("landuse") == "commercial"])
                industrial_areas = len([e for e in elements if e.get("tags", {}).get("landuse") == "industrial"])
                fuel_stations = len([e for e in elements if e.get("tags", {}).get("amenity") == "fuel"])
                existing_ev_chargers = len([e for e in elements if e.get("tags", {}).get("amenity") == "charging_station"])
                
                # Calculate economic activity score
                economic_score = (
                    major_roads * 1.5 + 
                    public_transport * 2 + 
                    commercial_areas * 2 + 
                    industrial_areas * 1.5 + 
                    fuel_stations * 1.2
                ) / 10
                
                # EV readiness score
                ev_readiness = min((fuel_stations * 0.3 + existing_ev_chargers * 2 + major_roads * 0.2), 10)
                
                return {
                    "major_roads": major_roads,
                    "public_transport_access": public_transport,
                    "commercial_areas": commercial_areas,
                    "industrial_areas": industrial_areas,
                    "fuel_stations": fuel_stations,
                    "existing_ev_chargers": existing_ev_chargers,
                    "economic_activity_score": round(economic_score, 1),
                    "ev_readiness_score": round(ev_readiness, 1)
                }
            
            return {"economic_activity_score": 5.0, "ev_readiness_score": 3.0}
            
        except Exception as e:
            logger.error(f"Economic indicators fetch failed: {e}")
            return {"economic_activity_score": 5.0, "error": str(e)}
    
    def _calculate_demographic_metrics(
        self, 
        place_data: Dict[str, Any], 
        amenities_data: Dict[str, Any], 
        economic_data: Dict[str, Any],
        location: str
    ) -> Dict[str, Any]:
        """Calculate demographic metrics from real data"""
        
        # Population density calculation
        total_population = place_data.get("total_population", 50000)
        area_km2 = 3.14159 * (10 ** 2)  # 10km radius area
        population_density = total_population / area_km2
        
        # Development level based on amenities
        development_index = amenities_data.get("development_index", 5.0)
        
        # Economic activity level
        economic_score = economic_data.get("economic_activity_score", 5.0)
        
        # EV adoption estimate based on development and economic factors
        base_adoption_rate = 0.02  # 2% base rate for Tamil Nadu
        development_multiplier = development_index / 5.0  # Normalize to 1.0
        economic_multiplier = economic_score / 5.0  # Normalize to 1.0
        
        estimated_ev_adoption = base_adoption_rate * development_multiplier * economic_multiplier
        estimated_ev_adoption = min(estimated_ev_adoption, 0.25)  # Cap at 25%
        
        # Income level estimation based on development and economic indicators
        if development_index >= 8 and economic_score >= 7:
            income_level = "Upper Middle"
            income_score = 8.5
        elif development_index >= 6 and economic_score >= 5:
            income_level = "Middle"
            income_score = 7.0
        elif development_index >= 4:
            income_level = "Lower Middle"
            income_score = 5.5
        else:
            income_level = "Lower"
            income_score = 4.0
        
        # Target market size
        if total_population > 500000:
            market_size = "Large"
        elif total_population > 100000:
            market_size = "Medium"
        else:
            market_size = "Small"
        
        # Overall demographic score
        demographic_score = (
            min(population_density / 1000, 10) * 0.3 +  # Population density factor
            development_index * 0.3 +  # Development factor
            economic_score * 0.2 +  # Economic activity factor
            (estimated_ev_adoption * 100) * 0.2  # EV adoption factor
        )
        demographic_score = min(demographic_score, 10)
        
        return {
            "population": total_population,
            "population_density": round(population_density, 1),
            "development_index": development_index,
            "economic_activity_score": economic_score,
            "ev_adoption_rate": round(estimated_ev_adoption, 3),
            "estimated_ev_vehicles": int(total_population * estimated_ev_adoption),
            "income_level": income_level,
            "income_score": income_score,
            "target_market_size": market_size,
            "demographic_score": round(demographic_score, 1),
            "ev_readiness": economic_data.get("ev_readiness_score", 3.0),
            "market_potential": "High" if demographic_score >= 7 else "Medium" if demographic_score >= 5 else "Low"
        }
    
    def _get_fallback_demographic_data(self, location: str) -> Dict[str, Any]:
        """Fallback demographic data when APIs fail"""
        return {
            "population": 100000,
            "population_density": 500,
            "income_level": "Middle",
            "ev_adoption_rate": 0.05,
            "demographic_score": 6.0,
            "target_market_size": "Medium",
            "market_potential": "Medium",
            "data_source": "fallback",
            "location": location,
            "note": "Using fallback data due to API unavailability"
        }