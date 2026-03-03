from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import asyncio

# Import our custom tools
from .security import scrub_pii
from .extract import extract_holdings, PortfolioHolding
from .mock_db import get_fund_data, WEALTHSIMPLE_EQUIVALENT

# 1. Define the State
class AgentState(TypedDict):
    raw_text: str
    sanitized_text: str
    holdings: List[PortfolioHolding]
    enriched_data: List[Dict[str, Any]]
    total_legacy_fee_dollars: float
    total_ws_fee_dollars: float
    analysis_summary: str
    overlap_analysis: str

# 2. Define the Nodes
def scrub_node(state: AgentState) -> dict:
    """Node 1: Scrubs PII from the raw input."""
    print("-> Running Scrub Node")
    clean_text = scrub_pii(state["raw_text"])
    return {"sanitized_text": clean_text}

async def extract_node(state: AgentState) -> dict:
    """Node 2: Extracts structured holdings using the LLM."""
    print("-> Running Extract Node")
    extracted_result = await extract_holdings(state["sanitized_text"])
    return {"holdings": extracted_result.holdings}

def enrich_node(state: AgentState) -> dict:
    """Node 3: Calculates deterministic fees against our mock database."""
    print("-> Running Enrich Node")
    enriched_portfolio = []
    legacy_fees = 0.0
    ws_fees = 0.0
    
    for holding in state["holdings"]:
        fund_data = get_fund_data(holding.ticker)
        
        # Calculate fee drag deterministically
        holding_legacy_fee = holding.dollar_amount * fund_data["mer"]
        holding_ws_fee = holding.dollar_amount * WEALTHSIMPLE_EQUIVALENT["mer"]
        
        legacy_fees += holding_legacy_fee
        ws_fees += holding_ws_fee
        
        enriched_portfolio.append({
            "fund_name": fund_data["fund_name"],
            "ticker": holding.ticker,
            "amount": holding.dollar_amount,
            "legacy_mer": fund_data["mer"],
            "fee_dollars": holding_legacy_fee,
            "top_holdings": fund_data["top_holdings"]
        })
        
    return {
        "enriched_data": enriched_portfolio,
        "total_legacy_fee_dollars": round(legacy_fees, 2),
        "total_ws_fee_dollars": round(ws_fees, 2)
    }

def overlap_node(state: AgentState) -> dict:
    """Node 4: A deterministic Python function (no LLM required) that flattens 
    the portfolio to find duplicate stock exposures across different funds."""
    print("-> Running Overlap Node")
    
    stock_exposure = {}
    total_portfolio_value = sum(item["amount"] for item in state.get("enriched_data", []))
    
    if total_portfolio_value == 0:
        return {"overlap_analysis": "No overlap detected. Portfolio value is zero."}
        
    # Calculate exactly how much money is sitting in each underlying stock
    for fund in state["enriched_data"]:
        fund_amount = fund["amount"]
        for stock in fund["top_holdings"]:
            ticker = stock["ticker"]
            dollar_value = fund_amount * stock["weight"]
            
            if ticker in stock_exposure:
                stock_exposure[ticker] += dollar_value
            else:
                stock_exposure[ticker] = dollar_value
                
    # Find the top 3 most duplicated exposures
    overlap_summary = []
    sorted_exposure = sorted(stock_exposure.items(), key=lambda x: x[1], reverse=True)
    
    for ticker, amount in sorted_exposure[:3]:
        percentage = (amount / total_portfolio_value) * 100
        overlap_summary.append(f"{percentage:.1f}% exposure to {ticker}")
        
    final_string = "High Concentration Risk: " + ", ".join(overlap_summary)
    return {"overlap_analysis": final_string}

def analyze_node(state: AgentState) -> dict:
    """Node 5: Generates the core narrative for the Tear Sheet."""
    print("-> Running Analyze Node")
    savings = state["total_legacy_fee_dollars"] - state["total_ws_fee_dollars"]
    summary = f"Client is paying ${state['total_legacy_fee_dollars']} in hidden fees. Moving to Wealthsimple saves ${savings} annually."
    return {"analysis_summary": summary}

# 3. Build the Graph
workflow = StateGraph(AgentState)

# Add all our nodes (including the missing overlap node)
workflow.add_node("scrub", scrub_node)
workflow.add_node("extract", extract_node)
workflow.add_node("enrich", enrich_node)
workflow.add_node("overlap", overlap_node)
workflow.add_node("analyze", analyze_node)

# Define the routing (the flow of data)
workflow.set_entry_point("scrub")
workflow.add_edge("scrub", "extract")
workflow.add_edge("extract", "enrich")
workflow.add_edge("enrich", "overlap")
workflow.add_edge("overlap", "analyze")
workflow.add_edge("analyze", END)

# Compile it into a runnable application
portfolio_agent = workflow.compile()