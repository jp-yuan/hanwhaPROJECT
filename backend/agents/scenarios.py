"""Conversation scenarios and guided flows."""

from typing import Dict, Any, List

class ConversationScenarios:
    """Predefined conversation scenarios for guided interactions."""
    
    @staticmethod
    def get_welcome_scenario() -> Dict[str, Any]:
        """Get the welcome scenario for new users."""
        return {
            "message": "Hi! I'm your personal study coach. I can help you:",
            "quick_replies": [
                {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
                {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
                {"text": "🤔 How am I doing now?", "action": "check_progress"},
                {"text": "📝 Come up with similar questions", "action": "create_quiz"}
            ]
        }
    
    @staticmethod
    def get_score_analysis_scenario(user_data: Dict) -> Dict[str, Any]:
        """Get scenario for score analysis."""
        return {
            "message": f"Let's analyze your performance! You're preparing for the {user_data.get('test_type', 'ABC Certification')}.",
            "quick_replies": [
                {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
                {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
                {"text": "🤔 How am I doing now?", "action": "check_progress"},
                {"text": "📝 Come up with similar questions", "action": "create_quiz"}
            ]
        }
    
    @staticmethod
    def get_quiz_scenario() -> Dict[str, Any]:
        """Get scenario for quiz practice."""
        return {
            "message": "Great! Let's create a personalized practice quiz for you.",
            "quick_replies": [
                {"text": "🎯 Start right away (20 questions)", "action": "quick_quiz"},
                {"text": "⚙️ Customize my quiz", "action": "customize_quiz"},
                {"text": "🎲 Random practice", "action": "random_quiz"},
                {"text": "📊 Focus on weak areas", "action": "weak_areas_quiz"}
            ]
        }
    
    @staticmethod
    def get_progress_scenario() -> Dict[str, Any]:
        """Get scenario for progress tracking."""
        return {
            "message": "Let me show you how you've been progressing!",
            "quick_replies": [
                {"text": "📈 Overall progress", "action": "overall_progress"},
                {"text": "🔥 My study streak", "action": "study_streak"},
                {"text": "🎯 Compare with goals", "action": "compare_goals"},
                {"text": "📊 Detailed analytics", "action": "detailed_analytics"}
            ]
        }
    
    @staticmethod
    def get_improvement_scenario(weak_topics: List[str]) -> Dict[str, Any]:
        """Get scenario for improvement suggestions."""
        topics_str = ", ".join(weak_topics[:3]) if weak_topics else "your weak areas"
        
        return {
            "message": f"Based on your performance, I recommend focusing on: {topics_str}",
            "quick_replies": [
                {"text": "✅ Give me practice questions", "action": "practice"},
                {"text": "📚 Explain the concepts", "action": "explain_concepts"},
                {"text": "🎯 Create a study plan", "action": "create_plan"},
                {"text": "📊 Show me my mistakes", "action": "show_mistakes"}
            ]
        }
    
    @staticmethod
    def get_quiz_complete_scenario(accuracy: float, total: int) -> Dict[str, Any]:
        """Get scenario after quiz completion."""
        if accuracy >= 80:
            message = f"🎉 Excellent work! You got {accuracy:.0f}% ({int(accuracy * total / 100)}/{total}) correct!"
            replies = [
                {"text": "📊 Show detailed breakdown", "action": "quiz_breakdown"},
                {"text": "🎯 Try harder questions", "action": "harder_quiz"},
                {"text": "📈 Check my progress", "action": "check_progress"},
                {"text": "✨ Practice more", "action": "practice"}
            ]
        elif accuracy >= 60:
            message = f"Good effort! You got {accuracy:.0f}% ({int(accuracy * total / 100)}/{total}) correct. Let's review and improve!"
            replies = [
                {"text": "📖 Review wrong answers", "action": "review_answers"},
                {"text": "🎯 Practice weak topics", "action": "weak_topics"},
                {"text": "💡 Get study tips", "action": "study_tips"},
                {"text": "🔄 Try similar quiz", "action": "similar_quiz"}
            ]
        else:
            message = f"You got {accuracy:.0f}% ({int(accuracy * total / 100)}/{total}) correct. Don't worry, let's work on improving!"
            replies = [
                {"text": "📖 Review all answers", "action": "review_all"},
                {"text": "📚 Explain concepts", "action": "explain_concepts"},
                {"text": "🎯 Easier practice", "action": "easier_quiz"},
                {"text": "💪 Get encouragement", "action": "encouragement"}
            ]
        
        return {
            "message": message,
            "quick_replies": replies
        }
    
    @staticmethod
    def get_encouragement_scenario(context: str = "general") -> Dict[str, Any]:
        """Get encouragement scenario based on context."""
        scenarios = {
            "struggling": {
                "message": "Remember, every expert was once a beginner! Take a break if needed, then come back fresh. You've got this! 💪",
                "quick_replies": [
                    {"text": "🎯 Try easier questions", "action": "easier_quiz"},
                    {"text": "📚 Learn the concepts", "action": "learn_concepts"},
                    {"text": "💡 Get study tips", "action": "study_tips"},
                    {"text": "📈 See my progress", "action": "check_progress"}
                ]
            },
            "milestone": {
                "message": "🎉 Amazing achievement! Your dedication is really paying off. Keep up the great work!",
                "quick_replies": [
                    {"text": "📊 Check my stats", "action": "check_stats"},
                    {"text": "🎯 Next challenge", "action": "next_challenge"},
                    {"text": "📈 Set new goals", "action": "set_goals"},
                    {"text": "🔥 Keep practicing", "action": "practice"}
                ]
            },
            "general": {
                "message": "You're making steady progress! Consistency is key to success. Keep going! 🌟",
                "quick_replies": [
                    {"text": "🎯 Practice now", "action": "practice"},
                    {"text": "📊 Check progress", "action": "check_progress"},
                    {"text": "💡 Study tips", "action": "study_tips"},
                    {"text": "🎓 My goals", "action": "my_goals"}
                ]
            }
        }
        
        return scenarios.get(context, scenarios["general"])
    
    @staticmethod
    def get_buttons_for_test_analysis() -> List[Dict[str, Any]]:
        """Get quick reply buttons for test analysis context."""
        return [
            {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
            {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
            {"text": "📈 Compare with my target", "action": "compare_progress"},
            {"text": "🎯 Generate practice questions", "action": "create_quiz"}
        ]
    
    @staticmethod
    def get_buttons_for_performance_analysis() -> List[Dict[str, Any]]:
        """Get quick reply buttons for performance breakdown context."""
        return [
            {"text": "🎯 Create practice on weak areas", "action": "create_quiz"},
            {"text": "📊 Show detailed breakdown", "action": "detailed_analysis"},
            {"text": "💡 What should I study next?", "action": "get_recommendations"},
            {"text": "📈 How am I doing overall?", "action": "check_progress"}
        ]
    
    @staticmethod
    def get_buttons_for_quiz_generation() -> List[Dict[str, Any]]:
        """Get quick reply buttons when a quiz is being generated."""
        return [
            {"text": "▶️ Start this quiz", "action": "start_quiz"},
            {"text": "⚙️ Customize quiz settings", "action": "customize_quiz"},
            {"text": "📚 Review concepts first", "action": "review_concepts"},
            {"text": "❌ Skip for now", "action": "cancel"}
        ]
    
    @staticmethod
    def get_buttons_for_recommendations() -> List[Dict[str, Any]]:
        """Get quick reply buttons for study recommendations context."""
        return [
            {"text": "🎯 Create practice quiz", "action": "create_quiz"},
            {"text": "📊 Analyze more details", "action": "analyze_exam"},
            {"text": "💡 Show study plan", "action": "get_recommendations"},
            {"text": "📈 Track my progress", "action": "check_progress"}
        ]
    
    @staticmethod
    def get_buttons_for_progress_check() -> List[Dict[str, Any]]:
        """Get quick reply buttons for progress checking context."""
        return [
            {"text": "🎯 Create practice questions", "action": "create_quiz"},
            {"text": "📊 Analyze my last test", "action": "analyze_exam"},
            {"text": "💡 Get recommendations", "action": "get_recommendations"},
            {"text": "🔥 Check my streak", "action": "check_progress"}
        ]
    
    @staticmethod
    def get_buttons_for_error_patterns() -> List[Dict[str, Any]]:
        """Get quick reply buttons for error pattern analysis context."""
        return [
            {"text": "🎯 Practice my weak topics", "action": "create_quiz"},
            {"text": "📊 Show detailed analysis", "action": "detailed_analysis"},
            {"text": "💡 How to fix these mistakes?", "action": "get_recommendations"},
            {"text": "📚 Review explanations", "action": "review_concepts"}
        ]
    
    @staticmethod
    def get_buttons_for_question_explanation() -> List[Dict[str, Any]]:
        """Get quick reply buttons after explaining a question."""
        return [
            {"text": "🎯 Try similar questions", "action": "create_quiz"},
            {"text": "📊 Analyze my test", "action": "analyze_exam"},
            {"text": "💡 Explain another topic", "action": "explain_concepts"},
            {"text": "📈 Check my progress", "action": "check_progress"}
        ]
    
    @staticmethod
    def get_buttons_post_quiz() -> List[Dict[str, Any]]:
        """Get quick reply buttons after completing a quiz."""
        return [
            {"text": "📊 Review my results", "action": "analyze_exam"},
            {"text": "🎯 Try another quiz", "action": "create_quiz"},
            {"text": "💡 Get study tips", "action": "get_recommendations"},
            {"text": "📈 Check overall progress", "action": "check_progress"}
        ]
    
    @staticmethod
    def get_buttons_for_improvement_discussion() -> List[Dict[str, Any]]:
        """Get quick reply buttons when discussing improvement."""
        return [
            {"text": "🎯 Create practice on weak areas", "action": "create_quiz"},
            {"text": "📊 Show detailed breakdown", "action": "analyze_exam"},
            {"text": "💡 Get personalized recommendations", "action": "get_recommendations"},
            {"text": "📚 Review explanations", "action": "review_concepts"}
        ]
    
    @staticmethod
    def get_buttons_default() -> List[Dict[str, Any]]:
        """Get default quick reply buttons."""
        return [
            {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
            {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
            {"text": "🤔 How am I doing now?", "action": "check_progress"},
            {"text": "📝 Come up with similar questions", "action": "create_quiz"}
        ]

