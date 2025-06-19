# PrivChat - PII Detection with Google Gemini

A full-stack application that detects personally identifiable information (PII) in text and provides AI-powered suggestions for safer communication using Google's Gemini API.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI Studio API Key ([Get one here](https://aistudio.google.com/apikey))

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run setup script
./setup.sh

# Add your Gemini API key to .env file
# Edit .env and replace 'your_api_key_here' with your actual API key
```

### 2. Configure Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Edit `backend/.env` file:

   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Start the Application

```bash
# Start the backend server
cd backend
python main.py

# The API will be available at http://localhost:8000
```

### 4. Open the Frontend

Open `frontend/index.html` in your web browser or serve it with a simple HTTP server:

```bash
# Option 1: Direct file open
open frontend/index.html

# Option 2: Serve with Python (recommended)
cd frontend
python -m http.server 8080
# Then open http://localhost:8080
```

## 🛠️ Development

### Project Structure

```
├── backend/
│   ├── main.py          # FastAPI backend with Gemini integration
│   ├── requirements.txt # Python dependencies
│   ├── .env            # Environment variables (API key)
│   └── setup.sh        # Setup script
├── frontend/
│   └── index.html      # Frontend application
└── README.md
```

### API Endpoints

- `POST /analyze` - Analyze text for PII and get AI suggestions
- `GET /health` - Health check endpoint

### Key Features

1. **PII Detection**: Uses spaCy NLP to identify:
   - Person names
   - Organizations
   - Locations (GPE)
   - Dates
   - Money amounts
   - Phone numbers

2. **AI-Powered Suggestions**: Gemini API provides:
   - Privacy-conscious text rewriting
   - Maintains original meaning while protecting sensitive data
   - Natural language output

3. **Interactive Frontend**:
   - Real-time PII highlighting
   - AI suggestion display
   - Modern, responsive UI

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Gemini Model Configuration

The application uses the `gemini-2.0-flash` model with these settings:

- Temperature: 0.3 (for consistent responses)
- Max tokens: 150
- Top-p: 0.8

## 🚀 Deployment Options

### Local Development

1. Follow the Quick Start guide above
2. Backend runs on `http://localhost:8000`
3. Frontend can be served from any web server

### Production Deployment

#### Backend (FastAPI)

```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Using gunicorn for production
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend

Serve the `frontend/index.html` using any web server:

- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

### Environment Variables for Production

```env
GEMINI_API_KEY=your_production_api_key
```

## 🔒 Security Notes

1. **API Key Security**: Never commit your `.env` file or expose your API key
2. **CORS**: Currently configured for development (allows all origins)
3. **Rate Limiting**: Consider adding rate limiting for production use
4. **Input Validation**: The API validates input text before processing

## 🛠️ Troubleshooting

### Common Issues

1. **"spaCy model not found"**

   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **"Gemini API key not configured"**
   - Check your `.env` file exists in the backend directory
   - Verify your API key is correct
   - Ensure you've enabled the Gemini API in Google AI Studio

3. **CORS errors**
   - Make sure the backend is running on `http://localhost:8000`
   - Check that the frontend is making requests to the correct URL

4. **Import errors**

   ```bash
   pip install -r requirements.txt
   ```

### Testing the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test analyze endpoint
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hi, I am John Doe and I work at Google in Mountain View."}'
```

## 📝 API Usage Example

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"text": "Hi, I'm John Doe from Acme Corp in New York."}
)

data = response.json()
print("Detected entities:", data["entities"])
print("AI suggestion:", data["ai_response"])
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.
