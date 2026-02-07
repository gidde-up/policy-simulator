#!/bin/bash

echo "========================================"
echo "Economic Policy Simulator - Startup"
echo "========================================"
echo

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo
echo "Starting servers..."
echo "Backend will be at: http://localhost:8000"
echo "Frontend will be at: http://localhost:5173"
echo "API docs at: http://localhost:8000/docs"
echo

# Start backend in background
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "Servers started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo
echo "Press Enter to stop servers..."

# Wait for user input
read

# Kill processes
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null

echo "Servers stopped."
