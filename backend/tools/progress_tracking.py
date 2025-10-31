"""Progress tracking and monitoring tools."""

from typing import Dict, Any
from datetime import datetime, timedelta
from storage.memory_store import store


def get_progress_summary(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive progress summary including milestones and trends.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Progress summary with trends and achievements
    """
    user = store.get_user(user_id)
    if not user:
        return {"error": "User not found"}
    
    responses = store.get_quiz_responses(user_id)
    test_results = store.get_test_results(user_id)
    
    if not responses and not test_results:
        return {
            "message": "No practice data yet. Start practicing to track your progress!",
            "total_questions": 0
        }
    
    # Calculate overall statistics
    total_questions = len(responses)
    total_correct = sum(1 for r in responses if r.get("is_correct"))
    overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate weekly trend
    one_week_ago = datetime.now() - timedelta(days=7)
    recent_responses = []
    for r in responses:
        try:
            timestamp = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            if timestamp >= one_week_ago:
                recent_responses.append(r)
        except:
            pass
    
    recent_accuracy = (
        sum(1 for r in recent_responses if r.get("is_correct")) / len(recent_responses) * 100
        if recent_responses else overall_accuracy
    )
    
    # Score progression
    score_progression = []
    if test_results:
        for test in test_results:
            score_progression.append({
                "date": test.get("date_taken"),
                "score": test.get("total_score"),
                "test_type": test.get("test_type")
            })
    
    # Calculate improvement
    improvement = None
    if len(test_results) >= 2:
        first_score = test_results[0].get("total_score")
        latest_score = test_results[-1].get("total_score")
        improvement = {
            "points": latest_score - first_score,
            "percentage": ((latest_score - first_score) / first_score * 100) if first_score > 0 else 0
        }
    
    # Milestones achieved
    milestones = []
    
    if total_questions >= 100:
        milestones.append({
            "type": "practice_volume",
            "title": "Century Club",
            "description": "Completed 100+ practice questions"
        })
    
    if overall_accuracy >= 80:
        milestones.append({
            "type": "accuracy",
            "title": "High Achiever",
            "description": "Maintaining 80%+ overall accuracy"
        })
    
    if len(test_results) >= 5:
        milestones.append({
            "type": "dedication",
            "title": "Test Pro",
            "description": "Completed 5+ full practice tests"
        })
    
    # Calculate days until test
    days_until_test = None
    test_date = user.get("test_date")
    if test_date:
        try:
            test_datetime = datetime.fromisoformat(test_date.replace("Z", "+00:00"))
            days_until_test = (test_datetime.date() - datetime.now().date()).days
        except:
            pass
    
    # Current score
    current_score = test_results[-1].get("total_score") if test_results else user.get("baseline_score")
    
    # Calculate topic-wise performance for weak/strong areas
    topic_performance = {}
    for r in responses:
        topic = r.get("topic", "unknown")
        if topic not in topic_performance:
            topic_performance[topic] = {"total": 0, "correct": 0}
        topic_performance[topic]["total"] += 1
        if r.get("is_correct"):
            topic_performance[topic]["correct"] += 1
    
    # Calculate accuracy per topic and sort
    topic_accuracies = []
    for topic, stats in topic_performance.items():
        if stats["total"] > 0:
            accuracy = (stats["correct"] / stats["total"]) * 100
            topic_accuracies.append({
                "topic": topic,
                "accuracy": round(accuracy, 1),
                "questions": stats["total"]
            })
    
    topic_accuracies.sort(key=lambda x: x["accuracy"])
    weak_areas = topic_accuracies[:3]  # Bottom 3
    strong_areas = sorted(topic_accuracies, key=lambda x: x["accuracy"], reverse=True)[:3]  # Top 3
    
    return {
        "user_id": user_id,
        "test_type": user.get("test_type"),
        "target_score": user.get("target_score"),
        "baseline_score": user.get("baseline_score"),
        "current_score": current_score,
        "days_until_test": days_until_test,
        "total_questions_attempted": total_questions,
        "overall_accuracy": round(overall_accuracy, 2),
        "recent_accuracy": round(recent_accuracy, 2),
        "accuracy_trend": "improving" if recent_accuracy > overall_accuracy else "stable" if recent_accuracy == overall_accuracy else "declining",
        "score_progression": score_progression,
        "improvement": improvement,
        "milestones": milestones,
        "practice_streak": _calculate_streak(responses),
        "weak_areas": weak_areas,
        "strong_areas": strong_areas
    }


def track_study_streak(user_id: str) -> Dict[str, Any]:
    """
    Track consecutive days of study activity.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Streak information and motivation
    """
    responses = store.get_quiz_responses(user_id)
    
    streak_days = _calculate_streak(responses)
    
    # Count unique study days
    study_dates = set()
    for r in responses:
        try:
            timestamp = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            study_dates.add(timestamp.date())
        except:
            pass
    
    return {
        "current_streak": streak_days,
        "streak_status": (
            "🔥 On fire!" if streak_days >= 7 else
            "⭐ Great start!" if streak_days >= 3 else
            "💪 Keep going!" if streak_days >= 1 else
            "Start your streak today!"
        ),
        "total_study_days": len(study_dates),
        "message": _get_streak_message(streak_days)
    }


def _calculate_streak(responses: list) -> int:
    """Calculate current study streak in days."""
    if not responses:
        return 0
    
    # Get unique dates
    activity_dates = set()
    for r in responses:
        try:
            timestamp = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            activity_dates.add(timestamp.date())
        except:
            pass
    
    if not activity_dates:
        return 0
    
    sorted_dates = sorted(activity_dates, reverse=True)
    streak = 0
    expected_date = datetime.now().date()
    
    for date in sorted_dates:
        if date == expected_date or (expected_date - date).days <= 1:
            streak += 1
            expected_date = date
        else:
            break
    
    return streak


def _get_streak_message(streak_days: int) -> str:
    """Get motivational message based on streak."""
    if streak_days == 0:
        return "Start your study streak today! Even 10 minutes counts."
    elif streak_days == 1:
        return "Great start! Come back tomorrow to build your streak."
    elif streak_days < 7:
        return f"{streak_days} days strong! Keep the momentum going."
    elif streak_days < 30:
        return f"Amazing {streak_days}-day streak! You're building a solid habit."
    else:
        return f"Incredible {streak_days}-day streak! Your dedication is inspiring."

