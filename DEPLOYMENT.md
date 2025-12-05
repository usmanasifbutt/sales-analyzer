# Deployment Guide

## Option 1: Streamlit Cloud (Recommended - Free & Easy)

### Steps:

1. **Create a GitHub Repository**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/sales-analyzer.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**

   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Your app is live!** 🎉
   - URL will be: `https://YOUR_APP_NAME.streamlit.app`
   - No server management needed
   - Free tier available

## Option 2: CodeSandbox

1. Go to https://codesandbox.io
2. Create a new sandbox
3. Upload your files
4. In the terminal, run:
   ```bash
   pip install streamlit
   streamlit run app.py
   ```
5. Use the port forwarding feature to access the app

## Option 3: Replit

1. Create a new Repl
2. Upload files
3. In the shell, run:
   ```bash
   pip install streamlit
   streamlit run app.py --server.port=8501
   ```
4. Use Replit's webview

## Option 4: Railway (Free Tier)

1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub
4. Add environment variable: `PORT=8501`
5. Set start command: `streamlit run app.py --server.port=$PORT`

## Option 5: Render (Free Tier)

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

## Files Needed for Deployment

- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration (optional)
- `README.md` - Documentation (optional)

## Testing Locally

Before deploying, test locally:

```bash
pip install streamlit
streamlit run app.py
```

Then open http://localhost:8501 in your browser.
