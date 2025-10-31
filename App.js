import React, { useState } from 'react';
import { StyleSheet, ScrollView, SafeAreaView, StatusBar } from 'react-native';
import Header from './components/Header';
import BudgetSection from './components/BudgetSection';
import StudyTimeCard from './components/StudyTimeCard';
import GoalsSection from './components/GoalsSection';
import BottomCards from './components/BottomCards';
import SavingsGoal from './components/SavingsGoal';
import UserProfile from './components/UserProfile';
import ChatScreen from './components/ChatScreen';
import { appData } from './data/appData';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('home');

  const renderScreen = () => {
    switch (currentScreen) {
      case 'chat':
        return <ChatScreen onBack={() => setCurrentScreen('home')} userProfile={appData.userProfile} />;
      case 'profile':
        return <UserProfile onBack={() => setCurrentScreen('home')} />;
      default:
        return (
          <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
            <Header onChatPress={() => setCurrentScreen('chat')} onProfilePress={() => setCurrentScreen('profile')} />
            <BudgetSection />
            <StudyTimeCard />
            <GoalsSection />
            <BottomCards />
            <SavingsGoal />
          </ScrollView>
        );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      {renderScreen()}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollView: {
    flex: 1,
  },
});
