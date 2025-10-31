// API Configuration
const isDevelopment = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;

export const API_URL = isDevelopment
  ? 'http://localhost:8000'
  : process.env.REACT_APP_API_URL || 'https://hanwhaproject.onrender.com';

export const config = {
  apiUrl: API_URL,
};

