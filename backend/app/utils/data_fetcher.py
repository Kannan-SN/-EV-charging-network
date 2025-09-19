
import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import overpy

logger = logging.getLogger(__name__)


class DataFetcher:
    """Utility class for fetching data from various external sources"""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
        self.overpass_api = overpy.Overpass()
        self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def fetch_location_data(self, location: str) -> Optional[Tuple[float, float]]:
        """Fetch coordinates for a location"""
        try:
            location_data = self.geolocator.geocode(f"{location}, Tamil Nadu, India")
            if location_data:
                return location_data.latitude, location_data.longitude
            return None
        except Exception as e:
            logger.error(f"Geocoding failed for {location}: {e}")
            return None

    async def fetch_traffic_data(
        self, lat: float, lon: float, radius_km: int
    ) -> Dict[str, Any]:
        """Fetch traffic and road data from OpenStreetMap"""
        try:
            query = f"""
            [out:json][timeout:25];
            (
              way["highway"]["highway"!="footway"]["highway"!="path"]
                  (around:{radius_km * 1000},{lat},{lon});
            );
            out geom;
            """

            result = self.overpass_api.query(query)

            # Analyze road network
            highway_types = {}
            total_roads = len(result.ways)

            for way in result.ways:
                highway_type = way.tags.get("highway", "unknown")
                highway_types[highway_type] = highway_types.get(highway_type, 0) + 1

            # Calculate traffic score based on road types
            traffic_weights = {
                "motorway": 10,
                "trunk": 9,
                "primary": 8,
                "secondary": 6,
                "tertiary": 4,
                "residential": 2,
            }

            weighted_score = sum(
                highway_types.get(road_type, 0) * weight
                for road_type, weight in traffic_weights.items()
            )

            traffic_score = min(weighted_score / 50, 10)  # Normalize to 0-10

            return {
                "total_roads": total_roads,
                "highway_types": highway_types,
                "traffic_score": round(traffic_score, 1),
                "estimated_daily_traffic": int(traffic_score * 5000),
            }

        except Exception as e:
            logger.error(f"Traffic data fetch failed: {e}")
            return {"error": str(e), "traffic_score": 5.0}

    async def fetch_government_data(self, location: str) -> Dict[str, Any]:
        """Fetch government and infrastructure data (placeholder for real APIs)"""
        # In production, this would call actual government APIs
        return {
            "power_infrastructure": "Available",
            "development_plans": "Under Review",
            "permits_required": ["Electrical", "Municipal", "Environmental"],
        }

    async def fetch_demographic_data(self, location: str) -> Dict[str, Any]:
        """Fetch demographic data (placeholder for census APIs)"""
        # In production, this would call census or demographic APIs
        city_data = {
            "chennai": {
                "population": 4646732,
                "density": 26553,
                "income_level": "Upper Middle",
            },
            "coimbatore": {
                "population": 1061447,
                "density": 5432,
                "income_level": "Middle",
            },
            "madurai": {
                "population": 1017865,
                "density": 6153,
                "income_level": "Middle",
            },
            "salem": {
                "population": 831038,
                "density": 4321,
                "income_level": "Lower Middle",
            },
        }

        # Simple matching
        for city, data in city_data.items():
            if city.lower() in location.lower():
                return data

        # Default for unknown cities
        return {"population": 500000, "density": 2000, "income_level": "Middle"}


