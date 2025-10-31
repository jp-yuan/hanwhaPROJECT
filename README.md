# Hanwha Mobile App

A React Native mobile application that replicates the design from the provided image, featuring budget tracking, goal management, and motivational content.

## Features

- **Budget Tracking**: Monthly budget overview with progress indicators
- **Goal Management**: Daily goals with circular progress indicators
- **Study Time Tracking**: Motivational messages and progress tracking
- **Interactive Elements**: Quiz cards and tips
- **Savings Goals**: Monthly savings progress tracking

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Expo CLI
- iOS Simulator or Android Emulator (or physical device with Expo Go app)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Run on your preferred platform:
- iOS: `npm run ios`
- Android: `npm run android`
- Web: `npm run web`

## Project Structure

```
├── App.js                 # Main app component
├── components/            # Reusable components
│   ├── Header.js         # Status bar and search
│   ├── BudgetSection.js  # Budget tracking
│   ├── StudyTimeCard.js  # Study motivation card
│   ├── GoalsSection.js   # Daily goals
│   ├── CircularProgress.js # Progress indicators
│   ├── BottomCards.js    # Quiz and tip cards
│   └── SavingsGoal.js    # Savings tracking
└── package.json          # Dependencies
```

## Components

- **Header**: Status bar, search functionality, and menu
- **BudgetSection**: Monthly budget with progress bar and categories
- **StudyTimeCard**: Motivational study time tracking
- **GoalsSection**: Daily goals with circular progress indicators
- **BottomCards**: Quiz and tip sections
- **SavingsGoal**: Monthly savings goal tracking

## Technologies Used

- React Native
- Expo
- React Native SVG (for circular progress)
- Expo Vector Icons
- React Native StyleSheet

## Backend (FastAPI) – Mock Agent

The project now includes a mock FastAPI backend for the multi-turn test-prep agent.

### Setup

1. Create virtual environment and install deps:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Create `.env` in `backend/` (defaults are fine):

```
ENVIRONMENT=development
MOCK_MODE=true
OPENAI_API_KEY=
```

3. Run the server:

```bash
uvicorn src.main:app --reload --port 8000
```

4. Healthcheck and endpoints:

- GET `http://localhost:8000/healthz`
- POST `http://localhost:8000/chat` { user_id, message, session_id? }
- GET `http://localhost:8000/user/{id}/profile`
- POST `http://localhost:8000/user/{id}/quiz` { config }
- POST `http://localhost:8000/quiz/{quiz_id}/submit` { user_id, responses[] }

### Mobile Chat

In the app home header, tap the chat icon to open the Chat screen. The chat posts to `http://localhost:8000/chat`.

## Design Features

- Clean, modern UI with rounded corners
- Consistent color scheme (grays and accent colors)
- Card-based layout with shadows
- Responsive design for mobile devices
- Interactive elements with proper touch feedback
