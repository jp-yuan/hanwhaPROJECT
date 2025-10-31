"""Motivation and engagement tools."""

from typing import Dict, Any
from datetime import datetime
from storage.memory_store import store


def generate_encouragement(user_id: str, context: str = "general") -> Dict[str, Any]:
    """
    Generate personalized encouragement based on user's progress.
    
    Args:
        user_id: User's unique identifier
        context: Context for encouragement (after_quiz, struggling, milestone, etc.)
        
    Returns:
        Personalized encouragement message
    """
    responses = store.get_quiz_responses(user_id)
    
    if not responses:
        return {
            "message": "Welcome! Every expert was once a beginner. Let's start your test prep journey together!",
            "type": "welcome"
        }
    
    # Get recent performance (last 20 responses)
    recent_responses = responses[-20:] if len(responses) > 20 else responses
    recent_accuracy = sum(1 for r in recent_responses if r.get("is_correct")) / len(recent_responses)
    
    if context == "after_quiz":
        if recent_accuracy >= 0.85:
            message = "Outstanding work! You're really mastering this material. Keep up this excellent momentum!"
        elif recent_accuracy >= 0.70:
            message = "Great progress! You're on the right track. With continued practice, you'll reach your target score."
        elif recent_accuracy >= 0.50:
            message = "Good effort! Remember, every mistake is a learning opportunity. Review the explanations and try again."
        else:
            message = "Don't get discouraged! This material takes time to master. Focus on understanding one topic at a time."
    
    elif context == "struggling":
        message = "Challenges are what make you stronger. Take a break if needed, then come back fresh. You've got this!"
    
    elif context == "milestone":
        message = "🎉 Congratulations on this achievement! Your dedication is paying off. Celebrate this win!"
    
    else:
        message = "Keep pushing forward! Consistent effort leads to remarkable results."
    
    return {
        "message": message,
        "type": context,
        "recent_accuracy": round(recent_accuracy * 100, 1)
    }


def celebrate_achievement(user_id: str, achievement_type: str) -> Dict[str, Any]:
    """
    Celebrate user achievements and milestones.
    
    Args:
        user_id: User's unique identifier
        achievement_type: Type of achievement
        
    Returns:
        Celebration message
    """
    celebrations = {
        "first_quiz": "🎯 First quiz complete! Great start to your learning journey!",
        "perfect_score": "💯 Perfect score! You absolutely crushed it!",
        "streak_week": "🔥 7-day streak! Your consistency is impressive!",
        "100_questions": "💪 100 questions completed! You're building serious momentum!",
        "score_improvement": "📈 Score improved! Your hard work is paying off!",
        "reached_target": "🎉 You reached your target score! Amazing achievement!",
        "10_day_streak": "⭐ 10-day streak! You're unstoppable!",
        "50_questions": "🌟 50 questions down! You're making great progress!",
    }
    
    message = celebrations.get(achievement_type, "🌟 Great achievement! Keep up the excellent work!")
    
    return {
        "achievement_type": achievement_type,
        "message": message,
        "earned_at": datetime.now().isoformat()
    }

