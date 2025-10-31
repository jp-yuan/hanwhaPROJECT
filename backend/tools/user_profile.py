"""User profile management tools."""

from typing import Dict, Any
from datetime import datetime
from storage.memory_store import store


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Retrieve complete user profile including preferences and goals.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Dictionary containing user profile information
    """
    user = store.get_user(user_id)
    
    if not user:
        return {"error": "User not found", "user_id": user_id}
    
    # Calculate days until test if test_date exists
    days_until_test = None
    if user.get("test_date"):
        try:
            test_date = datetime.fromisoformat(user["test_date"].replace("Z", "+00:00"))
            days_until_test = (test_date - datetime.now()).days
        except:
            pass
    
    return {
        "user_id": user.get("user_id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "test_type": user.get("test_type"),
        "target_score": user.get("target_score"),
        "test_date": user.get("test_date"),
        "baseline_score": user.get("baseline_score"),
        "current_level": user.get("current_level"),
        "study_hours_per_week": user.get("study_hours_per_week"),
        "preferences": user.get("preferences", {}),
        "days_until_test": days_until_test
    }


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user preferences, goals, or profile information.
    
    Args:
        user_id: User's unique identifier
        updates: Dictionary of fields to update
        
    Returns:
        Success status and message
    """
    # Remove fields that shouldn't be updated directly
    safe_updates = {k: v for k, v in updates.items() 
                   if k not in ['user_id', 'email']}
    
    success = store.update_user(user_id, safe_updates)
    
    if not success:
        return {"error": "User not found", "user_id": user_id, "success": False}
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "updated_fields": list(safe_updates.keys())
    }


def get_learning_history(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Get user's practice history and activity over specified period.
    
    Args:
        user_id: User's unique identifier
        days: Number of days to look back
        
    Returns:
        Dictionary containing learning history and statistics
    """
    user = store.get_user(user_id)
    if not user:
        return {"error": "User not found"}
    
    # Get quiz responses
    responses = store.get_quiz_responses(user_id)
    
    # Filter by timeframe
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    recent_responses = []
    for r in responses:
        try:
            timestamp = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).timestamp()
            if timestamp >= cutoff:
                recent_responses.append(r)
        except:
            # Include if can't parse timestamp
            recent_responses.append(r)
    
    # Calculate statistics
    total_questions = len(recent_responses)
    correct_answers = sum(1 for r in recent_responses if r.get("is_correct"))
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate streak (consecutive days with activity)
    activity_dates = set()
    for r in recent_responses:
        try:
            date = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).date()
            activity_dates.add(date)
        except:
            pass
    
    sorted_dates = sorted(activity_dates, reverse=True)
    current_streak = 0
    if sorted_dates:
        expected_date = datetime.now().date()
        for date in sorted_dates:
            if date == expected_date or (expected_date - date).days <= 1:
                current_streak += 1
                expected_date = date
            else:
                break
    
    # Group by topic
    topic_stats = {}
    for r in recent_responses:
        topic = r.get("topic", "unknown")
        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "correct": 0}
        topic_stats[topic]["total"] += 1
        if r.get("is_correct"):
            topic_stats[topic]["correct"] += 1
    
    return {
        "period_days": days,
        "total_questions_attempted": total_questions,
        "accuracy_rate": round(accuracy, 2),
        "current_streak_days": current_streak,
        "topics_practiced": len(topic_stats),
        "topic_breakdown": {
            topic: {
                "attempted": stats["total"],
                "accuracy": round(stats["correct"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0
            }
            for topic, stats in topic_stats.items()
        }
    }

