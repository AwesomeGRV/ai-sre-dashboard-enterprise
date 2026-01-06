#!/bin/bash

echo "Starting AI-Powered SRE Dashboard Demo..."
echo

# Function to start service in background
start_service() {
    local service_name=$1
    local command=$2
    local dir=$3
    
    echo "[$service_name] Starting..."
    cd "$dir"
    osascript -e "tell app \"Terminal\" to do script \"$command\""
    sleep 3
}

echo "[1/4] Starting Sample Node.js Application..."
start_service "Sample App" "cd '$PWD/apps/sample-node-app' && npm install && npm start" "$PWD"

echo "[2/4] Starting Backend API..."
start_service "Backend API" "cd '$PWD/backend/api' && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000" "$PWD"

echo "[3/4] Starting Frontend Dashboard..."
start_service "Frontend" "cd '$PWD/frontend/dashboard' && npm install && npm start" "$PWD"

echo "[4/4] Waiting for services to start..."
sleep 10

echo "Opening Dashboard in Browser..."
open http://localhost:3000

echo
echo "========================================"
echo "AI-Powered SRE Dashboard is starting!"
echo
echo "Access URLs:"
echo "- Main Dashboard: http://localhost:3000"
echo "- Backend API:   http://localhost:8000"
echo "- Sample App:    http://localhost:3000"
echo
echo "Services are starting in separate terminal windows."
echo "Press any key to continue..."
read -n 1
