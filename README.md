# KeyPath Replay — Simple Python + Streamlit Project

A beginner-friendly prototype based on the KeyPath Replay / CRIMEATHON 2026 case presentation.

## Included features
1. Overview of the project
2. CSV/JSON evidence upload and basic column checks
3. Sample integration key profile review
4. Safe synthetic replay with mock actions
5. Proof pack export as CSV and JSON

## Safety
The replay is synthetic and local only. It does not send requests to real APIs, connect to company systems, or use real credentials. Uploaded evidence files are displayed for review and are not modified. Missing evidence is labelled UNKNOWN, not treated as proof.

The case presentation refers to a separate E01–E20 evidence package. This simple project does not include those real case files. Use only authorized evidence copies.

## Installation
Open a terminal in this folder and run:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the app:
```bash
streamlit run app.py
```

## Project files
- `app.py` — complete Streamlit application
- `requirements.txt` — required Python packages
- `sample_data/` — small fabricated CSV examples for testing
