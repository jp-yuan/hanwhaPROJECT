import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { G, Path, Text as SvgText } from 'react-native-svg';

const PerformanceAnalysisCard = ({ data }) => {
  if (!data || !data.pie_chart || !data.pie_chart.segments) return null;

  const { pie_chart, test_id, total_score, insights = [] } = data;
  const { segments, test_number } = pie_chart;
  const size = 120;
  const center = size / 2;
  const radius = 50;
  const strokeWidth = 0;

  // Calculate pie chart segments
  const total = segments.reduce((sum, seg) => sum + seg.score, 0);
  let currentAngle = -90; // Start at top

  const pieSegments = segments.map((segment, index) => {
    const percentage = (segment.score / total) * 100;
    const angle = (percentage / 100) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;

    // Calculate path for pie slice
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;

    const x1 = center + radius * Math.cos(startAngleRad);
    const y1 = center + radius * Math.sin(startAngleRad);
    const x2 = center + radius * Math.cos(endAngleRad);
    const y2 = center + radius * Math.sin(endAngleRad);

    const largeArcFlag = angle > 180 ? 1 : 0;

    const pathData = [
      `M ${center} ${center}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z',
    ].join(' ');

    currentAngle += angle;

    return (
      <Path
        key={index}
        d={pathData}
        fill={segment.color}
        stroke="#FFFFFF"
        strokeWidth={strokeWidth}
      />
    );
  });

  return (
    <View style={styles.card}>
      <View style={styles.chartContainer}>
        <View style={styles.pieChartWrapper}>
          <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
            <G>{pieSegments}</G>
            <SvgText
              x={center}
              y={center + 5}
              fontSize={24}
              fontWeight="600"
              fill="#1C1C1E"
              textAnchor="middle"
            >
              {test_number || '#'}
            </SvgText>
          </Svg>
        </View>

        <View style={styles.topicList}>
          {segments.map((segment, index) => (
            <View key={index} style={styles.topicRow}>
              <View style={[styles.colorDot, { backgroundColor: segment.color }]} />
              <View style={styles.topicInfo}>
                <Text style={styles.topicName}>{segment.name}</Text>
                <Text style={styles.topicScore}>
                  {segment.score.toLocaleString()} ({segment.percentage}%)
                </Text>
              </View>
            </View>
          ))}
        </View>
      </View>

      {insights && insights.length > 0 && (
        <View style={styles.insightsSection}>
          <Text style={styles.insightsTitle}>Analysis</Text>
          {insights.map((insight, index) => (
            <View key={index} style={styles.insightRow}>
              <Text style={styles.insightIcon}>{insight.icon || '✅'}</Text>
              <Text style={styles.insightText}>{insight.text}</Text>
            </View>
          ))}
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
  chartContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  pieChartWrapper: {
    marginRight: 20,
  },
  topicList: {
    flex: 1,
    marginTop: 4,
  },
  topicRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  colorDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
  },
  topicInfo: {
    flex: 1,
  },
  topicName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000',
    marginBottom: 2,
  },
  topicScore: {
    fontSize: 13,
    color: '#8E8E93',
  },
  insightsSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#F2F2F7',
  },
  insightsTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
    marginBottom: 12,
    letterSpacing: -0.3,
  },
  insightRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  insightText: {
    fontSize: 14,
    color: '#000',
    flex: 1,
  },
});

export default PerformanceAnalysisCard;

