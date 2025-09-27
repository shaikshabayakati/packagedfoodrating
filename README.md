# 🍎 Packaged Food Rating (Nutrition Score Scanner)

A comprehensive Flask web application that analyzes packaged food nutrition through multiple scanning methods. Upload product images, scan live with your camera, or enter barcodes manually to get AI-powered nutrition scores (0-100) with detailed health insights.

## ✨ Features

### 📸 Multiple Scan Methods
- **Image Upload**: Upload product photos with automatic barcode detection
- **Live Camera Scan**: Real-time barcode scanning with auto-stop functionality  
- **Manual Entry**: Direct barcode input for quick analysis

### 🤖 AI-Powered Analysis
- **Smart Nutrition Scoring**: 0-100 scale based on comprehensive health criteria
- **Detailed Explanations**: Plain-English health insights using Google Gemini AI
- **Real-time Processing**: Instant analysis with OpenFoodFacts database integration

### 💻 User Experience
- **Clean, Responsive UI**: Modern interface optimized for all devices
- **Auto-Detection**: Supports EAN-13, EAN-8, UPC-A, UPC-E barcode formats
- **Error Handling**: Graceful fallbacks and clear user guidance
- **JSON API**: RESTful endpoints for programmatic access

## 🏗️ Architecture

The application follows a modular architecture for maintainability and scalability:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│ OpenFoodFacts   │
│  (HTML/JS UI)   │    │    (app.py)      │    │      API        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌───────────┐ ┌─────────┐ ┌──────────┐
            │  Barcode  │ │Nutrition│ │   Utils  │
            │ Scanner   │ │Analyzer │ │ Helper   │
            │(pyzbar)   │ │(Gemini) │ │Functions │
            └───────────┘ └─────────┘ └──────────┘
                    ▲
            ┌───────────────┐
            │ Camera Module │
            │  (OpenCV)     │
            └───────────────┘
```

### 🔧 Core Components

- **`app.py`** - Flask web server with REST API endpoints
- **`barcode_scanner.py`** - Image processing and OpenFoodFacts integration  
- **`nutrition_analyzer.py`** - AI-powered nutrition scoring with LangChain + Gemini
- **`utils.py`** - Text processing and validation utilities
- **`opencv_auto_stop.py`** - Live camera barcode scanning with auto-detection
- **`templates/nutrition_score.html`** - Responsive web interface

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Git** (to clone the repository)
- **Google Generative AI API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Webcam** (optional, for live scanning)

### 🐍 Installation

#### Option 1: Conda (Recommended for Windows)
```bash
# 1. Clone the repository
git clone https://github.com/shaikshabayakati/packagedfoodrating.git
cd packagedfoodrating

# 2. Create conda environment with dependencies
conda env create -f environment.yml
conda activate barcode-scan

# 3. Install additional Python packages
pip install flask langchain-google-genai langchain-core pydantic

# 4. Set your Google API key
# Windows PowerShell:
$env:GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
# or permanently:
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY","YOUR_KEY","User")

# Linux/Mac:
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"

# 5. Run the application
python app.py
```

#### Option 2: Virtual Environment (pip)
```bash
# 1. Clone and setup
git clone https://github.com/shaikshabayakati/packagedfoodrating.git
cd packagedfoodrating

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install flask pillow pyzbar requests opencv-python
pip install langchain-google-genai langchain-core pydantic

# 4. Install zbar (system dependency)
# Windows: Use conda or install prebuilt binaries
# macOS: brew install zbar  
# Ubuntu/Debian: sudo apt-get install libzbar0

# 5. Set API key and run
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
python app.py
```

### 🎯 Usage

1. **Start the application**: `python app.py`
2. **Open your browser**: Navigate to `http://localhost:5000`
3. **Choose your scanning method**:
   - **Upload Image**: Click "Choose File" and select a product image
   - **Live Camera**: Click "📷 Live Camera Scan" for real-time scanning
   - **Manual Entry**: If barcode detection fails, enter the barcode manually

## 📡 API Reference

The application provides RESTful endpoints for integration:

### Web Interface
- **`GET /`** - Serves the main web interface

### Image Analysis  
- **`POST /analyze`** - Analyze uploaded image with barcode
  - **Content-Type**: `multipart/form-data`
  - **Form field**: `image` (image file)
  - **Response**: `{"score": number, "comment": string, "details": string}`

### Direct Barcode Analysis
- **`POST /analyze_barcode`** - Analyze barcode directly
  - **Content-Type**: `application/json` 
  - **Body**: `{"barcode": "1234567890123"}`
  - **Response**: `{"score": number, "comment": string, "details": string}`

### Live Camera Scanning
- **`POST /start_live_scan`** - Start live camera scan (auto-stops on detection)
  - **Content-Type**: `application/json`
  - **Response**: `{"score": number, "comment": string, "details": string}` or `{"error": string}`

### 🧪 API Examples

#### Upload Image Analysis
```bash
curl -X POST http://localhost:5000/analyze \
  -F "image=@product_image.jpg"
```

#### Direct Barcode Analysis  
```bash
curl -X POST http://localhost:5000/analyze_barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode":"737628064502"}'
```

#### Live Camera Scan
```bash
curl -X POST http://localhost:5000/start_live_scan \
  -H "Content-Type: application/json"
```

### 📄 Response Format
```json
{
  "score": 78,
  "comment": "This product has good protein content (12g) and moderate calories (180). The sugar content is relatively low (4g), which is positive. However, watch the sodium levels (350mg). Overall, this is a decent choice for a balanced diet, but consider portion control due to moderate calorie density.",
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

## 📁 Project Structure

```
packagedfoodrating/
├── 📄 app.py                          # Flask web server & API routes
├── 🔍 barcode_scanner.py              # Image processing & OpenFoodFacts API
├── 🧠 nutrition_analyzer.py           # AI scoring with LangChain + Gemini  
├── 🛠️ utils.py                        # Text processing & validation utilities
├── 📷 opencv_auto_stop.py             # Live camera scanning (auto-detection)
├── 📷 opencv.py                       # Original camera script (manual)
├── 🧪 camera_test.py                  # Camera diagnostic utility
├── 🌐 templates/
│   └── 📄 nutrition_score.html        # Responsive web interface
├── 📦 environment.yml                 # Conda environment specification
├── 🖼️ sample3.webp                    # Sample test images
├── 🖼️ sample7.png                     # Sample test images  
├── 📖 README.md                       # This documentation
└── 📂 __pycache__/                    # Python bytecode cache
```

## 🏃‍♂️ Nutrition Scoring Algorithm  

The AI uses a comprehensive 100-point scoring system based on established nutritional guidelines:

### 📊 Scoring Breakdown

| **Category** | **Weight** | **Criteria** |
|--------------|------------|--------------|
| **Calories** | 20 points | Low (0-150): +20 → High (500+): 0 |
| **Protein** | 15 points | High (15g+): +15 → Low (0-2g): 0 |
| **Sugar** | 15 points | Low (0-5g): +15 → Very High (25g+): -10 |
| **Fiber** | 15 points | High (8g+): +15 → Low (0-1g): 0 |
| **Fat** | 10 points | Low (0-5g): +10 → Very High (25g+): -10 |
| **Sodium** | 10 points | Low (0-200mg): +10 → Very High (1200mg+): -10 |
| **Vitamins/Minerals** | 10 points | Rich: +10 → None listed: 0 |
| **Additives** | 5 points | Natural: +5 → Many artificial: -5 |

### 🎯 Bonus Points
- **Organic**: +5 points
- **Non-GMO**: +3 points  
- **Whole grains**: +5 points
- **Natural ingredients**: +3 points

### ⚠️ Penalty Points
- **Trans fats**: -15 points
- **High fructose corn syrup**: -10 points
- **Artificial colors/flavors**: -5 points

**Base Score**: 50 points | **Final Range**: 0-100 points

## ⚙️ Configuration

### 🔑 Environment Variables
- **`GOOGLE_API_KEY`** - Required. Your Google Generative AI API key
  - Get yours: [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Set via: `export GOOGLE_API_KEY="your-key-here"`

### 🚨 Security Notes
- **Never commit API keys** to version control
- Use environment variables or `.env` files with proper `.gitignore`
- Consider removing the fallback API key in `nutrition_analyzer.py` for production
- For production deployment, use a WSGI server (not Flask dev server)

### 🔧 Application Settings
- **Port**: Default `5000` (change in `app.py`)
- **Max file size**: 16MB (configurable in `app.py`)
- **Camera timeout**: 120 seconds for live scanning
- **Supported formats**: JPG, PNG, GIF, BMP, WebP

### 🎛️ Camera Configuration
The live scanner automatically tries multiple camera backends:
1. **DirectShow (CAP_DSHOW)** - Primary Windows backend
2. **Microsoft Media Foundation (CAP_MSMF)** - Secondary Windows backend  
3. **CAP_ANY** - Fallback for other systems

## 🛠️ Troubleshooting

### 🎥 Camera Issues

**"Unable to access webcam" / "Camera not found"**
- ✅ **Windows**: Settings → Privacy & Security → Camera → Allow apps and desktop apps
- ✅ **Close competing apps**: Teams, Zoom, OBS, browser tabs using camera
- ✅ **Update drivers**: Device Manager → Cameras → Update driver
- ✅ **Try different USB port** (for external webcams)
- ✅ **Run camera test**: `python camera_test.py`

**"ImportError: Unable to find zbar shared library"**
- ✅ **Windows**: Use conda installation (installs zbar automatically)
- ✅ **macOS**: `brew install zbar`
- ✅ **Ubuntu/Debian**: `sudo apt-get install libzbar0 zbar-tools`
- ✅ **Alternative**: `pip install pyzbar[scripts]`

### 🔍 Barcode Detection Issues

**"No barcode found in image"**
- ✅ **Image quality**: Ensure good lighting and focus
- ✅ **Barcode visibility**: Check barcode isn't damaged or obscured
- ✅ **Supported formats**: EAN-13, EAN-8, UPC-A, UPC-E
- ✅ **Fallback**: Use manual barcode entry

**"Product not found" / OpenFoodFacts 404**
- ✅ **Database coverage**: Not all products are in OpenFoodFacts
- ✅ **Barcode format**: Try adding/removing leading zeros
- ✅ **Regional variations**: Some barcodes vary by country
- ✅ **Manual entry**: Double-check barcode digits

### 🤖 AI Analysis Issues

**"Analysis failed" / API errors**
- ✅ **API Key**: Verify `GOOGLE_API_KEY` is set correctly
- ✅ **Network**: Check internet connection
- ✅ **Quota**: Ensure API key hasn't exceeded rate limits
- ✅ **Fallback**: API includes backup key for testing

### 🌐 Web Interface Issues

**"Failed to connect" / 500 errors**
- ✅ **Dependencies**: Run `pip install -r requirements.txt` (if exists)
- ✅ **Python version**: Ensure Python 3.10+
- ✅ **Port conflicts**: Try different port in `app.py`
- ✅ **Logs**: Check console output for detailed error messages

## 🚀 Development & Deployment

### 🧪 Testing
```bash
# Test camera functionality
python camera_test.py

# Test live scanning
python opencv_auto_stop.py

# Manual API testing
curl -X POST http://localhost:5000/analyze_barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode":"3017620425035"}'
```

### 🐳 Docker Deployment (Optional)
```dockerfile
# Dockerfile example
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### 📊 Performance Optimization
- **Caching**: Consider Redis for OpenFoodFacts API responses
- **CDN**: Host static assets on CDN for production
- **Database**: Add database layer for user analytics
- **Load balancing**: Use multiple Flask instances behind nginx
- **Monitoring**: Implement logging and health checks

## 🔮 Roadmap & Ideas

### 🎯 Planned Features
- [ ] **User Accounts**: Save scan history and preferences
- [ ] **Batch Processing**: Upload multiple images at once
- [ ] **Nutrition Goals**: Personalized scoring based on dietary needs
- [ ] **Ingredient Analysis**: Detailed ingredient breakdown and allergen detection
- [ ] **Mobile App**: React Native or Flutter mobile companion
- [ ] **Offline Mode**: Local barcode database for offline scanning

### 💡 Enhancement Ideas  
- [ ] **Voice Interface**: "Scan this product" voice commands
- [ ] **Comparison Tool**: Side-by-side product comparisons
- [ ] **Recommendation Engine**: Suggest healthier alternatives
- [ ] **Integration APIs**: Connect with fitness tracking apps
- [ ] **Advanced Analytics**: Nutrition trend analysis and reports
- [ ] **Multi-language Support**: Internationalization (i18n)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and **add tests**
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`  
6. **Submit** a Pull Request

### 🏷️ Development Guidelines
- Follow **PEP 8** Python style guidelines
- Add **docstrings** for all functions and classes
- Include **unit tests** for new functionality
- Update **README** for any new features
- Test on **multiple platforms** when possible

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements & Credits

- **[OpenFoodFacts](https://world.openfoodfacts.org/)** - Open product database and comprehensive API
- **[Google AI (Gemini)](https://ai.google.dev/)** - Advanced AI for nutrition analysis and scoring  
- **[LangChain](https://python.langchain.com/)** - Framework for LLM application development
- **[pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)** - Python barcode reading library
- **[OpenCV](https://opencv.org/)** - Computer vision library for camera functionality
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight Python web framework

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ by [shaikshabayakati](https://github.com/shaikshabayakati)

[🐛 Report Bug](https://github.com/shaikshabayakati/packagedfoodrating/issues) • [✨ Request Feature](https://github.com/shaikshabayakati/packagedfoodrating/issues) • [💬 Discussions](https://github.com/shaikshabayakati/packagedfoodrating/discussions)

</div>
