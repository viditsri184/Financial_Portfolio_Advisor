# backend/routers/portfolio.py

from fastapi import APIRouter, HTTPException, Query

from ..agents.portfolio_agent import portfolio_agent

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("")
def get_portfolio(session_id: str = Query(..., description="User session ID")):
    """
    Returns asset allocation + explanation based on the user's risk profile.
    Uses PortfolioAgent.
    """
    try:
        result = portfolio_agent.construct_portfolio(session_id)

        return {
            "allocation": result["allocation"],
            "explanation": result["explanation"]
        }

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
