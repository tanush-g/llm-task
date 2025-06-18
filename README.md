# PrivChat - PII Detection Web Application

A privacy-focused web application that detects Personally Identifiable Information (PII) in text using advanced NLP techniques and provides AI-powered paraphrasing to help users protect their sensitive information.

![Demo](demo.gif)

## Features

- **PII Detection**: Uses spaCy's Named Entity Recognition to identify personal information including:
  - Names (PERSON)
  - Organizations (ORG)
  - Locations (GPE)
  - Dates (DATE)
  - Phone numbers and other sensitive data
  
- **AI-Powered Paraphrasing**: Integrates with Ollama's Llama 3.2 model to provide privacy-safe text alternatives

- **Interactive UI**: Modern, Mac-style interface with:
  - Real-time PII highlighting with visual effects
  - Expandable details panel showing all detected entities
  - Confidence scores for each detected PII element
  - Responsive design matching the provided reference

- **Privacy-First**: All processing happens locally - no data is sent to external services

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with CORS support
- **NLP**: spaCy with `en_core_web_sm` model for entity recognition
- **AI Integration**: Local Ollama API for text paraphrasing
- **Confidence Scoring**: Custom algorithm based on entity type, length, and context

### Frontend (Vanilla JavaScript)
- **Design**: Mac-style window interface with sidebar navigation
- **Highlighting**: Dynamic PII highlighting with color-coded categories
- **Interactions**: Smooth animations and responsive layout
- **Accessibility**: Keyboard navigation and screen reader support

## Prerequisites

Before running this application, ensure you have:

1. **Python 3.8+** installed
2. **Node.js** (optional, for serving frontend)
3. **Ollama** installed and running locally
4. **spaCy English model** downloaded

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd llm-task
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

### 3. AI Model Setup
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the Llama 3.2 model
ollama pull llama3.2

# Start Ollama service
ollama serve
```

## Usage

### 1. Start the Backend Server
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

### 2. Serve the Frontend
Option A - Using Python's built-in server:
```bash
cd frontend
python -m http.server 3000
```

Option B - Using Node.js (if available):
```bash
cd frontend
npx serve .
```

Option C - Open directly in browser:
```bash
open frontend/index.html
```

### 3. Access the Application
Navigate to `http://localhost:3000` (or the served URL) in your web browser.

## How to Use

1. **Input Text**: Click the "+" button to toggle input mode
2. **Analyze**: Type or paste text containing potential PII and click "Send"
3. **Review Results**: 
   - View the AI-paraphrased version of your text
   - See highlighted PII elements in the original text
   - Click the "i" button to view detailed PII analysis
4. **Privacy Protection**: Use the paraphrased version for safer communication

## API Endpoints

### `POST /analyze`
Analyzes text for PII and generates a privacy-safe paraphrase.

**Request Body:**
```json
{
  "text": "Hi, I'm John Smith from Acme Corp. Call me at 555-123-4567."
}
```

**Response:**
```json
{
  "entities": [
    {
      "text": "John Smith",
      "label": "PERSON",
      "confidence": 0.95,
      "start": 8,
      "end": 18
    }
  ],
  "ai_response": "Hi, I'm [Name] from [Company]. Call me at [Phone].",
  "original_text": "Hi, I'm John Smith from Acme Corp. Call me at 555-123-4567.",
  "sanitized_text": "Hi, I'm [Name] from [Company]. Call me at [Phone]."
}
```

### `GET /health`
Health check endpoint to verify service status.

## Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama API host (default: `http://localhost:11434`)
- `SPACY_MODEL`: spaCy model to use (default: `en_core_web_sm`)

### Model Configuration
You can adjust the AI model parameters in `backend/main.py`:
- `temperature`: Controls randomness (0.3 for consistent results)
- `num_predict`: Maximum response length (100 tokens)
- `top_p`: Nucleus sampling parameter (0.8)

## Development

### Project Structure
```
llm-task/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Single-page application
├── chatpage_2.html         # Reference design
├── demo.gif                # Demo animation
└── README.md               # This file
```

### Adding New Entity Types
To support additional PII types, modify the entity filter in `backend/main.py`:

```python
if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "MONEY", "CARDINAL", "YOUR_NEW_TYPE"]:
```

### Customizing UI
The frontend uses a single HTML file with embedded CSS and JavaScript. Key customization points:
- Color schemes in CSS variables
- Animation timing and effects
- Layout breakpoints for responsive design

## Troubleshooting

### Common Issues

**1. spaCy Model Not Found**
```bash
python -m spacy download en_core_web_sm
```

**2. Ollama Connection Error**
- Ensure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Pull the model if missing: `ollama pull llama3.2`

**3. CORS Issues**
- The backend is configured to allow all origins for development
- For production, update the CORS settings in `main.py`

**4. Port Conflicts**
- Backend runs on port 8000 by default
- Frontend can be served on any available port
- Update the API URL in `frontend/index.html` if needed

### Performance Optimization

- **Caching**: Consider implementing Redis for entity caching
- **Model Loading**: spaCy model is loaded once at startup
- **Response Time**: Ollama responses typically take 2-5 seconds

## Security Considerations

- All processing happens locally
- No data is sent to external APIs
- Consider implementing rate limiting for production use
- Validate and sanitize all user inputs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is created for educational and interview purposes. Please check with the original authors for licensing terms.

## Acknowledgments

- **spaCy**: For excellent NLP capabilities
- **Ollama**: For local LLM inference
- **FastAPI**: For the robust backend framework
- **Design Inspiration**: Mac OS interface design principles

---

**Note**: This application is designed for demonstration purposes. For production use, consider additional security measures, error handling, and performance optimizations.
