#!/bin/bash
set -euo pipefail

# --- Logging function ---
log() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"
}

log "Starting entrypoint script."

# Log environment info for debugging
log "Running as user: $(whoami)"
log "Checking shared memory size:"
df -h /dev/shm || log "/dev/shm not available"

# Verify required binaries exist
command -v Xvfb >/dev/null 2>&1 || { log "ERROR: Xvfb is not installed."; exit 1; }
command -v mvn >/dev/null 2>&1 || { log "ERROR: Maven is not installed."; exit 1; }

# Start Xvfb in the background
log "Starting Xvfb on :99"
Xvfb :99 -screen 0 1920x1080x24 -ac &
XVFB_PID=$!
export DISPLAY=:99

# Wait for Xvfb to be ready (up to 10s)
log "Waiting for Xvfb to start..."
timeout=10
for i in $(seq 1 $timeout); do
  if ps aux | grep -v grep | grep Xvfb >/dev/null; then
    log "Xvfb is running."
    break
  fi
  sleep 1
done
if ! ps aux | grep -v grep | grep Xvfb >/dev/null; then
  log "ERROR: Xvfb did not start."
  exit 1
fi

# Print browser and webdriver versions for debugging
log "Checking browser and driver versions..."
{
  echo "Chrome version:"
  /usr/bin/google-chrome --version || echo "Chrome not found"

  echo "Chrome headless test:"
  /usr/bin/google-chrome --headless --no-sandbox --disable-dev-shm-usage --disable-gpu --dump-dom https://example.com || echo "Chrome headless test failed"

  echo "ChromeDriver version:"
  /usr/local/bin/chromedriver --version || echo "ChromeDriver not found"

  echo "Edge version:"
  /usr/bin/microsoft-edge --version || echo "Edge not found"

  echo "Edge headless test:"
  /usr/bin/microsoft-edge --headless --no-sandbox --disable-dev-shm-usage --disable-gpu --dump-dom https://example.com || echo "Edge headless test failed"

  echo "EdgeDriver version:"
  /usr/local/bin/msedgedriver --version || echo "EdgeDriver not found"
} | tee /dev/stderr

# Set CLASSPATH if needed (adjust paths as necessary)
export CLASSPATH="target/classes:/app/selenium/*:/app/selenium/libs/*"
log "CLASSPATH set to $CLASSPATH"

# Clean up Xvfb
log "Cleaning up Xvfb..."
kill $XVFB_PID || log "Xvfb process already terminated"

log "Entrypoint script completed."
