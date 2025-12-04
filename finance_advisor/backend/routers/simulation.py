# backend/routers/simulation.py

from fastapi import APIRouter, HTTPException, Query

from ..agents.simulation_agent import simulation_agent

router = APIRouter(prefix="/simulate", tags=["simulation"])


@router.get("")
def simulate_portfolio(session_id: str = Query(..., description="User session ID")):
    """
    Runs Monte Carlo simulation using SimulationAgent.
    """
    try:
        result = simulation_agent.run_simulation(session_id)

        return {
            "expected_value": result["expected_value"],
            "best_case": result["best_case"],
            "worst_case": result["worst_case"],
            "probability_of_goal_achievement": result["probability_of_goal_achievement"]
        }

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
