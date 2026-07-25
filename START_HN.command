#!/bin/bash

cd "$(dirname "$0")" || exit 1
printf '\033c'

echo "=========================================="
echo "     HN Radiology Suite - Starting"
echo "=========================================="
echo

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js was not found on this Mac."
  echo "Please install Node.js, then run this file again."
  echo
  read -r -p "Press Enter to close..."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm was not found on this Mac."
  echo "Please reinstall Node.js, then run this file again."
  echo
  read -r -p "Press Enter to close..."
  exit 1
fi

VITE_FILE="./node_modules/vite/bin/vite.js"

clean_install() {
  echo "Preparing dependencies for this Mac..."
  rm -rf node_modules package-lock.json
  npm install --include=optional --no-audit --no-fund
}

if [ ! -f "$VITE_FILE" ]; then
  clean_install || {
    echo
    echo "Dependency installation failed. Check the internet connection and try again."
    read -r -p "Press Enter to close..."
    exit 1
  }
fi

echo "Opening HN Radiology Suite..."
echo

# Invoke Vite from its real package path. This avoids broken .bin links after ZIP extraction.
node "$VITE_FILE" --open
STATUS=$?

# If packaged native dependencies do not match this Mac, reinstall them once.
if [ "$STATUS" -ne 0 ]; then
  echo
  echo "The packaged dependencies were not compatible with this Mac."
  echo "A clean one-time installation will now be performed..."
  echo

  clean_install || {
    echo
    echo "Clean installation failed. Check the internet connection and try again."
    read -r -p "Press Enter to close..."
    exit 1
  }

  echo
  echo "Opening HN Radiology Suite..."
  node "$VITE_FILE" --open
  STATUS=$?
fi

if [ "$STATUS" -ne 0 ]; then
  echo
  echo "HN Radiology Suite could not start."
  echo "Please copy the complete error text and send it for review."
  read -r -p "Press Enter to close..."
fi

exit "$STATUS"
