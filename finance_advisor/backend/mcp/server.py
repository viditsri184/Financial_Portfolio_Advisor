# backend/mcp/server.py
"""
Minimal MCP-style tool registry for Azure function calling.

We don't depend on external MCP libraries. Instead, we:
- Register tools (name, description, JSON schema, handler function)
- Expose them as OpenAI/Azure 'tools' (function calling schema)
- Provide a call_mcp_tool() helper to execute a tool from a tool_call object.
"""

from typing import Any, Callable, Dict, List
import json

from backend.tools.risk_profile import compute_risk_score
from backend.tools.portfolio_engine import build_portfolio
from backend.tools.portfolio_sim import run_monte_carlo_simulation
from backend.tools.currency_convertor import convert_currency_amount
from backend.tools.finance_data import fetch_nav_data
from backend.rag.retriever import retrieve_top_k
from backend.models.simulate import (
    PortfolioSimulationRequest,
    Allocation,
    InvestmentDetails,
    SimulationParams,
)

# -------------------------------------------------------------------
# Internal tool registry
# -------------------------------------------------------------------

ToolHandler = Callable[..., Any]

_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_tool(name: str, description: str, parameters_schema: Dict[str, Any]):
    """Decorator to register a function as a tool."""

    def decorator(fn: ToolHandler):
        _TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters_schema,
            "handler": fn,
        }
        return fn

    return decorator


# -------------------------------------------------------------------
# Tool implementations (thin wrappers around your existing logic)
# -------------------------------------------------------------------

@register_tool(
    name="risk_profile_tool",
    description="Compute risk profile based on user inputs.",
    parameters_schema={
        "type": "object",
        "properties": {
            "age": {"type": "integer"},
            "income_stability": {"type": "string"},
            "liquidity_needs": {"type": "string"},
            "investment_knowledge": {"type": "string"},
            "answers": {
                "type": "object",
                "description": "Question-wise answers for risk profiling.",
            },
        },
        "required": ["age", "income_stability", "liquidity_needs", "investment_knowledge"],
    },
)
def risk_profile_tool(age: int,
                      income_stability: str,
                      liquidity_needs: str,
                      investment_knowledge: str,
                      answers: Dict[str, Any] = None):
    payload = {
        "session_id": "mcp_temp",
        "age": age,
        "income_stability": income_stability,
        "liquidity_needs": liquidity_needs,
        "investment_knowledge": investment_knowledge,
        "answers": answers or {},
    }
    return compute_risk_score(payload)


@register_tool(
    name="portfolio_tool",
    description="Build portfolio allocation for a given risk category.",
    parameters_schema={
        "type": "object",
        "properties": {
            "risk_category": {
                "type": "string",
                "description": "Risk profile: conservative, moderate, aggressive, etc.",
            }
        },
        "required": ["risk_category"],
    },
)
def portfolio_tool(risk_category: str):
    return build_portfolio(risk_category)


@register_tool(
    name="simulate_tool",
    description="Run Monte Carlo simulation on a given portfolio allocation.",
    parameters_schema={
        "type": "object",
        "properties": {
            "allocation": {
                "type": "object",
                "description": "Allocation JSON with equity, debt, etc.",
            },
            "investment": {
                "type": "object",
                "description": "Investment details (SIP amount, tenure, lump sum, etc.)",
            },
            "num_simulations": {
                "type": "integer",
                "description": "Number of Monte Carlo simulations to run.",
                "default": 1000,
            },
        },
        "required": ["allocation", "investment"],
    },
)
def simulate_tool(allocation: Dict[str, Any],
                  investment: Dict[str, Any],
                  num_simulations: int = 1000):
    req = PortfolioSimulationRequest(
        session_id="mcp_temp",
        allocation=Allocation(**allocation),
        investment=InvestmentDetails(**investment),
        simulation_params=SimulationParams(num_simulations=num_simulations),
    )
    return run_monte_carlo_simulation(req)


@register_tool(
    name="currency_tool",
    description="Convert an amount from one currency to another.",
    parameters_schema={
        "type": "object",
        "properties": {
            "from_currency": {"type": "string"},
            "to_currency": {"type": "string"},
            "amount": {"type": "number"},
        },
        "required": ["from_currency", "to_currency", "amount"],
    },
)
def currency_tool(from_currency: str, to_currency: str, amount: float):
    return convert_currency_amount(from_currency, to_currency, amount)


@register_tool(
    name="nav_tool",
    description="Fetch NAV for a mutual fund scheme.",
    parameters_schema={
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "description": "Fund symbol / code"},
            "date": {
                "type": "string",
                "description": "Optional date in YYYY-MM-DD format",
            },
        },
        "required": ["symbol"],
    },
)
def nav_tool(symbol: str, date: str = None):
    return fetch_nav_data(symbol=symbol, date_str=date)


@register_tool(
    name="rag_tool",
    description="Retrieve top-k RAG chunks from SEBI / MF docs.",
    parameters_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
)
def rag_tool(query: str, top_k: int = 5):
    return retrieve_top_k(query, top_k=top_k)


# -------------------------------------------------------------------
# Public helpers used by /chat
# -------------------------------------------------------------------

def get_mcp_schema() -> List[Dict[str, Any]]:
    """
    Return tools in OpenAI function-calling format:
    [
      {
        "type": "function",
        "function": {
          "name": ...,
          "description": ...,
          "parameters": {...}
        }
      }, ...
    ]
    """
    tools = []
    for tool in _TOOL_REGISTRY.values():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
        )
    return tools


def call_mcp_tool(tool_call: Any) -> Any:
    """
    Execute a tool call returned by Azure GPT.

    Expects an object with shape like:
      tool_call.function.name
      tool_call.function.arguments (JSON string)
    """
    try:
        func = tool_call.function
        name = func.name
        raw_args = func.arguments or "{}"
        args = json.loads(raw_args)

        if name not in _TOOL_REGISTRY:
            raise ValueError(f"Unknown tool: {name}")

        handler = _TOOL_REGISTRY[name]["handler"]
        result = handler(**args)
        return result

    except Exception as ex:
        return {"error": str(ex)}
