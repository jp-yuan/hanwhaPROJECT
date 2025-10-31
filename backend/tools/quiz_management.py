"""Quiz generation and management tools."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import random
from storage.memory_store import store


def search_questions(filters: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
    """
    Find questions matching specific criteria.
    
    Args:
        filters: Dictionary of filter criteria (topic, difficulty, section, etc.)
        limit: Maximum number of questions to return
        
    Returns:
        List of questions matching criteria
    """
    questions = store.get_questions(filters, limit)
    return questions


def generate_adaptive_quiz(user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a personalized quiz based on user's performance and preferences.
    
    Args:
        user_id: User's unique identifier
        config: Quiz configuration (size, topics, difficulty, etc.)
        
    Returns:
        Generated quiz with questions
    """
    # Get user profile
    print(f"🔍 generate_adaptive_quiz called: user_id={user_id}, config={config}")
    user = store.get_user(user_id)
    if not user:
        error_msg = f"User not found: {user_id}"
        print(f"  ❌ {error_msg}")
        return {"error": error_msg, "message": "User profile not found. Please check the user ID."}
    
    quiz_size = config.get("size", 20)
    test_type = config.get("test_type", user.get("test_type"))
    section = config.get("section")
    focus_topics = config.get("topics", [])
    
    # Get user's recent performance to determine weak areas
    responses = store.get_quiz_responses(user_id)
    recent_responses = responses[-50:] if len(responses) > 50 else responses  # Last 50
    
    # Analyze weak topics
    topic_performance = {}
    for response in recent_responses:
        # Find the question
        question = next((q for q in store.questions if q.get("question_id") == response.get("question_id")), None)
        if question:
            topic = question.get("topic")
            if topic not in topic_performance:
                topic_performance[topic] = {"total": 0, "correct": 0}
            topic_performance[topic]["total"] += 1
            if response.get("is_correct"):
                topic_performance[topic]["correct"] += 1
    
    # Identify weak topics (< 70% accuracy)
    weak_topics = [
        topic for topic, perf in topic_performance.items()
        if perf["total"] >= 3 and (perf["correct"] / perf["total"]) < 0.7
    ]
    
    # Build filter - try to match test type first
    filters = {"test_type": test_type}
    if section:
        filters["section"] = section
    
    # Get all matching questions
    all_questions = store.get_questions(filters, limit=1000)
    
    # If no questions found for this test type, try without test type filter (fallback)
    if not all_questions:
        print(f"⚠️  No questions found for test_type='{test_type}', trying without test type filter")
        filters_without_test_type = {}
        if section:
            filters_without_test_type["section"] = section
        all_questions = store.get_questions(filters_without_test_type, limit=1000)
        
        if all_questions:
            print(f"✅ Found {len(all_questions)} questions using fallback (any test type)")
    
    # Prioritize weak topics if available
    target_topics = focus_topics or weak_topics
    
    # Exclude recently seen questions (only if we have enough questions)
    recent_question_ids = {r.get("question_id") for r in recent_responses[-20:]}
    available_questions = [q for q in all_questions if q.get("question_id") not in recent_question_ids]
    
    # If excluding recent questions leaves us with too few, use all questions
    if len(available_questions) < quiz_size and len(all_questions) >= quiz_size:
        print(f"⚠️  Only {len(available_questions)} new questions available, using all {len(all_questions)} questions (including recent ones)")
        available_questions = all_questions
    
    if not available_questions:
        return {
            "error": "No questions available matching criteria",
            "details": f"Tried test_type='{test_type}', section='{section}', found {len(all_questions)} total questions"
        }
    
    # If we have target topics, prioritize them
    if target_topics:
        prioritized = [q for q in available_questions if q.get("topic") in target_topics]
        if prioritized:
            available_questions = prioritized
    
    # Separate by difficulty
    questions_by_difficulty = {
        "easy": [q for q in available_questions if q.get("difficulty") == "easy"],
        "medium": [q for q in available_questions if q.get("difficulty") == "medium"],
        "hard": [q for q in available_questions if q.get("difficulty") == "hard"]
    }
    
    # Select questions with 30% easy, 50% medium, 20% hard distribution
    selected_questions = []
    
    num_easy = int(quiz_size * 0.3)
    num_medium = int(quiz_size * 0.5)
    num_hard = quiz_size - num_easy - num_medium
    
    # Randomly select from each difficulty
    if questions_by_difficulty["easy"]:
        selected_questions.extend(
            random.sample(questions_by_difficulty["easy"], min(num_easy, len(questions_by_difficulty["easy"])))
        )
    if questions_by_difficulty["medium"]:
        selected_questions.extend(
            random.sample(questions_by_difficulty["medium"], min(num_medium, len(questions_by_difficulty["medium"])))
        )
    if questions_by_difficulty["hard"]:
        selected_questions.extend(
            random.sample(questions_by_difficulty["hard"], min(num_hard, len(questions_by_difficulty["hard"])))
        )
    
    # If we don't have enough, fill from available
    if len(selected_questions) < quiz_size:
        remaining = [q for q in available_questions if q not in selected_questions]
        needed = quiz_size - len(selected_questions)
        selected_questions.extend(random.sample(remaining, min(needed, len(remaining))))
    
    # Shuffle questions
    random.shuffle(selected_questions)
    
    quiz_id = str(uuid.uuid4())
    
    # Save quiz
    quiz_data = {
        "quiz_id": quiz_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "questions": selected_questions
    }
    store.save_quiz(quiz_id, quiz_data)
    
    return {
        "success": True,  # Explicit success marker
        "message": f"Successfully created a personalized quiz with {len(selected_questions)} questions",
        "quiz_id": quiz_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "total_questions": len(selected_questions),
        "section": section or "mixed",
        "focus_areas": target_topics[:3] if target_topics else ["general"],
        "questions": [
            {
                "question_number": idx + 1,
                "question_id": q.get("question_id"),
                "content": q.get("content"),
                "options": q.get("options"),
                "difficulty": q.get("difficulty"),
                "topic": q.get("topic"),
                "estimated_time": q.get("average_time", 90)
            }
            for idx, q in enumerate(selected_questions)
        ]
    }


def submit_quiz_response(
    user_id: str,
    quiz_id: str,
    responses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Record quiz answers and provide immediate feedback.
    
    Args:
        user_id: User's unique identifier
        quiz_id: Quiz identifier
        responses: List of responses (question_id, answer, time_spent)
        
    Returns:
        Feedback on performance with explanations
    """
    results = []
    total_correct = 0
    total_time = 0
    
    for response_data in responses:
        question_id = response_data.get("question_id")
        user_answer = response_data.get("answer")
        time_spent = response_data.get("time_spent", 0)
        
        # Get question
        question = next((q for q in store.questions if q.get("question_id") == question_id), None)
        
        if not question:
            continue
        
        is_correct = user_answer == question.get("correct_answer")
        if is_correct:
            total_correct += 1
        
        total_time += time_spent
        
        # Save response
        store.add_quiz_response(user_id, {
            "response_id": str(uuid.uuid4()),
            "quiz_id": quiz_id,
            "question_id": question_id,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "time_spent": time_spent,
            "timestamp": datetime.now().isoformat(),
            "topic": question.get("topic"),
            "difficulty": question.get("difficulty")
        })
        
        results.append({
            "question_id": str(question_id),
            "user_answer": user_answer,
            "correct_answer": question.get("correct_answer"),
            "is_correct": is_correct,
            "topic": question.get("topic"),
            "difficulty": question.get("difficulty"),
            "explanation": question.get("explanation") if not is_correct else None
        })
    
    accuracy = (total_correct / len(responses) * 100) if responses else 0
    
    # Determine performance level
    if accuracy >= 85:
        performance_level = "excellent"
    elif accuracy >= 70:
        performance_level = "good"
    elif accuracy >= 60:
        performance_level = "fair"
    else:
        performance_level = "needs_improvement"
    
    return {
        "quiz_id": quiz_id,
        "total_questions": len(responses),
        "correct_answers": total_correct,
        "accuracy": round(accuracy, 2),
        "total_time_seconds": total_time,
        "average_time_per_question": round(total_time / len(responses), 2) if responses else 0,
        "performance_level": performance_level,
        "results": results
    }

