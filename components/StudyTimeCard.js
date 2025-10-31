import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { appData } from '../data/appData';

const StudyTimeCard = () => {
  const { studyTime } = appData;
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{studyTime.title}</Text>
        <TouchableOpacity>
          <Text style={styles.detailsText}>{studyTime.detailsText}</Text>
        </TouchableOpacity>
      </View>
      
      <Text style={styles.message}>
        {studyTime.message}
      </Text>
      
      <View style={styles.characterContainer}>
        <View style={styles.character}>
          <View style={styles.characterBody} />
          <View style={styles.characterHorn} />
          <View style={styles.characterMouth} />
        </View>
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
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    flex: 1,
    marginRight: 10,
  },
  detailsText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  message: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 16,
  },
  characterContainer: {
    alignItems: 'flex-end',
  },
  character: {
    width: 40,
    height: 40,
    position: 'relative',
  },
  characterBody: {
    width: 30,
    height: 30,
    backgroundColor: '#fff',
    borderRadius: 15,
    borderWidth: 2,
    borderColor: '#E5E5EA',
    position: 'absolute',
    bottom: 0,
    left: 5,
  },
  characterHorn: {
    width: 8,
    height: 8,
    backgroundColor: '#E5E5EA',
    borderRadius: 4,
    position: 'absolute',
    top: 2,
    left: 11,
  },
  characterMouth: {
    width: 6,
    height: 3,
    backgroundColor: '#FF3B30',
    borderRadius: 2,
    position: 'absolute',
    bottom: 8,
    left: 12,
  },
});

export default StudyTimeCard;
