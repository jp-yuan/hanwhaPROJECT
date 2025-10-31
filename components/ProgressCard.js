import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const ProgressCard = ({ data }) => {
  if (!data) return null;

  const {
    total_questions_attempted = 0,
    overall_accuracy = 0,
    recent_accuracy = 0,
    practice_streak = 0,
    milestones = []
  } = data;

  const trend = recent_accuracy > overall_accuracy ? 'up' : recent_accuracy < overall_accuracy ? 'down' : 'stable';

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>📈 Your Progress</Text>
      
      <View style={styles.statsGrid}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{total_questions_attempted}</Text>
          <Text style={styles.statLabel}>Questions</Text>
        </View>
        
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{overall_accuracy.toFixed(1)}%</Text>
          <Text style={styles.statLabel}>Accuracy</Text>
        </View>
        
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{practice_streak} 🔥</Text>
          <Text style={styles.statLabel}>Day Streak</Text>
        </View>
      </View>

      {milestones && milestones.length > 0 && (
        <View style={styles.milestonesSection}>
          <Text style={styles.sectionTitle}>🏆 Achievements</Text>
          {milestones.map((milestone, index) => (
            <View key={index} style={styles.milestoneRow}>
              <Text style={styles.milestoneTitle}>{milestone.title}</Text>
              <Text style={styles.milestoneDesc}>{milestone.description}</Text>
            </View>
          ))}
        </View>
      )}

      <View style={styles.trendSection}>
        <Text style={styles.trendLabel}>Recent Trend:</Text>
        <View style={[styles.trendBadge, { backgroundColor: trend === 'up' ? '#E8F5E9' : trend === 'down' ? '#FFEBEE' : '#F5F5F5' }]}>
          <Text style={[styles.trendText, { color: trend === 'up' ? '#4CAF50' : trend === 'down' ? '#F44336' : '#757575' }]}>
            {trend === 'up' ? '↗ Improving' : trend === 'down' ? '↘ Focus Needed' : '→ Stable'}
          </Text>
        </View>
      </View>
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
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    marginHorizontal: 4,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#8E8E93',
  },
  milestonesSection: {
    marginTop: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8E8E93',
    marginBottom: 12,
  },
  milestoneRow: {
    marginBottom: 12,
  },
  milestoneTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
    marginBottom: 2,
  },
  milestoneDesc: {
    fontSize: 13,
    color: '#8E8E93',
  },
  trendSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
  },
  trendLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginRight: 8,
  },
  trendBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  trendText: {
    fontSize: 13,
    fontWeight: '600',
  },
});

export default ProgressCard;

