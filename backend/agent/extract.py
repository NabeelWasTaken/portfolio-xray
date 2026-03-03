import os
from pydantic import BaseModel, Field
from typing import List
from pydantic_ai import Agent
from dotenv import load_dotenv
import asyncio

# Load the API key from .env (PydanticAI will automatically look for GROQ_API_KEY)
load_dotenv(dotenv_path="../.env")

# 1. Define the Strict Schema (The "Wealthsimple Polish")
class PortfolioHolding(BaseModel):
    fund_name: str = Field(description="The full name of the mutual fund, ETF, or stock")
    ticker: str = Field(description="The exact ticker symbol. If not found, output 'UNKNOWN'")
    dollar_amount: float = Field(description="The total monetary value or balance of the holding. Strip out commas and dollar signs.")

class ExtractionResult(BaseModel):
    holdings: List[PortfolioHolding] = Field(description="A list of all the financial holdings extracted from the document.")

# 2. Initialize the PydanticAI Agent with Groq
extractor_agent = Agent(
    'gemini-3-flash-preview', 
    output_type=ExtractionResult,
    system_prompt=(
        "You are an expert financial data extraction assistant. "
        "Your job is to read messy, unstructured portfolio statements "
        "and precisely extract the fund name, ticker, and dollar amount for each holding. "
        "You will receive text that has already had PII (like names and account numbers) masked. "
        "Output the data strictly adhering to the requested schema. Do not include introductory text."
    )
)


# 3. The main extraction function
async def extract_holdings(sanitized_text: str) -> ExtractionResult:
    """
    Takes the PII-scrubbed text and uses Gemini + PydanticAI to return structured data.
    """
    result = await extractor_agent.run(sanitized_text)
    return result.output

# A quick way to test the extraction directly
if __name__ == "__main__":
    async def test():
        sample_messy_text = """
        PAGE 1
        Client: <PERSON>
        Account: <ACCOUNT_NUMBER>
        Holdings:
        TD Comfort Balanced Growth Portfolio (TDB886) - Value: $15,432.50
        RBC Select Balanced Portfolio - RBF460 - $8,900.00
        """
        print("Sending to Groq...")
        structured_data = await extract_holdings(sample_messy_text)
        print("\n--- Structured Output ---")
        print(structured_data.model_dump_json(indent=2))

    asyncio.run(test())
