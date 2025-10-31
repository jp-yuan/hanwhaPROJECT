import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { appData } from '../data/appData';

const SavingsGoal = () => {
  const { savingsGoal } = appData;
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{savingsGoal.title}</Text>
      
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${savingsGoal.progress * 100}%` }]} />
          <View style={styles.progressStripes} />
        </View>
        <Text style={styles.progressText}>{savingsGoal.progressText}</Text>
      </View>
      
      {/* Home indicator */}
      <View style={styles.homeIndicator} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 16,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#F2F2F7',
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 12,
    position: 'relative',
  },
  progressFill: {
    height: '100%',
    width: '68%',
    backgroundColor: '#8E8E93',
    borderRadius: 4,
  },
  progressStripes: {
    position: 'absolute',
    top: 0,
    left: '68%',
    right: 0,
    height: '100%',
    backgroundColor: '#E5E5EA',
    borderRadius: 4,
    // Note: In a real app, you'd use a pattern or image for stripes
    // For now, we'll use a solid color
  },
  progressText: {
    fontSize: 14,
    color: '#8E8E93',
    fontWeight: '500',
  },
  homeIndicator: {
    width: 134,
    height: 5,
    backgroundColor: '#000',
    borderRadius: 2.5,
    alignSelf: 'center',
    marginTop: 20,
  },
});

export default SavingsGoal;
