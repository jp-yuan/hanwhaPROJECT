import React, { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Markdown from 'react-native-markdown-display';
import { config } from '../config';
import QuickReplyButtons from './QuickReplyButtons';
import PerformanceCard from './PerformanceCard';
import PerformanceAnalysisCard from './PerformanceAnalysisCard';
import ProgressCard from './ProgressCard';
import ScoreBreakdownChart from './ScoreBreakdownChart';
import BarChart from './BarChart';
import CircularProgress from './CircularProgress';
import ProfileOverviewCard from './ProfileOverviewCard';
import TestGoalCard from './TestGoalCard';
import QuizCard from './QuizCard';

const DEFAULT_QUICK_REPLIES = [
  { text: '📊 Analyze my last test', action: 'analyze_exam' },
  { text: '💡 How can I improve my scores?', action: 'improve_scores' },
  { text: '📈 How am I doing now?', action: 'check_progress' },
  { text: '📝 Come up with similar questions', action: 'similar_questions' },
];

const ChatScreen = ({ onBack, userProfile }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [goalData, setGoalData] = useState(null);
  const flatListRef = useRef(null);

  // Fetch welcome message on component mount
  React.useEffect(() => {
    const initializeChat = async () => {
      try {
        const res = await fetch(`${config.apiUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            user_id: userProfile?.user_id || 'mock-user', 
            message: '__INIT__',  // Special init message
            session_id: null 
          }),
        });
        const data = await res.json();
        setSessionId(data.session_id);
        
        // Extract goal data from response metadata or ui_elements
        let extractedGoalData = null;
        if (data.ui_elements && data.ui_elements.cards) {
          const profileCard = data.ui_elements.cards.find(card => card.type === 'profile_overview');
          if (profileCard) {
            extractedGoalData = {
              testType: profileCard.data.test_type || 'ABC Certification',
              goalScore: profileCard.data.target_score || 1600,
              currentScore: profileCard.data.current_score || profileCard.data.baseline_score || 1200
            };
          }
        }
        
        // If no goal data from backend response, try to use default
        if (!extractedGoalData) {
          extractedGoalData = {
            testType: 'ABC Certification',
            goalScore: 1600,
            currentScore: 1200
          };
        }
        
        setGoalData(extractedGoalData);
        
        // Add welcome message
        const welcomeMessage = {
          id: '1',
          role: 'assistant',
          content: data.response,
          ui_elements: data.ui_elements || null
        };
        
        setMessages([welcomeMessage]);
        setIsLoading(false);
      } catch (e) {
        // Fallback to default message if backend is not available
        setGoalData({
          testType: 'ABC Certification',
          goalScore: 1600,
          currentScore: 1200
        });
        
        setMessages([{
          id: '1',
          role: 'assistant',
          content: `Hi ${userProfile?.name || 'there'}! I can analyze your scores or create a practice quiz. What would you like to do today?`,
          ui_elements: {
            quick_replies: [
              { text: '📊 Analyze my last exam', action: 'analyze_exam' },
              { text: '🎯 Create practice questions', action: 'create_quiz' },
              { text: '📈 Check my progress', action: 'check_progress' }
            ]
          }
        }]);
        setIsLoading(false);
      }
    };

    initializeChat();
  }, [userProfile]);

  const sendMessage = async (text = null) => {
    // If text is provided as a string, use it; otherwise use input
    const messageText = (typeof text === 'string' && text) ? text : input.trim();
    if (!messageText) return;
    
    const localId = String(Date.now());
    const nextMessages = [...messages, { id: localId, role: 'user', content: messageText }];
    setMessages(nextMessages);
    setInput('');

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      const res = await fetch(`${config.apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userProfile?.user_id || 'mock-user', 
          message: messageText, 
          session_id: sessionId 
        }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      
      // Debug: Log UI elements
      console.log('📦 Backend response:', {
        hasUiElements: !!data.ui_elements,
        quickRepliesCount: data.ui_elements?.quick_replies?.length || 0,
        quickReplies: data.ui_elements?.quick_replies || []
      });
      
      // Add assistant message with UI elements
      const assistantMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: data.response,
        ui_elements: data.ui_elements || null
      };
      
      setMessages([...nextMessages, assistantMessage]);
      
      // Scroll to bottom after response
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (e) {
      console.error('Error sending message:', e);
      setMessages([...nextMessages, { 
        id: String(Date.now() + 1), 
        role: 'assistant', 
        content: 'Error contacting backend. Make sure the server is running.' 
      }]);
    }
  };

  const handleQuickReply = (reply) => {
    // Map actions to messages
    const actionMessages = {
      // Main actions
      'analyze_exam': 'Analyze my last test',
      'create_quiz': 'I want to do some practice questions',
      'check_progress': 'How am I doing now?',
      'get_recommendations': 'What should I focus on studying?',
      
      // Test day actions
      'confirm_ready': 'Yes! I feel ready and confident!',
      'last_minute_review': 'I want to do a quick last minute review',
      'nervous': 'I\'m feeling a bit nervous actually',
      
      // Error/confirmation actions
      'confirm_test_taken': 'Yes, I have completed a practice test recently',
      'no_test_yet': 'No, I haven\'t taken a practice test yet',
      'check_profile': 'Can you check my profile?',
      'support': 'I need some help',
      
      // Quiz actions
      'start_quiz': 'Yes! Let\'s start the quiz',
      'customize_quiz': 'I want to customize the quiz settings',
      'review_concepts': 'Let me review some concepts first',
      
      // Confirmation actions
      'confirm_yes': 'Yes, sounds good!',
      'confirm_no': 'No, not right now',
      'more_info': 'Tell me more about this',
      
      // Schedule actions
      'schedule_test': 'I want to schedule my test date',
      'focus_study': 'Let\'s just focus on studying',
      
      // Analysis actions
      'improve_scores': 'How can I improve my scores?',
      'practice': 'Help me practice my weak areas',
      'detailed_analysis': 'Show me detailed analysis',
      'mistakes': 'Where am I making mistakes?',
      'similar_questions': 'Come up with similar questions',
      
      // General
      'cancel': 'Never mind'
    };

    const message = actionMessages[reply.action] || reply.text;
    sendMessage(message);
  };

  const renderItem = ({ item, index }) => {
    const isUser = item.role === 'user';
    const uiElements = item.ui_elements;
    const isLastMessage = index === messages.length - 1;
    
    // Determine quick replies - only for assistant messages
    let quickReplies = [];
    if (!isUser) {
      if (uiElements && uiElements.quick_replies && uiElements.quick_replies.length > 0) {
        quickReplies = uiElements.quick_replies;
        // Debug: Log when using backend quick replies
        if (isLastMessage) {
          console.log('✅ Using backend quick replies:', quickReplies.map(r => r.text));
        }
      } else {
        // Fallback to defaults only if no backend quick replies provided
        quickReplies = DEFAULT_QUICK_REPLIES;
        if (isLastMessage) {
          console.log('⚠️ No backend quick replies, using defaults:', quickReplies.map(r => r.text));
        }
      }
    }

    return (
      <View style={styles.messageContainer}>
        {/* Text Bubble with Markdown Support */}
        <View style={[styles.bubble, isUser ? styles.user : styles.assistant]}>
          <Markdown
            style={{
              body: {
                color: isUser ? '#FFFFFF' : '#000000',
                fontSize: 16,
                lineHeight: 22,
              },
              paragraph: {
                marginTop: 0,
                marginBottom: 8,
              },
              strong: {
                fontWeight: '700',
                color: isUser ? '#FFFFFF' : '#000000',
              },
              em: {
                fontStyle: 'italic',
                color: isUser ? '#F0F0F0' : '#3A3A3C',
              },
              bullet_list: {
                marginBottom: 8,
              },
              ordered_list: {
                marginBottom: 8,
              },
              list_item: {
                marginBottom: 4,
                flexDirection: 'row',
              },
              bullet_list_icon: {
                marginLeft: 0,
                marginRight: 8,
                color: isUser ? '#FFFFFF' : '#000000',
              },
              heading2: {
                fontSize: 18,
                fontWeight: '600',
                marginTop: 12,
                marginBottom: 8,
                color: isUser ? '#FFFFFF' : '#000000',
              },
              heading3: {
                fontSize: 16,
                fontWeight: '600',
                marginTop: 10,
                marginBottom: 6,
                color: isUser ? '#FFFFFF' : '#000000',
              },
              code_inline: {
                backgroundColor: isUser ? 'rgba(255, 255, 255, 0.2)' : '#F2F2F7',
                paddingHorizontal: 4,
                paddingVertical: 2,
                borderRadius: 3,
                fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
              },
            }}
          >
            {item.content}
          </Markdown>
        </View>

        {/* Rich UI Elements for Assistant Messages */}
        {!isUser && uiElements && (
          <View style={styles.richContent}>
            {/* Render Charts */}
            {uiElements.charts && uiElements.charts.map((chart, idx) => {
              if (chart.type === 'circular_progress') {
                return (
                  <View key={`chart-${idx}`} style={styles.chartCard}>
                    <Text style={styles.chartTitle}>{chart.title}</Text>
                    <View style={styles.chartContainer}>
                      <CircularProgress 
                        percentage={chart.value} 
                        size={100}
                        strokeWidth={10}
                      />
                      <Text style={styles.chartLabel}>{chart.label}</Text>
                    </View>
                  </View>
                );
              }
              if (chart.type === 'score_breakdown') {
                return <ScoreBreakdownChart key={`chart-${idx}`} data={chart.data} title={chart.title} />;
              }
              if (chart.type === 'bar_chart') {
                return <BarChart key={`chart-${idx}`} data={chart.data} title={chart.title} />;
              }
              return null;
            })}

            {/* Render Cards */}
            {uiElements.cards && uiElements.cards.map((card, idx) => {
              if (card.type === 'performance') {
                return <PerformanceCard key={`card-${idx}`} data={card.data} />;
              }
              if (card.type === 'performance_analysis') {
                return <PerformanceAnalysisCard key={`card-${idx}`} data={card.data} />;
              }
              if (card.type === 'progress_card') {
                return <ProgressCard key={`card-${idx}`} data={card.data} />;
              }
              if (card.type === 'profile_overview') {
                return <ProfileOverviewCard key={`card-${idx}`} data={card.data} />;
              }
              if (card.type === 'quiz_ready') {
                return (
                  <QuizCard 
                    key={`card-${idx}`}
                    title={card.title}
                    message={card.message}
                    totalQuestions={card.total_questions}
                    focusAreas={card.focus_areas}
                    onStartQuiz={() => handleQuickReplyPress({ action: 'start_quiz' })}
                  />
                );
              }
              return null;
            })}
          </View>
        )}

        {/* Render Quick Replies - Show only for the last assistant message */}
        {!isUser && index === messages.length - 1 && quickReplies.length > 0 && (
          <QuickReplyButtons 
            replies={quickReplies}
            onPress={handleQuickReply}
          />
        )}
      </View>
    );
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Ionicons name="arrow-back" size={24} color="#000" />
        </TouchableOpacity>
        <Text style={styles.title}>Study Coach</Text>
        <View style={{ width: 32 }} />
      </View>

      {/* Test Goal Card - Always visible at top */}
      {goalData && (
        <TestGoalCard
          testType={goalData.testType}
          goalScore={goalData.goalScore}
          currentScore={goalData.currentScore}
          onSeeMore={() => {
            // Could navigate to progress details or show more info
            sendMessage('Show me my progress details');
          }}
        />
      )}

      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading your profile...</Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />
      )}

      <View style={styles.composer}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Type a message"
          style={styles.input}
          editable={!isLoading}
          multiline
          maxLength={500}
          onSubmitEditing={() => {
            if (!isLoading && input.trim()) {
              sendMessage();
            }
          }}
          blurOnSubmit={false}
        />
        <TouchableOpacity 
          style={styles.send} 
          onPress={() => sendMessage()} 
          disabled={isLoading || !input.trim()}
        >
          <Ionicons name="send" size={18} color="#fff" />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9F9F9' },
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between', 
    paddingHorizontal: 20, 
    paddingTop: 10, 
    paddingBottom: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA'
  },
  backButton: { padding: 8 },
  title: { fontSize: 17, fontWeight: '600', color: '#000' },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: '#8E8E93',
  },
  list: { paddingHorizontal: 16, paddingBottom: 16, paddingTop: 12 },
  messageContainer: { marginVertical: 6 },
  bubble: { 
    padding: 14, 
    borderRadius: 18, 
    maxWidth: '75%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  assistant: { 
    backgroundColor: '#FFFFFF', 
    alignSelf: 'flex-start',
    marginRight: 50,
  },
  user: { 
    backgroundColor: '#007AFF', 
    alignSelf: 'flex-end',
    marginLeft: 50,
  },
  bubbleText: { 
    color: '#000', 
    fontSize: 15, 
    lineHeight: 22,
    letterSpacing: -0.2,
  },
  userText: { color: '#FFFFFF' },
  richContent: { marginTop: 12, marginLeft: 0 },
  chartCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F0F0F0',
    alignItems: 'center',
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 18,
    alignSelf: 'flex-start',
    letterSpacing: -0.3,
  },
  chartContainer: {
    alignItems: 'center',
  },
  chartLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 12,
  },
  composer: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: 12, 
    paddingBottom: 16,
    borderTopWidth: 1, 
    borderTopColor: '#E5E5EA', 
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 3,
  },
  input: { 
    flex: 1, 
    backgroundColor: '#F2F2F7', 
    borderRadius: 22, 
    paddingHorizontal: 16, 
    paddingVertical: 11, 
    marginRight: 8, 
    fontSize: 15,
    lineHeight: 20,
    maxHeight: 100,
  },
  send: { 
    backgroundColor: '#007AFF', 
    borderRadius: 22, 
    width: 44, 
    height: 44, 
    alignItems: 'center', 
    justifyContent: 'center',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
  },
});

export default ChatScreen;


