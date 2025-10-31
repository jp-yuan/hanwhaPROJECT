"""LLM client with function calling capabilities."""

from typing import Dict, Any, List
import json
from openai import OpenAI
from openai import OpenAIError, AuthenticationError, APIError

from config import get_settings

# Import all tools
from tools import user_profile, performance_analysis, quiz_management, recommendations
from tools import progress_tracking, explanations, motivation

settings = get_settings()


class TestPrepAgent:
    """LLM-powered test prep agent with function calling."""
    
    def __init__(self):
        self.settings = settings
        # Ensure API key is stripped of whitespace
        api_key = settings.OPENAI_API_KEY.strip() if settings.OPENAI_API_KEY else None
        
        # Debug: Show API key info (masked for security)
        if api_key:
            masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
            print(f"🔑 Initializing OpenAI client with API key (length: {len(api_key)}, preview: {masked_key})")
            
            # Verify API key format
            if not api_key.startswith('sk-'):
                print(f"⚠️  WARNING: API key doesn't start with 'sk-'")
            if len(api_key) < 20:
                print(f"⚠️  WARNING: API key seems too short (length: {len(api_key)})")
        else:
            raise ValueError("OPENAI_API_KEY is missing or empty!")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
        self.tools = self._define_tools()
        self.tool_map = self._create_tool_map()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define all available tools for function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_user_profile",
                    "description": "Retrieve user's complete profile including test type, target score, study preferences, and timeline",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learning_history",
                    "description": "Get user's practice history, study sessions, and activity statistics over a time period",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "days": {
                                "type": "integer",
                                "description": "Number of days to look back",
                                "default": 30
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_latest_test_results",
                    "description": "Get most recent practice test results with detailed breakdown by section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "test_id": {
                                "type": "string",
                                "description": "Optional specific test ID"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_performance_by_topic",
                    "description": "Get detailed breakdown of performance across topics and subtopics for a specific section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "section": {
                                "type": "string",
                                "enum": ["math", "reading", "writing", "verbal", "quantitative"],
                                "description": "Test section to analyze"
                            },
                            "timeframe": {
                                "type": "string",
                                "enum": ["week", "month", "all"],
                                "default": "all"
                            }
                        },
                        "required": ["user_id", "section"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "identify_error_patterns",
                    "description": "Analyze mistakes to identify patterns like topic weaknesses, difficulty struggles, or time management issues",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_progress",
                    "description": "Compare current performance vs past performance or target score to show improvement",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "comparison_type": {
                                "type": "string",
                                "enum": ["historical", "target"],
                                "default": "historical"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_adaptive_quiz",
                    "description": "Create a personalized quiz based on user's weak areas, preferences, and performance history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "config": {
                                "type": "object",
                                "properties": {
                                    "size": {"type": "integer", "default": 20},
                                    "section": {"type": "string"},
                                    "topics": {"type": "array", "items": {"type": "string"}},
                                    "difficulty": {"type": "string"}
                                }
                            }
                        },
                        "required": ["user_id", "config"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_study_recommendations",
                    "description": "Generate personalized study recommendations based on performance analysis and time until test",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_progress_summary",
                    "description": "Get comprehensive progress summary with trends, milestones, and achievements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "track_study_streak",
                    "description": "Track consecutive days of study activity and provide motivation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_question_explanation",
                    "description": "Get detailed explanation for a specific question with step-by-step breakdown",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question_id": {"type": "string"},
                            "detailed": {"type": "boolean", "default": True}
                        },
                        "required": ["question_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_encouragement",
                    "description": "Generate personalized encouragement based on user's progress and current context",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "context": {
                                "type": "string",
                                "enum": ["general", "after_quiz", "struggling", "milestone"],
                                "default": "general"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_bar_chart_data",
                    "description": "Generate bar chart data visualization from test results showing scores by section/topic. Use this when user asks to analyze their test scores or wants to see a visual breakdown.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string"},
                            "test_id": {
                                "type": "string",
                                "description": "Optional specific test ID to analyze. If not provided, uses most recent test."
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ]
    
    def _create_tool_map(self) -> Dict[str, Any]:
        """Map function names to actual function implementations."""
        return {
            "get_user_profile": user_profile.get_user_profile,
            "update_user_profile": user_profile.update_user_profile,
            "get_learning_history": user_profile.get_learning_history,
            "get_latest_test_results": performance_analysis.get_latest_test_results,
            "analyze_performance_by_topic": performance_analysis.analyze_performance_by_topic,
            "identify_error_patterns": performance_analysis.identify_error_patterns,
            "compare_progress": performance_analysis.compare_progress,
            "generate_bar_chart_data": performance_analysis.generate_bar_chart_data,
            "search_questions": quiz_management.search_questions,
            "generate_adaptive_quiz": quiz_management.generate_adaptive_quiz,
            "submit_quiz_response": quiz_management.submit_quiz_response,
            "generate_study_recommendations": recommendations.generate_study_recommendations,
            "suggest_practice_topics": recommendations.suggest_practice_topics,
            "get_progress_summary": progress_tracking.get_progress_summary,
            "track_study_streak": progress_tracking.track_study_streak,
            "get_question_explanation": explanations.get_question_explanation,
            "explain_topic_concept": explanations.explain_topic_concept,
            "generate_encouragement": motivation.generate_encouragement,
            "celebrate_achievement": motivation.celebrate_achievement,
        }
    
    def _get_system_prompt(self) -> str:
        """Return comprehensive system prompt."""
        return """You are an expert test preparation coach specializing in standardized tests and certifications (ABC Certification, SAT, GRE, GMAT, etc.).

Your role is to:
1. Analyze student performance and identify strengths/weaknesses using the available tools
2. Provide personalized study recommendations based on actual data
3. Generate adaptive practice quizzes tailored to each student's needs
4. Explain concepts and solutions clearly with step-by-step breakdowns
5. Motivate and encourage students throughout their learning journey
6. Track progress and celebrate achievements
7. Help students develop effective test-taking strategies

CRITICAL: YOU MUST USE TOOLS - NEVER GUESS OR ASSUME

MANDATORY TOOL USAGE RULES (CRITICAL - FOLLOW EXACTLY):

**CRITICAL RULE**: When a tool returns data with "success": true and "total_score", that means DATA EXISTS.
You MUST acknowledge the data and use it. NEVER say "I couldn't find" or "you haven't taken" when tools return actual data.

1. When user asks to "analyze my test", "analyze my exam", "analyze my last test", YOU MUST:
   - STEP 1: get_latest_test_results(user_id) - ALWAYS call this first
   - STEP 2: If get_latest_test_results returns {"success": true, "total_score": X, "sections": {...}}, DATA EXISTS! Use it!
   - STEP 3: generate_bar_chart_data(user_id) - Always call this to create visualizations
   - STEP 4: analyze_performance_by_topic(user_id, section) - Call for relevant sections
   - NEVER say "you haven't taken a test" if get_latest_test_results returned data with scores

2. When user asks about scores/results/performance/test/exam (without "analyze"), YOU MUST CALL:
   - get_latest_test_results(user_id) - This is MANDATORY, never assume test results exist

3. When user asks about progress/how they're doing, YOU MUST CALL:
   - get_progress_summary(user_id) - Mandatory for progress questions

4. If you see [SYSTEM: User explicitly requested to analyze their test...] in the message, THIS IS A DIRECT ORDER:
   - You MUST call all three tools: get_latest_test_results, analyze_performance_by_topic, and generate_bar_chart_data
   - DO NOT respond without calling these tools
   - If a tool returns an error, still acknowledge the error and explain what went wrong

5. If NO data is pre-fetched, YOU MUST CALL TOOLS:
   - User asks about test/exam/score/results → CALL get_latest_test_results
   - User asks to "analyze my test" or "analyze my exam" → CALL get_latest_test_results AND analyze_performance_by_topic AND generate_bar_chart_data
   - User asks about progress/how they're doing → CALL get_progress_summary
   - User asks how to improve → CALL get_latest_test_results AND identify_error_patterns
   - User asks for practice questions/quiz → CALL generate_adaptive_quiz
   - User asks about specific topics/weak areas → CALL analyze_performance_by_topic
   - User asks for recommendations → CALL generate_study_recommendations
   - User asks to see charts/visualization → CALL generate_bar_chart_data

QUIZ GENERATION INTERPRETATION:
- If generate_adaptive_quiz returns {"success": true, "quiz_id": "...", "total_questions": N}, quiz was CREATED SUCCESSFULLY
- NEVER say "hiccup" or "issue finding profile" when quiz tool returns success=true
- When quiz is created, acknowledge it: "I've created a personalized quiz with N questions for you!"

6. NEVER respond without calling tools when users ask about:
   - Their test scores or exam results (ALWAYS call get_latest_test_results first)
   - Their performance or progress
   - How to improve their scores
   - Weak areas or topics
   - Practice questions or quizzes
   - Charts or visualizations

7. If a tool returns an error (e.g., "No test results found"), acknowledge it clearly:
   - Explain what the error means
   - Offer alternatives (e.g., "It looks like you haven't taken a practice test yet. Would you like to take one now?")
   - Never make up or guess test results

Conversation Guidelines:
- Be warm, encouraging, and supportive - you're their personal coach
- Always use tools to access actual data before making claims about performance
- Ask clarifying questions when needed to understand the student's goals
- Remember context from previous messages in the conversation
- Break down complex topics into digestible explanations
- Celebrate progress and milestones genuinely
- Be honest about challenges but always provide actionable next steps
- Use specific numbers and metrics when discussing performance

Response Formatting (CRITICAL - ALWAYS USE MARKDOWN):
- **MANDATORY**: Use **Markdown formatting** in ALL responses for better readability
- **ALWAYS bold these key elements**:
  * ALL scores (e.g., **800**, **240 points**, **85th percentile**)
  * Section names when showing results (e.g., **Reading**, **Algebra**, **Geometry**)
  * Key metrics and percentages (e.g., **60% accuracy**, **90 days**)
  * Important terms and focus areas (e.g., **weak areas**, **strongest section**)
  * Action items and recommendations (e.g., **Practice daily**, **Take practice tests**)
- Use *italic* for subtle emphasis or terminology
- Use bullet points (- or *) for lists and multiple items
- Use numbered lists (1., 2., 3.) for sequential steps or rankings
- Use headers (##, ###) sparingly for major sections if needed
- Write naturally and conversationally, as if speaking to a friend
- Use emojis sparingly and only when appropriate (🎯, 💪, 📈, etc.)
- The mobile app will render your markdown beautifully

Markdown Examples (FOLLOW THIS FORMAT):
- Scores: "You scored a **800** which is a marked improvement!"
- Sections: "**Reading**: **240 points** (**85th percentile**)"
- Lists: "Here are your weak areas:\n- **Algebra** (45%)\n- **Geometry** (52%)\n- **Data Analysis** (68%)"
- Emphasis: "Your *strongest section* is **Reading** with **90% accuracy**!"
- Steps: "1. **Focus on algebra** - Practice 15-20 questions daily\n2. **Review geometry** - Study theorems\n3. **Track progress** - Take weekly tests"

EXAMPLE RESPONSE FORMAT:
"After analyzing your latest test results, here's a detailed breakdown:

**Total Score: 800**
**Date Taken:** October 17, 2025

Here's how you performed across different sections:
- **Reading**: **240** (**85th percentile**) 🎯
- **Writing**: **220** (**74th percentile**)
- **Reasoning**: **140** (**75th percentile**)
- **Algebra**: **100** (**25th percentile**)
- **Geometry**: **100** (**25th percentile**)

Your strengths lie in the **Reading** section, where you scored the highest. However, there's a significant opportunity for improvement in **Algebra** and **Geometry**, where your scores are in the lower percentile."

Response Length (IMPORTANT):
- Keep responses concise and focused - aim for 2-4 sentences for most responses
- Be direct and get to the point quickly
- Only provide details when specifically asked
- Use bullet points or numbered lists when listing items
- Avoid lengthy explanations unless the user explicitly requests more detail

When analyzing performance:
- MANDATORY: Always call tools to pull actual data - NEVER guess or assume scores
- For test analysis: Call get_latest_test_results FIRST, then analyze_performance_by_topic, then generate_bar_chart_data
- For progress questions: Call get_progress_summary
- CRITICAL: When you call a tool and it returns data (NOT an error), that means the data EXISTS and is available
- IMPORTANT: If get_latest_test_results returns a JSON object with "total_score" and "sections" (no "error" field), then test results ARE FOUND and available
- DO NOT say "I couldn't find test results" if the tool returned data with scores - the data IS there, you must acknowledge it
- When tool returns data successfully, acknowledge the scores and provide analysis based on the actual numbers returned
- Be specific with numbers, percentages, and comparisons from actual tool results
- Identify patterns, not just individual scores
- Connect findings to concrete, actionable recommendations
- Prioritize the most impactful areas for improvement

TOOL RESPONSE INTERPRETATION:
- If tool returns {"error": "..."} → No data found, acknowledge this clearly
- If tool returns {"total_score": ..., "sections": {...}} → Data EXISTS, use it in your response
- NEVER claim "I couldn't find results" when a tool successfully returns data

When explaining concepts:
- Start with the big picture before diving into details
- Use examples relevant to actual test questions
- Point out common mistakes and misconceptions
- Provide practice opportunities and check for understanding
- Adapt your explanation style based on the student's level

When recommending practice:
- Base recommendations on actual performance data
- Consider time until the test and study availability
- Balance weak areas with maintaining strengths
- Make recommendations specific and actionable
- Follow up on previous commitments and goals

Maintain conversation context:
- Reference previous discussions naturally
- Follow up on commitments ("Last time you mentioned...")
- Track user sentiment and adjust tone accordingly
- Remember stated goals, preferences, and concerns

Always strive to be helpful, accurate, and motivating. Your goal is to help students achieve their target scores and build confidence."""

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process user message with function calling.
        
        Args:
            user_id: User's unique identifier
            message: User's message
            conversation_history: Previous conversation turns
            
        Returns:
            Assistant response with metadata
        """
        # Limit conversation history to recent messages for faster processing
        # Keep only last 5 exchanges (10 messages) to reduce context size
        limited_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        # Build messages
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ] + limited_history + [
            {"role": "user", "content": message}
        ]
        
        tool_calls_made = []
        
        try:
            response = await self._process_with_tools(user_id, messages, tool_calls_made)
            
            return {
                "message": response,
                "tool_calls_made": len(tool_calls_made),
                "tools_used": [tc["name"] for tc in tool_calls_made]
            }
        
        except AuthenticationError as e:
            error_msg = str(e)
            error_code = e.status_code if hasattr(e, 'status_code') else 401
            print(f"Error processing message: Error code: {error_code} - {error_msg}")
            # Extract error details from response body if available
            error_body = getattr(e, 'body', None)
            if isinstance(error_body, dict) and 'error' in error_body:
                print(f"Error details: {error_body.get('error', {})}")
            return {
                "message": "I apologize, but there's an authentication issue with the API. Please check your API key configuration in the .env file.",
                "error": error_msg,
                "error_code": error_code,
                "tool_calls_made": 0,
                "tools_used": []
            }
        except APIError as e:
            error_msg = str(e)
            error_code = e.status_code if hasattr(e, 'status_code') else 'N/A'
            print(f"Error processing message: Error code: {error_code} - {error_msg}")
            # Extract error details from response body if available
            error_body = getattr(e, 'body', None)
            if isinstance(error_body, dict) and 'error' in error_body:
                print(f"Error details: {error_body.get('error', {})}")
            return {
                "message": f"I encountered an API error (code {error_code}). Please try again later.",
                "error": error_msg,
                "error_code": error_code,
                "tool_calls_made": 0,
                "tools_used": []
            }
        except OpenAIError as e:
            error_msg = str(e)
            print(f"Error processing message: OpenAI Error - {error_msg}")
            return {
                "message": "I encountered an error with the AI service. Please try again.",
                "error": error_msg,
                "tool_calls_made": 0,
                "tools_used": []
            }
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing message: {error_msg}")
            return {
                "message": "I apologize, but I encountered an error. Let's try that again.",
                "error": error_msg,
                "tool_calls_made": 0,
                "tools_used": []
            }
    
    async def _process_with_tools(
        self,
        user_id: str,
        messages: List[Dict],
        tool_calls_made: List[Dict]
    ) -> str:
        """Process message using OpenAI with tool calling."""
        print(f"\n{'='*60}")
        print(f"🎯 Processing message for user_id: {user_id}")
        print(f"{'='*60}\n")
        
        # Initial LLM call
        # Debug: Check if we have tools available
        print(f"🔧 Available tools: {len(self.tools)} tools")
        print(f"📝 User message preview: {messages[-1].get('content', '')[:100]}...")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto",  # Let model decide when to use tools
            temperature=0.7,  # Slightly higher for better tool usage decisions
            max_tokens=500  # Increased to allow for tool calls
        )
        
        # Handle function calls iteratively
        max_iterations = 5  # Reduced to prevent long loops
        iterations = 0
        
        finish_reason = response.choices[0].finish_reason
        print(f"🤖 Initial LLM finish_reason: {finish_reason}")
        
        if finish_reason != "tool_calls":
            print(f"⚠️  LLM did not request tool calls. Finish reason: {finish_reason}")
            # If user is asking about data but no tools were called, log this
            user_message = messages[-1].get('content', '').lower()
            data_keywords = ['test', 'exam', 'score', 'result', 'performance', 'progress', 'analyze', 'how am i']
            if any(keyword in user_message for keyword in data_keywords):
                print(f"⚠️  WARNING: User asked about data but LLM didn't call tools!")
                print(f"   User message contains: {[kw for kw in data_keywords if kw in user_message]}")
        
        while response.choices[0].finish_reason == "tool_calls" and iterations < max_iterations:
            iterations += 1
            tool_calls = response.choices[0].message.tool_calls
            print(f"\n📞 LLM wants to call {len(tool_calls)} tool(s) (iteration {iterations})")
            
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                print(f"  📋 Tool: {function_name}, Args from LLM: {arguments}")
                
                # Add user_id to arguments if not present
                function_params = self._get_function_params(function_name)
                if "user_id" in function_params:
                    if "user_id" not in arguments:
                        print(f"  ➕ Injecting user_id: {user_id}")
                        arguments["user_id"] = user_id
                    else:
                        llm_user_id = arguments.get("user_id")
                        if llm_user_id != user_id:
                            print(f"  ⚠️  WARNING: LLM provided wrong user_id '{llm_user_id}', correcting to '{user_id}'")
                            arguments["user_id"] = user_id
                        else:
                            print(f"  ✅ user_id already correct in args: {user_id}")
                else:
                    print(f"  ℹ️  user_id not needed for this function")
                
                # Execute the function
                result = self._execute_tool(function_name, arguments)
                
                # Track tool call
                tool_calls_made.append({
                    "name": function_name,
                    "arguments": arguments
                })
                
                # Format result for LLM - make it more readable and clear
                if isinstance(result, dict):
                    # Check if there's an error
                    if result.get("error"):
                        content = json.dumps(result, indent=2)
                        print(f"  ⚠️  Tool returned error: {result.get('error')}")
                    else:
                        # Success - format clearly so LLM understands the data
                        content = json.dumps(result, indent=2)
                        print(f"  ✅ Tool returned SUCCESS - data available: {list(result.keys())}")
                        if "total_score" in result:
                            print(f"     Total score: {result.get('total_score')}, Sections: {len(result.get('sections', {}))}")
                else:
                    content = json.dumps(result, indent=2)
                
                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": content
                })
            
            # Get next response from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,  # Slightly higher for better tool usage decisions
                max_tokens=500  # Increased to allow for tool calls
            )
            finish_reason = response.choices[0].finish_reason
            print(f"🤖 Next LLM finish_reason: {finish_reason}")
            if finish_reason != "tool_calls":
                print(f"⚠️  LLM stopped calling tools. Finish reason: {finish_reason}")
        
        final_response = response.choices[0].message.content
        
        # Safety check: If tools returned data but LLM says it couldn't find data, correct this
        final_response = self._validate_response_against_tools(final_response, tool_calls_made, messages)
        
        # NOTE: Markdown formatting is now PRESERVED and sent to frontend for rendering
        # The _clean_markdown function is no longer called - we want to keep the markdown!
        
        print(f"\n✨ Final response (with markdown): {final_response[:200]}...\n")
        return final_response
    
    def _validate_response_against_tools(self, response: str, tool_calls_made: List[Dict], messages: List[Dict]) -> str:
        """
        Validate that the LLM response correctly interprets tool results.
        If tools returned data but LLM claims no data found, FIX the response.
        """
        import json
        
        # Check if LLM claimed no data/error but tools returned success
        response_lower = response.lower()
        no_data_keywords = ["haven't taken", "no test", "no results", "couldn't find", "could not find", "didn't find", "unable to find", "issue finding", "don't have any results", "hiccup", "issue with", "not being recognized", "verify your user"]
        claimed_error = any(keyword in response_lower for keyword in no_data_keywords)
        
        if claimed_error:
            # Check what tools were called and what they returned
            test_data = None
            quiz_data = None
            
            for message in messages:
                # Check test results
                if message.get("role") == "tool" and message.get("name") == "get_latest_test_results":
                    tool_result = message.get("content", "")
                    try:
                        result_data = json.loads(tool_result)
                        # If tool returned success (has total_score, no error), data EXISTS
                        if result_data.get("success") and result_data.get("total_score"):
                            test_data = result_data
                            print(f"\n🚨 CRITICAL ERROR DETECTED:")
                            print(f"   LLM claimed no data but get_latest_test_results returned:")
                            print(f"   - total_score: {result_data.get('total_score')}")
                            print(f"   - sections: {len(result_data.get('sections', {}))}")
                            print(f"   - success: {result_data.get('success')}")
                            print(f"   OVERRIDING LLM response with correct information!\n")
                    except Exception as e:
                        print(f"   Error parsing test result: {e}")
                
                # Check quiz generation
                if message.get("role") == "tool" and message.get("name") == "generate_adaptive_quiz":
                    tool_result = message.get("content", "")
                    try:
                        result_data = json.loads(tool_result)
                        # If tool returned success, quiz WAS created
                        if result_data.get("success") and result_data.get("quiz_id"):
                            quiz_data = result_data
                            print(f"\n🚨 CRITICAL ERROR DETECTED:")
                            print(f"   LLM claimed issue/error but generate_adaptive_quiz returned:")
                            print(f"   - success: {result_data.get('success')}")
                            print(f"   - quiz_id: {result_data.get('quiz_id')}")
                            print(f"   - total_questions: {result_data.get('total_questions')}")
                            print(f"   - message: {result_data.get('message')}")
                            print(f"   OVERRIDING LLM response with correct information!\n")
                    except Exception as e:
                        print(f"   Error parsing quiz result: {e}")
            
            # Override response if we found successful quiz generation
            if quiz_data:
                total_questions = quiz_data.get("total_questions")
                focus_areas = quiz_data.get("focus_areas", ["general"])
                section = quiz_data.get("section", "mixed")
                
                corrected_response = f"I've created a personalized quiz for you with {total_questions} questions! "
                if section != "mixed":
                    corrected_response += f"It focuses on {section}. "
                if focus_areas and focus_areas != ["general"]:
                    corrected_response += f"The quiz covers: {', '.join(focus_areas)}. "
                corrected_response += "Ready to start when you are!"
                
                print(f"✅ Replaced incorrect LLM response with correct quiz confirmation")
                return corrected_response
            
            # If we found test data but LLM said no data, override the response
            if test_data:
                total_score = test_data.get("total_score")
                sections = test_data.get("sections", {})
                
                # Create a corrected response
                corrected_response = f"I found your latest test results! You scored {total_score} total. "
                
                # Add section breakdown
                if sections:
                    corrected_response += "Here's your breakdown:\n\n"
                    for section_name, section_data in sections.items():
                        score = section_data.get("score")
                        percentile = section_data.get("percentile")
                        corrected_response += f"{section_name.title()}: {score} points ({percentile}th percentile)\n"
                    
                    # Add analysis
                    corrected_response += "\nYour strongest areas are Reading and Writing. Let's focus on improving your Math sections (Algebra and Geometry) to boost your overall score!"
                
                print(f"✅ Replaced incorrect LLM response with correct data-based response")
                return corrected_response
        
        return response
    
    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text to ensure clean display in frontend."""
        import re
        
        if not text:
            return text
        
        # Remove bold (**text** or __text__)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        # Remove italic (*text* or _text_)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove strikethrough (~~text~~)
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        
        # Remove headers (# Header, ## Header, etc.)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown code blocks ```code``` -> code
        text = re.sub(r'```[\w]*\n?([^`]+)```', r'\1', text, flags=re.DOTALL)
        
        # Remove inline code `code` -> code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove markdown list markers at start of lines (-, *, +)
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Remove numbered list markers (1., 2., etc.) at start of lines
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up multiple consecutive newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _get_function_params(self, function_name: str) -> List[str]:
        """Get parameter names for a function."""
        tool = next((t for t in self.tools if t["function"]["name"] == function_name), None)
        if tool and "parameters" in tool["function"]:
            return list(tool["function"]["parameters"].get("properties", {}).keys())
        return []
    
    def _execute_tool(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute the appropriate tool function."""
        func = self.tool_map.get(function_name)
        if not func:
            print(f"❌ Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
        
        try:
            print(f"🔧 Calling {function_name} with args: {arguments}")
            result = func(**arguments)
            print(f"✅ Result from {function_name}: {json.dumps(result, indent=2)[:200]}...")
            return result
        except Exception as e:
            print(f"❌ Error in {function_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

