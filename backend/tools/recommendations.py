"""Study recommendation tools."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from storage.memory_store import store


def generate_study_recommendations(user_id: str) -> Dict[str, Any]:
    """
    Generate personalized study recommendations based on performance analysis.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Prioritized study recommendations
    """
    user = store.get_user(user_id)
    if not user:
        return {"error": "User not found"}
    
    responses = store.get_quiz_responses(user_id)
    
    if not responses:
        return {
            "message": "Start practicing to get personalized recommendations!",
            "recommendations": [
                {
                    "priority": "high",
                    "type": "get_started",
                    "action": "Take a diagnostic quiz to assess your current level",
                    "reason": "We need baseline data to create a personalized study plan"
                }
            ]
        }
    
    # Analyze performance by topic
    topic_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    
    for response in responses:
        question = next((q for q in store.questions if q.get("question_id") == response.get("question_id")), None)
        if question:
            topic = question.get("topic")
            topic_stats[topic]["total"] += 1
            if response.get("is_correct"):
                topic_stats[topic]["correct"] += 1
    
    # Generate recommendations
    recommendations = []
    
    # 1. Identify weak topics
    weak_topics = []
    for topic, stats in topic_stats.items():
        accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        if stats["total"] >= 5 and accuracy < 0.6:
            weak_topics.append({
                "topic": topic,
                "accuracy": accuracy,
                "attempts": stats["total"]
            })
    
    weak_topics.sort(key=lambda x: x["accuracy"])
    
    for i, topic_data in enumerate(weak_topics[:3]):
        recommendations.append({
            "priority": "high" if i == 0 else "medium",
            "type": "improve_weak_topic",
            "topic": topic_data["topic"],
            "action": f"Focus on {topic_data['topic']} - practice 10-15 questions daily",
            "reason": f"Current accuracy: {topic_data['accuracy']*100:.1f}%. This is below target.",
            "estimated_impact": "high"
        })
    
    # 2. Check study frequency
    if responses:
        most_recent = responses[-1]
        try:
            last_activity = datetime.fromisoformat(most_recent["timestamp"].replace("Z", "+00:00"))
            days_since = (datetime.now() - last_activity).days
            if days_since > 3:
                recommendations.append({
                    "priority": "high",
                    "type": "consistency",
                    "action": "Resume daily practice - aim for at least 20 minutes per day",
                    "reason": f"You haven't practiced in {days_since} days. Consistency is key!",
                    "estimated_impact": "high"
                })
        except:
            pass
    
    # 3. Test date urgency
    test_date = user.get("test_date")
    if test_date:
        try:
            test_datetime = datetime.fromisoformat(test_date.replace("Z", "+00:00"))
            days_until_test = (test_datetime - datetime.now()).days
            if days_until_test <= 30 and days_until_test > 0:
                recommendations.insert(0, {
                    "priority": "critical",
                    "type": "test_prep",
                    "action": "Take full-length practice tests weekly",
                    "reason": f"Only {days_until_test} days until your test. Focus on test-taking strategies.",
                    "estimated_impact": "critical"
                })
        except:
            pass
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "recommendations": recommendations[:5]  # Top 5 recommendations
    }


def suggest_practice_topics(user_id: str, section: str) -> List[str]:
    """
    Suggest specific topics to practice based on performance gaps.
    
    Args:
        user_id: User's unique identifier
        section: Test section to get suggestions for
        
    Returns:
        List of suggested topics
    """
    responses = store.get_quiz_responses(user_id)
    
    if not responses:
        # Get all available topics for this section
        questions = store.get_questions({"section": section}, limit=1000)
        topics = list(set(q.get("topic") for q in questions if q.get("topic")))
        return topics[:5]
    
    # Calculate accuracy by topic for this section
    topic_accuracy = defaultdict(lambda: {"total": 0, "correct": 0})
    
    for response in responses:
        question = next((q for q in store.questions if q.get("question_id") == response.get("question_id")), None)
        if question and question.get("section") == section:
            topic = question.get("topic")
            topic_accuracy[topic]["total"] += 1
            if response.get("is_correct"):
                topic_accuracy[topic]["correct"] += 1
    
    # Find topics with low accuracy or insufficient practice
    suggestions = []
    for topic, stats in topic_accuracy.items():
        accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        # Suggest if accuracy < 75% and enough attempts to be significant
        if stats["total"] >= 3 and accuracy < 0.75:
            suggestions.append((topic, accuracy, stats["total"]))
    
    # Sort by accuracy (lowest first)
    suggestions.sort(key=lambda x: x[1])
    
    return [topic for topic, _, _ in suggestions[:5]]

