from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import logging
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="PII Detection API", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise HTTPException(status_code=500, detail="Gemini API key not configured")

genai.configure(api_key=GEMINI_API_KEY)
# Using Gemini 2.0 Flash - newer stable model (January 2025)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the spaCy model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded successfully")
except OSError:
    logger.error("spaCy model not found. Please install it with: python -m spacy download en_core_web_sm")
    raise HTTPException(status_code=500, detail="spaCy model not available")

# Finish reason constants for Gemini API
FINISH_REASON_SAFETY = 2
FINISH_REASON_RECITATION = 3

# Define the data model for the request  
class MessageRequest(BaseModel):
    text: str

def get_entity_confidence(ent, doc):
    """Calculate confidence based on entity properties"""
    base_confidence = 0.75
    
    # Entity type reliability
    type_confidence = {
        "PERSON": 0.9,
        "ORG": 0.85, 
        "GPE": 0.88,
        "DATE": 0.82,
        "MONEY": 0.90,
        "CARDINAL": 0.70,
        "PERCENT": 0.85,
        "TIME": 0.80,
        "PHONE": 0.95,
        "EMAIL": 0.95
    }
    
    # Length-based confidence boost
    length_factor = min(len(ent.text.split()) * 0.05, 0.15)
    
    # Context confidence
    context_factor = 0.05 if ent.start > 0 and ent.end < len(doc) else 0.0
    
    final_confidence = (
        base_confidence * 
        type_confidence.get(ent.label_, 0.7) + 
        length_factor + 
        context_factor
    )
    
    return min(final_confidence, 0.98)

@app.post("/analyze")
async def analyze_text(request: MessageRequest):
    text = request.text
    logger.info(f"Analyzing text: {text[:100]}...")
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract entities with confidence scores
    entities = []
    entity_map = {}
    sanitized_text = text
    
    for ent in doc.ents:
        confidence = get_entity_confidence(ent, doc)
        
        # Only include entities with confidence > 60%
        if confidence > 0.6:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": round(confidence, 2)
            })
            
            # Create placeholder for sanitization
            placeholder = f"[{ent.label_.title()}]" if ent.label_ != "PERSON" else "[Name]"
            if ent.label_ == "ORG":
                placeholder = "[Company]"
            elif ent.label_ == "GPE":
                placeholder = "[Location]"
            elif ent.label_ in ["PHONE", "CARDINAL"]:
                placeholder = "[Phone]" if "phone" in ent.text.lower() or len(ent.text.replace("-", "").replace(" ", "")) > 7 else "[Number]"
            
            # Replace in sanitized text
            sanitized_text = sanitized_text.replace(ent.text, placeholder)
            entity_map[placeholder] = ent.text
    
    logger.info(f"Found {len(entities)} entities")
    logger.info(f"Sanitized text: {sanitized_text}")
    
    # Generate AI response using Gemini
    prompt = f"""
    Please rewrite the following text to be more privacy-friendly by removing or generalizing any personal information, while maintaining the overall meaning and tone. The text may contain placeholders like [Name], [Company], [Location], etc. where personal information was detected.

    Original text: {sanitized_text}

    Please provide a rewritten version that:
    1. Maintains the original intent and tone
    2. Removes or generalizes personal information
    3. Sounds natural and professional
    4. Is concise (under 100 words)

    Rewritten text:
    """
    
    try:
        # Generate response using Gemini with safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=100,
                top_p=0.8
            ),
            safety_settings=safety_settings
        )
        
        # Check if response was blocked
        if response.candidates and response.candidates[0].finish_reason == FINISH_REASON_SAFETY:
            ai_text = "Response was blocked by safety filters. Please try rephrasing your text."
            logger.warning("Gemini response blocked by safety filter")
        elif response.candidates and response.candidates[0].finish_reason == FINISH_REASON_RECITATION:
            ai_text = "Response was blocked due to recitation. Please try with different text."
            logger.warning("Gemini response blocked due to recitation")
        elif response.text:
            ai_text = response.text.strip()
            
            # Simple cleanup - remove quotes if present
            if ai_text.startswith('"') and ai_text.endswith('"'):
                ai_text = ai_text[1:-1]
            
            logger.info(f"Gemini Response: {ai_text}")
        else:
            ai_text = "No response generated. Please try again."
            logger.warning("Empty response from Gemini")
            
    except Exception as e:
        if "API_KEY" in str(e):
            ai_text = "Gemini API key not configured or invalid"
        elif "quota" in str(e).lower():
            ai_text = "Gemini API quota exceeded"
        else:
            ai_text = f"Gemini API error: {str(e)}"
        logger.error(f"Gemini API error: {e}")
    
    return {
        "entities": entities,
        "ai_response": ai_text,
        "original_text": text,
        "sanitized_text": sanitized_text
    }

@app.get("/health")
async def health_check():
    try:
        # Test spaCy
        spacy_status = nlp is not None
        
        # Test Gemini API key
        gemini_status = GEMINI_API_KEY is not None
        
        return {
            "status": "healthy",
            "spacy_loaded": spacy_status,
            "gemini_configured": gemini_status,
            "model": "gemini-2.0-flash"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/")
async def root():
    return {
        "message": "PrivChat PII Detection API", 
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }
    
if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable from Render, fallback to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)