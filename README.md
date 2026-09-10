# Campus Findr

College Campus Lost & Found System — B.Tech CSE 3rd Semester Project.

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

## Deploy to Vercel

1. Push this project to a GitHub repository.
2. Go to [vercel.com](https://vercel.com) → **New Project** → Import your GitHub repo.
3. Vercel auto-detects `vercel.json` — just click **Deploy**.
4. Your app will be live at `https://your-project.vercel.app`.

> **Note:** Vercel uses serverless functions with an ephemeral filesystem.
> The SQLite database is recreated with seed data on each cold start.
> For a persistent production deployment, consider Render or PythonAnywhere.
