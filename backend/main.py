from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import requests
import logging

# Initialize FastAPI app
app = FastAPI(title="PII Detection API", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "GPE": 0.88,  # Geopolitical entities (locations)
        "DATE": 0.82,
        "MONEY": 0.90,
        "CARDINAL": 0.70,  # Numbers
        "PERCENT": 0.85,
        "TIME": 0.80,
        "PHONE": 0.95,  # Custom for phone numbers
        "EMAIL": 0.95   # Custom for emails
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
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Find personal information using spaCy
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        # Filter for PII-relevant entity types
        if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "MONEY", "CARDINAL", "PHONE_NUMBER"]:
            confidence = get_entity_confidence(ent, doc)
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "confidence": round(confidence, 2),
                "start": ent.start_char,
                "end": ent.end_char
            })

    logger.info(f"Found entities: {[(ent['text'], ent['label']) for ent in entities]}")
    
    # Send to simple Llama model
    try:
        # Create sanitized version
        sanitized_text = text
        for ent in entities:
            placeholder = f"[{ent['label']}]"
            sanitized_text = sanitized_text.replace(ent['text'], placeholder)
        
        # Simple prompt for Llama 3.2
        prompt = f"You are a cybersecurity expert powering a secure chat application. Your job is to paraphrase this sanitized text professionally while keeping the meaning, the context, and the user's intent intact: {sanitized_text}"

        ai_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",  # Simpler model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 100  # Limit response length
                }
            },
            timeout=30
        )
        
        if ai_response.status_code == 200:
            ai_text = ai_response.json().get("response", "AI response unavailable")
            logger.info(f"LLM Response: {ai_text}")
        else:
            ai_text = f"AI service error (Status: {ai_response.status_code})"
            
    except requests.exceptions.ConnectionError:
        ai_text = "AI service unavailable - please ensure Ollama is running"
        logger.error("Failed to connect to Ollama API")
    except requests.exceptions.Timeout:
        ai_text = "AI service timeout"
        logger.error("Ollama API request timed out")
    except Exception as e:
        ai_text = f"AI service error: {str(e)}"
        logger.error(f"Unexpected error: {e}")

    return {
        "entities": entities,
        "ai_response": ai_text,
        "original_text": text,
        "sanitized_text": sanitized_text if entities else text
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "spacy_loaded": nlp is not None
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)