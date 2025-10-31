"""In-memory data storage for MVP - no database needed."""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import json
import os

class MemoryStore:
    """Singleton in-memory storage for all application data."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # Load mock data
        self.users: Dict[str, Dict] = self._load_mock_users()
        self.questions: List[Dict] = self._load_sample_questions()
        
        # Runtime data storage
        self.test_results: Dict[str, List[Dict]] = {}  # user_id -> list of results
        self.quiz_responses: Dict[str, List[Dict]] = {}  # user_id -> list of responses
        self.conversation_history: Dict[str, List[Dict]] = {}  # session_id -> list of messages
        self.study_sessions: Dict[str, List[Dict]] = {}  # user_id -> list of sessions
        self.quizzes: Dict[str, Dict] = {}  # quiz_id -> quiz data
        
        # Initialize with some sample data
        self._seed_sample_data()
    
    def _load_mock_users(self) -> Dict[str, Dict]:
        """Load mock users from JSON file."""
        try:
            data_dir = os.path.dirname(__file__) + "/../data"
            with open(f"{data_dir}/mock_users.json", "r") as f:
                users_list = json.load(f)
                return {user["user_id"]: user for user in users_list}
        except:
            # Fallback if file doesn't exist yet
            return self._get_default_users()
    
    def _load_sample_questions(self) -> List[Dict]:
        """Load sample questions from JSON file."""
        try:
            data_dir = os.path.dirname(__file__) + "/../data"
            with open(f"{data_dir}/sample_questions.json", "r") as f:
                return json.load(f)
        except:
            # Fallback if file doesn't exist yet
            return self._get_default_questions()
    
    def _get_default_users(self) -> Dict[str, Dict]:
        """Default users if JSON file not loaded."""
        default_users = [
            {
                "user_id": "mock-user",
                "email": "student@example.com",
                "name": "Suzy",
                "test_type": "ABC Certification",
                "target_score": 1600,
                "baseline_score": 1200,
                "current_level": "intermediate",
                "study_hours_per_week": 10,
                "test_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "preferences": {"preferred_study_time": "evening"}
            }
        ]
        return {user["user_id"]: user for user in default_users}
    
    def _get_default_questions(self) -> List[Dict]:
        """Default questions if JSON file not loaded."""
        return []  # Will be populated from JSON
    
    def _seed_sample_data(self):
        """Seed with sample test results and quiz responses."""
        # Add sample test result for mock-user
        mock_user_id = "mock-user"
        self.test_results[mock_user_id] = [
            {
                "test_id": str(uuid.uuid4()),
                "test_type": "SAT",
                "total_score": 800,
                "sections": {
                    "reading": {"score": 240, "percentile": 85},
                    "writing": {"score": 220, "percentile": 74},
                    "reasoning": {"score": 140, "percentile": 75},
                    "algebra": {"score": 100, "percentile": 25},
                    "geometry": {"score": 100, "percentile": 25}
                },
                "date_taken": (datetime.now() - timedelta(days=14)).isoformat(),
                "completion_status": "completed"
            }
        ]
        
        # Add sample quiz responses for mock-user
        self.quiz_responses[mock_user_id] = []
        if self.questions:
            for i, question in enumerate(self.questions[:10]):
                is_correct = (i % 3 != 0)  # ~66% accuracy
                self.quiz_responses[mock_user_id].append({
                    "response_id": str(uuid.uuid4()),
                    "quiz_id": "sample-quiz-1",
                    "question_id": question["question_id"],
                    "user_answer": question["correct_answer"] if is_correct else "A",
                    "is_correct": is_correct,
                    "time_spent": question.get("average_time", 90) + (i * 10),
                    "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                    "topic": question.get("topic"),
                    "difficulty": question.get("difficulty")
                })
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data."""
        if user_id in self.users:
            self.users[user_id].update(updates)
            return True
        return False
    
    def add_test_result(self, user_id: str, result: Dict):
        """Add a test result."""
        if user_id not in self.test_results:
            self.test_results[user_id] = []
        self.test_results[user_id].append(result)
    
    def get_test_results(self, user_id: str) -> List[Dict]:
        """Get all test results for a user."""
        return self.test_results.get(user_id, [])
    
    def add_quiz_response(self, user_id: str, response: Dict):
        """Add a quiz response."""
        if user_id not in self.quiz_responses:
            self.quiz_responses[user_id] = []
        self.quiz_responses[user_id].append(response)
    
    def get_quiz_responses(self, user_id: str) -> List[Dict]:
        """Get all quiz responses for a user."""
        return self.quiz_responses.get(user_id, [])
    
    def add_conversation_message(self, session_id: str, message: Dict):
        """Add a conversation message."""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        self.conversation_history[session_id].append(message)
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a session."""
        messages = self.conversation_history.get(session_id, [])
        return messages[-limit:] if messages else []
    
    def save_quiz(self, quiz_id: str, quiz_data: Dict):
        """Save a generated quiz."""
        self.quizzes[quiz_id] = quiz_data
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Get a quiz by ID."""
        return self.quizzes.get(quiz_id)
    
    def get_questions(self, filters: Optional[Dict] = None, limit: int = 20) -> List[Dict]:
        """Get questions with optional filters."""
        questions = self.questions
        
        if filters:
            if "test_type" in filters:
                questions = [q for q in questions if q.get("test_type") == filters["test_type"]]
            if "section" in filters:
                questions = [q for q in questions if q.get("section") == filters["section"]]
            if "topic" in filters:
                questions = [q for q in questions if q.get("topic") == filters["topic"]]
            if "difficulty" in filters:
                if isinstance(filters["difficulty"], list):
                    questions = [q for q in questions if q.get("difficulty") in filters["difficulty"]]
                else:
                    questions = [q for q in questions if q.get("difficulty") == filters["difficulty"]]
        
        return questions[:limit]


# Global instance
store = MemoryStore()

