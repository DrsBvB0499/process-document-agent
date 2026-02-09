#!/bin/bash

echo "============================================"
echo " Process Document Agent - Web Interface"
echo "============================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.12+ and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found"
    echo "Please create a .env file with your API keys"
    echo "See .env.example for reference"
    echo ""
    read -p "Press Enter to continue..."
fi

# Install/update dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================"
echo " Starting Web Server..."
echo "============================================"
echo ""
echo "Server will be available at: http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the Flask server
python3 web/server.py
