import os
import pickle
import numpy as np
from urllib.parse import urlparse
import requests
import urllib3
from .features import url_features_extraction

# Disable insecure request warnings when bypassing SSL verification.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables for caching
_MODEL = None
_KNOWN_URL_LABELS = {}
_KNOWN_DOMAIN_LABELS = {}
_DATASET_LOADED = False

def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'phishing_model.pkl')
    
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                _MODEL = pickle.load(f)
            return _MODEL
        except Exception as e:
            print(f"Error loading model: {e}")
    return None

def _normalize_url_for_lookup(url: str) -> str:
    if not url:
        return ""
    working = url.strip()
    if not working.startswith(("http://", "https://")):
        working = f"http://{working}"
    parsed = urlparse(working)
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":", 1)[0]
    path = parsed.path or ""
    normalized = f"{host}{path}".rstrip("/")
    return normalized

def _extract_domain(url: str) -> str:
    if not url:
        return ""
    working = url.strip()
    if not working.startswith(("http://", "https://")):
        working = f"http://{working}"
    parsed = urlparse(working)
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":", 1)[0]
    return host

def _load_resource_data() -> None:
    global _DATASET_LOADED
    if _DATASET_LOADED:
        return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_root, "phishing_url_dataset_unique.csv")
    if not os.path.exists(dataset_path):
        _DATASET_LOADED = True
        return

    import csv
    try:
        with open(dataset_path, "r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                raw_url = (row.get("url") or "").strip()
                raw_label = (row.get("label") or "").strip()
                if not raw_url or raw_label not in {"0", "1"}:
                    continue

                label = int(raw_label)
                normalized = _normalize_url_for_lookup(raw_url)
                domain = _extract_domain(raw_url)
                if normalized:
                    _KNOWN_URL_LABELS[normalized] = label
                if domain and domain not in _KNOWN_DOMAIN_LABELS:
                    _KNOWN_DOMAIN_LABELS[domain] = label
    except Exception as e:
        print(f"Error loading dataset: {e}")

    _DATASET_LOADED = True

def _lookup_in_resources(url: str):
    _load_resource_data()
    normalized = _normalize_url_for_lookup(url)
    domain = _extract_domain(url)

    if normalized in _KNOWN_URL_LABELS:
        return _KNOWN_URL_LABELS[normalized], "Exact URL match in dataset"

    if domain in _KNOWN_DOMAIN_LABELS:
        return _KNOWN_DOMAIN_LABELS[domain], "Domain match in dataset"

    return None, "No dataset match"

def analyze_website(url: str):
    """
    Detection strategy:
    1) Check local resource dataset first (known phishing/safe URLs).
    2) If not found, use the AI Random Forest model.
    3) Supplementary check: real-time reachability.
    """
    features_dict = {
        "URL Length": len(url),
        "Source": "AI Engine"
    }

    # 1. Dataset Lookup
    label, source_detail = _lookup_in_resources(url)
    if label is not None:
        prediction = "Phishing" if label == 1 else "Safe"
        confidence = 99.0
        features_dict.update({
            "Source": source_detail,
            "Detection": "Dataset Match",
            "Result": prediction
        })
        return prediction, confidence, features_dict

    # 2. AI Model Prediction
    model = _load_model()
    if model:
        try:
            # Extract features for the model
            feature_vector = url_features_extraction(url)
            # Reshape for single sample prediction
            features_np = np.array(feature_vector).reshape(1, -1)
            
            prediction_idx = model.predict(features_np)[0]
            probabilities = model.predict_proba(features_np)[0]
            
            prediction = "Phishing" if prediction_idx == 1 else "Safe"
            confidence = round(float(probabilities[prediction_idx]) * 100, 2)
            
            features_dict.update({
                "Source": "Random Forest AI",
                "Dots Count": feature_vector[1],
                "Subdomains": feature_vector[22],
                "Security": "HTTPS" if feature_vector[19] else "No HTTPS",
                "IP Check": "IP Address Found" if feature_vector[21] else "No IP Address",
                "Result": prediction
            })
            return prediction, confidence, features_dict
        except Exception as e:
            print(f"AI Prediction Error: {e}")

    # 3. Fallback: Reachability check
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }
        # Use a short timeout for the fallback
        response = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
        prediction = "Safe"
        confidence = 70.0 # Lower confidence for fallback
        features_dict.update({
            "Source": "Reachability Fallback",
            "Status": f"Online ({response.status_code})",
            "Result": "Safe (Accessible)"
        })
        return prediction, confidence, features_dict
    except requests.RequestException:
        prediction = "Phishing"
        confidence = 75.0
        features_dict.update({
            "Source": "Reachability Fallback",
            "Status": "Offline / Unreachable",
            "Result": "Phishing (Likely Dead Link)"
        })
        return prediction, confidence, features_dict
