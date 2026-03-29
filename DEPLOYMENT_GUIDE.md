# AI Phishing URL Detector - Global Deployment Guide

To deploy your project to the public internet for free, please follow these exact steps.

## Part 1: Push to GitHub 🚀

1.  **Create a Repository**: Go to [GitHub](https://github.com/new) and create a new repository called `ai-phishing-detector`.
2.  **Initialize Git**: Open your terminal in `d:/Projects/AI based phishing url detector` and run:
    ```bash
    git init
    git add .
    git commit -m "Initial commit of Astronomia Phishing Detector"
    git branch -M main
    ```
3.  **Connect & Push**: Replace `YOUR_USERNAME` with your real GitHub username:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/ai-phishing-detector.git
    git push -u origin main
    ```

---

## Part 2: Deploy Backend to Render.com ☁️

1.  Go to **[Render.com](https://dashboard.render.com/)** and log in with GitHub.
2.  Click **New +** > **Web Service**.
3.  Connect the `ai-phishing-detector` repository you just pushed.
4.  **Settings**:
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt` (We skip training during build to save memory)
    - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5.  Click **Deploy Web Service**.
6.  **Copy the URL**: Once it is "Live", copy the URL (e.g., `https://ai-phishing-detector.onrender.com`).

---

## Part 3: Update Frontend Link 🌌

1.  Open **[script.js](file:///d:/Projects/AI%20based%20phishing%20url%20detector/frontend/script.js)**.
2.  Change line 35 from `http://127.0.0.1:8000` to your **Render URL** from the previous step.
3.  **Push the update**:
    ```bash
    git add frontend/script.js
    git commit -m "Update API URL for deployment"
    git push origin main
    ```

---

## Part 4: Deploy Frontend to Vercel/GitHub Pages ✨

1.  **Vercel (Recommended)**: Go to [Vercel](https://vercel.com/new), import your GitHub repo.
2.  **Settings**: Set the "Root Directory" to `frontend`.
3.  Click **Deploy**.

**You now have a globally accessible AI Phishing URL Detector!** 🛡️✨
