# backend/app/services/weaviate_service.py
import weaviate
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for interacting with Weaviate vector database"""

    def __init__(self):
        self.client = None
        self.schema_created = False

    async def initialize(self):
        """Initialize Weaviate connection and schema"""
        try:
            # Connect to Weaviate
            auth_config = None
            if settings.weaviate_api_key:
                auth_config = weaviate.AuthApiKey(api_key=settings.weaviate_api_key)

            self.client = weaviate.Client(
                url=settings.weaviate_url, auth_client_secret=auth_config
            )

            # Test connection
            if self.client.is_ready():
                logger.info("✅ Weaviate connection established")
                await self._create_schema()
            else:
                raise Exception("Weaviate is not ready")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Weaviate: {e}")
            raise

    async def _create_schema(self):
        """Create Weaviate schema for storing location data"""
        if self.schema_created:
            return

        schema = {
            "classes": [
                {
                    "class": "ChargingLocation",
                    "description": "EV charging station location with optimization data",
                    "properties": [
                        {
                            "name": "name",
                            "dataType": ["text"],
                            "description": "Location name",
                        },
                        {
                            "name": "address",
                            "dataType": ["text"],
                            "description": "Full address",
                        },
                        {
                            "name": "coordinates",
                            "dataType": ["geoCoordinates"],
                            "description": "Geographic coordinates",
                        },
                        {
                            "name": "trafficScore",
                            "dataType": ["number"],
                            "description": "Traffic flow score",
                        },
                        {
                            "name": "gridScore",
                            "dataType": ["number"],
                            "description": "Grid capacity score",
                        },
                        {
                            "name": "competitionScore",
                            "dataType": ["number"],
                            "description": "Competition gap score",
                        },
                        {
                            "name": "demographicScore",
                            "dataType": ["number"],
                            "description": "Demographic suitability score",
                        },
                        {
                            "name": "roiScore",
                            "dataType": ["number"],
                            "description": "ROI potential score",
                        },
                        {
                            "name": "overallScore",
                            "dataType": ["number"],
                            "description": "Overall optimization score",
                        },
                        {
                            "name": "metadata",
                            "dataType": ["text"],
                            "description": "Additional metadata as JSON string",
                        },
                    ],
                }
            ]
        }

        try:
            # Check if schema exists
            existing_schema = self.client.schema.get()
            classes = [cls["class"] for cls in existing_schema["classes"]]

            if "ChargingLocation" not in classes:
                self.client.schema.create(schema)
                logger.info("✅ Weaviate schema created")
            else:
                logger.info("✅ Weaviate schema already exists")

            self.schema_created = True

        except Exception as e:
            logger.error(f"Failed to create Weaviate schema: {e}")
            raise

    async def store_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """Store a recommendation in Weaviate"""
        try:
            data_object = {
                "name": recommendation["location"]["name"],
                "address": recommendation["location"]["address"],
                "coordinates": {
                    "latitude": recommendation["location"]["coordinates"]["latitude"],
                    "longitude": recommendation["location"]["coordinates"]["longitude"],
                },
                "trafficScore": recommendation["scores"]["traffic_score"],
                "gridScore": recommendation["scores"]["grid_capacity"],
                "competitionScore": recommendation["scores"]["competition_gap"],
                "demographicScore": recommendation["scores"]["demographics"],
                "roiScore": recommendation["scores"]["roi_potential"],
                "overallScore": recommendation["scores"]["overall_score"],
                "metadata": str(recommendation.get("insights", {})),
            }

            result = self.client.data_object.create(
                data_object=data_object, class_name="ChargingLocation"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to store recommendation: {e}")
            raise

    async def search_similar_locations(
        self,
        latitude: float,
        longitude: float,
        max_distance: float = 50000,  # 50km in meters
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for similar locations within distance"""
        try:
            where_filter = {
                "path": ["coordinates"],
                "operator": "WithinGeoRange",
                "valueGeoRange": {
                    "geoCoordinates": {"latitude": latitude, "longitude": longitude},
                    "distance": {"max": max_distance},
                },
            }

            result = (
                self.client.query.get(
                    "ChargingLocation",
                    [
                        "name",
                        "address",
                        "coordinates",
                        "trafficScore",
                        "gridScore",
                        "competitionScore",
                        "demographicScore",
                        "roiScore",
                        "overallScore",
                    ],
                )
                .with_where(where_filter)
                .with_limit(limit)
                .do()
            )

            return result["data"]["Get"]["ChargingLocation"]

        except Exception as e:
            logger.error(f"Failed to search locations: {e}")
            return []
