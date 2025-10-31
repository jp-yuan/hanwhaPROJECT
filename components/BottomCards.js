import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { appData } from '../data/appData';

const BottomCards = () => {
  const { bottomCards } = appData;
  
  return (
    <View style={styles.container}>
      {/* Quiz Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>{bottomCards.quiz.title}</Text>
        <TouchableOpacity style={styles.button}>
          <Ionicons name="bag" size={16} color="#fff" style={styles.buttonIcon} />
          <Text style={styles.buttonText}>{bottomCards.quiz.buttonText}</Text>
        </TouchableOpacity>
      </View>
      
      {/* Tip Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>{bottomCards.tip.title}</Text>
        <Text style={styles.tipText}>
          {bottomCards.tip.text}
        </Text>
        <View style={styles.tipFooter}>
          <Text style={styles.tipText}>{bottomCards.tip.footerText}</Text>
          <Ionicons name="school" size={16} color="#8E8E93" style={styles.graduationIcon} />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginBottom: 20,
    gap: 12,
  },
  card: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#2C2C2E',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonIcon: {
    marginRight: 6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  tipText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  tipFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  graduationIcon: {
    marginLeft: 4,
  },
});

export default BottomCards;
