

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
cp .env.example .env
# Add your Gemini API key in .env file
python main.py
```

Open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---
**Files**
- `main.py` → Flask backend
- `src/index.html` → frontend form
- `requirements.txt` → dependencies
- `.env.example` → environment variable template
