import google.generativeai as genai
import logging
from typing import Dict, Any, Optional
from app.config import settings
# No api_service or llm_service instance here

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Gemini LLM"""

    def __init__(self):
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize Gemini API"""
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not provided. LLM features will be limited.")
            return

        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("✅ Gemini LLM initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")

    async def generate_reasoning(
        self, agent_data: Dict[str, Any], location: str, scores: Dict[str, float]
    ) -> str:
        """Generate AI reasoning for recommendations"""
        if not self.model:
            return self._fallback_reasoning(scores, location)

        try:
            prompt = f"""
            Analyze the following EV charging station location data and provide a concise reasoning:
            
            Location: {location}
            
            Scores:
            - Traffic Score: {scores.get('traffic_score', 0)}/10
            - Grid Capacity: {scores.get('grid_capacity', 0)}/10  
            - Competition Gap: {scores.get('competition_gap', 0)}/10
            - Demographics: {scores.get('demographics', 0)}/10
            - ROI Potential: {scores.get('roi_potential', 0)}/10
            - Overall Score: {scores.get('overall_score', 0)}/10
            
            Agent Analysis Data:
            Traffic Data: {agent_data.get('traffic_data', {})}
            Grid Data: {agent_data.get('grid_data', {})}
            Competitor Data: {agent_data.get('competitor_data', {})}
            Demographic Data: {agent_data.get('demographic_data', {})}
            ROI Data: {agent_data.get('roi_data', {})}
            
            Provide a 2-3 sentence reasoning for why this location is recommended for EV charging station placement.
            Focus on the key strengths and business opportunity.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"LLM reasoning generation failed: {e}")
            return self._fallback_reasoning(scores, location)

    def _fallback_reasoning(self, scores: Dict[str, float], location: str) -> str:
        """Fallback reasoning when LLM is not available"""
        overall_score = scores.get("overall_score", 0)

        if overall_score >= 8:
            return f"Excellent location near {location} with high traffic flow, strong grid infrastructure, limited competition, favorable demographics, and strong ROI potential making it ideal for EV charging station deployment."
        elif overall_score >= 6:
            return f"Good location near {location} with solid fundamentals across traffic, infrastructure, and market conditions providing a viable opportunity for EV charging station installation."
        else:
            return f"Moderate location near {location} with some challenges but still presenting opportunities for strategic EV charging station placement with proper planning."

    async def analyze_market_trends(self, location: str) -> Dict[str, Any]:
        """Analyze EV market trends for the location"""
        if not self.model:
            return {"analysis": "Market trend analysis requires LLM service"}

        try:
            prompt = f"""
            Analyze the EV market trends and opportunities for {location}, Tamil Nadu:
            
            Consider:
            1. EV adoption rates in Tamil Nadu
            2. Government policies and incentives
            3. Infrastructure development plans
            4. Market growth potential
            5. Key challenges and opportunities
            
            Provide a brief analysis in JSON format with key insights.
            """

            response = self.model.generate_content(prompt)
            return {"analysis": response.text.strip()}

        except Exception as e:
            logger.error(f"Market trend analysis failed: {e}")
            return {
                "analysis": f"Growing EV market in {location} with government support and increasing infrastructure development."
            }