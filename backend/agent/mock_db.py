# backend/agent/mock_db.py

"""
A deterministic mock database simulating an external financial API.
This is used by the Enrich Node to fetch Management Expense Ratios (MER) 
and underlying stock overlap without relying on AI hallucinations.
"""

MUTUAL_FUND_DB = {
    "TDB886": {
        "fund_name": "TD Comfort Balanced Growth Portfolio",
        "mer": 0.0204,  # 2.04% MER
        "top_holdings": [
            {"ticker": "MSFT", "weight": 0.045}, # 4.5% of the fund is Microsoft
            {"ticker": "AAPL", "weight": 0.041},
            {"ticker": "TD",   "weight": 0.038},
            {"ticker": "RY",   "weight": 0.035},
            {"ticker": "AMZN", "weight": 0.029},
        ]
    },
    "RBF460": {
        "fund_name": "RBC Select Balanced Portfolio",
        "mer": 0.0194,  # 1.94% MER
        "top_holdings": [
            {"ticker": "RY",   "weight": 0.052},
            {"ticker": "MSFT", "weight": 0.048},
            {"ticker": "AAPL", "weight": 0.040},
            {"ticker": "NVDA", "weight": 0.031},
            {"ticker": "CNR",  "weight": 0.025},
        ]
    },
    "IG100": {
        "fund_name": "IG Core Portfolio Balanced",
        "mer": 0.0225,  # 2.25% MER
        "top_holdings": [
            {"ticker": "AAPL", "weight": 0.050},
            {"ticker": "MSFT", "weight": 0.042},
            {"ticker": "GOOG", "weight": 0.035},
            {"ticker": "TD",   "weight": 0.030},
            {"ticker": "ENB",  "weight": 0.028},
        ]
    }
}

# The baseline Wealthsimple equivalent we will use to calculate the savings
WEALTHSIMPLE_EQUIVALENT = {
    "fund_name": "Wealthsimple Balanced Managed Portfolio",
    "mer": 0.0040,  # 0.40% base management fee
}

def get_fund_data(ticker: str) -> dict:
    """Safely retrieves fund data, returning a default high-fee mock if the ticker isn't found."""
    return MUTUAL_FUND_DB.get(ticker.upper(), {
        "fund_name": "Unknown Legacy Mutual Fund",
        "mer": 0.0210, # Default to a 2.10% fee for dramatic effect if unknown
        "top_holdings": []
    })