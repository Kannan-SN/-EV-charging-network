# backend/app/routers/optimization.py (Fixed for TypedDict state)
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import uuid
import time
import logging

from app.models import (
    OptimizationRequest, 
    OptimizationResponse, 
    AgentState,
    OptimizationRecommendation,
    LocationInfo,
    Coordinates,
    AgentScores,
    LocationInsights
)
from app.workflows.optimization_workflow import OptimizationWorkflow

router = APIRouter(prefix="/optimize", tags=["optimization"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=OptimizationResponse)
async def optimize_charging_stations(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
) -> OptimizationResponse:
    """
    Optimize EV charging station locations using AI agents
    
    This endpoint orchestrates multiple specialized agents to analyze:
    - Traffic flow patterns
    - Electricity grid capacity
    - Competitor presence
    - Demographics
    - ROI potential
    
    Returns optimized location recommendations with detailed insights.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"Starting optimization request {request_id} for {request.location}")
        
        # Initialize agent state as TypedDict
        agent_state: AgentState = {
            'location': request.location,
            'radius_km': request.radius_km,
            'budget': request.budget or 5000000,
            'station_type': request.station_type.value,  # Convert enum to string
            'traffic_data': None,
            'grid_data': None,
            'competitor_data': None,
            'demographic_data': None,
            'roi_data': None,
            'recommendations': [],
            'errors': []
        }
        
        # Initialize and run workflow
        workflow = OptimizationWorkflow()
        final_state = await workflow.run(agent_state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Check for errors
        errors = final_state.get('errors', [])
        if errors:
            logger.warning(f"Request {request_id} completed with errors: {errors}")
        
        # Convert dict recommendations to Pydantic models
        pydantic_recommendations = []
        dict_recommendations = final_state.get('recommendations', [])
        
        for rec_dict in dict_recommendations[:request.max_recommendations]:
            try:
                # Convert dict to Pydantic models
                recommendation = OptimizationRecommendation(
                    location=LocationInfo(
                        name=rec_dict['location']['name'],
                        coordinates=Coordinates(
                            latitude=rec_dict['location']['coordinates']['latitude'],
                            longitude=rec_dict['location']['coordinates']['longitude']
                        ),
                        address=rec_dict['location']['address'],
                        city=rec_dict['location'].get('city'),
                        state=rec_dict['location']['state']
                    ),
                    scores=AgentScores(
                        traffic_score=rec_dict['scores']['traffic_score'],
                        grid_capacity=rec_dict['scores']['grid_capacity'],
                        competition_gap=rec_dict['scores']['competition_gap'],
                        demographics=rec_dict['scores']['demographics'],
                        roi_potential=rec_dict['scores']['roi_potential'],
                        overall_score=rec_dict['scores']['overall_score']
                    ),
                    insights=LocationInsights(
                        daily_traffic=rec_dict['insights'].get('daily_traffic'),
                        nearest_competitor_km=rec_dict['insights'].get('nearest_competitor_km'),
                        estimated_monthly_revenue=rec_dict['insights'].get('estimated_monthly_revenue'),
                        payback_period_months=rec_dict['insights'].get('payback_period_months'),
                        grid_capacity_mw=rec_dict['insights'].get('grid_capacity_mw'),
                        population_density=rec_dict['insights'].get('population_density')
                    ),
                    confidence=rec_dict['confidence'],
                    reasoning=rec_dict['reasoning']
                )
                pydantic_recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Failed to convert recommendation: {e}")
                continue
        
        # Build response
        response = OptimizationResponse(
            request_id=request_id,
            recommendations=pydantic_recommendations,
            processing_time_seconds=processing_time,
            timestamp=datetime.now(),
            metadata={
                "request": request.model_dump(),
                "errors": errors,
                "agents_executed": [
                    "traffic_analysis",
                    "grid_analysis", 
                    "competitor_analysis",
                    "demographic_analysis",
                    "roi_analysis",
                    "final_optimization"
                ]
            }
        )
        
        logger.info(f"Request {request_id} completed successfully in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Optimization failed: {str(e)}"
        
        logger.error(f"Request {request_id} failed: {error_msg}")
        
        # Return error response
        return OptimizationResponse(
            request_id=request_id,
            recommendations=[],
            processing_time_seconds=processing_time,
            timestamp=datetime.now(),
            metadata={
                "request": request.model_dump(),
                "errors": [error_msg],
                "agents_executed": []
            }
        )

@router.get("/health")
async def optimization_health():
    """Check optimization service health"""
    return {
        "service": "optimization",
        "status": "healthy",
        "timestamp": datetime.now(),
        "agents_available": [
            "traffic_flow_analyst",
            "grid_capacity_evaluator",
            "competitor_mapping_agent", 
            "demographic_insights_agent",
            "cost_roi_estimator",
            "location_optimizer"
        ]
    }