#!/bin/bash

echo "==================================="
echo "realtime chat server - startup"
echo "==================================="
echo ""

# check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "warning: virtual environment not activated"
    echo "activating .venv..."
    source .venv/bin/activate
fi

# check if redis is running
echo "checking redis connection..."
if python -c "import redis; r = redis.from_url('redis://localhost:6379'); r.ping()" 2>/dev/null; then
    echo "redis is running"
else
    echo "redis is not running or not installed"
    echo ""
    echo "to install redis:"
    echo "  sudo apt update"
    echo "  sudo apt install redis-server"
    echo "  sudo service redis-server start"
    echo ""
    echo "or use docker:"
    echo "  docker run -d -p 6379:6379 redis:latest"
    echo ""
    read -p "do you want to continue without redis? (websocket features will not work) [y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# check if .env exists
if [ ! -f .env ]; then
    echo "creating .env file from .env.example..."
    cp .env.example .env
    echo ".env file created"
fi

# check if database exists
if [ ! -f chatserver.db ]; then
    echo "initializing database..."
    python manage_db.py init
    echo "database initialized"
else
    echo "database exists"
fi

echo ""
echo "==================================="
echo "starting fastapi server..."
echo "==================================="
echo ""
echo "api will be available at:"
echo "  - http://localhost:8000"
echo "  - docs: http://localhost:8000/docs"
echo "  - health: http://localhost:8000/health"
echo ""
echo "press ctrl+c to stop the server"
echo ""

# start the server
python run_server.py
