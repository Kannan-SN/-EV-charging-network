# backend/app/models.py (Fixed for LangGraph compatibility)
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StationType(str, Enum):
    """Types of charging stations"""
    FAST = "fast"
    REGULAR = "regular"
    ULTRA_FAST = "ultra_fast"

class OptimizationRequest(BaseModel):
    """Request model for optimization endpoint"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    location: str = Field(..., description="Target location (e.g., 'Chennai, Tamil Nadu')")
    radius_km: int = Field(default=50, ge=1, le=200, description="Search radius in kilometers")
    budget: Optional[int] = Field(default=5000000, ge=100000, description="Budget in INR")
    station_type: StationType = Field(default=StationType.FAST, description="Type of charging station")
    max_recommendations: int = Field(default=5, ge=1, le=20, description="Maximum recommendations to return")

class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class LocationInfo(BaseModel):
    """Location information"""
    name: str
    coordinates: Coordinates
    address: str
    city: Optional[str] = None
    state: str = "Tamil Nadu"

class AgentScores(BaseModel):
    """Scores from different agents"""
    traffic_score: float = Field(..., ge=0, le=10)
    grid_capacity: float = Field(..., ge=0, le=10)
    competition_gap: float = Field(..., ge=0, le=10)
    demographics: float = Field(..., ge=0, le=10)
    roi_potential: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)

class LocationInsights(BaseModel):
    """Detailed insights for a location"""
    daily_traffic: Optional[int] = None
    nearest_competitor_km: Optional[float] = None
    estimated_monthly_revenue: Optional[int] = None
    payback_period_months: Optional[int] = None
    grid_capacity_mw: Optional[float] = None
    population_density: Optional[int] = None

class OptimizationRecommendation(BaseModel):
    """Single location recommendation"""
    location: LocationInfo
    scores: AgentScores
    insights: LocationInsights
    confidence: float = Field(..., ge=0, le=1, description="Confidence level of recommendation")
    reasoning: str = Field(..., description="AI reasoning for recommendation")

class OptimizationResponse(BaseModel):
    """Response model for optimization endpoint"""
    request_id: str
    recommendations: List[OptimizationRecommendation]
    processing_time_seconds: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}

# FIXED: Use TypedDict for LangGraph compatibility instead of Pydantic
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """State passed between agents in LangGraph workflow - Using TypedDict for compatibility"""
    location: str
    radius_km: int
    budget: int
    station_type: str
    
    # Agent results - all optional since they're populated during workflow
    traffic_data: Optional[Dict[str, Any]]
    grid_data: Optional[Dict[str, Any]]
    competitor_data: Optional[Dict[str, Any]]
    demographic_data: Optional[Dict[str, Any]]
    roi_data: Optional[Dict[str, Any]]
    
    # Final results
    recommendations: List[Dict[str, Any]]
    errors: List[str]

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str] = {}

class AgentResult(BaseModel):
    """Result from individual agent"""
    agent_name: str
    status: str  # success, error, partial
    data: Dict[str, Any]
    processing_time_seconds: float
    error_message: Optional[str] = None