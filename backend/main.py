"""FastAPI application for test prep conversational agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from config import get_settings
from agents.orchestrator import ConversationOrchestrator

settings = get_settings()
app = FastAPI(title="Test Prep Agent API", version="1.0.0")

# Enable CORS for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ConversationOrchestrator()


# Request/Response Models
class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    follow_ups: List[str] = []
    tools_used: List[str] = []
    ui_elements: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class QuizConfig(BaseModel):
    size: int = 20
    section: Optional[str] = None
    topics: Optional[List[str]] = None


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {"name": "Test Prep Agent API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint for conversational interaction.
    
    Process user messages and return AI-generated responses with tool usage.
    """
    print(f"\n{'='*80}")
    print(f"🌐 API /chat endpoint received:")
    print(f"  📧 user_id: '{message.user_id}'")
    print(f"  💬 message: '{message.message[:100]}{'...' if len(message.message) > 100 else ''}'")
    print(f"  🔗 session_id: {message.session_id}")
    print(f"{'='*80}\n")
    
    try:
        result = await orchestrator.handle_message(
            user_id=message.user_id,
            message=message.message,
            session_id=message.session_id
        )
        # Check if there's an error in the result
        if result.get('error'):
            print(f"\n⚠️  Response generated with error: {result.get('error')}")
            print(f"  Error code: {result.get('error_code', 'N/A')}")
        else:
            print(f"\n✅ Response generated successfully")
        print(f"  Tools used: {result.get('tools_used', [])}")
        
        # Debug: Check if ui_elements and quick_replies are present
        ui_elements = result.get('ui_elements', {})
        quick_replies = ui_elements.get('quick_replies', [])
        print(f"  UI Elements present: {bool(ui_elements)}")
        print(f"  Quick replies count: {len(quick_replies)}")
        if quick_replies:
            print(f"  Quick replies: {[r.get('text', '')[:30] for r in quick_replies]}\n")
        else:
            print(f"  ⚠️  No quick replies in response!\n")
        
        return result
    except Exception as e:
        print(f"\n❌ Error in chat endpoint: {str(e)}\n")
        if settings.DEBUG:
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail="An error occurred processing your message")


@app.get("/user/{user_id}/profile")
async def get_profile(user_id: str):
    """Get user profile information."""
    from tools.user_profile import get_user_profile
    try:
        profile = get_user_profile(user_id)
        if "error" in profile:
            raise HTTPException(status_code=404, detail=profile["error"])
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user/{user_id}/quiz/generate")
async def create_quiz(user_id: str, config: QuizConfig):
    """Generate a personalized quiz."""
    from tools.quiz_management import generate_adaptive_quiz
    try:
        quiz = generate_adaptive_quiz(user_id, config.model_dump())
        if "error" in quiz:
            raise HTTPException(status_code=400, detail=quiz["error"])
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user/{user_id}/quiz/submit")
async def submit_quiz(user_id: str, quiz_id: str, responses: List[dict]):
    """Submit quiz responses and get results."""
    from tools.quiz_management import submit_quiz_response
    try:
        result = submit_quiz_response(user_id, quiz_id, responses)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

