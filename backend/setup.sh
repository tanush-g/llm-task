#!/bin/bash

# Setup script for PrivChat with Gemini API

echo "🚀 Setting up PrivChat with Google Gemini API"
echo "=============================================="

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file not found. Creating one..."
    echo "GEMINI_API_KEY=your_api_key_here" > .env
fi

# Check if API key is set
if grep -q "your_api_key_here" .env; then
    echo "⚠️  Please update your .env file with your actual Gemini API key"
    echo "   Edit the .env file and replace 'your_api_key_here' with your API key from Google AI Studio"
    echo ""
    echo "   Get your API key from: https://aistudio.google.com/apikey"
    echo ""
    exit 1
else
    echo "✅ API key appears to be configured"
fi

# Check if spaCy model is installed
echo ""
echo "Checking spaCy model..."
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ spaCy English model is installed"
else
    echo "📦 Installing spaCy English model..."
    python -m spacy download en_core_web_sm
fi

echo ""
echo "🎉 Setup complete! You can now start the server with:"
echo "   python main.py"
echo ""
echo "The application will be available at:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend: Open frontend/index.html in your browser"
