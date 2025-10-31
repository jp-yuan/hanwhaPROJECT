import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import CircularProgress from './CircularProgress';

const PerformanceCard = ({ data }) => {
  if (!data) return null;

  const { topics = [], overall_accuracy = 0, section } = data;

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>📊 {section || 'Performance'} Analysis</Text>
      
      <View style={styles.overallSection}>
        <CircularProgress 
          percentage={overall_accuracy} 
          size={80}
          strokeWidth={8}
        />
        <View style={styles.overallText}>
          <Text style={styles.accuracyText}>{overall_accuracy.toFixed(1)}%</Text>
          <Text style={styles.accuracyLabel}>Overall Accuracy</Text>
        </View>
      </View>

      {topics && topics.length > 0 && (
        <View style={styles.topicsSection}>
          <Text style={styles.sectionTitle}>Topic Breakdown</Text>
          {topics.slice(0, 3).map((topic, index) => (
            <View key={index} style={styles.topicRow}>
              <View style={styles.topicInfo}>
                <Text style={styles.topicName}>{topic.topic}</Text>
                <Text style={styles.topicStats}>
                  {topic.correct}/{topic.attempted} questions
                </Text>
              </View>
              <View style={styles.topicAccuracy}>
                <Text style={[
                  styles.accuracyNumber,
                  { color: topic.accuracy >= 70 ? '#34C759' : topic.accuracy >= 50 ? '#FF9500' : '#FF3B30' }
                ]}>
                  {topic.accuracy.toFixed(0)}%
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
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
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 18,
    letterSpacing: -0.3,
  },
  overallSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  overallText: {
    marginLeft: 16,
    flex: 1,
  },
  accuracyText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
  },
  accuracyLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  topicsSection: {
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8E8E93',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  topicRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  topicInfo: {
    flex: 1,
  },
  topicName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#000',
    marginBottom: 4,
    textTransform: 'capitalize',
  },
  topicStats: {
    fontSize: 13,
    color: '#8E8E93',
  },
  topicAccuracy: {
    marginLeft: 16,
  },
  accuracyNumber: {
    fontSize: 18,
    fontWeight: '600',
  },
});

export default PerformanceCard;

