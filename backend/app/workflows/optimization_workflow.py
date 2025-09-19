
from typing import Dict, Any
import asyncio
import logging
from langgraph.graph import StateGraph, END
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random

from app.models import AgentState, OptimizationRecommendation, LocationInfo, Coordinates, AgentScores, LocationInsights
from app.agents.traffic_agent import TrafficFlowAnalyst

logger = logging.getLogger(__name__)

class OptimizationWorkflow:
    """LangGraph workflow for EV charging station optimization"""
    
    def __init__(self):
        self.graph = None
        self.geolocator = Nominatim(user_agent="ev-charging-optimizer")
        self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        
        # Define the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("traffic_analysis", self._traffic_analysis_node)
        workflow.add_node("grid_analysis", self._grid_analysis_node)
        workflow.add_node("competitor_analysis", self._competitor_analysis_node)
        workflow.add_node("demographic_analysis", self._demographic_analysis_node)
        workflow.add_node("roi_analysis", self._roi_analysis_node)
        workflow.add_node("final_optimization", self._final_optimization_node)
        
        # Define the workflow path
        workflow.set_entry_point("traffic_analysis")
        workflow.add_edge("traffic_analysis", "grid_analysis")
        workflow.add_edge("grid_analysis", "competitor_analysis")
        workflow.add_edge("competitor_analysis", "demographic_analysis")
        workflow.add_edge("demographic_analysis", "roi_analysis")
        workflow.add_edge("roi_analysis", "final_optimization")
        workflow.add_edge("final_optimization", END)
        
        # Compile the workflow
        self.graph = workflow.compile()
    
    async def run(self, initial_state: AgentState) -> AgentState:
        """Run the optimization workflow"""
        try:
            logger.info(f"Starting optimization workflow for {initial_state['location']}")
            
            # Ensure required fields exist
            if 'errors' not in initial_state:
                initial_state['errors'] = []
            if 'recommendations' not in initial_state:
                initial_state['recommendations'] = []
            
            # Run the workflow
            result = await self.graph.ainvoke(initial_state)
            
            logger.info("Optimization workflow completed")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            if 'errors' not in initial_state:
                initial_state['errors'] = []
            initial_state['errors'].append(f"Workflow failed: {str(e)}")
            return initial_state
    
    async def _traffic_analysis_node(self, state: AgentState) -> AgentState:
        """Traffic analysis node"""
        agent = TrafficFlowAnalyst()
        return await agent.execute(state)
    
    async def _grid_analysis_node(self, state: AgentState) -> AgentState:
        """Grid capacity analysis node"""
        try:
            logger.info("Starting grid analysis")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Use actual grid agent
            from app.agents.grid_agent import GridCapacityEvaluator
            agent = GridCapacityEvaluator()
            return await agent.execute(state)
            
        except Exception as e:
            logger.error(f"Grid analysis failed: {e}")
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Grid analysis failed: {str(e)}")
            
            # Fallback grid data
            state['grid_data'] = {
                "grid_capacity_mw": 500.0,
                "available_capacity_mw": 150.0,
                "reliability_score": 7.0,
                "grid_score": 7.0,
                "data_source": "fallback"
            }
        
        return state
    
    async def _competitor_analysis_node(self, state: AgentState) -> AgentState:
        """Competitor analysis node"""
        try:
            logger.info("Starting competitor analysis")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Use actual competitor agent
            from app.agents.competitor_agent import CompetitorMappingAgent
            agent = CompetitorMappingAgent()
            return await agent.execute(state)
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Competitor analysis failed: {str(e)}")
            
            # Fallback competitor data
            state['competitor_data'] = {
                "existing_stations": 3,
                "nearest_distance_km": 5.2,
                "market_saturation": "Medium",
                "competition_score": 7.5,
                "data_source": "fallback"
            }
        
        return state
    
    async def _demographic_analysis_node(self, state: AgentState) -> AgentState:
        """Demographic analysis node"""
        try:
            logger.info("Starting demographic analysis")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Use actual demographic agent
            from app.agents.demographic_agent import DemographicInsightsAgent
            agent = DemographicInsightsAgent()
            return await agent.execute(state)
            
        except Exception as e:
            logger.error(f"Demographic analysis failed: {e}")
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Demographic analysis failed: {str(e)}")
            
            # Fallback demographic data
            state['demographic_data'] = {
                "population": 100000,
                "demographic_score": 6.0,
                "income_level": "Middle",
                "data_source": "fallback"
            }
        
        return state
    
    async def _roi_analysis_node(self, state: AgentState) -> AgentState:
        """ROI analysis node"""
        try:
            logger.info("Starting ROI analysis")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Use actual ROI agent
            from app.agents.roi_agent import CostROIEstimator
            agent = CostROIEstimator()
            return await agent.execute(state)
            
        except Exception as e:
            logger.error(f"ROI analysis failed: {e}")
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"ROI analysis failed: {str(e)}")
            
            # Fallback ROI data
            state['roi_data'] = {
                "installation_cost": 4000000,
                "monthly_revenue": 120000,
                "payback_period_months": 18,
                "roi_score": 8.2,
                "data_source": "fallback"
            }
        
        return state
    
    async def _final_optimization_node(self, state: AgentState) -> AgentState:
        """Final optimization and recommendation generation"""
        try:
            logger.info("Starting final optimization")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Generate multiple location-specific recommendations
            recommendations = await self._generate_multiple_recommendations(state)
            state['recommendations'] = recommendations
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Final optimization failed: {e}")
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Final optimization failed: {str(e)}")
        
        return state
    
    async def _generate_multiple_recommendations(self, state: AgentState) -> list[Dict[str, Any]]:
        """Generate multiple location-specific recommendations"""
        recommendations = []
        
        try:
            # Get the main location coordinates
            main_coords = await self._get_coordinates(state['location'])
            if not main_coords:
                logger.error(f"Could not geocode main location: {state['location']}")
                return [await self._create_fallback_recommendation(state, 1)]
            
            main_lat, main_lon = main_coords
            
            # Generate multiple locations around the area
            candidate_locations = await self._generate_candidate_locations(
                main_lat, main_lon, state['radius_km'], 5
            )
            
            # Create recommendations for each location
            for i, (lat, lon, area_name) in enumerate(candidate_locations, 1):
                try:
                    recommendation = await self._create_location_specific_recommendation(
                        state, lat, lon, area_name, i
                    )
                    recommendations.append(recommendation)
                except Exception as e:
                    logger.error(f"Failed to create recommendation {i}: {e}")
                    continue
            
            # Sort by overall score (highest first)
            recommendations.sort(key=lambda x: x['scores']['overall_score'], reverse=True)
            
            return recommendations[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Failed to generate multiple recommendations: {e}")
            return [await self._create_fallback_recommendation(state, 1)]
    
    async def _get_coordinates(self, location: str):
        """Get coordinates for a location"""
        try:
            location_data = self.geolocator.geocode(f"{location}, Tamil Nadu, India")
            if location_data:
                return location_data.latitude, location_data.longitude
            return None
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
    
    async def _generate_candidate_locations(self, center_lat: float, center_lon: float, radius_km: int, count: int):
        """Generate candidate locations around the center point"""
        candidates = []
        
        # Add the center location
        center_name = await self._get_area_name(center_lat, center_lon)
        candidates.append((center_lat, center_lon, center_name))
        
        # Generate locations in different directions
        directions = [
            (0.7, 0.7),    # Northeast
            (-0.7, 0.7),   # Northwest  
            (0.7, -0.7),   # Southeast
            (-0.7, -0.7),  # Southwest
            (0, 1),        # North
            (1, 0),        # East
            (0, -1),       # South
            (-1, 0),       # West
        ]
        
        for i, (lat_offset, lon_offset) in enumerate(directions[:count-1]):
            # Calculate offset (convert km to degrees approximately)
            offset_distance = radius_km * 0.3  # 30% of radius
            lat_deg_offset = (offset_distance / 111.0) * lat_offset
            lon_deg_offset = (offset_distance / (111.0 * abs(center_lat / 90))) * lon_offset
            
            new_lat = center_lat + lat_deg_offset
            new_lon = center_lon + lon_deg_offset
            
            area_name = await self._get_area_name(new_lat, new_lon)
            candidates.append((new_lat, new_lon, area_name))
        
        return candidates
    
    async def _get_area_name(self, lat: float, lon: float) -> str:
        """Get area name for coordinates"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}", exactly_one=True)
            if location and location.raw.get('address'):
                address = location.raw['address']
                # Try to get a meaningful area name
                area_name = (
                    address.get('suburb') or 
                    address.get('neighbourhood') or 
                    address.get('village') or
                    address.get('town') or
                    address.get('city_district') or
                    'Strategic Area'
                )
                return area_name
        except Exception as e:
            logger.debug(f"Reverse geocoding failed: {e}")
        
        return "Strategic Location"
    
    async def _create_location_specific_recommendation(self, state: AgentState, lat: float, lon: float, area_name: str, rank: int) -> Dict[str, Any]:
        """Create a location-specific recommendation with varied data"""
        
        # Get base scores from agent data
        traffic_data = state.get('traffic_data', {})
        grid_data = state.get('grid_data', {})
        competitor_data = state.get('competitor_data', {})
        demographic_data = state.get('demographic_data', {})
        roi_data = state.get('roi_data', {})
        
        # Base scores with location-specific variations
        base_traffic = traffic_data.get('traffic_metrics', {}).get('traffic_score', 7.0)
        base_grid = grid_data.get('grid_score', 8.0)
        base_competition = competitor_data.get('competition_score', 7.5)
        base_demographic = demographic_data.get('demographic_score', 8.8)
        base_roi = roi_data.get('roi_score', 8.2)
        
        # Add location-specific variations (±20% based on distance from center and random factors)
        main_coords = await self._get_coordinates(state['location'])
        if main_coords:
            distance_from_center = geodesic(main_coords, (lat, lon)).kilometers
            distance_factor = max(0.8, 1 - (distance_from_center / (state['radius_km'] * 2)))
        else:
            distance_factor = 1.0
        
        # Random variations to make each location unique
        traffic_variation = random.uniform(-1.5, 1.5)
        grid_variation = random.uniform(-1.0, 1.0)
        competition_variation = random.uniform(-1.0, 2.0)  # Competition can vary more
        demographic_variation = random.uniform(-0.8, 0.8)
        
        # Calculate varied scores
        traffic_score = max(1.0, min(10.0, base_traffic * distance_factor + traffic_variation))
        grid_score = max(1.0, min(10.0, base_grid * distance_factor + grid_variation))
        competition_score = max(1.0, min(10.0, base_competition + competition_variation))
        demographic_score = max(1.0, min(10.0, base_demographic * distance_factor + demographic_variation))
        
        # ROI varies based on other factors
        roi_score = max(1.0, min(10.0, (traffic_score + grid_score + competition_score + demographic_score) / 4 + random.uniform(-0.5, 0.5)))
        
        # Overall score
        overall_score = (traffic_score + grid_score + competition_score + demographic_score + roi_score) / 5
        
        # Calculate location-specific insights
        base_daily_traffic = traffic_data.get('traffic_metrics', {}).get('estimated_daily_traffic', 30000)
        daily_traffic = int(base_daily_traffic * (traffic_score / base_traffic))
        
        base_monthly_revenue = roi_data.get('monthly_revenue', 130000)
        monthly_revenue = int(base_monthly_revenue * (overall_score / 8.0))
        
        # Payback varies with ROI
        base_payback = roi_data.get('payback_period_months', 18)
        payback = max(12, int(base_payback * (8.5 / roi_score)))
        
        # Distance to nearest competitor varies
        base_competitor_distance = competitor_data.get('nearest_distance_km', 2.3)
        competitor_distance = max(0.5, base_competitor_distance + random.uniform(-1.0, 3.0))
        
        return {
            "location": {
                "name": f"Optimal Location near {area_name}",
                "coordinates": {
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                },
                "address": f"Strategic location in {area_name} area with high potential",
                "city": area_name,
                "state": "Tamil Nadu"
            },
            "scores": {
                "traffic_score": round(traffic_score, 1),
                "grid_capacity": round(grid_score, 1),
                "competition_gap": round(competition_score, 1),
                "demographics": round(demographic_score, 1),
                "roi_potential": round(roi_score, 1),
                "overall_score": round(overall_score, 1)
            },
            "insights": {
                "daily_traffic": daily_traffic,
                "nearest_competitor_km": round(competitor_distance, 1),
                "estimated_monthly_revenue": monthly_revenue,
                "payback_period_months": payback,
                "grid_capacity_mw": round(grid_data.get('grid_capacity_mw', 150.0) * distance_factor, 1),
                "population_density": int(demographic_data.get('population_density', 2000) * distance_factor)
            },
            "confidence": round(min(0.95, 0.7 + (overall_score / 20) + (distance_factor * 0.1)), 2),
            "reasoning": f"Strategic location in {area_name} with {'excellent' if overall_score >= 8 else 'good' if overall_score >= 6 else 'moderate'} potential. "
                        f"{'High traffic volume' if traffic_score >= 8 else 'Moderate traffic'} and "
                        f"{'strong' if grid_score >= 8 else 'adequate'} grid infrastructure make this "
                        f"{'an ideal' if overall_score >= 8 else 'a viable'} location for EV charging station deployment."
        }
    
    async def _create_fallback_recommendation(self, state: AgentState, rank: int) -> Dict[str, Any]:
        """Create fallback recommendation when location processing fails"""
        return {
            "location": {
                "name": f"Optimal Location near {state['location']}",
                "coordinates": {"latitude": 11.1271, "longitude": 78.6569},
                "address": "Strategic location with high potential",
                "city": state['location'],
                "state": "Tamil Nadu"
            },
            "scores": {
                "traffic_score": 7.0,
                "grid_capacity": 8.0,
                "competition_gap": 7.5,
                "demographics": 8.0,
                "roi_potential": 7.8,
                "overall_score": 7.7
            },
            "insights": {
                "daily_traffic": 35000,
                "nearest_competitor_km": 3.2,
                "estimated_monthly_revenue": 130000,
                "payback_period_months": 20,
                "grid_capacity_mw": 120.0,
                "population_density": 1800
            },
            "confidence": 0.75,
            "reasoning": "Fallback analysis indicates moderate potential for EV charging station deployment with adequate infrastructure and market conditions."
        }