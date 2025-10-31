import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { appData } from '../data/appData';

const BudgetSection = () => {
  const { budget } = appData;
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{budget.title}</Text>
        <TouchableOpacity style={styles.toggle}>
          <Text style={styles.toggleText}>{budget.toggleText}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.budgetInfo}>
        <Text style={styles.amount}>${budget.currentAmount.toLocaleString()} / ${budget.totalAmount.toLocaleString()}</Text>
      </View>
      
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={styles.progressSegments}>
            {budget.categories.map((category, index) => (
              <View
                key={index}
                style={[
                  styles.progressSegment,
                  {
                    width: `${category.percentage * 100}%`,
                    backgroundColor: category.color,
                    borderTopLeftRadius: index === 0 ? 4 : 0,
                    borderBottomLeftRadius: index === 0 ? 4 : 0,
                    borderTopRightRadius: index === budget.categories.length - 1 ? 4 : 0,
                    borderBottomRightRadius: index === budget.categories.length - 1 ? 4 : 0,
                  }
                ]}
              />
            ))}
          </View>
        </View>
      </View>
      
      <View style={styles.categories}>
        {budget.categories.map((category, index) => (
          <View key={index} style={styles.category}>
            <View style={[styles.categoryDot, { backgroundColor: category.color }]} />
            <Text style={styles.categoryText}>{category.name}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
  },
  toggle: {
    backgroundColor: '#2C2C2E',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  toggleText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  budgetInfo: {
    marginBottom: 12,
  },
  amount: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#F2F2F7',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2C2C2E',
    borderRadius: 4,
  },
  progressSegments: {
    height: '100%',
    flexDirection: 'row',
    width: '100%',
  },
  progressSegment: {
    height: '100%',
    borderRadius: 0,
  },
  categories: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  category: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  categoryDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  categoryText: {
    fontSize: 14,
    color: '#8E8E93',
    fontWeight: '500',
  },
});

export default BudgetSection;
