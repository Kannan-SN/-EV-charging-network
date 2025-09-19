# backend/tests/test_agents.py
import pytest
import asyncio
from app.agents.traffic_agent import TrafficFlowAnalyst
from app.agents.grid_agent import GridCapacityEvaluator
from app.agents.competitor_agent import CompetitorMappingAgent
from app.agents.demographic_agent import DemographicInsightsAgent
from app.agents.roi_agent import CostROIEstimator
from app.models import AgentState, StationType


@pytest.fixture
def sample_state():
    """Create a sample agent state for testing"""
    return AgentState(
        location="Chennai, Tamil Nadu",
        radius_km=50,
        budget=5000000,
        station_type=StationType.FAST,
    )


class TestTrafficFlowAnalyst:
    """Test cases for Traffic Flow Analyst"""

    def test_agent_initialization(self):
        agent = TrafficFlowAnalyst()
        assert agent.name == "Traffic Flow Analyst"

    @pytest.mark.asyncio
    async def test_traffic_analysis(self, sample_state):
        agent = TrafficFlowAnalyst()
        result_state = await agent.execute(sample_state)

        # Check that traffic data was added
        assert result_state.traffic_data is not None

        # Check for required fields
        if "error" not in result_state.traffic_data:
            assert "traffic_metrics" in result_state.traffic_data
            assert "coordinates" in result_state.traffic_data


class TestGridCapacityEvaluator:
    """Test cases for Grid Capacity Evaluator"""

    def test_agent_initialization(self):
        agent = GridCapacityEvaluator()
        assert agent.name == "Grid Capacity Evaluator"

    @pytest.mark.asyncio
    async def test_grid_analysis(self, sample_state):
        agent = GridCapacityEvaluator()
        result_state = await agent.execute(sample_state)

        # Check that grid data was added
        assert result_state.grid_data is not None
        assert "grid_score" in result_state.grid_data
        assert result_state.grid_data["grid_score"] >= 0
        assert result_state.grid_data["grid_score"] <= 10


class TestCompetitorMappingAgent:
    """Test cases for Competitor Mapping Agent"""

    def test_agent_initialization(self):
        agent = CompetitorMappingAgent()
        assert agent.name == "Competitor Mapping Agent"

    @pytest.mark.asyncio
    async def test_competitor_analysis(self, sample_state):
        agent = CompetitorMappingAgent()
        result_state = await agent.execute(sample_state)

        # Check that competitor data was added
        assert result_state.competitor_data is not None

        # Check for required fields
        if "error" not in result_state.competitor_data:
            assert "existing_stations" in result_state.competitor_data
            assert "competition_score" in result_state.competitor_data


class TestDemographicInsightsAgent:
    """Test cases for Demographic Insights Agent"""

    def test_agent_initialization(self):
        agent = DemographicInsightsAgent()
        assert agent.name == "Demographic Insights Agent"

    @pytest.mark.asyncio
    async def test_demographic_analysis(self, sample_state):
        agent = DemographicInsightsAgent()
        result_state = await agent.execute(sample_state)

        # Check that demographic data was added
        assert result_state.demographic_data is not None
        assert "demographic_score" in result_state.demographic_data
        assert result_state.demographic_data["demographic_score"] >= 0
        assert result_state.demographic_data["demographic_score"] <= 10


class TestCostROIEstimator:
    """Test cases for Cost & ROI Estimator"""

    def test_agent_initialization(self):
        agent = CostROIEstimator()
        assert agent.name == "Cost & ROI Estimator"

    @pytest.mark.asyncio
    async def test_roi_analysis(self, sample_state):
        agent = CostROIEstimator()
        result_state = await agent.execute(sample_state)

        # Check that ROI data was added
        assert result_state.roi_data is not None
        assert "roi_score" in result_state.roi_data
        assert "installation_cost" in result_state.roi_data
        assert "payback_period_months" in result_state.roi_data


# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self):
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    def test_optimization_health(self):
        response = client.get("/api/v1/optimize/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "optimization"
        assert data["status"] == "healthy"


class TestOptimizationEndpoints:
    """Test optimization endpoints"""

    def test_optimization_endpoint_valid_request(self):
        request_data = {
            "location": "Chennai, Tamil Nadu",
            "radius_km": 50,
            "budget": 5000000,
            "station_type": "fast",
            "max_recommendations": 5,
        }

        response = client.post("/api/v1/optimize/", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "request_id" in data
        assert "recommendations" in data
        assert "processing_time_seconds" in data
        assert isinstance(data["recommendations"], list)

    def test_optimization_endpoint_invalid_request(self):
        request_data = {
            "location": "",  # Empty location should cause error
            "radius_km": -10,  # Negative radius should be invalid
        }

        response = client.post("/api/v1/optimize/", json=request_data)
        # Should either return 422 (validation error) or 200 with errors in metadata
        assert response.status_code in [200, 422]

    def test_optimization_endpoint_missing_fields(self):
        request_data = {}  # Missing required location field

        response = client.post("/api/v1/optimize/", json=request_data)
        assert response.status_code == 422  # Validation error
