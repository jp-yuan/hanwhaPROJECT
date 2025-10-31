import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const QuizCard = ({ title, message, totalQuestions, focusAreas, onStartQuiz }) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.icon}>📝</Text>
        <Text style={styles.title}>{title || 'Quiz Ready'}</Text>
      </View>
      
      <Text style={styles.message}>
        {message || 'Your personalized quiz has been created and is ready to start.'}
      </Text>
      
      {totalQuestions && (
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Questions:</Text>
          <Text style={styles.infoValue}>{totalQuestions}</Text>
        </View>
      )}
      
      {focusAreas && focusAreas.length > 0 && (
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Focus Areas:</Text>
          <Text style={styles.infoValue}>{focusAreas.join(', ')}</Text>
        </View>
      )}
      
      <TouchableOpacity style={styles.startButton} onPress={onStartQuiz}>
        <Text style={styles.startButtonText}>▶️ Start Quiz</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 16,
    marginTop: 12,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  icon: {
    fontSize: 24,
    marginRight: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  message: {
    fontSize: 14,
    color: '#3A3A3C',
    marginBottom: 16,
    lineHeight: 20,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#6D6D70',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 14,
    color: '#1C1C1E',
    fontWeight: '600',
  },
  startButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
    marginTop: 12,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default QuizCard;

