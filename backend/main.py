from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import re
from .analyzer import analyze_website
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="AI Phishing URL Detector API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins including file://
    allow_credentials=False, # Must be False if allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
frontend_dir = os.path.join(project_root, 'frontend')

class URLRequest(BaseModel):
    url: str

class PredictionResponse(BaseModel):
    url: str
    prediction: str
    probability: float
    features: dict

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: URLRequest):
    # Clean the URL input
    raw_url = request.url.strip()
    processed_url = raw_url if raw_url.startswith(("http://", "https://")) else "http://" + raw_url
        
    # Extract features using the standardized function
    prediction, probability, features_dict = analyze_website(processed_url)
    
    return {
        "url": processed_url,
        "prediction": prediction,
        "probability": probability,
        "features": features_dict
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Phishing detection API is running"}

# Serve Frontend
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, 'index.html'))
    
    # Catch-all for other frontend files
    @app.get("/{path:path}")
    async def serve_any_file(path: str):
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, 'index.html'))

@app.post("/predict-file")
async def predict_file(file: UploadFile = File(...)):    
    content = await file.read()
    text = content.decode('utf-8', errors='ignore')
    
    # Improved regex to find URLs with or without http/www
    url_pattern = r'(?:https?://|www\.)(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        return {"results": [], "summary": {"total": 0, "phishing": 0, "safe": 0}}
    
    results = []
    phish_count = 0
    
    # Deduplicate and limit to top 50 to avoid timeout
    unique_urls = list(set(urls))[:50]
    
    for url in unique_urls:
        # Ensure scheme for extraction
        if not url.startswith("http"):
            url = "http://" + url
            
        prediction, probability, features_dict = analyze_website(url)
        
        if prediction == "Phishing":
            phish_count += 1
            
        results.append({
            "url": url,
            "prediction": prediction,
            "probability": probability
        })
        
    return {
        "results": results,
        "summary": {
            "total": len(results),
            "phishing": phish_count,
            "safe": len(results) - phish_count
        }
    }
