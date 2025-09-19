# backend/app/agents/grid_agent.py (Fixed imports)
import asyncio
import httpx
from typing import Dict, Any, List, Tuple  # Added missing imports
import logging
import json
from geopy.geocoders import Nominatim

from app.agents.base_agent import BaseAgent
from app.models import AgentState

logger = logging.getLogger(__name__)

class GridCapacityEvaluator(BaseAgent):
    """Agent for evaluating electricity grid capacity using real APIs"""
    
    def __init__(self):
        super().__init__("Grid Capacity Evaluator")
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute grid capacity analysis using real data"""
        try:
            logger.info(f"Starting grid analysis for {state['location']}")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Get coordinates first
            coordinates = await self._get_coordinates(state['location'])
            if not coordinates:
                state['errors'].append(f"Could not geocode location: {state['location']}")
                state['grid_data'] = await self._get_fallback_grid_data(state['location'])
                return state
            
            lat, lon = coordinates
            
            # Fetch real grid data from APIs
            grid_data = await self._fetch_real_grid_data(lat, lon, state['location'])
            
            state['grid_data'] = grid_data
            logger.info("Grid analysis completed successfully")
            
        except Exception as e:
            error_msg = f"Grid analysis failed: {str(e)}"
            logger.error(error_msg)
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(error_msg)
            state['grid_data'] = await self._get_fallback_grid_data(state['location'])
        
        return state
    
    async def _get_coordinates(self, location: str) -> Tuple[float, float] | None:
        """Get latitude and longitude for a location"""
        try:
            location_data = self.geolocator.geocode(f"{location}, Tamil Nadu, India")
            if location_data:
                return location_data.latitude, location_data.longitude
            return None
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
    
    async def _fetch_real_grid_data(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Fetch real grid data from multiple APIs"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Fetch electrical infrastructure from OpenStreetMap
                power_infrastructure = await self._fetch_power_infrastructure(client, lat, lon)
                
                # 2. Fetch population density (affects grid load)
                population_data = await self._fetch_population_data(client, lat, lon)
                
                # 3. Fetch industrial data (affects grid capacity needs)
                industrial_data = await self._fetch_industrial_data(client, lat, lon)
                
                # 4. Calculate dynamic grid metrics
                grid_metrics = self._calculate_dynamic_grid_metrics(
                    power_infrastructure, population_data, industrial_data, location
                )
                
                return {
                    **grid_metrics,
                    "power_infrastructure": power_infrastructure,
                    "population_data": population_data,
                    "industrial_data": industrial_data,
                    "coordinates": {"lat": lat, "lon": lon},
                    "data_source": "real_apis",
                    "location": location
                }
                
            except Exception as e:
                logger.error(f"Real grid data fetch failed: {e}")
                return await self._get_fallback_grid_data(location)
    
    async def _fetch_power_infrastructure(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch power infrastructure from OpenStreetMap"""
        try:
            # Query for power infrastructure around the location
            query = f"""
            [out:json][timeout:25];
            (
              node["power"~"substation|generator|plant"](around:20000,{lat},{lon});
              way["power"~"line|cable"](around:20000,{lat},{lon});
              node["amenity"="charging_station"](around:10000,{lat},{lon});
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
                
                # Analyze infrastructure
                substations = [e for e in elements if e.get("tags", {}).get("power") == "substation"]
                power_lines = [e for e in elements if e.get("tags", {}).get("power") in ["line", "cable"]]
                existing_chargers = [e for e in elements if e.get("tags", {}).get("amenity") == "charging_station"]
                
                # Calculate infrastructure density
                substation_count = len(substations)
                power_line_count = len(power_lines)
                existing_charger_count = len(existing_chargers)
                
                # Analyze substation capacity indicators
                high_voltage_substations = len([
                    s for s in substations 
                    if s.get("tags", {}).get("voltage", "").replace("kV", "").replace("000", "").isdigit() 
                    and int(s.get("tags", {}).get("voltage", "0").replace("kV", "").replace("000", "")) >= 110
                ])
                
                return {
                    "substation_count": substation_count,
                    "high_voltage_substations": high_voltage_substations,
                    "power_line_count": power_line_count,
                    "existing_chargers": existing_charger_count,
                    "infrastructure_density": substation_count + (power_line_count * 0.1),
                    "grid_connectivity": "High" if high_voltage_substations > 2 else "Medium" if high_voltage_substations > 0 else "Low"
                }
            else:
                raise Exception(f"OSM API returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"Power infrastructure fetch failed: {e}")
            return {
                "substation_count": 0,
                "power_line_count": 0,
                "existing_chargers": 0,
                "infrastructure_density": 0,
                "error": str(e)
            }
    
    async def _fetch_population_data(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch population data from GeoNames API (free tier)"""
        try:
            # Use GeoNames API for population data
            response = await client.get(
                f"http://api.geonames.org/findNearbyPlaceNameJSON",
                params={
                    "lat": lat,
                    "lng": lon,
                    "radius": 50,
                    "maxRows": 5,
                    "username": "demo"  # Free demo account - replace with your username
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("geonames", [])
                
                if places:
                    # Get the largest nearby place
                    largest_place = max(places, key=lambda x: x.get("population", 0))
                    population = largest_place.get("population", 0)
                    
                    # Estimate population density (rough calculation)
                    area_km2 = 3.14159 * (50 ** 2)  # 50km radius area
                    density = population / area_km2 if area_km2 > 0 else 0
                    
                    return {
                        "population": population,
                        "population_density": round(density, 1),
                        "largest_city": largest_place.get("name", "Unknown"),
                        "admin_name": largest_place.get("adminName1", ""),
                        "grid_load_estimate": population * 0.001  # kW per person estimate
                    }
            
            # Fallback calculation
            return {"population": 100000, "population_density": 200, "grid_load_estimate": 100}
            
        except Exception as e:
            logger.error(f"Population data fetch failed: {e}")
            return {"population": 100000, "population_density": 200, "error": str(e)}
    
    async def _fetch_industrial_data(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch industrial area data from OpenStreetMap"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              way["landuse"~"industrial|commercial"](around:15000,{lat},{lon});
              node["amenity"~"fuel|restaurant|hospital"](around:10000,{lat},{lon});
              way["highway"~"motorway|trunk|primary"](around:10000,{lat},{lon});
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
                
                industrial_areas = len([e for e in elements if e.get("tags", {}).get("landuse") == "industrial"])
                commercial_areas = len([e for e in elements if e.get("tags", {}).get("landuse") == "commercial"])
                fuel_stations = len([e for e in elements if e.get("tags", {}).get("amenity") == "fuel"])
                major_roads = len([e for e in elements if e.get("tags", {}).get("highway") in ["motorway", "trunk", "primary"]])
                
                # Calculate industrial load factor
                industrial_score = (industrial_areas * 2) + commercial_areas + (fuel_stations * 0.5)
                
                return {
                    "industrial_areas": industrial_areas,
                    "commercial_areas": commercial_areas,
                    "fuel_stations": fuel_stations,
                    "major_roads": major_roads,
                    "industrial_score": industrial_score,
                    "grid_stress_factor": min(industrial_score / 10, 1.0)  # 0-1 scale
                }
            
            return {"industrial_areas": 0, "commercial_areas": 0, "industrial_score": 0}
            
        except Exception as e:
            logger.error(f"Industrial data fetch failed: {e}")
            return {"industrial_areas": 0, "commercial_areas": 0, "error": str(e)}
    
    def _calculate_dynamic_grid_metrics(
        self, 
        power_infra: Dict[str, Any], 
        population: Dict[str, Any], 
        industrial: Dict[str, Any],
        location: str
    ) -> Dict[str, Any]:
        """Calculate dynamic grid metrics based on real data"""
        
        # Infrastructure score (0-10)
        infra_score = min((
            power_infra.get("substation_count", 0) * 1.5 +
            power_infra.get("high_voltage_substations", 0) * 3 +
            power_infra.get("infrastructure_density", 0) * 0.1
        ), 10)
        
        # Load factor based on population and industrial activity
        base_load = population.get("grid_load_estimate", 100)
        industrial_load = industrial.get("industrial_score", 0) * 50
        total_load = base_load + industrial_load
        
        # Estimated grid capacity based on infrastructure
        estimated_capacity = (
            power_infra.get("substation_count", 0) * 50 +  # 50MW per substation estimate
            power_infra.get("high_voltage_substations", 0) * 200  # 200MW per HV substation
        )
        estimated_capacity = max(estimated_capacity, 100)  # Minimum 100MW
        
        # Load factor (utilization)
        load_factor = min(total_load / estimated_capacity, 0.95) if estimated_capacity > 0 else 0.8
        
        # Available capacity for EV charging
        available_capacity = estimated_capacity * (1 - load_factor)
        
        # Reliability score based on infrastructure redundancy
        reliability = min((
            power_infra.get("substation_count", 0) * 0.8 +
            power_infra.get("power_line_count", 0) * 0.1 +
            power_infra.get("high_voltage_substations", 0) * 1.5
        ), 10)
        
        # Overall grid score
        grid_score = (infra_score * 0.4 + reliability * 0.4 + (10 - load_factor * 10) * 0.2)
        
        return {
            "grid_capacity_mw": round(estimated_capacity, 1),
            "available_capacity_mw": round(available_capacity, 1),
            "load_factor": round(load_factor, 2),
            "reliability_score": round(reliability, 1),
            "infrastructure_score": round(infra_score, 1),
            "grid_score": round(grid_score, 1),
            "capacity_sufficient": available_capacity > 20,  # 20MW threshold for EV charging
            "grid_stress_level": "Low" if load_factor < 0.7 else "Medium" if load_factor < 0.85 else "High",
            "infrastructure_quality": (
                "Excellent" if infra_score >= 8 else
                "Good" if infra_score >= 6 else
                "Fair" if infra_score >= 4 else "Poor"
            )
        }
    
    async def _get_fallback_grid_data(self, location: str) -> Dict[str, Any]:
        """Fallback grid data when APIs fail"""
        return {
            "grid_capacity_mw": 500.0,
            "available_capacity_mw": 150.0,
            "load_factor": 0.70,
            "reliability_score": 7.0,
            "grid_score": 7.0,
            "capacity_sufficient": True,
            "infrastructure_quality": "Fair",
            "data_source": "fallback",
            "location": location,
            "note": "Using fallback data due to API unavailability"
        }
