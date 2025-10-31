"""Conversation orchestrator for managing multi-turn interactions."""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from agents.llm_client import TestPrepAgent
from storage.memory_store import store


class ConversationOrchestrator:
    """Orchestrates conversation flow and manages state."""
    
    def __init__(self):
        self.llm_agent = TestPrepAgent()
        self.max_context_turns = 10
    
    async def handle_message(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for handling user messages.
        
        Args:
            user_id: User's unique identifier
            message: User's message
            session_id: Optional session ID for continuing conversations
            
        Returns:
            Response with assistant message and metadata
        """
        # Create or retrieve session
        is_new_session = session_id is None
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Get conversation history
            history = self._get_formatted_history(session_id)
            
            # If this is a new session with no history, automatically fetch user profile
            if is_new_session and len(history) == 0:
                return await self._handle_session_start(user_id, session_id, message)
            
            # Save user message
            self._save_message(session_id, "user", message)
            
            # Check if user is asking for analysis - if so, DON'T pre-fetch (let LLM call tools)
            message_lower = message.lower()
            analysis_keywords = ['analyze', 'analysis', 'chart', 'visual', 'graph', 'breakdown', 'detailed analysis', 'show me']
            is_explicit_analysis = any(keyword in message_lower for keyword in analysis_keywords)
            
            if is_explicit_analysis:
                print(f"📊 User requested analysis - skipping pre-fetch to force tool calls")
                enriched_message = self._force_tool_usage_message(user_id, message)
            else:
                # Don't pre-fetch at all - always let LLM call tools for data
                print(f"🔧 Skipping pre-fetch - letting LLM call tools")
                enriched_message = message
            
            # Process with LLM agent
            response = await self.llm_agent.process_message(
                user_id=user_id,
                message=enriched_message,
                conversation_history=history
            )
            
            # Save assistant response
            self._save_message(
                session_id,
                "assistant",
                response["message"],
                tool_calls=response.get("tools_used", [])
            )
            
            # Check for follow-up suggestions
            follow_ups = self._identify_follow_ups(response)
            
            # Enhance response with structured UI elements
            structured_response = self._create_structured_response(
                response["message"],
                response.get("tools_used", []),
                user_id
            )
            
            # Add smart quick replies based on message content, tools used, and conversation context
            self._add_contextual_quick_replies(
                response["message"], 
                structured_response, 
                message,
                tools_used=response.get("tools_used", []),
                conversation_history=history
            )
            
            return {
                "session_id": session_id,
                "response": response["message"],
                "follow_ups": follow_ups,
                "tools_used": response.get("tools_used", []),
                "ui_elements": structured_response,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "tool_calls_made": response.get("tool_calls_made", 0)
                }
            }
        
        except Exception as e:
            # Error handling
            error_message = "I apologize, but I encountered an issue. Could you please rephrase your question?"
            
            self._save_message(
                session_id,
                "system",
                f"Error: {str(e)}"
            )
            
            return {
                "session_id": session_id,
                "response": error_message,
                "error": str(e) if self.llm_agent.settings.DEBUG else "An error occurred",
                "follow_ups": [],
                "tools_used": [],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "error": True
                }
            }
    
    async def _handle_session_start(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Handle the start of a new session by fetching user profile.
        
        Args:
            user_id: User's unique identifier
            session_id: New session ID
            message: User's first message
            
        Returns:
            Response with user profile information and personalized greeting
        """
        from tools.user_profile import get_user_profile
        from tools.progress_tracking import get_progress_summary
        
        # Fetch user profile
        profile = get_user_profile(user_id)
        
        if profile.get("error"):
            # If profile not found, proceed normally
            self._save_message(session_id, "user", message)
            response = await self.llm_agent.process_message(
                user_id=user_id,
                message=message,
                conversation_history=[]
            )
            self._save_message(session_id, "assistant", response["message"])
            
            return {
                "session_id": session_id,
                "response": response["message"],
                "follow_ups": [],
                "tools_used": response.get("tools_used", []),
                "ui_elements": self._create_structured_response(
                    response["message"],
                    response.get("tools_used", []),
                    user_id
                ),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "tool_calls_made": response.get("tool_calls_made", 0)
                }
            }
        
        # Get progress summary
        progress = get_progress_summary(user_id)
        
        # Create personalized welcome message
        welcome_message = self._create_welcome_message(profile, progress)
        
        # Save the welcome message
        self._save_message(session_id, "assistant", welcome_message)
        
        # Create UI elements for the welcome screen
        ui_elements = self._create_welcome_ui_elements(profile, progress)
        
        return {
            "session_id": session_id,
            "response": welcome_message,
            "follow_ups": [
                "What would you like to work on today?"
            ],
            "tools_used": ["get_user_profile", "get_progress_summary"],
            "ui_elements": ui_elements,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tool_calls_made": 2,
                "is_welcome": True
            }
        }
    
    def _create_welcome_message(
        self,
        profile: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> str:
        """Create a personalized welcome message based on user profile."""
        from tools.performance_analysis import get_latest_test_results
        
        name = profile.get("name", "there").split()[0]  # Use first name only
        test_type = profile.get("test_type", "ABC Certification")
        target_score = profile.get("target_score")
        baseline_score = profile.get("baseline_score")
        user_id = profile.get("user_id")
        
        # Check for recent test results
        latest_test = get_latest_test_results(user_id) if user_id else None
        current_score = None
        if latest_test and not latest_test.get("error"):
            current_score = latest_test.get("total_score")
        
        # Use current score from progress or latest test, fallback to baseline
        if not current_score and progress and not progress.get("error"):
            current_score = progress.get("current_score") or progress.get("latest_score")
        
        if not current_score:
            current_score = baseline_score
        
        # Create message based on whether there's a recent exam score
        if latest_test and not latest_test.get("error") and current_score:
            # Format like the image: "Hey Suzy! Well done on that last exam! You scored a 1,200..."
            greeting = f"Hey {name}!"
            message_parts = [greeting]
            
            message_parts.append(f"\nWell done on that last exam!")
            message_parts.append(f"\nYou scored a {current_score} which is a marked improvement but I think there's still room to grow.")
            message_parts.append(f"\nYou got this! 😉")
        else:
            # Standard greeting if no recent exam
            days_until_test = profile.get("days_until_test")
            if days_until_test is not None:
                if days_until_test <= 0:
                    greeting = f"Hey {name}!\n\nYay! It's test day! 🎉"
                elif days_until_test <= 7:
                    greeting = f"Hey {name}! 👋\n\nYour {test_type} is coming up soon!"
                elif days_until_test <= 30:
                    greeting = f"Hey {name}! 👋\n\nGreat to see you preparing for your {test_type}!"
                else:
                    greeting = f"Hey {name}! 👋\n\nWelcome back to your {test_type} prep!"
            else:
                greeting = f"Hey {name}! 👋\n\nReady to ace your {test_type}?"
            
            message_parts = [greeting]
            
            # Add encouraging message based on test date
            if days_until_test is not None:
                if days_until_test <= 0:
                    message_parts.append("\n\nAre you excited? I hope you're feeling confident and ready to show what you know! 💪")
                elif days_until_test <= 7:
                    message_parts.append(f"\n\nOnly {days_until_test} days to go! Let's make sure you're fully prepared.")
                elif days_until_test <= 30:
                    message_parts.append(f"\n\nYou have {days_until_test} days to prepare. We've got this! 🎯")
        
        return "".join(message_parts)
    
    def _create_welcome_ui_elements(
        self,
        profile: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create UI elements for the welcome screen."""
        ui_elements = {
            "cards": [],
            "quick_replies": [],
            "charts": []
        }
        
        # Add profile card
        test_type = profile.get("test_type", "N/A")
        target_score = profile.get("target_score", "N/A")
        days_until_test = profile.get("days_until_test")
        user_id = profile.get("user_id")
        baseline_score = profile.get("baseline_score")
        
        # Get current score - prioritize latest test results over progress/baseline
        from tools.performance_analysis import get_latest_test_results
        current_score = None
        
        # First, try to get the latest test score
        if user_id:
            latest_test = get_latest_test_results(user_id)
            if latest_test and not latest_test.get("error"):
                current_score = latest_test.get("total_score")
                print(f"  📊 Using latest test score for UI: {current_score}")
        
        # If no test score, try progress data
        if not current_score and not progress.get("error"):
            current_score = progress.get("current_score") or progress.get("latest_score")
            if current_score:
                print(f"  📊 Using progress score for UI: {current_score}")
        
        # Finally, fallback to baseline
        if not current_score:
            current_score = baseline_score
            print(f"  📊 Using baseline score for UI: {current_score}")
        
        ui_elements["cards"].append({
            "type": "profile_overview",
            "data": {
                "test_type": test_type,
                "target_score": target_score,
                "baseline_score": profile.get("baseline_score", "N/A"),
                "current_score": current_score,
                "days_until_test": days_until_test if days_until_test and days_until_test > 0 else None,
                "study_hours_per_week": profile.get("study_hours_per_week", "N/A")
            }
        })
        
        # Add progress chart if available
        if not progress.get("error"):
            total_questions = progress.get("total_questions_attempted", 0)
            overall_accuracy = progress.get("overall_accuracy", 0)
            
            if total_questions > 0:
                ui_elements["charts"].append({
                    "type": "circular_progress",
                    "title": "Overall Accuracy",
                    "value": overall_accuracy,
                    "label": f"{total_questions} questions attempted"
                })
                
                # Add progress card with weak areas
                weak_areas = progress.get("weak_areas", [])
                strong_areas = progress.get("strong_areas", [])
                
                if weak_areas or strong_areas:
                    ui_elements["cards"].append({
                        "type": "progress_card",
                        "data": {
                            "overall_accuracy": overall_accuracy,
                            "total_questions": total_questions,
                            "weak_areas": weak_areas[:3],
                            "strong_areas": strong_areas[:3]
                        }
                    })
        
        # Add quick reply buttons matching the image
        ui_elements["quick_replies"] = [
            {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
            {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
            {"text": "🤔 How am I doing now?", "action": "check_progress"},
            {"text": "📝 Come up with similar questions", "action": "create_quiz"}
        ]
        
        return ui_elements
    
    def _add_contextual_quick_replies(
        self, 
        response_text: str, 
        ui_elements: Dict[str, Any],
        user_message: str,
        tools_used: List[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """
        Add contextual quick reply buttons based on the response content, tools used, and conversation context.
        
        Args:
            response_text: The agent's response text
            ui_elements: UI elements dict to modify
            user_message: Original user message
            tools_used: List of tools that were called in this response
            conversation_history: Previous conversation messages for context
        """
        from agents.scenarios import ConversationScenarios
        
        response_lower = response_text.lower()
        user_msg_lower = user_message.lower()
        tools_used = tools_used or []
        conversation_history = conversation_history or []
        
        # Build conversation context string from recent history
        conversation_context = ""
        if conversation_history:
            conversation_context = " ".join([msg.get("content", "") for msg in conversation_history[-3:]])
            conversation_context = conversation_context.lower()
        
        # Priority 1: Check tools_used to determine context (most reliable)
        if tools_used:
            if "get_latest_test_results" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
                    {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
                    {"text": "📈 Compare with my target", "action": "compare_progress"},
                    {"text": "🎯 Generate practice questions", "action": "create_quiz"}
                ]
                return
            
            if "analyze_performance_by_topic" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Create practice on weak areas", "action": "create_quiz"},
                    {"text": "📊 Show detailed breakdown", "action": "detailed_analysis"},
                    {"text": "💡 What should I study next?", "action": "get_recommendations"},
                    {"text": "📈 How am I doing overall?", "action": "check_progress"}
                ]
                return
            
            if "generate_adaptive_quiz" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "▶️ Start this quiz", "action": "start_quiz"},
                    {"text": "⚙️ Customize quiz settings", "action": "customize_quiz"},
                    {"text": "📚 Review concepts first", "action": "review_concepts"},
                    {"text": "❌ Skip for now", "action": "cancel"}
                ]
                return
            
            if "generate_bar_chart_data" in tools_used or "generate_study_recommendations" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Create practice quiz", "action": "create_quiz"},
                    {"text": "📊 Analyze more details", "action": "analyze_exam"},
                    {"text": "💡 Show study plan", "action": "get_recommendations"},
                    {"text": "📈 Track my progress", "action": "check_progress"}
                ]
                return
            
            if "get_progress_summary" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Create practice questions", "action": "create_quiz"},
                    {"text": "📊 Analyze my last test", "action": "analyze_exam"},
                    {"text": "💡 Get recommendations", "action": "get_recommendations"},
                    {"text": "🔥 Check my streak", "action": "check_progress"}
                ]
                return
            
            if "identify_error_patterns" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Practice my weak topics", "action": "create_quiz"},
                    {"text": "📊 Show detailed analysis", "action": "detailed_analysis"},
                    {"text": "💡 How to fix these mistakes?", "action": "get_recommendations"},
                    {"text": "📚 Review explanations", "action": "review_concepts"}
                ]
                return
            
            if "get_question_explanation" in tools_used:
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Try similar questions", "action": "create_quiz"},
                    {"text": "📊 Analyze my test", "action": "analyze_exam"},
                    {"text": "💡 Explain another topic", "action": "explain_concepts"},
                    {"text": "📈 Check my progress", "action": "check_progress"}
                ]
                return
        
        # Priority 2: Check conversation history for specific states
        if conversation_context:
            # Check if user just completed a quiz
            if any(phrase in conversation_context for phrase in ['quiz', 'practice', 'question']) and \
               any(phrase in response_lower for phrase in ['complete', 'finished', 'done', 'result', 'score', 'correct']):
                # Try to extract quiz accuracy from response if available
                import re
                accuracy_match = re.search(r'(\d+)%|(\d+)/(\d+)', response_text)
                if accuracy_match:
                    # Use scenario helper for quiz completion
                    try:
                        total = 20  # Default
                        correct = int(accuracy_match.group(2)) if accuracy_match.group(2) else 0
                        if accuracy_match.group(3):
                            total = int(accuracy_match.group(3))
                        accuracy = (correct / total * 100) if total > 0 else 0
                        scenario = ConversationScenarios.get_quiz_complete_scenario(accuracy, total)
                        ui_elements["quick_replies"] = scenario.get("quick_replies", [])
                        return
                    except:
                        pass
                
                # Fallback to generic post-quiz buttons
                ui_elements["quick_replies"] = [
                    {"text": "📊 Review my results", "action": "analyze_exam"},
                    {"text": "🎯 Try another quiz", "action": "create_quiz"},
                    {"text": "💡 Get study tips", "action": "get_recommendations"},
                    {"text": "📈 Check overall progress", "action": "check_progress"}
                ]
                return
            
            # Check if we're in an improvement discussion
            if any(phrase in conversation_context for phrase in ['improve', 'better', 'weak', 'struggl', 'help']):
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Create practice on weak areas", "action": "create_quiz"},
                    {"text": "📊 Show detailed breakdown", "action": "analyze_exam"},
                    {"text": "💡 Get personalized recommendations", "action": "get_recommendations"},
                    {"text": "📚 Review explanations", "action": "review_concepts"}
                ]
                return
        
        # Priority 3: Check response text for specific patterns
        # If response mentions error/issue with data retrieval
        if any(phrase in response_lower for phrase in [
            'issue retrieving', 'error', 'could not', 'unable to', 
            'no recent test results', 'no test results', 'haven\'t taken'
        ]):
            ui_elements["quick_replies"] = [
                {"text": "✅ I did take a test!", "action": "confirm_test_taken"},
                {"text": "🎯 Let's do a practice quiz", "action": "create_quiz"},
                {"text": "📊 Check my profile", "action": "check_profile"},
                {"text": "💬 I need help", "action": "support"}
            ]
            return
        
        # If response asks a question or requests confirmation
        if any(phrase in response_lower for phrase in [
            'would you like', 'do you want', 'shall we', 'ready to',
            'can you confirm', 'please confirm', 'let me know'
        ]):
            # Check what they're asking about
            if 'quiz' in response_lower or 'practice' in response_lower:
                ui_elements["quick_replies"] = [
                    {"text": "✅ Yes! Let's do it", "action": "start_quiz"},
                    {"text": "⚙️ Let me customize it", "action": "customize_quiz"},
                    {"text": "📚 Review first", "action": "review_concepts"},
                    {"text": "❌ Maybe later", "action": "cancel"}
                ]
            elif 'test' in response_lower or 'exam' in response_lower:
                ui_elements["quick_replies"] = [
                    {"text": "✅ Yep, I took one!", "action": "confirm_test_taken"},
                    {"text": "❌ Not yet", "action": "no_test_yet"},
                    {"text": "🎯 Let's practice", "action": "create_quiz"}
                ]
            elif 'schedule' in response_lower or 'reschedule' in response_lower:
                ui_elements["quick_replies"] = [
                    {"text": "📅 Set a new date", "action": "schedule_test"},
                    {"text": "📊 Just study for now", "action": "focus_study"},
                    {"text": "💬 Tell me more", "action": "more_info"}
                ]
            else:
                # Generic confirmation buttons
                ui_elements["quick_replies"] = [
                    {"text": "✅ Yes, sounds good!", "action": "confirm_yes"},
                    {"text": "❌ Nope, I'm good", "action": "confirm_no"},
                    {"text": "💬 Tell me more", "action": "more_info"}
                ]
            return
        
        # If response provides analysis or recommendations (score analysis, performance breakdown)
        if any(phrase in response_lower for phrase in [
            'based on', 'you scored', 'your performance', 'recommend', 'suggest',
            'weak areas', 'strengths', 'improve', 'focus on', 'analysis', 'breakdown'
        ]):
            # Extract weak topics if mentioned
            weak_topics = []
            topic_keywords = ['algebra', 'geometry', 'reading', 'writing', 'math', 'verbal', 'quantitative']
            for topic in topic_keywords:
                if topic in response_lower and ('weak' in response_lower or 'struggle' in response_lower or 'difficulty' in response_lower):
                    weak_topics.append(topic)
            
            if weak_topics:
                # Use scenario helper for improvement recommendations
                scenario = ConversationScenarios.get_improvement_scenario(weak_topics)
                ui_elements["quick_replies"] = scenario.get("quick_replies", [])
            else:
                # Generic analysis response buttons
                ui_elements["quick_replies"] = [
                    {"text": "🎯 Help me practice", "action": "create_quiz"},
                    {"text": "📊 Show me more details", "action": "analyze_exam"},
                    {"text": "💡 What should I study?", "action": "get_recommendations"},
                    {"text": "📈 How am I doing now?", "action": "check_progress"}
                ]
            return
        
        # Check if discussing progress/streaks
        if any(phrase in response_lower for phrase in [
            'streak', 'progress', 'improvement', 'better', 'days', 'practice'
        ]) and not tools_used:
            ui_elements["quick_replies"] = [
                {"text": "📈 Overall progress", "action": "check_progress"},
                {"text": "🎯 Create practice quiz", "action": "create_quiz"},
                {"text": "📊 Analyze my test", "action": "analyze_exam"},
                {"text": "💡 Get recommendations", "action": "get_recommendations"}
            ]
            return
        
        # Default helpful buttons if no specific context detected
        if not ui_elements.get("quick_replies") or len(ui_elements["quick_replies"]) == 0:
            ui_elements["quick_replies"] = [
                {"text": "📊 Analyze my last exam", "action": "analyze_exam"},
                {"text": "💰 How can I improve my scores?", "action": "improve_scores"},
                {"text": "🤔 How am I doing now?", "action": "check_progress"},
                {"text": "📝 Come up with similar questions", "action": "create_quiz"}
            ]
        
        # Debug: Log final quick replies
        final_replies = ui_elements.get("quick_replies", [])
        print(f"\n🔘 Quick replies set ({len(final_replies)}): {[r.get('text', '')[:30] for r in final_replies]}\n")
    
    def _enrich_message_with_context(self, user_id: str, message: str) -> str:
        """
        Enrich user message with relevant context data if they're asking about their performance.
        NOTE: When user explicitly asks to "analyze" test, we skip pre-fetching to FORCE tool calls.
        
        Args:
            user_id: User's unique identifier
            message: Original user message
            
        Returns:
            Enriched message with context (or original if analysis requested)
        """
        message_lower = message.lower()
        
        # If user explicitly asks to analyze, SKIP pre-fetching to force tool calls
        analysis_keywords = ['analyze', 'analysis', 'analyze my test', 'analyze my exam', 'analyze my last test']
        is_analysis_request = any(keyword in message_lower for keyword in analysis_keywords)
        
        if is_analysis_request:
            print(f"📊 User requested analysis - skipping pre-fetch to FORCE tool calls")
            print(f"⚠️  LLM MUST call get_latest_test_results, analyze_performance_by_topic, and generate_bar_chart_data")
            # Return enriched message that emphasizes tool usage
            return f"{message}\n\n[SYSTEM: User explicitly requested to analyze their test. You MUST call these tools:\n1. get_latest_test_results(user_id='{user_id}') - to get test scores\n2. analyze_performance_by_topic(user_id='{user_id}', section='<appropriate_section>') - to analyze performance\n3. generate_bar_chart_data(user_id='{user_id}') - to create visualizations\nDO NOT respond without calling these tools.]"
        
        # Keywords that indicate user wants their data
        score_keywords = ['score', 'result', 'performance', 'test', 'exam']
        progress_keywords = ['progress', 'improvement', 'better', 'worse', 'how am i doing']
        
        should_add_context = any(keyword in message_lower for keyword in score_keywords + progress_keywords)
        
        if not should_add_context:
            return message
        
        print(f"🎯 Detected data request keywords, enriching message with context...")
        print(f"⚠️  NOTE: Pre-fetching data for reference, but LLM MUST STILL call tools to get actual data!")
        
        # Fetch relevant data
        from tools.user_profile import get_user_profile
        from tools.performance_analysis import get_latest_test_results
        from tools.progress_tracking import get_progress_summary
        
        context_parts = [f"User's original question: {message}\n"]
        context_parts.append("\n[SYSTEM: I've pre-fetched the following data for quick reference. However, YOU MUST STILL CALL TOOLS to get actual test results (get_latest_test_results), generate charts (generate_bar_chart_data), and detailed analysis (analyze_performance_by_topic) when requested.]\n")
        
        try:
            # Get user profile
            profile = get_user_profile(user_id)
            if not profile.get("error"):
                context_parts.append(f"\nUSER PROFILE:")
                context_parts.append(f"- Name: {profile.get('name')}")
                context_parts.append(f"- Test Type: {profile.get('test_type')}")
                context_parts.append(f"- Target Score: {profile.get('target_score')}")
                context_parts.append(f"- Baseline Score: {profile.get('baseline_score')}")
                context_parts.append(f"- Days Until Test: {profile.get('days_until_test')}")
                print(f"  ✅ Added user profile context")
            else:
                print(f"  ⚠️ Profile has error: {profile.get('error')}")
        except Exception as e:
            print(f"  ⚠️ Could not add profile context: {e}")
        
        try:
            # Get latest test results - log both success and errors
            test_results = get_latest_test_results(user_id)
            print(f"  🔍 Test results query result: error={test_results.get('error')}, user_id={user_id}")
            if not test_results.get("error"):
                context_parts.append(f"\nLATEST TEST RESULTS (Pre-fetched):")
                context_parts.append(f"- Total Score: {test_results.get('total_score')}")
                context_parts.append(f"- Date Taken: {test_results.get('date_taken')}")
                sections = test_results.get('sections', {})
                if sections:
                    context_parts.append(f"- Section Scores:")
                    for section, data in sections.items():
                        context_parts.append(f"  • {section.title()}: {data.get('score')} (percentile: {data.get('percentile')})")
                print(f"  ✅ Added test results context")
            else:
                print(f"  ⚠️ Test results NOT FOUND - error: {test_results.get('error')}, user_id: {user_id}")
                context_parts.append(f"\n[NOTE: Pre-fetch did not find test results. YOU MUST CALL get_latest_test_results(user_id='{user_id}') to check for test results.]")
        except Exception as e:
            print(f"  ❌ Exception getting test results: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            # Get progress summary
            progress = get_progress_summary(user_id)
            if not progress.get("error") and progress.get("total_questions_attempted", 0) > 0:
                context_parts.append(f"\nPROGRESS SUMMARY:")
                context_parts.append(f"- Questions Attempted: {progress.get('total_questions_attempted')}")
                context_parts.append(f"- Overall Accuracy: {progress.get('overall_accuracy')}%")
                context_parts.append(f"- Recent Accuracy: {progress.get('recent_accuracy')}%")
                context_parts.append(f"- Practice Streak: {progress.get('practice_streak')} days")
                print(f"  ✅ Added progress summary context")
        except Exception as e:
            print(f"  ⚠️ Could not add progress context: {e}")
        
        enriched = "\n".join(context_parts)
        print(f"  📝 Message enriched with {len(context_parts)} context items\n")
        return enriched
    
    def _force_tool_usage_message(self, user_id: str, message: str) -> str:
        """
        Force the LLM to call tools by adding explicit instructions.
        Used when user explicitly asks for analysis or detailed information.
        """
        return f"{message}\n\n[SYSTEM: User explicitly requested analysis. You MUST call these tools:\n1. get_latest_test_results(user_id='{user_id}') - MANDATORY to get test scores\n2. generate_bar_chart_data(user_id='{user_id}') - MANDATORY to create visualizations\n3. analyze_performance_by_topic(user_id='{user_id}', section='<appropriate_section>') - Call for relevant sections\n\nDO NOT respond without calling these tools. When get_latest_test_results returns data with 'success': true and 'total_score', that means DATA EXISTS - you MUST acknowledge and use it. NEVER say 'no test results' or 'haven't taken' when tools return actual data.]"
    
    def _get_formatted_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieve and format conversation history.
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Formatted conversation history
        """
        history = store.get_conversation_history(session_id, limit=self.max_context_turns)
        
        # Format for LLM
        formatted = []
        for msg in history:
            if msg.get("message_type") in ["user", "assistant"]:
                formatted.append({
                    "role": msg["message_type"],
                    "content": msg["content"]
                })
        
        return formatted
    
    def _save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List] = None
    ):
        """Save message to conversation history."""
        store.add_conversation_message(session_id, {
            "message_type": role,
            "content": content,
            "tool_calls": tool_calls,
            "timestamp": datetime.now().isoformat()
        })
    
    def _identify_follow_ups(self, response: Dict[str, Any]) -> List[str]:
        """
        Identify potential follow-up actions or suggestions.
        
        Args:
            response: Agent response
            
        Returns:
            List of follow-up suggestions
        """
        follow_ups = []
        tools_used = response.get("tools_used", [])
        
        # Suggest follow-ups based on tools used
        if "analyze_performance_by_topic" in tools_used:
            follow_ups.append("Would you like me to create a practice quiz focused on your weak areas?")
        
        if "generate_adaptive_quiz" in tools_used:
            follow_ups.append("Ready to start the quiz whenever you are!")
        
        if "get_latest_test_results" in tools_used:
            follow_ups.append("Want to see how this compares to your previous attempts?")
        
        if "get_progress_summary" in tools_used:
            follow_ups.append("Would you like specific recommendations to improve further?")
        
        # Limit to 2 most relevant follow-ups
        return follow_ups[:2]
    
    def start_new_session(self, user_id: str) -> str:
        """
        Start a new conversation session.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            New session ID
        """
        return str(uuid.uuid4())
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of a conversation session.
        
        Args:
            session_id: Session to summarize
            
        Returns:
            Session summary
        """
        history = store.get_conversation_history(session_id, limit=100)
        
        message_counts = {
            "user": 0,
            "assistant": 0,
            "system": 0
        }
        
        for msg in history:
            role = msg.get("message_type", "unknown")
            message_counts[role] = message_counts.get(role, 0) + 1
        
        return {
            "session_id": session_id,
            "total_turns": message_counts["user"],  # Number of user messages
            "message_counts": message_counts,
            "started_at": history[0].get("timestamp") if history else None,
            "last_activity": history[-1].get("timestamp") if history else None
        }
    
    def _create_structured_response(
        self,
        message: str,
        tools_used: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create structured UI elements based on tools used and context.
        
        IMPORTANT: Charts and cards are ONLY generated when specific functions are explicitly called.
        This ensures charts don't appear unless the agent actually analyzes the test.
        
        Args:
            message: The text message
            tools_used: List of tools that were called (empty if no tools were used)
            user_id: User identifier
            
        Returns:
            Dictionary with UI elements (cards, buttons, charts)
        """
        ui_elements = {
            "cards": [],
            "quick_replies": [],
            "charts": []
        }
        
        # Debug: Log tool usage
        print(f"\n📊 Creating structured response - Tools used: {tools_used}")
        if not tools_used:
            print(f"⚠️  No tools called - charts will NOT be generated\n")
            return ui_elements
        
        # Note: Quick replies are now handled by _add_contextual_quick_replies
        # Charts and cards should ONLY be generated when specific functions are called
        
        if "get_progress_summary" in tools_used:
            from tools.progress_tracking import get_progress_summary
            progress = get_progress_summary(user_id)
            if not progress.get("error"):
                ui_elements["charts"].append({
                    "type": "circular_progress",
                    "title": "Overall Progress",
                    "value": progress.get("overall_accuracy", 0),
                    "target": 85,
                    "label": f"{progress.get('total_questions_attempted', 0)} questions"
                })
                
                ui_elements["cards"].append({
                    "type": "progress_card",
                    "title": "Your Progress",
                    "data": progress
                })
        
        if "generate_adaptive_quiz" in tools_used:
            # Try to get quiz data from the most recent tool call
            # We'll look for the quiz details in the conversation context
            # For now, add a default quiz card with basic info
            ui_elements["quick_replies"].extend([
                {"text": "▶️ Start Quiz", "action": "start_quiz"},
                {"text": "⚙️ Customize Quiz", "action": "customize_quiz"},
                {"text": "❌ Cancel", "action": "cancel"}
            ])
            
            # Add a quiz card to show quiz is ready
            ui_elements["cards"].append({
                "type": "quiz_ready",
                "title": "Quiz Ready!",
                "message": "Your personalized quiz has been created and is ready to start.",
                "action": "start_quiz",
                # Note: In a real implementation, we'd fetch quiz details from the tool result
                # stored in the conversation context or session state
            })
            print(f"✅ Quiz card generated")
        
        # Generate bar chart ONLY when generate_bar_chart_data function is explicitly called
        # This prevents duplicate charts when both get_latest_test_results and generate_bar_chart_data are called
        if "generate_bar_chart_data" in tools_used:
            from tools.performance_analysis import generate_bar_chart_data
            bar_chart_data = generate_bar_chart_data(user_id)
            if not bar_chart_data.get("error") and bar_chart_data.get("bars"):
                ui_elements["charts"].append({
                    "type": "bar_chart",
                    "title": "Score Breakdown by Subject",
                    "data": bar_chart_data
                })
                print(f"✅ Bar chart generated from generate_bar_chart_data tool: {len(bar_chart_data.get('bars', []))} bars")
        
        # Note: We no longer generate charts from get_latest_test_results to avoid duplicates
        # Charts are only generated when generate_bar_chart_data is explicitly called
        
        # Generate Math Analysis card (with circular progress) ONLY when analyze_performance_by_topic is called
        if "analyze_performance_by_topic" in tools_used:
            from tools.performance_analysis import analyze_performance_by_topic
            # Check if math was analyzed (from the tool call arguments, but we'll analyze math as default)
            # In a real implementation, we'd need to track which section was analyzed
            # For now, we'll generate math analysis if the tool was called
            perf = analyze_performance_by_topic(user_id, "math", "all")
            if not perf.get("error") and perf.get("topics"):
                ui_elements["cards"].append({
                    "type": "performance",
                    "title": "Math Analysis",
                    "data": perf
                })
                print(f"✅ Math Analysis card generated from function call")
        
        # Debug: Log what charts/cards were generated
        charts_count = len(ui_elements.get("charts", []))
        cards_count = len(ui_elements.get("cards", []))
        if charts_count > 0 or cards_count > 0:
            print(f"📊 Generated: {charts_count} chart(s), {cards_count} card(s)")
            if charts_count > 0:
                print(f"   Chart types: {[c.get('type') for c in ui_elements['charts']]}")
            if cards_count > 0:
                print(f"   Card types: {[c.get('type') for c in ui_elements['cards']]}")
        else:
            print(f"📊 No charts or cards generated (no matching tools called)\n")
        
        # Note: Quick replies are handled by _add_contextual_quick_replies (called separately)
        # Don't set default quick replies here
        
        return ui_elements
    
    def _generate_pie_chart_data(self, sections: Dict[str, Any], test_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate pie chart data from section scores.
        
        Args:
            sections: Dictionary of section scores
            test_id: Optional test ID to display
            
        Returns:
            Pie chart data structure
        """
        if not sections:
            return None
        
        # Define colors for different sections/topics
        section_colors = {
            "reading": "#1C1C1E",      # Darkest gray
            "writing": "#3A3A3C",      # Medium-dark gray
            "math": "#6D6D70",         # Medium gray
            "verbal": "#8E8E93",       # Light gray
            "quantitative": "#AEAEB2",  # Lightest gray
            "reasoning": "#5A5A5D",    # Medium-light gray
            "algebra": "#AEAEB2",       # Lightest gray
            "geometry": "#C7C7CC"       # Very light gray
        }
        
        # Calculate total score for percentage calculation
        total_score = sum(section.get("score", 0) for section in sections.values())
        
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
        
        # Build pie chart segments
        segments = []
        for section_key, section_data in sections.items():
            score = section_data.get("score", 0)
            percentage = round((score / total_score * 100) if total_score > 0 else 0, 0)
            
            display_name = display_names.get(section_key, section_key.title())
            color = section_colors.get(section_key, "#8E8E93")
            
            segments.append({
                "name": display_name,
                "score": score,
                "percentage": int(percentage),
                "color": color,
                "section_key": section_key
            })
        
        # Sort by score (largest first)
        segments.sort(key=lambda x: x["score"], reverse=True)
        
        # Extract test number from test_id if available
        test_number = None
        if test_id:
            try:
                # Try to extract a number from test_id, or use a hash
                import hashlib
                hash_int = int(hashlib.md5(test_id.encode()).hexdigest()[:8], 16)
                test_number = str((hash_int % 99) + 1)  # Number between 1-99
            except:
                test_number = "#"
        
        return {
            "type": "pie_chart",
            "title": "Performance Breakdown",
            "data": {
                "segments": segments,
                "test_number": test_number or "#",
                "total_score": total_score
            }
        }
    
    def _generate_performance_insights(self, results: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """
        Generate performance insights based on test results.
        
        Args:
            results: Test results dictionary
            user_id: User identifier
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Get user profile for comparison
        from tools.user_profile import get_user_profile
        from tools.performance_analysis import compare_progress
        
        profile = get_user_profile(user_id)
        if not profile.get("error"):
            # Compare with previous tests
            comparison = compare_progress(user_id, "historical")
            if not comparison.get("error"):
                if comparison.get("score_change", 0) > 0:
                    improvement = comparison.get("score_change", 0)
                    insights.append({
                        "type": "improvement",
                        "text": f"Score improved by {improvement} points since last test!",
                        "icon": "✅"
                    })
                
                # Check section improvements
                section_changes = comparison.get("section_changes", {})
                for section, changes in section_changes.items():
                    change = changes.get("change", 0)
                    if change > 0:
                        section_name = section.title()
                        insights.append({
                            "type": "section_improvement",
                            "text": f"{section_name} score improved {change} points",
                            "icon": "✅"
                        })
        
        # Calculate expected score range based on current performance
        total_score = results.get("total_score", 0)
        if total_score > 0:
            # Estimate range (roughly +/- 10%)
            low_range = int(total_score * 0.9)
            high_range = int(total_score * 1.1)
            insights.append({
                "type": "score_range",
                "text": f"Your expected range is {low_range:,} to {high_range:,}",
                "icon": "📈"
            })
        
        return insights

