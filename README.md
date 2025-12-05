# Sales Data Analyzer

A web application for analyzing sales data grouped by shop and product code.

## Features

- 📤 Upload CSV files
- 🔄 Process data in memory (no file storage)
- 📊 Group sales by branch and product
- 📥 Download processed results as CSV
- ✅ Filter by allowed branches
- 🔍 Preview summary statistics

## Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Deployment to Streamlit Cloud (Free)

1. **Push to GitHub:**

   - Create a new repository on GitHub
   - Push this code to the repository

2. **Deploy to Streamlit Cloud:**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set main file path to: `app.py`
   - Click "Deploy"

3. **Your app will be live!** 🎉

## Alternative: Deploy to Other Platforms

### Replit

- Create a new Repl
- Upload files
- Run `streamlit run app.py`
- Use Replit's webview

### CodeSandbox

- Create a new sandbox
- Install streamlit: `pip install streamlit`
- Run: `streamlit run app.py`
- Use port forwarding

### Railway / Render

- Create a new web service
- Set build command: `pip install -r requirements.txt`
- Set start command: `streamlit run app.py --server.port=$PORT`
- Deploy!

## Configuration

Edit `ALLOWED_BRANCHES` in `app.py` to change which branches are processed:

```python
ALLOWED_BRANCHES = [
    'AWAISIA',
    'BAHRIA TOWN',
    'IQBAL TOWN',
    'JOHAR TOWN PHARMACY'
]
```

## File Format

The CSV file should have the following columns:

- Shop
- Receipt
- Customer Name
- Product Code
- Product Name
- Retail Price
- Quantity
- Sales + Tax
