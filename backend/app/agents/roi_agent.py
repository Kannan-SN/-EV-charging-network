# backend/app/agents/roi_agent.py (Fixed imports)
import logging
from typing import Dict, Any, List  # Added missing imports

from app.agents.base_agent import BaseAgent
from app.models import AgentState, StationType

logger = logging.getLogger(__name__)

class CostROIEstimator(BaseAgent):
    """Agent for calculating costs and ROI using dynamic data"""
    
    def __init__(self):
        super().__init__("Cost & ROI Estimator")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute ROI analysis using real collected data"""
        try:
            logger.info(f"Starting ROI analysis for {state['location']}")
            
            if 'errors' not in state:
                state['errors'] = []
            
            # Calculate ROI based on all collected data from other agents
            roi_data = await self._calculate_dynamic_roi(state)
            
            state['roi_data'] = roi_data
            logger.info("ROI analysis completed successfully")
            
        except Exception as e:
            error_msg = f"ROI analysis failed: {str(e)}"
            logger.error(error_msg)
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(error_msg)
            state['roi_data'] = self._get_fallback_roi_data(state)
        
        return state
    
    async def _calculate_dynamic_roi(self, state: AgentState) -> Dict[str, Any]:
        """Calculate ROI using real data from other agents"""
        
        # Get data from other agents
        traffic_data = state.get('traffic_data', {})
        grid_data = state.get('grid_data', {})
        competitor_data = state.get('competitor_data', {})
        demographic_data = state.get('demographic_data', {})
        
        # Base installation costs by station type (realistic INR costs)
        station_costs = {
            "fast": 4500000,      # 45L for DC fast charging
            "regular": 2000000,   # 20L for AC charging  
            "ultra_fast": 7000000 # 70L for ultra-fast charging
        }
        
        station_type = state.get('station_type', 'fast')
        base_installation_cost = station_costs.get(station_type, 4500000)
        
        # Dynamic cost adjustments based on real data
        cost_adjustments = self._calculate_cost_adjustments(grid_data, traffic_data)
        total_installation_cost = base_installation_cost * cost_adjustments['cost_multiplier']
        
        # Dynamic revenue calculation based on real data
        revenue_factors = self._calculate_revenue_factors(
            traffic_data, demographic_data, competitor_data
        )
        
        base_monthly_revenue = {
            "fast": 180000,       # 1.8L for DC fast
            "regular": 80000,     # 80K for AC
            "ultra_fast": 320000  # 3.2L for ultra-fast
        }
        
        monthly_revenue = base_monthly_revenue.get(station_type, 180000)
        monthly_revenue *= revenue_factors['revenue_multiplier']
        
        # Operating costs (percentage of revenue + fixed costs)
        monthly_operating_cost = (monthly_revenue * 0.25) + 25000  # 25% + 25K fixed
        net_monthly_income = monthly_revenue - monthly_operating_cost
        
        # Payback period calculation
        if net_monthly_income > 0:
            payback_months = total_installation_cost / net_monthly_income
        else:
            payback_months = 999  # Indicates negative cash flow
        
        # ROI Score calculation (0-10)
        roi_score = self._calculate_roi_score(
            payback_months, revenue_factors, cost_adjustments
        )
        
        # Risk assessment
        risk_factors = self._assess_risk_factors(
            competitor_data, grid_data, demographic_data
        )
        
        return {
            "installation_cost": int(total_installation_cost),
            "cost_adjustments": cost_adjustments,
            "monthly_revenue": int(monthly_revenue),
            "monthly_operating_cost": int(monthly_operating_cost),
            "net_monthly_income": int(net_monthly_income),
            "revenue_factors": revenue_factors,
            "payback_period_months": int(min(payback_months, 99)),
            "roi_score": round(roi_score, 1),
            "annual_roi_percentage": round((net_monthly_income * 12 / total_installation_cost * 100), 1) if total_installation_cost > 0 else 0,
            "profitability": self._assess_profitability(roi_score),
            "risk_assessment": risk_factors,
            "break_even_utilization": self._calculate_break_even_utilization(monthly_operating_cost, station_type),
            "location": state.get('location', 'Unknown')
        }
    
    def _calculate_cost_adjustments(self, grid_data: Dict[str, Any], traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost adjustments based on infrastructure requirements"""
        
        base_multiplier = 1.0
        adjustments = {}
        
        # Grid infrastructure adjustments
        if grid_data:
            grid_score = grid_data.get('grid_score', 7.0)
            available_capacity = grid_data.get('available_capacity_mw', 100)
            
            if available_capacity < 20:
                # Need grid upgrades
                base_multiplier *= 1.25
                adjustments['grid_upgrade_needed'] = True
                adjustments['grid_cost_increase'] = 25
            elif grid_score < 5:
                # Poor grid quality
                base_multiplier *= 1.15
                adjustments['grid_reinforcement'] = True
                adjustments['grid_cost_increase'] = 15
            
            # High voltage availability reduces costs
            if grid_data.get('infrastructure_quality') == 'Excellent':
                base_multiplier *= 0.95
                adjustments['infrastructure_bonus'] = True
        
        # Traffic accessibility adjustments
        if traffic_data:
            road_analysis = traffic_data.get('road_analysis', {})
            highway_types = road_analysis.get('highway_types', {})
            
            # Check if major road access available
            major_roads = highway_types.get('primary', 0) + highway_types.get('motorway', 0)
            
            if major_roads == 0:
                # Poor road access increases civil work costs
                base_multiplier *= 1.20
                adjustments['access_road_needed'] = True
                adjustments['civil_cost_increase'] = 20
            elif major_roads >= 2:
                # Excellent access reduces costs
                base_multiplier *= 0.98
                adjustments['excellent_access'] = True
        
        return {
            'cost_multiplier': round(base_multiplier, 2),
            'adjustments': adjustments,
            'base_cost_factors': {
                'grid_impact': round((base_multiplier - 1.0) * 100, 1),
                'access_impact': 0  # Could be expanded
            }
        }
    
    def _calculate_revenue_factors(
        self, 
        traffic_data: Dict[str, Any], 
        demographic_data: Dict[str, Any], 
        competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate revenue multipliers based on market conditions"""
        
        base_multiplier = 1.0
        factors = {}
        
        # Traffic volume impact
        if traffic_data:
            traffic_metrics = traffic_data.get('traffic_metrics', {})
            daily_traffic = traffic_metrics.get('estimated_daily_traffic', 10000)
            
            if daily_traffic > 50000:
                traffic_multiplier = 1.4
                factors['high_traffic'] = True
            elif daily_traffic > 30000:
                traffic_multiplier = 1.2
                factors['good_traffic'] = True
            elif daily_traffic > 15000:
                traffic_multiplier = 1.0
                factors['average_traffic'] = True
            else:
                traffic_multiplier = 0.8
                factors['low_traffic'] = True
            
            base_multiplier *= traffic_multiplier
        
        # Demographic impact
        if demographic_data:
            ev_adoption = demographic_data.get('ev_adoption_rate', 0.05)
            income_score = demographic_data.get('income_score', 6.0)
            population = demographic_data.get('population', 50000)
            
            # EV adoption rate impact
            if ev_adoption > 0.15:
                ev_multiplier = 1.3
                factors['high_ev_adoption'] = True
            elif ev_adoption > 0.08:
                ev_multiplier = 1.1
                factors['growing_ev_adoption'] = True
            else:
                ev_multiplier = 0.9
                factors['early_ev_market'] = True
            
            # Income level impact
            if income_score > 8:
                income_multiplier = 1.2
                factors['high_income_area'] = True
            elif income_score > 6:
                income_multiplier = 1.0
                factors['middle_income_area'] = True
            else:
                income_multiplier = 0.85
                factors['lower_income_area'] = True
            
            # Population size impact
            if population > 500000:
                pop_multiplier = 1.15
                factors['large_market'] = True
            elif population > 100000:
                pop_multiplier = 1.0
                factors['medium_market'] = True
            else:
                pop_multiplier = 0.9
                factors['small_market'] = True
            
            base_multiplier *= ev_multiplier * income_multiplier * pop_multiplier
        
        # Competition impact
        if competitor_data:
            market_opportunity = competitor_data.get('market_opportunity', 'Medium')
            
            if market_opportunity == 'Excellent':
                competition_multiplier = 1.25
                factors['no_competition'] = True
            elif market_opportunity == 'High':
                competition_multiplier = 1.1
                factors['low_competition'] = True
            elif market_opportunity == 'Medium':
                competition_multiplier = 1.0
                factors['moderate_competition'] = True
            else:
                competition_multiplier = 0.75
                factors['high_competition'] = True
            
            base_multiplier *= competition_multiplier
        
        return {
            'revenue_multiplier': round(base_multiplier, 2),
            'factors': factors,
            'market_attractiveness': 'High' if base_multiplier > 1.3 else 'Medium' if base_multiplier > 0.9 else 'Low'
        }
    
    def _calculate_roi_score(
        self, 
        payback_months: float, 
        revenue_factors: Dict[str, Any], 
        cost_adjustments: Dict[str, Any]
    ) -> float:
        """Calculate ROI score (0-10) based on financial metrics"""
        
        # Base score from payback period
        if payback_months <= 12:
            payback_score = 10.0
        elif payback_months <= 18:
            payback_score = 8.5
        elif payback_months <= 24:
            payback_score = 7.0
        elif payback_months <= 36:
            payback_score = 5.5
        elif payback_months <= 48:
            payback_score = 4.0
        else:
            payback_score = 2.0
        
        # Adjust for market attractiveness
        market_attractiveness = revenue_factors.get('market_attractiveness', 'Medium')
        if market_attractiveness == 'High':
            payback_score += 0.5
        elif market_attractiveness == 'Low':
            payback_score -= 1.0
        
        # Adjust for cost factors
        cost_multiplier = cost_adjustments.get('cost_multiplier', 1.0)
        if cost_multiplier > 1.2:
            payback_score -= 0.5
        elif cost_multiplier < 1.0:
            payback_score += 0.3
        
        return max(0, min(10, payback_score))
    
    def _assess_profitability(self, roi_score: float) -> str:
        """Assess profitability category"""
        if roi_score >= 8.0:
            return "Excellent"
        elif roi_score >= 6.5:
            return "Good"
        elif roi_score >= 5.0:
            return "Fair"
        else:
            return "Poor"
    
    def _assess_risk_factors(
        self, 
        competitor_data: Dict[str, Any], 
        grid_data: Dict[str, Any], 
        demographic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk factors for the investment"""
        
        risks = []
        risk_level = "Low"
        
        # Competition risks
        if competitor_data and competitor_data.get('market_opportunity') == 'Low':
            risks.append("High competition in market")
            risk_level = "High"
        
        # Infrastructure risks
        if grid_data and grid_data.get('available_capacity_mw', 100) < 20:
            risks.append("Limited grid capacity requires upgrades")
            risk_level = "Medium" if risk_level == "Low" else "High"
        
        # Market risks
        if demographic_data and demographic_data.get('ev_adoption_rate', 0.05) < 0.03:
            risks.append("Low EV adoption rate in area")
            risk_level = "Medium" if risk_level == "Low" else risk_level
        
        return {
            'risk_level': risk_level,
            'risk_factors': risks,
            'mitigation_strategies': self._suggest_mitigation_strategies(risks)
        }
    
    def _suggest_mitigation_strategies(self, risks: List[str]) -> List[str]:
        """Suggest risk mitigation strategies"""
        strategies = []
        
        for risk in risks:
            if "competition" in risk.lower():
                strategies.append("Focus on premium service and faster charging speeds")
            elif "grid" in risk.lower():
                strategies.append("Partner with utility company for grid upgrades")
            elif "adoption" in risk.lower():
                strategies.append("Implement aggressive marketing and partnerships with auto dealers")
        
        return strategies
    
    def _calculate_break_even_utilization(self, monthly_operating_cost: int, station_type: str) -> Dict[str, Any]:
        """Calculate break-even utilization rates"""
        
        # Average revenue per charging session by type
        revenue_per_session = {
            "fast": 400,       # INR per session
            "regular": 150,    # INR per session
            "ultra_fast": 600  # INR per session
        }
        
        session_revenue = revenue_per_session.get(station_type, 400)
        sessions_needed = monthly_operating_cost / session_revenue
        daily_sessions_needed = sessions_needed / 30
        
        return {
            'monthly_sessions_needed': int(sessions_needed),
            'daily_sessions_needed': round(daily_sessions_needed, 1),
            'utilization_hours_needed': round(daily_sessions_needed * 0.5, 1),  # 30 min per session avg
            'revenue_per_session': session_revenue
        }
    
    def _get_fallback_roi_data(self, state: AgentState) -> Dict[str, Any]:
        """Fallback ROI data when calculation fails"""
        budget = state.get('budget', 5000000)
        
        return {
            "installation_cost": int(budget * 0.8),
            "monthly_revenue": 120000,
            "monthly_operating_cost": 40000,
            "net_monthly_income": 80000,
            "payback_period_months": 24,
            "roi_score": 6.0,
            "profitability": "Fair",
            "data_source": "fallback",
            "location": state.get('location', 'Unknown'),
            "note": "Using fallback data due to calculation errors"
        }