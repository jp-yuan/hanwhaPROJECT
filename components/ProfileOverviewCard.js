import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const ProfileOverviewCard = ({ data }) => {
  const renderInfoRow = (icon, label, value, iconColor = '#007AFF') => (
    <View style={styles.infoRow}>
      <View style={styles.iconContainer}>
        <Ionicons name={icon} size={20} color={iconColor} />
      </View>
      <View style={styles.infoContent}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Your Test Profile</Text>
      
      <View style={styles.infoContainer}>
        {renderInfoRow('school-outline', 'Test Type', data.test_type, '#5856D6')}
        
        {renderInfoRow(
          'trending-up-outline', 
          'Target Score', 
          `${data.target_score} (from ${data.current_score})`,
          '#34C759'
        )}
        
        {data.days_until_test !== null && data.days_until_test !== undefined && (
          renderInfoRow(
            'calendar-outline', 
            'Days Until Test', 
            data.days_until_test,
            '#FF9500'
          )
        )}
        
        {renderInfoRow(
          'time-outline', 
          'Study Hours/Week', 
          data.study_hours_per_week,
          '#FF3B30'
        )}
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
  infoContainer: {
    gap: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F2F2F7',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 13,
    color: '#8E8E93',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
});

export default ProfileOverviewCard;

