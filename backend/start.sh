#!/bin/bash

echo "==================================="
echo "Realtime Chat Server - Startup"
echo "==================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating .venv..."
    source .venv/bin/activate
fi

# Check if Redis is running
echo "Checking Redis connection..."
if python -c "import redis; r = redis.from_url('redis://localhost:6379'); r.ping()" 2>/dev/null; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running or not installed"
    echo ""
    echo "To install Redis:"
    echo "  sudo apt update"
    echo "  sudo apt install redis-server"
    echo "  sudo service redis-server start"
    echo ""
    echo "Or use Docker:"
    echo "  docker run -d -p 6379:6379 redis:latest"
    echo ""
    read -p "Do you want to continue without Redis? (WebSocket features will not work) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Check if database exists
if [ ! -f chatserver.db ]; then
    echo "Initializing database..."
    python manage_db.py init
    echo "✅ Database initialized"
else
    echo "✅ Database exists"
fi

echo ""
echo "==================================="
echo "Starting FastAPI server..."
echo "==================================="
echo ""
echo "API will be available at:"
echo "  - http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the server
python run_server.py
