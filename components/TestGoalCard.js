import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const TestGoalCard = ({ testType, goalScore, currentScore, onSeeMore }) => {
  // Calculate progress percentage (ensure valid values)
  const safeGoalScore = goalScore || 1600;
  const safeCurrentScore = currentScore || 0;
  let progressPercentage = Math.min(Math.max((safeCurrentScore / safeGoalScore), 0), 1);

  // Ensure minimum visibility (at least 5% filled if score > 0)
  if (safeCurrentScore > 0 && progressPercentage < 0.05) {
    progressPercentage = 0.05;
  }

  const scoreFillFlex = progressPercentage;
  const scoreEmptyFlex = Math.max(1 - progressPercentage, 0.001);

  const formatNumber = (value) => {
    if (value === null || value === undefined) {
      return '--';
    }
    try {
      return Number(value).toLocaleString();
    } catch (err) {
      return String(value);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{(testType || 'ABC Certification')} Preparation</Text>
        <TouchableOpacity onPress={onSeeMore}>
          <Text style={styles.seeMoreText}>See more</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.content}>
        {/* Goals Row */}
        <View style={styles.row}>
          <Text style={styles.label}>Goals</Text>
          <View style={styles.metricContainer}>
            <View style={styles.metricTrack}>
              <View style={styles.goalFill} />
            </View>
            <Text style={styles.metricValueMuted}>{formatNumber(safeGoalScore)}</Text>
          </View>
        </View>
        
        {/* Score Row with Progress Bar */}
        <View style={styles.row}>
          <Text style={styles.label}>Score</Text>
          <View style={styles.metricContainer}>
            <View style={styles.metricTrack}>
              <View
                style={[
                  styles.scoreFill,
                  { flex: scoreFillFlex },
                ]}
              />
              <View
                style={[
                  styles.scoreEmpty,
                  { flex: scoreEmptyFlex },
                ]}
              />
            </View>
            <Text style={styles.metricValue}>{formatNumber(safeCurrentScore)}</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  title: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000000',
    letterSpacing: -0.3,
  },
  seeMoreText: {
    fontSize: 13,
    color: '#8E8E93',
    fontWeight: '400',
  },
  content: {
    marginTop: 4,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    color: '#8E8E93',
    width: 50,
    marginRight: 8,
  },
  metricContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  metricTrack: {
    flex: 1,
    height: 6,
    backgroundColor: '#E5E5EA',
    borderRadius: 3,
    overflow: 'hidden',
    marginRight: 12,
    flexDirection: 'row',
  },
  goalFill: {
    flex: 1,
    height: '100%',
    backgroundColor: '#D1D1D6',
  },
  scoreFill: {
    height: 6,
    backgroundColor: '#8E8E93', // Darker gray to match the image
  },
  scoreEmpty: {
    height: 6,
    backgroundColor: '#E5E5EA',
  },
  metricValueMuted: {
    fontSize: 13,
    color: '#8E8E93',
    fontWeight: '500',
  },
  metricValue: {
    fontSize: 13,
    color: '#000000',
    fontWeight: '600',
    minWidth: 48,
    textAlign: 'right',
  },
});

export default TestGoalCard;

