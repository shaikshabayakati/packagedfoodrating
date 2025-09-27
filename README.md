# Packaged Food Rating (Nutrition Score Scanner)

A simple Flask web app that scans a product barcode from an image, fetches its nutrition facts from OpenFoodFacts, and generates a health score (0–100) plus a plain‑English explanation using Google Gemini via LangChain.

## Features

- Upload a product photo; auto-detects barcode (EAN-13, EAN-8, UPC-A, UPC-E)
- Manual barcode entry fallback if scanning fails
- Fetches nutrition data from OpenFoodFacts API
- AI-generated nutrition score and explanation using Gemini (LangChain)
- Clean, minimal UI; returns JSON for API use as well

## Architecture (high level)

- Browser UI → Flask backend (`app.py`)
- Image processing + barcode decode (`barcode_scanner.py`, PIL + pyzbar + zbar)
- Nutrition facts from OpenFoodFacts
- Scoring with Gemini (LangChain) in `nutrition_analyzer.py`
- Utility helpers in `utils.py`

```
[Image/Barcode] → [pyzbar + zbar] → [OpenFoodFacts] → [Gemini scoring] → [Score + Comment]
```

## Prerequisites

- Python 3.10+
- Recommended: Conda (for easy zbar install on Windows)
- Git (to clone the repo)
- A Google Generative AI API key (set as `GOOGLE_API_KEY`)

## Quick start (Conda: recommended on Windows)

```powershell
# 1) Clone
git clone https://github.com/shaikshabayakati/packagedfoodrating.git
cd packagedfoodrating

# 2) Create & activate env (installs Python, pillow, pyzbar, zbar, requests)
conda env create -f environment.yml
conda activate barcode-scan

# 3) Install app/runtime dependencies (Flask + LangChain + Pydantic)
pip install flask langchain-google-genai langchain-core pydantic

# 4) Set your Google Generative AI API key
# Current PowerShell session only:
$env:GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
# or persist for your Windows user profile:
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY","YOUR_API_KEY_HERE","User")

# 5) Run the app
python app.py
# Open http://127.0.0.1:5000 in your browser
```

### Alternative: pip/venv (you must install zbar yourself)

If you prefer venv/pip, you need the zbar native library available on your system (common error: `ImportError: Unable to find zbar shared library`). On Windows, the simplest path is using Conda above. If you continue with pip:

```powershell
# Create venv
python -m venv .venv ; .\.venv\Scripts\Activate.ps1

# Install Python packages
pip install flask pillow pyzbar requests langchain-google-genai langchain-core pydantic

# Install zbar (native)
# - Windows: install via Conda (recommended) or a prebuilt binary and ensure it is on PATH
# - macOS (Homebrew): brew install zbar
# - Linux (Debian/Ubuntu): sudo apt-get install -y zbar-tools libzbar0

# Run
$env:GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
python app.py
```

## Usage

- Web UI: Upload a product image containing a barcode. If scan fails, enter a barcode manually.
- Programmatic API: See endpoints below.

### Endpoints

- `GET /` — Serves the web UI
- `POST /analyze` — Analyze an uploaded image
  - Content-Type: `multipart/form-data`
  - Form field: `image`
  - Response: `{"score": number, "comment": string, "details": object|string}`
- `POST /analyze_barcode` — Analyze a barcode directly
  - Content-Type: `application/json`
  - Body: `{ "barcode": "<digits>" }`
  - Response: `{"score": number, "comment": string, "details": object|string}`

#### cURL examples

```powershell
# Image upload
curl -X POST https://localhost:5000/analyze -F "image=@sample7.png"

# Manual barcode
curl -X POST https://localhost:5000/analyze_barcode ^
  -H "Content-Type: application/json" ^
  -d "{\"barcode\":\"737628064502\"}"
```

### Response shape (example)

```json
{
  "score": 78,
  "comment": "Good protein, low sugar, moderate sodium. Consider portion control.",
  "details": {
    "energy-kcal_serving": 180,
    "proteins_serving": 12,
    "sugars_serving": 4,
    "fiber_serving": 5,
    "fat_serving": 7,
    "sodium_serving": 350
  }
}
```

## Repo structure

```
packagedfoodrating/
├─ app.py                      # Flask app (routes: /, /analyze, /analyze_barcode)
├─ barcode_scanner.py          # Image decode + OpenFoodFacts integration
├─ nutrition_analyzer.py       # AI scoring with LangChain + Gemini
├─ utils.py                    # Text cleanup + upload validation
├─ templates/
│  └─ nutrition_score.html     # Minimal UI
├─ environment.yml             # Conda env (Python, pillow, pyzbar, zbar, requests)
├─ sample3.webp                # Sample image(s)
├─ sample7.png                 # Sample image(s)
└─ README.md                   # This file
```

## Configuration

- Google API key: Set `GOOGLE_API_KEY` in your environment. The current code includes a fallback key in `nutrition_analyzer.py` for experimentation only; you should remove that and use your own key for security and rate‑limit reasons.
- Port: The app runs on port 5000 by default. Adjust in `app.py` if needed.

## Troubleshooting

- `ImportError: Unable to find zbar shared library`
  - Use the Conda setup above (installs `zbar` automatically on Windows), or install the native zbar package for your OS and ensure it is on PATH.
- OpenFoodFacts 404 or missing data
  - Some barcodes/products lack nutrition facts. Try a different item or enter a different barcode.
- Blank score/comment
  - Ensure `GOOGLE_API_KEY` is set and valid; check your network.

## Security notes

- Do not commit API keys. Prefer environment variables or a `.env` file with a proper `.gitignore`.
- Consider removing the fallback API key in `nutrition_analyzer.py` before pushing public code.

## Roadmap / ideas

- Cache OpenFoodFacts results to reduce API calls
- Add explicit unit tests for parsing and scoring
- Display more nutrition details in the UI
- Containerize with Docker

## Acknowledgements

- [OpenFoodFacts](https://world.openfoodfacts.org/) — open product database and API
- Google Generative AI (Gemini) — for scoring via LangChain

## License

Add a license (e.g., MIT) if you plan to open‑source contributions.
