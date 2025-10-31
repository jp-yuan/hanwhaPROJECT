import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { appData } from '../data/appData';

const Header = ({ onProfilePress, onChatPress }) => {
  const { header } = appData;
  
  return (
    <View style={styles.container}>
      {/* Status Bar */}
      <View style={styles.statusBar}>
        <Text style={styles.time}>{header.time}</Text>
        <View style={styles.statusIcons}>
          <Ionicons name="cellular" size={16} color="#000" />
          <Ionicons name="wifi" size={16} color="#000" style={styles.icon} />
          <Ionicons name="battery-full" size={16} color="#000" style={styles.icon} />
        </View>
      </View>
      
      {/* Search Bar and Menu */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Text style={styles.searchText}>{header.searchText}</Text>
          <TouchableOpacity>
            <Ionicons name="mic" size={20} color="#666" />
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.menuButton} onPress={onChatPress}>
          <Ionicons name="chatbubble-ellipses" size={24} color="#666" />
        </TouchableOpacity>
        <TouchableOpacity style={[styles.menuButton, { marginLeft: 8 }]} onPress={onProfilePress}>
          <Ionicons name="person" size={24} color="#666" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  time: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  statusIcons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    marginLeft: 4,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  searchBar: {
    flex: 1,
    backgroundColor: '#2C2C2E',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginRight: 12,
  },
  searchText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  menuButton: {
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default Header;
