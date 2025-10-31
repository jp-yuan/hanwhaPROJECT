import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const ScoreBreakdownChart = ({ data, title }) => {
  if (!data) return null;

  const sections = Object.entries(data);
  const maxScore = Math.max(...sections.map(([, value]) => value.score || 0));

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title || '📊 Score Breakdown'}</Text>
      
      {sections.map(([sectionName, sectionData], index) => {
        const score = sectionData.score || 0;
        const percentile = sectionData.percentile || 0;
        const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;

        return (
          <View key={index} style={styles.sectionRow}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionName}>{sectionName.charAt(0).toUpperCase() + sectionName.slice(1)}</Text>
              <Text style={styles.sectionScore}>{score}</Text>
            </View>
            
            <View style={styles.barContainer}>
              <View 
                style={[
                  styles.barFill, 
                  { 
                    width: `${percentage}%`,
                    backgroundColor: percentile >= 70 ? '#34C759' : percentile >= 50 ? '#FF9500' : '#007AFF'
                  }
                ]} 
              />
            </View>
            
            <Text style={styles.percentile}>{percentile}th percentile</Text>
          </View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 16,
  },
  sectionRow: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionName: {
    fontSize: 15,
    fontWeight: '500',
    color: '#000',
  },
  sectionScore: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  barContainer: {
    height: 8,
    backgroundColor: '#F2F2F7',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 6,
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
  percentile: {
    fontSize: 12,
    color: '#8E8E93',
  },
});

export default ScoreBreakdownChart;

