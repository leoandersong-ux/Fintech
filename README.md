# Zambia Digital Lending Ops Radar

Personal public-source research platform for tracking Zambia digital-lending operations signals.

This Streamlit app is for market understanding and capability-building. It is not legal advice, a regulatory conclusion, a customer deliverable, or a commercial compliance engine.

## Streamlit Deploy

Use these settings in Streamlit Community Cloud:

- Repository: `leoandersong-ux/Fintech`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python dependencies: `requirements.txt`
- Python runtime: `runtime.txt` pins Python 3.12 so binary wheels such as `pyarrow` install cleanly.

## Local Run

```powershell
& '.\.venv-lending\Scripts\streamlit.exe' run .\streamlit_app.py --server.port 8501
```

## Main Commands

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py source-health
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\brief_generator.py --week current
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\competitor_matrix.py
```

## Included Data

The checked-in SQLite database and generated briefs contain reviewed public-source monitoring records only. Do not add private borrower data, logged-in pages, private social groups, employer-internal information, or paywalled/CAPTCHA sources.
