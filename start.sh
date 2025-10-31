#!/bin/bash

# Increase file descriptor limit
ulimit -n 65536

# Check if the limit was set
echo "File descriptor limit set to: $(ulimit -n)"

# Start Expo with reduced file watching
npx expo start --clear
