#!/bin/bash

# Telecom News Multi-Agent System Startup Script

echo "🚀 Starting Telecom News Multi-Agent System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys and configuration"
    echo "   Required: SERPER_API_KEY, PERPLEXITY_API_KEY, SCALEWAY_API_KEY"
    exit 1
fi

# Check if required API keys are set
source .env

if [ -z "$SERPER_API_KEY" ] || [ "$SERPER_API_KEY" = "your_serper_api_key_here" ]; then
    echo "❌ SERPER_API_KEY not configured in .env file"
    exit 1
fi

if [ -z "$PERPLEXITY_API_KEY" ] || [ "$PERPLEXITY_API_KEY" = "your_perplexity_api_key_here" ]; then
    echo "❌ PERPLEXITY_API_KEY not configured in .env file"
    exit 1
fi

if [ -z "$SCALEWAY_API_KEY" ] || [ "$SCALEWAY_API_KEY" = "your_scaleway_api_key_here" ]; then
    echo "❌ SCALEWAY_API_KEY not configured in .env file"
    exit 1
fi

# SCALEWAY_PROJECT_ID is not needed for the new API format

echo "✅ API keys configured"

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if database is accessible
echo "🗄️  Checking database connection..."
python -c "
import asyncio
from services.database import init_db
try:
    asyncio.run(init_db())
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your database configuration."
    exit 1
fi

# Run system test
echo "🧪 Running system test..."
python test_system.py

if [ $? -ne 0 ]; then
    echo "❌ System test failed. Please check the logs above."
    exit 1
fi

echo "✅ System test passed"

# Start the application
echo "🚀 Starting FastAPI server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"

python main.py
