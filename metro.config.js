const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Reduce file watching to prevent EMFILE errors
config.watchFolders = [];
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

module.exports = config;
