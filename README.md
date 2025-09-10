# Flask Random Meme (Azure-ready)

A tiny Flask app that shows a random meme. It first tries the public **Meme API** and, if unavailable, generates a simple meme locally using Pillow. Designed to run locally and deploy easily to **Azure App Service (Linux)**.

## Features
- `/` – HTML page that displays a random meme with a button for the next one.
- `/meme` – JSON endpoint returning `{ title, url, source }` (where `url` is an external image URL or a base64 data URL for locally generated fallback).

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```

## Azure deployment options

### Option A – Quick deploy from your terminal (creates resources & deploys)
1. Install the Azure CLI and sign in:
   ```bash
   az login
   ```
2. From the project folder, run (choose a unique app name):
   ```bash
   az webapp up --runtime PYTHON:3.11 --sku B1 --name <your-unique-app-name>
   ```
   This command provisions an App Service plan and a web app and deploys your code. Subsequent runs will redeploy changes.

> Notes
> - Azure’s Python build engine (Oryx) automatically creates a virtual environment and runs `pip install -r requirements.txt` on deploy. Keep **requirements.txt** in the project root.
> - For standard Flask layouts where your entry file is `app.py` and the app object is named `app`, **no custom startup command** is needed. Azure will run Gunicorn for you.

### Option B – Continuous deployment with GitHub Actions
1. Push this project to a GitHub repository.
2. Create an App Service web app (once) using the Azure portal or `az webapp up` as above.
3. Add the following repository secret in GitHub: `AZURE_CREDENTIALS_GITHUB_SECRET` containing your Azure service principal JSON.
4. Commit the workflow at `.github/workflows/azure-webapp.yml` (included in this project). It builds and deploys on every push to `main`.

### Optional – Custom startup
If you want to customize Gunicorn (workers, threads, etc.), set a **Startup Command** in your App Service configuration, e.g.:
```
gunicorn --bind=0.0.0.0:8000 --workers=2 --threads=4 app:app
```

## Project structure
```
flask-random-meme-azure/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── .github/
    └── workflows/
        └── azure-webapp.yml
```

## License
MIT (for this project). External memes are loaded from public sources; respect their terms of use.
