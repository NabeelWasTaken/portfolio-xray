import PyPDF2
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from agent.chat import portfolio_chat_agent

# Import our compiled LangGraph agent
from agent.graph import portfolio_agent

# Load environment variables
load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Portfolio X-Ray API")



# Allow the Next.js frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://portfolio-xray-your-unique-link.vercel.app" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a specialized agent for drafting the sales pitch
email_agent = Agent(
    'gemini-3-flash-preview',
    system_prompt=(
        "You are an expert Wealthsimple financial advisor. "
        "Write a concise, professional, and highly persuasive email to a client. "
        "Highlight the hidden fees they are paying, the specific concentration/overlap risks, "
        "and exactly how much they will save annually by switching to Wealthsimple. "
        "Keep the tone empathetic but mathematically direct. Keep it under 150 words. "
        "Include a subject line at the very top."
    )
)

@app.get("/")
def read_root():
    return {"status": "Portfolio X-Ray Backend is running smoothly."}

@app.post("/api/analyze-portfolio")
async def analyze_portfolio(file: UploadFile = File(...)):
    """
    1. Receives the uploaded file from the frontend.
    2. Extracts the raw text (handles both PDF and TXT).
    3. Triggers the LangGraph workflow.
    4. Returns the structured JSON for the frontend Tear Sheet.
    """
    try:
        print(f"Receiving file: {file.filename}")
        
        file_bytes = await file.read()
        raw_text = ""
        
        # 1. Check if it's a PDF and extract the text
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    raw_text += extracted + "\n"
        else:
            # Fallback for plain text files (like our test-clean.txt)
            raw_text = file_bytes.decode("utf-8")
            
        print(f"Extracted {len(raw_text)} characters of text. Starting LangGraph...")
        
        # 2. Kick off the LangGraph state machine
        initial_state = {"raw_text": raw_text}
        final_state = await portfolio_agent.ainvoke(initial_state)
        
        # 3. Shape the final response for the Next.js dashboard
        return {
            "filename": file.filename,
            "status": "success",
            "holdings": final_state.get("enriched_data", []),
            "legacy_fees": final_state.get("total_legacy_fee_dollars", 0.0),
            "wealthsimple_fees": final_state.get("total_ws_fee_dollars", 0.0),
            "summary": final_state.get("analysis_summary", ""),
            "overlap_analysis": final_state.get("overlap_analysis", "")
        }
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        # Return a 500 error to the frontend if something breaks in the pipeline
        raise HTTPException(status_code=500, detail=str(e))

class EmailRequest(BaseModel):
    client_name: str
    legacy_fees: float
    savings: float
    overlap_summary: str

@app.post("/api/draft-email")
async def draft_pitch_email(request: EmailRequest):
    """
    Node 6: Triggered only when the human advisor clicks "Approve & Draft Pitch Email".
    Passes the strict mathematical context to Gemini to draft a highly personalized sales email.
    """
    print(f"Drafting personalized email for {request.client_name}...")
    
    # We feed the deterministic math to the LLM so it can't hallucinate the numbers
    context_prompt = f"""
    Client Name: {request.client_name}
    Current Legacy Fees: ${request.legacy_fees:,.2f}
    Annual Savings with Wealthsimple: ${request.savings:,.2f}
    Specific Portfolio Overlap/Risk: {request.overlap_summary}
    """
    
    try:
        # Run the agent to generate the text
        result = await email_agent.run(context_prompt)
        dynamic_email = result.output 
        
        return {"email_draft": dynamic_email}
        
    except Exception as e:
        print(f"Error drafting email: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate email draft.")
    
class ChatRequest(BaseModel):
    message: str
    portfolio_context: str # We pass the tear sheet data here so the AI knows what portfolio it is discussing

@app.post("/api/chat")
async def chat_with_portfolio(request: ChatRequest):
    """
    An exploratory ReAct endpoint. The agent can use tools to answer dynamic questions.
    """
    # Give the agent the current portfolio data + the user's question
    full_prompt = f"""
    Context regarding the client's current portfolio:
    {request.portfolio_context}
    
    Advisor Question: {request.message}
    """
    
    try:
        result = await portfolio_chat_agent.run(full_prompt)
        return {"reply": result.output}
    except Exception as e:
        print(f"Error in chat agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat response.")