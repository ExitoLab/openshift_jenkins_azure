#!/bin/bash
set -e

# Start Xvfb in the background
Xvfb :99 -screen 0 1920x1080x24 -ac &
export DISPLAY=:99

# Wait for Xvfb to start
sleep 2

# Print browser and webdriver versions for debugging
echo "Using Chrome version:"
google-chrome --version
echo "Using ChromeDriver version:"
chromedriver --version
echo "Using Edge version:"
microsoft-edge --version
echo "Using EdgeDriver version:"
msedgedriver --version

# Print environment info
echo "Running as user:" $(whoami)
echo "DISPLAY=$DISPLAY"

# Check if a specific test group is specified
if [ ! -z "$TEST_GROUP" ]; then
  echo "Running tests for group: $TEST_GROUP"
  mvn test -Dgroups=$TEST_GROUP
# Check if a specific browser is specified
elif [ ! -z "$BROWSER" ]; then
  echo "Running tests with browser: $BROWSER"
  mvn test -Dbrowser=$BROWSER
# Run all tests by default
else
  echo "Running all tests"
  mvn test
fi