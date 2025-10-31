# Test Prep Agent - Backend MVP

An intelligent, multi-turn conversational agent powered by OpenAI GPT-4 that helps students prepare for standardized tests (SAT, GRE, etc.) with personalized coaching, adaptive quizzes, and performance analysis.

## 🌟 Features

- **Intelligent Conversation**: Natural multi-turn conversations with GPT-4
- **Performance Analysis**: Deep analysis of test results and practice performance
- **Adaptive Quizzing**: Personalized quiz generation based on weak areas
- **Study Recommendations**: Data-driven study plans and topic suggestions
- **Progress Tracking**: Comprehensive progress monitoring with streaks and milestones
- **Explanations & Tutoring**: Detailed step-by-step explanations
- **Motivation System**: Encouraging feedback and achievement celebrations

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key

## 🚀 Quick Start

### 1. Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the backend directory:

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

Your `.env` file should contain:

```
OPENAI_API_KEY=sk-your-key-here
ENVIRONMENT=development
DEBUG=True
```

### 3. Run the Server

```bash
# Start the FastAPI server
python main.py

# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

## 📱 Testing with the Mobile App

The backend is designed to work seamlessly with the existing React Native mobile app:

1. **Start the backend** (as shown above)
2. **Start the mobile app** in a separate terminal:
   ```bash
   cd ..  # Go back to v1 directory
   npm start
   ```
3. **Open the app** and navigate to the chat screen
4. **Start chatting!** Try: "Hi! Can you help me prepare for the SAT?"

## 🔧 API Endpoints

### Main Chat Endpoint

```bash
POST /chat
```

**Request:**
```json
{
  "user_id": "mock-user",
  "message": "I want to practice geometry",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "response": "I can help with that! Let me analyze your performance...",
  "follow_ups": ["Would you like a practice quiz?"],
  "tools_used": ["analyze_performance_by_topic"],
  "metadata": {
    "timestamp": "2025-01-01T12:00:00",
    "tool_calls_made": 1
  }
}
```

### Other Endpoints

- `GET /health` - Health check
- `GET /` - API information
- `GET /user/{user_id}/profile` - Get user profile
- `POST /user/{user_id}/quiz/generate` - Generate quiz
- `POST /user/{user_id}/quiz/submit` - Submit quiz

## 📊 Sample Users

The system comes with 3 pre-configured users:

1. **mock-user** (Used by mobile app)
   - Test: SAT
   - Target Score: 1500
   - Current Level: Intermediate

2. **sarah-123**
   - Test: SAT
   - Target Score: 1550
   - Current Level: Advanced

3. **john-456**
   - Test: GRE
   - Target Score: 325
   - Current Level: Intermediate

## 💬 Example Conversations

### Performance Analysis
```
User: "How am I doing in math?"
Agent: [Analyzes performance] "You've attempted 45 math questions with 71% accuracy. 
       Your strongest area is algebra (85%) but geometry needs work (55%). 
       Would you like to focus on geometry practice?"
```

### Quiz Generation
```
User: "Create a geometry quiz for me"
Agent: [Generates adaptive quiz] "I've created a 20-question quiz focused on your 
       weak areas: circles and triangles. The difficulty adapts based on your 
       performance. Ready to start?"
```

### Progress Tracking
```
User: "Show me my progress"
Agent: [Gets progress summary] "Great progress! You've completed 127 questions 
       with 73% accuracy (up from 68%). You're on a 5-day streak 🔥 and scored 
       +50 points since your baseline!"
```

## 🛠️ Tools Available

The agent has access to 18 tools across 8 categories:

### User Profile (3 tools)
- `get_user_profile` - Retrieve user information
- `update_user_profile` - Update preferences
- `get_learning_history` - Get practice history

### Performance Analysis (4 tools)
- `get_latest_test_results` - Recent test scores
- `analyze_performance_by_topic` - Topic breakdown
- `identify_error_patterns` - Mistake analysis
- `compare_progress` - Historical comparison

### Quiz Management (3 tools)
- `search_questions` - Find questions
- `generate_adaptive_quiz` - Create personalized quizzes
- `submit_quiz_response` - Record answers

### Recommendations (2 tools)
- `generate_study_recommendations` - Personalized study plans
- `suggest_practice_topics` - Topic suggestions

### Progress Tracking (2 tools)
- `get_progress_summary` - Comprehensive progress
- `track_study_streak` - Monitor daily habits

### Explanations (2 tools)
- `get_question_explanation` - Detailed explanations
- `explain_topic_concept` - Conceptual overviews

### Motivation (2 tools)
- `generate_encouragement` - Personalized motivation
- `celebrate_achievement` - Milestone celebrations

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application
├── config.py                  # Configuration management
├── requirements.txt           # Dependencies
├── .env                      # Environment variables (create this)
├── data/
│   ├── mock_users.json       # Sample users
│   └── sample_questions.json # Sample questions (15+)
├── agents/
│   ├── llm_client.py        # OpenAI GPT-4 integration
│   └── orchestrator.py       # Conversation management
├── tools/
│   ├── user_profile.py       # User management
│   ├── performance_analysis.py
│   ├── quiz_management.py
│   ├── recommendations.py
│   ├── progress_tracking.py
│   ├── explanations.py
│   └── motivation.py
└── storage/
    └── memory_store.py       # In-memory data storage
```

## 🔍 How It Works

1. **User sends message** via mobile app or API
2. **Orchestrator** retrieves conversation history
3. **LLM (GPT-4)** decides which tools to call
4. **Tools execute** and return data
5. **LLM synthesizes** natural response
6. **Response sent** back to user

## 🧪 Testing

### Test the API directly:

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "mock-user",
    "message": "Hi! Can you help me prepare for the SAT?"
  }'

# Get user profile
curl http://localhost:8000/user/mock-user/profile
```

## 🎯 Key Features

### Adaptive Quiz Algorithm
- Analyzes user's recent performance
- Identifies topics with <70% accuracy
- Excludes recently seen questions
- Balances difficulty: 30% easy, 50% medium, 20% hard

### Intelligent Recommendations
- Data-driven priority scoring
- Time-until-test urgency
- Pattern-based suggestions
- Impact estimation

### Conversation Intelligence
- 10-turn context window
- Natural follow-up suggestions
- Tool call tracking
- Error recovery

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenAI API Error"
- Check your API key in `.env`
- Verify your OpenAI account has credits
- Ensure key has proper permissions

### "Connection refused" from mobile app
- Make sure backend is running on port 8000
- Check that you're using the correct IP address
- For iOS simulator, use `localhost`
- For physical devices, use your computer's local IP

## 📈 Next Steps

- [ ] Add user authentication
- [ ] Implement vector database for semantic search
- [ ] Add spaced repetition algorithm
- [ ] Create admin dashboard
- [ ] Add more test types (GMAT, MCAT, etc.)
- [ ] Implement progress analytics visualization

## 💡 Tips

- The agent works best with specific questions
- Give context about your goals and test date
- Review explanations for wrong answers
- Practice consistently for best results
- Use the progress tracking to stay motivated

## 🤝 Support

For issues:
1. Check the API documentation at `/docs`
2. Review this README
3. Check server logs for errors

---

**Built with ❤️ for students preparing for their future.**

