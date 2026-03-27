# 🌌 Astronomia: AI Phishing URL Detector

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=YOUR_GITHUB_REPO_HERE)

> **One-Click Deploy**: Replace `YOUR_GITHUB_REPO_HERE` with your actual GitHub link in `README.md` to enable the button above!

---

## Project Structure 📂
-   **`backend/`**: Contains the AI model, feature extraction logic, and FastAPI server.
    -   `main.py`: The FastAPI application.
    -   `features.py`: URL feature extraction algorithms.
    -   `train_model.py`: Script to train and save the `RandomForest` model.
-   **`frontend/`**: Contains the modern user interface.
    -   `index.html`: Dashboard structure.
    -   `styles.css`: Glassmorphism and animations.
    -   `script.js`: Frontend logic and backend integration.
-   **`run.py`**: A one-click script to train the model and start the entire system.

## Getting Started 🚀

### 1. Installation
Install the required dependencies using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 2. Running the System
Simply run the root-level `run.py` script:
```bash
python run.py
```
This script will:
1.  Automatically train the AI model if it's the first time you're running it.
2.  Start the FastAPI backend on `http://localhost:8000`.
3.  Open the modern dashboard in your default browser.

### 3. Usage
1.  Enter a URL in the dashboard input field (e.g., `http://verify-microsoft-security.com/login`).
2.  Click **"Check Now"**.
3.  View the detailed AI analysis, probability of phishing, and feature breakdown.

## Tech Stack 🛠️
-   **Backend**: Python, FastAPI, Scikit-Learn, Pandas, Numpy, TLDextract
-   **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+), FontAwesome for icons, Google Fonts (Outfit)

---
*Stay Safe Online!* 🛡️
