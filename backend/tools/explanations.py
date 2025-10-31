"""Explanation and tutoring tools."""

from typing import Dict, Any, Optional
from storage.memory_store import store


def get_question_explanation(question_id: str, detailed: bool = True) -> Dict[str, Any]:
    """
    Get detailed explanation for a specific question.
    
    Args:
        question_id: Question identifier
        detailed: Whether to include step-by-step breakdown
        
    Returns:
        Question explanation with steps
    """
    question = next((q for q in store.questions if q.get("question_id") == question_id), None)
    
    if not question:
        return {"error": "Question not found"}
    
    explanation = {
        "question_id": str(question.get("question_id")),
        "topic": question.get("topic"),
        "subtopic": question.get("subtopic"),
        "correct_answer": question.get("correct_answer"),
        "explanation": question.get("explanation")
    }
    
    if detailed:
        explanation["learning_tips"] = _generate_learning_tips(question.get("topic"))
    
    return explanation


def explain_topic_concept(topic: str, subtopic: Optional[str] = None) -> Dict[str, Any]:
    """
    Provide conceptual explanation for a topic.
    
    Args:
        topic: Main topic
        subtopic: Optional subtopic
        
    Returns:
        Topic explanation and key concepts
    """
    return {
        "topic": topic,
        "subtopic": subtopic,
        "explanation_type": "conceptual_overview",
        "message": f"Explaining {topic}" + (f" - {subtopic}" if subtopic else ""),
        "learning_tips": _generate_learning_tips(topic)
    }


def _generate_learning_tips(topic: str) -> list:
    """Generate topic-specific learning tips."""
    general_tips = [
        "Practice regularly to build familiarity",
        "Review incorrect answers carefully",
        "Time yourself to improve speed",
        "Identify patterns in question types"
    ]
    
    # Topic-specific tips
    topic_tips = {
        "algebra": [
            "Master FOIL and factoring techniques",
            "Draw diagrams for word problems",
            "Check your work by substituting answers back"
        ],
        "geometry": [
            "Memorize key formulas for area and volume",
            "Draw and label diagrams",
            "Look for similar triangles and parallel lines"
        ],
        "reading_comprehension": [
            "Read the questions before the passage",
            "Underline key phrases",
            "Eliminate obviously wrong answers first"
        ],
        "vocabulary": [
            "Learn word roots and prefixes",
            "Use flashcards for daily practice",
            "Read widely to see words in context"
        ],
        "probability": [
            "Draw tree diagrams for complex problems",
            "Remember: P(A and B) = P(A) × P(B) for independent events",
            "Count carefully and check your work"
        ]
    }
    
    return topic_tips.get(topic.lower(), general_tips)

