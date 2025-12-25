# Domo Card Annotations Manager

A Streamlit app to add and delete annotations on Domo cards.

## Features

- 🔍 **Load Card** - Enter a card ID to view its annotations
- ➕ **Add Annotation** - Add new annotations with text, date, and color
- 🗑️ **Delete Annotation** - Remove existing annotations
- 📋 **View Annotations** - See all annotations in a table

## Deployment to Streamlit Cloud

### Step 1: Create GitHub Repository

1. Create a new repository on GitHub
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`

**⚠️ DO NOT upload `secrets.toml` or any file containing your token!**

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

1. In Streamlit Cloud, go to your app's settings
2. Click "Secrets" in the left sidebar
3. Add the following (replace with your values):

```toml
[domo]
instance = "keshet-tv"
developer_token = "YOUR_DOMO_DEVELOPER_TOKEN"
```

4. Click "Save"

### Step 4: Get Your Domo Developer Token

1. Log in to Domo
2. Go to **Admin** → **Authentication** → **Access tokens**
3. Click **Generate access token**
4. Copy the token (it's only shown once!)
5. Paste it in the Streamlit Cloud secrets

## Local Development

1. Clone the repository
2. Create `.streamlit/secrets.toml`:

```toml
[domo]
instance = "keshet-tv"
developer_token = "YOUR_TOKEN"
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
streamlit run app.py
```

## Files

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files to exclude from Git |
| `secrets.toml.example` | Example secrets structure (for reference) |

## Security Notes

- Never commit your developer token to GitHub
- Use Streamlit Cloud secrets for sensitive configuration
- Rotate your Domo token periodically
- The token gives access to modify cards - share the app URL carefully
