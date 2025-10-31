import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';

const QuickReplyButtons = ({ replies, onPress }) => {
  if (!replies || replies.length === 0) return null;

  return (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
    >
      {replies.map((reply, index) => (
        <TouchableOpacity
          key={index}
          style={styles.button}
          onPress={() => onPress(reply)}
        >
          <Text style={styles.buttonText}>{reply.text}</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 10,
    marginHorizontal: 0,
  },
  contentContainer: {
    paddingHorizontal: 16,
    paddingRight: 16,
  },
  button: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    paddingHorizontal: 18,
    paddingVertical: 12,
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  buttonText: {
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '600',
    letterSpacing: -0.2,
  },
});

export default QuickReplyButtons;

