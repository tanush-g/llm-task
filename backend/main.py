from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import requests

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define the data model for the request
class MessageRequest(BaseModel):
    text: str
    
@app.post("/analyze")
async def analyze_text(request: MessageRequest):
    text = request.text
    
    # Find personal information
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "confidence": 0.9  # Placeholder confidence for now
        })

    print(f"Found entities: {entities}")
    
    # Send to Deepseek llm model running via ollama
    try:
        ai_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1",
                "prompt": f"Analyze the following text for personal information:\n\n{text}\n\nEntities found: {entities}",
                "stream": False
            },
            timeout=30
        )
        
        if ai_response.status_code == 200:
            ai_text = ai_response.json().get("response", "AI unavailable")
        else:
            ai_text = "AI unavailable"
            
    except Exception as e:
        print(f"Error calling AI model: {e}")
        ai_text = "AI unavailable"

    # Return the results
    return {
        "entities": entities,
        "ai_response": ai_text,
        "original_text": text
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)