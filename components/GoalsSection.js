import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import CircularProgress from './CircularProgress';
import { appData } from '../data/appData';

const GoalsSection = () => {
  const { goals } = appData;
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{goals.title}</Text>
        <TouchableOpacity>
          <Text style={styles.editText}>{goals.editText}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.progressContainer}>
        {goals.progressItems.map((item, index) => (
          <View key={index} style={styles.progressItem}>
            <CircularProgress percentage={item.percentage} size={60} />
            <Text style={styles.progressLabel}>{item.label}</Text>
          </View>
        ))}
      </View>
      
      <View style={styles.tipsContainer}>
        {goals.tips.map((tip, index) => (
          <TouchableOpacity key={index} style={styles.tipItem}>
            <Ionicons name="bulb" size={16} color="#FF9500" style={styles.tipIcon} />
            <Text style={styles.tipText}>{tip.text}</Text>
          </TouchableOpacity>
        ))}
      </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
  },
  editText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  progressItem: {
    alignItems: 'center',
  },
  progressLabel: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 8,
    fontWeight: '500',
  },
  tipsContainer: {
    gap: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  tipIcon: {
    marginRight: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
    flex: 1,
  },
});

export default GoalsSection;
