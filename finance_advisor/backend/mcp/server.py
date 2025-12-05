# backend/mcp/server.py
'''
from mcp.server.fastapi import FastAPIMCPServer

from backend.tools.risk_profile import compute_risk_score
from backend.tools.portfolio_engine import build_portfolio
from backend.tools.portfolio_sim import run_monte_carlo_simulation
from backend.tools.currency_convertor import convert_currency_amount
from backend.tools.finance_data import fetch_nav_data
from backend.rag.retriever import retrieve_top_k

from backend.models.simulate import PortfolioSimulationRequest, Allocation, InvestmentDetails, SimulationParams


# Create MCP Server instance
mcp_server = FastAPIMCPServer()


# -------------------------------------------------------
# Register Tools Below
# -------------------------------------------------------

@mcp_server.tool()
def risk_profile_tool(age: int,
                      income_stability: str,
                      liquidity_needs: str,
                      investment_knowledge: str,
                      answers: dict):
    """Compute risk category based on inputs"""
    payload = {
        "session_id": "mcp_temp",
        "age": age,
        "income_stability": income_stability,
        "liquidity_needs": liquidity_needs,
        "investment_knowledge": investment_knowledge,
        "answers": answers
    }
    return compute_risk_score(payload)


@mcp_server.tool()
def portfolio_tool(risk_category: str):
    """Build portfolio allocation for a risk category."""
    return build_portfolio(risk_category)


@mcp_server.tool()
def simulate_tool(allocation: dict, investment: dict, num_simulations: int):
    """Run Monte Carlo simulation for a given allocation and investment profile."""

    request = PortfolioSimulationRequest(
        session_id="mcp_temp",
        allocation=Allocation(**allocation),
        investment=InvestmentDetails(**investment),
        simulation_params=SimulationParams(num_simulations=num_simulations)
    )
    result = run_monte_carlo_simulation(request)
    return result


@mcp_server.tool()
def currency_tool(from_currency: str, to_currency: str, amount: float):
    """Convert currency using available APIs."""
    return convert_currency_amount(from_currency, to_currency, amount)


@mcp_server.tool()
def nav_tool(symbol: str, date: str = None):
    """Fetch NAV for a fund."""
    return fetch_nav_data(symbol=symbol, date_str=date)


@mcp_server.tool()
def rag_tool(query: str, top_k: int = 5):
    """Run a semantic search using the RAG FAISS index."""
    return retrieve_top_k(query, top_k=top_k)


# Export for use inside /chat
def get_mcp_schema():
    return mcp_server.openai_schema()


def call_mcp_tool(call):
    """Executes a tool call received from Azure GPT."""
    return mcp_server.call_tool(call)
'''