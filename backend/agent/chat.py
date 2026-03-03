from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# 1. Initialize the ReAct Agent
portfolio_chat_agent = Agent(
    'gemini-3-flash-preview',
    system_prompt=(
        "You are an analytical Wealthsimple Advisory Co-Pilot. "
        "You help human advisors answer deep-dive questions about a client's portfolio. "
        "Always use your available tools to perform calculations rather than guessing the math. "
        "Keep your answers concise and professional."
    )
)

# 2. Give the Agent a Tool (This makes it a ReAct agent!)
@portfolio_chat_agent.tool
def calculate_compound_interest(ctx: RunContext, principal: float, annual_addition: float, years: int, rate: float = 0.06) -> str:
    """
    Calculates future portfolio value using compound interest.
    Call this whenever the user asks about future projections or compounding savings.
    """
    print(f"-> ReAct Agent called tool: calculate_compound_interest(principal={principal}, addition={annual_addition}, years={years})")
    
    total = principal
    for _ in range(years):
        total = (total + annual_addition) * (1 + rate)
        
    return f"The projected future value is ${total:,.2f} assuming a {rate*100}% annual return."

# A quick way to test the ReAct agent directly
if __name__ == "__main__":
    import asyncio
    async def test():
        # The AI will read this, realize it needs to do math, autonomously call the tool, and then formulate a response.
        question = "If my client invests their $1,590 in annual fee savings every year for 10 years, starting with a $0 baseline, what will it grow to at a 6% return?"
        print(f"Question: {question}")
        result = await portfolio_chat_agent.run(question)
        print(f"\nAnswer: {result.data}")

    asyncio.run(test())