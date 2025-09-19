# backend/app/agents/base_agent.py
from abc import ABC, abstractmethod
import time
import logging
from typing import Any, Dict, List # Import List for better type hinting

from app.models import AgentState, AgentResult # Now AgentState definitely has 'errors'

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the optimization workflow"""

    def __init__(self, name: str):
        super().__init__() # Call superclass __init__ if it exists (for ABC)
        self.name = name
        self.logger = logging.getLogger(f"agent.{name.lower().replace(' ', '_')}")

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute the agent's main functionality

        Args:
            state: Current workflow state

        Returns:
            Updated state with agent's results (must be an AgentState object)
        """
        pass

    async def run_with_metrics(self, state: AgentState) -> AgentResult:
        """Run agent with performance metrics"""
        start_time = time.time()

        try:
            self.logger.info(f"Starting execution of {self.name}")

            # Execute agent logic. Agents are expected to modify 'state' and return it.
            updated_state = await self.execute(state)

            processing_time = time.time() - start_time

            self.logger.info(f"{self.name} completed in {processing_time:.2f}s")

            # Ensure updated_state is actually an AgentState object before accessing its attributes
            if not isinstance(updated_state, AgentState):
                error_msg = f"Agent {self.name} returned an invalid state type: {type(updated_state)}. Expected AgentState."
                self.logger.error(error_msg)
                return AgentResult(
                    agent_name=self.name,
                    status="error",
                    data={},
                    processing_time_seconds=processing_time,
                    error_message=error_msg,
                )

            return AgentResult(
                agent_name=self.name,
                status="success",
                data=self._extract_agent_data(updated_state), # This is where the error was, now updated_state is verified
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"{self.name} failed: {str(e)}"

            self.logger.error(error_msg)

            # In case of an error *during* execution, the initial 'state' might still be valid
            # Or if `updated_state` was not assigned/became invalid, use an empty dict.
            # If the error happened before `updated_state` was properly set, it could be None.
            # We ensure 'data' is always a dict.
            extracted_data = {}
            if isinstance(state, AgentState): # Use original state if execution failed before returning updated_state
                extracted_data = self._extract_agent_data(state)
            else:
                self.logger.warning(f"Original state was not AgentState type in error handler for {self.name}.")

            return AgentResult(
                agent_name=self.name,
                status="error",
                data=extracted_data, # Use extracted data from the initial state
                processing_time_seconds=processing_time,
                error_message=error_msg,
            )

    def _extract_agent_data(self, state: AgentState) -> Dict[str, Any]:
        """Extract relevant data from state for this agent"""
        # Default implementation: return basic state info and errors
        # Subclasses can override to return specific data they produced
        return {
            "errors": state.errors,
            "location_name": state.location,
            "traffic_data": state.traffic_data,
            "grid_data": state.grid_data,
            "competitor_data": state.competitor_data,
            "demographic_data": state.demographic_data,
            "roi_data": state.roi_data,
        }


    def log_info(self, message: str):
        """Log info message with agent name"""
        self.logger.info(f"[{self.name}] {message}")

    def log_warning(self, message: str):
        """Log warning message with agent name"""
        self.logger.warning(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """Log error message with agent name"""
        self.logger.error(f"[{self.name}] {message}")

    def validate_input(self, state: AgentState) -> bool:
        """Validate input state before processing"""
        # Assuming AgentState always has a location and radius_km based on Pydantic defaults/requirements
        if not state.location:
            self.log_error("No location provided in state")
            state.errors.append(f"{self.name}: No location provided.")
            return False

        if state.radius_km <= 0:
            self.log_error("Invalid radius provided")
            state.errors.append(f"{self.name}: Invalid radius provided.")
            return False

        return True