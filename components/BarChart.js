import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const BarChart = ({ data, title }) => {
  // Debug logging
  console.log('BarChart received data:', JSON.stringify(data, null, 2));
  
  if (!data) {
    console.log('BarChart: No data provided');
    return null;
  }
  
  if (!data.bars || data.bars.length === 0) {
    console.log('BarChart: No bars in data or empty array');
    return null;
  }

  const { bars, max_value, y_axis_label, x_axis_label } = data;
  const maxValue = max_value || Math.max(...bars.map(bar => bar.value));

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title || '📊 Score Breakdown'}</Text>
      
      <View style={styles.chartContainer}>
        {bars.map((bar, index) => {
          const percentage = maxValue > 0 ? (bar.value / maxValue) * 100 : 0;
          
          return (
            <View key={index} style={styles.barRow}>
              <View style={styles.barInfo}>
                <View style={styles.labelRow}>
                  <View style={[styles.colorDot, { backgroundColor: bar.color }]} />
                  <Text style={styles.barLabel}>{bar.label}</Text>
                </View>
                <Text style={styles.barValue}>{bar.value.toLocaleString()}</Text>
              </View>
              
              <View style={styles.barContainer}>
                <View 
                  style={[
                    styles.barFill, 
                    { 
                      width: `${percentage}%`,
                      backgroundColor: bar.color
                    }
                  ]} 
                />
              </View>
              
              <Text style={styles.percentage}>{bar.percentage}%</Text>
            </View>
          );
        })}
      </View>
      
      {(x_axis_label || y_axis_label) && (
        <View style={styles.axisLabels}>
          {y_axis_label && <Text style={styles.axisLabel}>{y_axis_label}</Text>}
          {x_axis_label && <Text style={styles.axisLabel}>{x_axis_label}</Text>}
        </View>
      )}
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
  chartContainer: {
    gap: 16,
  },
  barRow: {
    marginBottom: 4,
  },
  barInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  colorDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
  },
  barLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: '#000',
    flex: 1,
  },
  barValue: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
    marginLeft: 8,
  },
  barContainer: {
    height: 10,
    backgroundColor: '#F2F2F7',
    borderRadius: 5,
    overflow: 'hidden',
    marginBottom: 6,
  },
  barFill: {
    height: '100%',
    borderRadius: 5,
  },
  percentage: {
    fontSize: 13,
    color: '#8E8E93',
    marginTop: 2,
  },
  axisLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
  },
  axisLabel: {
    fontSize: 12,
    color: '#8E8E93',
    fontWeight: '500',
  },
});

export default BarChart;

