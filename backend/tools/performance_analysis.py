"""Performance analysis tools."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from storage.memory_store import store


def get_latest_test_results(user_id: str, test_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get most recent test performance or specific test by ID.
    
    Args:
        user_id: User's unique identifier
        test_id: Optional specific test ID
        
    Returns:
        Test results with detailed breakdown
    """
    print(f"🔍 get_latest_test_results called: user_id={user_id}, test_id={test_id}")
    test_results = store.get_test_results(user_id)
    print(f"  📊 Retrieved {len(test_results) if test_results else 0} test result(s) for user {user_id}")
    
    if not test_results:
        error_msg = f"No test results found for user {user_id}"
        print(f"  ❌ {error_msg}")
        return {"error": error_msg, "user_id": user_id, "message": "No test results found. Make sure you have taken a practice test."}
    
    # Get specific test or most recent
    if test_id:
        test = next((t for t in test_results if t.get("test_id") == test_id), None)
        if not test:
            error_msg = f"Test with ID {test_id} not found for user {user_id}"
            print(f"  ❌ {error_msg}")
            return {"error": error_msg, "test_id": test_id, "user_id": user_id}
    else:
        test = test_results[-1]  # Most recent
        print(f"  ✅ Using most recent test: {test.get('test_id')}, score: {test.get('total_score')}")
    
    result = {
        "success": True,  # Explicitly mark success
        "test_id": test.get("test_id"),
        "test_type": test.get("test_type"),
        "total_score": test.get("total_score"),
        "date_taken": test.get("date_taken"),
        "sections": test.get("sections", {}),
        "completion_status": test.get("completion_status"),
        "message": "Test results found successfully"  # Clear success message for LLM
    }
    print(f"  ✅ Returning test results: total_score={result.get('total_score')}, sections={len(result.get('sections', {}))}")
    return result


def analyze_performance_by_topic(
    user_id: str,
    section: str,
    timeframe: str = "all"
) -> Dict[str, Any]:
    """
    Break down performance by topic and subtopic for a specific section.
    
    Args:
        user_id: User's unique identifier
        section: Section to analyze (math, reading, writing, verbal, quantitative)
        timeframe: Time period (week, month, all)
        
    Returns:
        Detailed breakdown of performance by topic
    """
    # Calculate date filter
    if timeframe == "week":
        cutoff_date = datetime.now() - timedelta(days=7)
    elif timeframe == "month":
        cutoff_date = datetime.now() - timedelta(days=30)
    else:
        cutoff_date = datetime.min
    
    # Get quiz responses
    responses = store.get_quiz_responses(user_id)
    
    # Filter by section and timeframe
    filtered_responses = []
    for response in responses:
        try:
            response_date = datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00"))
            if response_date >= cutoff_date:
                # Get question to check section
                question_id = response.get("question_id")
                question = next((q for q in store.questions if q.get("question_id") == question_id), None)
                if question and question.get("section") == section:
                    filtered_responses.append((response, question))
        except:
            pass
    
    if not filtered_responses:
        return {
            "section": section,
            "timeframe": timeframe,
            "message": "No practice data found for this section",
            "topics": []
        }
    
    # Organize by topic
    topic_stats = defaultdict(lambda: {
        "total": 0,
        "correct": 0,
        "subtopics": defaultdict(lambda: {"total": 0, "correct": 0})
    })
    
    for response, question in filtered_responses:
        topic = question.get("topic", "unknown")
        subtopic = question.get("subtopic", "general")
        
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["subtopics"][subtopic]["total"] += 1
        
        if response.get("is_correct"):
            topic_stats[topic]["correct"] += 1
            topic_stats[topic]["subtopics"][subtopic]["correct"] += 1
    
    # Format results
    topics = []
    for topic, stats in topic_stats.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        subtopics = [
            {
                "name": subtopic,
                "attempted": sub_stats["total"],
                "correct": sub_stats["correct"],
                "accuracy": round(sub_stats["correct"] / sub_stats["total"] * 100, 2) if sub_stats["total"] > 0 else 0
            }
            for subtopic, sub_stats in stats["subtopics"].items()
        ]
        
        # Sort subtopics by accuracy (weakest first)
        subtopics.sort(key=lambda x: x["accuracy"])
        
        topics.append({
            "topic": topic,
            "attempted": stats["total"],
            "correct": stats["correct"],
            "accuracy": round(accuracy, 2),
            "subtopics": subtopics
        })
    
    # Sort topics by accuracy (weakest first)
    topics.sort(key=lambda x: x["accuracy"])
    
    overall_accuracy = (
        sum(t["correct"] for t in topics) / sum(t["attempted"] for t in topics) * 100
    ) if topics else 0
    
    return {
        "section": section,
        "timeframe": timeframe,
        "total_questions": sum(t["attempted"] for t in topics),
        "overall_accuracy": round(overall_accuracy, 2),
        "topics": topics
    }


def identify_error_patterns(user_id: str, question_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Categorize types of mistakes and identify patterns.
    
    Args:
        user_id: User's unique identifier
        question_ids: Optional list of specific question IDs to analyze
        
    Returns:
        Analysis of error patterns
    """
    responses = store.get_quiz_responses(user_id)
    
    # Filter incorrect responses
    errors = [(r, next((q for q in store.questions if q.get("question_id") == r.get("question_id")), None))
              for r in responses if not r.get("is_correct")]
    
    # Further filter by question_ids if provided
    if question_ids:
        errors = [(r, q) for r, q in errors if r.get("question_id") in question_ids]
    
    if not errors:
        return {
            "message": "No errors found - excellent work!",
            "patterns": []
        }
    
    # Analyze patterns
    difficulty_errors = defaultdict(int)
    topic_errors = defaultdict(int)
    time_related = []
    
    for response, question in errors:
        if question:
            difficulty_errors[question.get("difficulty", "unknown")] += 1
            topic_errors[question.get("topic", "unknown")] += 1
            
            # Check if time pressure might be an issue
            avg_time = question.get("average_time", 90)
            time_spent = response.get("time_spent", avg_time)
            if time_spent and time_spent < avg_time * 0.5:
                time_related.append({
                    "question_id": str(question.get("question_id")),
                    "topic": question.get("topic"),
                    "time_spent": time_spent,
                    "average_time": avg_time
                })
    
    patterns = []
    
    # Most common error topics
    top_error_topics = sorted(topic_errors.items(), key=lambda x: x[1], reverse=True)[:5]
    if top_error_topics:
        patterns.append({
            "type": "topic_weakness",
            "description": "Topics with most errors",
            "details": [{"topic": topic, "errors": count} for topic, count in top_error_topics]
        })
    
    # Difficulty analysis
    if difficulty_errors:
        patterns.append({
            "type": "difficulty_distribution",
            "description": "Errors by difficulty level",
            "details": dict(difficulty_errors)
        })
    
    # Time pressure
    if len(time_related) > 3:
        patterns.append({
            "type": "time_pressure",
            "description": "Possible rushing on questions",
            "details": {
                "count": len(time_related),
                "message": "You're answering quickly but getting them wrong. Consider slowing down."
            }
        })
    
    return {
        "total_errors_analyzed": len(errors),
        "patterns": patterns
    }


def compare_progress(user_id: str, comparison_type: str = "historical") -> Dict[str, Any]:
    """
    Compare current performance vs past performance or target.
    
    Args:
        user_id: User's unique identifier
        comparison_type: Type of comparison (historical, target)
        
    Returns:
        Comparison analysis
    """
    user = store.get_user(user_id)
    if not user:
        return {"error": "User not found"}
    
    test_results = store.get_test_results(user_id)
    
    if not test_results:
        baseline = user.get("baseline_score")
        if baseline:
            return {
                "message": "No test results yet, but your baseline score is recorded",
                "baseline_score": baseline,
                "target_score": user.get("target_score")
            }
        return {"error": "No test history available"}
    
    if comparison_type == "historical":
        if len(test_results) < 2:
            current_score = test_results[0].get("total_score")
            baseline_score = user.get("baseline_score", current_score)
            
            return {
                "message": "Great start! Take another practice test to track improvement",
                "current_score": current_score,
                "baseline_score": baseline_score,
                "score_change": current_score - baseline_score if baseline_score else 0
            }
        
        current = test_results[-1]
        previous = test_results[-2]
        
        score_change = current.get("total_score") - previous.get("total_score")
        
        # Section-level changes
        section_changes = {}
        for section in current.get("sections", {}).keys():
            if section in previous.get("sections", {}):
                current_score = current["sections"][section].get("score", 0)
                previous_score = previous["sections"][section].get("score", 0)
                section_changes[section] = {
                    "current": current_score,
                    "previous": previous_score,
                    "change": current_score - previous_score
                }
        
        return {
            "comparison_type": "historical",
            "current_score": current.get("total_score"),
            "previous_score": previous.get("total_score"),
            "score_change": score_change,
            "improvement": score_change > 0,
            "section_changes": section_changes,
            "tests_taken": len(test_results)
        }
    
    elif comparison_type == "target":
        current_score = test_results[-1].get("total_score")
        target_score = user.get("target_score")
        
        if not target_score:
            return {"error": "No target score set"}
        
        gap = target_score - current_score
        
        return {
            "comparison_type": "target",
            "current_score": current_score,
            "target_score": target_score,
            "score_gap": gap,
            "on_track": gap <= 0,
            "message": "You've reached your target!" if gap <= 0 else f"You need {gap} more points to reach your target"
        }
    
    return {"error": f"Unknown comparison type: {comparison_type}"}


def generate_bar_chart_data(user_id: str, test_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate bar chart data from test results showing scores by section/topic.
    
    Args:
        user_id: User's unique identifier
        test_id: Optional specific test ID to analyze
        
    Returns:
        Bar chart data structure with scores by section
    """
    test_results = store.get_test_results(user_id)
    
    if not test_results:
        return {"error": "No test results found", "user_id": user_id}
    
    # Get specific test or most recent
    if test_id:
        test = next((t for t in test_results if t.get("test_id") == test_id), None)
        if not test:
            return {"error": "Test not found", "test_id": test_id}
    else:
        test = test_results[-1]  # Most recent
    
    sections = test.get("sections", {})
    
    if not sections:
        return {"error": "No section data available"}
    
    # Define colors for different sections/topics
    section_colors = {
        "reading": "#1C1C1E",      # Darkest gray
        "writing": "#3A3A3C",       # Medium-dark gray
        "math": "#6D6D70",         # Medium gray
        "verbal": "#8E8E93",       # Light gray
        "quantitative": "#AEAEB2",  # Lightest gray
        "reasoning": "#5A5A5D",    # Medium-light gray
        "algebra": "#AEAEB2",      # Lightest gray
        "geometry": "#C7C7CC"      # Very light gray
    }
    
    # Map section names to display names
    display_names = {
        "reading": "Reading",
        "writing": "Writing",
        "math": "Math",
        "verbal": "Verbal",
        "quantitative": "Quantitative",
        "reasoning": "Reasoning",
        "algebra": "Algebra",
        "geometry": "Geometry"
    }
    
    # Build bar chart data
    bars = []
    max_score = 0
    
    for section_key, section_data in sections.items():
        score = section_data.get("score", 0)
        max_score = max(max_score, score)
        
        display_name = display_names.get(section_key, section_key.title())
        color = section_colors.get(section_key, "#8E8E93")
        
        # Calculate percentage if total score available
        total_score = test.get("total_score", 0)
        percentage = round((score / total_score * 100) if total_score > 0 else 0, 0)
        
        bars.append({
            "label": display_name,
            "value": score,
            "percentage": int(percentage),
            "color": color,
            "section_key": section_key,
            "max_value": max_score
        })
    
    # Sort by value (descending) for better visualization
    bars.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "test_id": test.get("test_id"),
        "test_type": test.get("test_type"),
        "total_score": test.get("total_score"),
        "date_taken": test.get("date_taken"),
        "bars": bars,
        "max_value": max_score,
        "y_axis_label": "Score",
        "x_axis_label": "Subject"
    }

