from typing import Dict, Any

from ..tools.portfolio_sim import run_monte_carlo_simulation
from ..models.simulate import (
    PortfolioSimulationRequest,
    Allocation,
    InvestmentDetails,
    SimulationParams
)
from ..memory.store import memory_store


class SimulationAgent:
    """
    Agent responsible for running portfolio simulations.
    """

    @staticmethod
    def run_simulation(session_id: str) -> Dict[str, Any]:

        # Load values from Redis
        entity = memory_store.get_entity(session_id)

        # FIX 1: Use last_portfolio, not recommended_portfolio
        portfolio = entity.get("last_portfolio")
        if not portfolio:
            raise ValueError("No portfolio available to simulate. Run PortfolioAgent first.")

        # FIX 2: Read REAL user inputs saved from UI (Option A)
        # Get values from Redis or fallback defaults
        investment_type = entity.get("investment_type", "sip")
        monthly_amount = entity.get("monthly_investment", 10000)
        lumpsum_amount = entity.get("lumpsum_investment", 0)
        duration = entity.get("tenure_years", 10)
        goal_amount = entity.get("goal_amount", 10000000)
        num_sims = entity.get("num_simulations", 5000)

        # Build simulation request model
        request = PortfolioSimulationRequest(
            session_id=session_id,
            allocation=Allocation(**portfolio),
            investment=InvestmentDetails(
                type=investment_type,
                monthly_amount=monthly_amount,
                lumpsum_amount=lumpsum_amount,
                duration_years=duration
            ),
            simulation_params=SimulationParams(num_simulations=num_sims)
        )

        # Run Monte Carlo simulation
        result = run_monte_carlo_simulation(request)

        # Custom probability using user goal
        probability_of_goal = 0
        try:
            probability_of_goal = sum(
                1 for v in result.final_values if v >= goal_amount
            ) / num_sims
        except:
            probability_of_goal = result.probability_of_goal_achievement

        return {
            "expected_value": result.expected_value,
            "best_case": result.best_case,
            "worst_case": result.worst_case,
            "probability_of_goal_achievement": probability_of_goal,
            "final_values": result.final_values 
        }


simulation_agent = SimulationAgent()
