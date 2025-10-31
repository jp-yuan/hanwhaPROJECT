// /Users/youngscholars/Desktop/hanwha_project/v1/data/appData.js

export const appData = {
  budget: {
    title: "This Month's Budget",
    toggleText: "Mon",
    currentAmount: 1576,
    totalAmount: 2000,
    progress: 0.788, // 1576/2000
    categories: [
      { name: "Savings", color: "#2C2C2E", percentage: 0.3 }, // Dark gray - 30%
      { name: "Food", color: "#8E8E93", percentage: 0.338 }, // Medium gray - 33.8%
      { name: "Leisure", color: "#C7C7CC", percentage: 0.15 } // Light gray - 15%
    ]
  },
  
  studyTime: {
    title: "12% less study time today",
    message: "Stay focused! The ABC Certification is an important milestone for you to become a Program Manager.",
    detailsText: "Details"
  },
  
  goals: {
    title: "My Goals For Today",
    editText: "Edit",
    progressItems: [
      { label: "Calories", percentage: 85 },
      { label: "Money", percentage: 75 },
      { label: "Steps", percentage: 54 }
    ],
    tips: [
      { text: "View 3 ways to save 15% on fixed costs →" },
      { text: "11% off your transport costs — Learn more!" }
    ]
  },
  
  bottomCards: {
    quiz: {
      title: "Today's 10-sec Quiz!",
      buttonText: "Get rewarded"
    },
    tip: {
      title: "Today's Tip",
      text: "Did you know that by registering for Selective Service, you may qualify for student aid?",
      footerText: "student aid?"
    }
  },
  
  savingsGoal: {
    title: "This month's savings goal",
    progress: 0.68, // 68%
    progressText: "+ $300 from last month"
  },
  
  header: {
    time: "9:41",
    searchText: "70% goal reached"
  },
  
  userProfile: {
    user_id: "mock-user", // Unique identifier for backend API - single demo user after auth login
    name: "Suzy",
    email: "student@example.com",
    role: "Student",
    avatar: "https://via.placeholder.com/100x100/007AFF/FFFFFF?text=S",
    stats: {
      studyHours: "142h",
      goalsAchieved: "23",
      savings: "2,450",
      streak: "12"
    }
  }
};
