#!/bin/bash
# Setup and upload data science project to GitHub repository "ADS"

set -e

echo "========================================="
echo "GitHub Repository Setup for ADS Project"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="ADS"
PROJECT_DIR="$(pwd)"
GITHUB_USERNAME=""  # You'll fill this in
GITHUB_TOKEN=""     # You'll need a personal access token

echo -e "${BLUE}Step 1: Check Git Configuration${NC}"
echo "-----------------------------------------"

# Check git config
if ! git config --global user.name; then
    echo -e "${YELLOW}Git user.name not set${NC}"
    echo "Please set your git username:"
    echo "  git config --global user.name \"Your Name\""
fi

if ! git config --global user.email; then
    echo -e "${YELLOW}Git user.email not set${NC}"
    echo "Please set your git email:"
    echo "  git config --global user.email \"your.email@example.com\""
fi

echo ""
echo -e "${BLUE}Step 2: Prepare Project for GitHub${NC}"
echo "-----------------------------------------"

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}Creating .gitignore file${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Database files
*.db
*.sqlite
*.sqlite3

# Jupyter Notebook
.ipynb_checkpoints/

# Plotly images
*.png
*.jpg
*.jpeg

# Logs
*.log

# Temporary files
*.tmp
*.temp
EOF
    echo -e "${GREEN}Created .gitignore${NC}"
else
    echo -e "${GREEN}.gitignore already exists${NC}"
fi

# Create comprehensive README if it doesn't exist
if [ ! -f "README.md" ]; then
    echo -e "${YELLOW}Creating comprehensive README.md${NC}"
    cat > README.md << 'EOF'
# Stock Market Anomaly Detection System (ADS)

A complete data science project for detecting anomalies in stock market data using free tools and local execution.

## 📊 Project Overview

This system detects anomalies in stock market data using three complementary methods:
1. **Z-Score** - Statistical outlier detection
2. **Isolation Forest** - Tree-based anomaly detection  
3. **Local Outlier Factor (LOF)** - Density-based anomaly detection

Anomalies are flagged when at least 2 out of 3 methods agree, providing high-confidence detection.

## 🛠️ Tech Stack (100% Free)

- **Data Collection**: yfinance (free Yahoo Finance API)
- **News Integration**: NewsAPI free tier
- **Database**: SQLite (local, no server needed)
- **Machine Learning**: scikit-learn
- **NLP/Sentiment**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Visualization**: Plotly (interactive charts)
- **Storage**: Local filesystem

## 📁 Project Structure

```
ADS/
├── src/
│   ├── database.py           # SQLite database schema (4 tables)
│   ├── data_ingestion.py     # yfinance + NewsAPI pipeline
│   ├── feature_engineering.py # Technical indicators & features
│   ├── anomaly_detection.py  # 3-method detection with agreement scoring
│   └── visualization.py      # Plotly interactive charts
├── data/                     # SQLite database & raw data
├── notebooks/                # Jupyter notebooks for analysis
├── visualizations/           # Generated charts and dashboards
├── tests/                    # Unit tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ADS.git
cd ADS

# Install dependencies
pip install -r requirements.txt

# Download NLTK data for VADER
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 2. Basic Usage
```bash
# Run the complete pipeline
python src/pipeline.py --symbol AAPL --period 1y

# Generate visualizations
python src/visualization.py --symbol AAPL --output charts/
```

### 3. Database Schema
The system uses 4 SQLite tables:
- `stocks` - Stock metadata
- `price_data` - Historical price data  
- `news_articles` - News with sentiment scores
- `anomalies` - Detected anomalies with agreement scores

## 📈 Features

### Data Pipeline
- Automated data ingestion from yfinance
- News collection with sentiment analysis (VADER)
- Feature engineering (50+ technical indicators)
- SQLite storage for reproducibility

### Anomaly Detection
- Three complementary detection methods
- Agreement scoring across methods
- Confidence levels for each detection
- Feature importance analysis

### Visualization
- Interactive Plotly charts
- Anomaly highlighting on price charts
- Method comparison visualizations
- HTML dashboard generation

## 📋 Requirements

See `requirements.txt` for complete list:
- pandas, numpy, scikit-learn
- yfinance, requests
- plotly, kaleido
- vaderSentiment, nltk
- sqlite3 (built-in)

## 🎯 Academic Use

This project is designed for data science courses with:
- **Full reproducibility** - All local tools, no cloud dependencies
- **Academic integrity** - No paid APIs or services
- **Clear documentation** - Commented code and explanations
- **Modular design** - Easy to extend and modify

## 📊 Example Output

1. **Price charts** with anomalies highlighted
2. **Agreement scores** across detection methods  
3. **Feature importance** for anomaly detection
4. **News sentiment** correlation with anomalies
5. **Performance metrics** for each method

## 🔧 Customization

### Add New Stocks
```python
from src.data_ingestion import DataIngestion
ingestor = DataIngestion()
ingestor.fetch_stock_data("TSLA", period="2y")
```

### Modify Detection Parameters
```python
from src.anomaly_detection import AnomalyDetector
detector = AnomalyDetector(contamination=0.05)  # Adjust expected outlier rate
```

### Add New Features
```python
from src.feature_engineering import FeatureEngineer
engineer = FeatureEngineer(window_sizes=[5, 10, 20, 50, 100, 200])
```

## 📚 Methodology

### 1. Data Collection
- Historical prices (open, high, low, close, volume)
- News headlines with sentiment scoring
- Corporate actions and events

### 2. Feature Engineering  
- Price transformations (returns, ratios)
- Technical indicators (SMA, EMA, Bollinger Bands, RSI, MACD)
- Statistical features (volatility, skewness, kurtosis)
- Volume indicators (OBV, VWAP)

### 3. Anomaly Detection
- **Z-Score**: Statistical outliers in individual features
- **Isolation Forest**: Tree-based isolation in feature space  
- **LOF**: Density-based local outlier detection
- **Agreement Scoring**: Consensus across methods

### 4. Validation
- Cross-referencing with news events
- Price action analysis around anomalies
- Method performance comparison

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for academic use. Please cite if used in research or publications.

## 🙏 Acknowledgments

- yfinance for free market data
- NewsAPI for news headlines
- scikit-learn for ML algorithms
- VADER for sentiment analysis
- Plotly for visualization

## 📧 Contact

For questions about this academic project, please open an issue on GitHub.

---
*Built for Data Science Course Project - 100% Free Tools*
EOF
    echo -e "${GREEN}Created README.md${NC}"
else
    echo -e "${GREEN}README.md already exists${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Initialize Git Repository${NC}"
echo "-----------------------------------------"

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing git repository${NC}"
    git init
    echo -e "${GREEN}Git repository initialized${NC}"
else
    echo -e "${GREEN}Git repository already initialized${NC}"
fi

# Add all files
echo -e "${YELLOW}Adding files to git${NC}"
git add .
echo -e "${GREEN}Files added to git${NC}"

# Commit
echo -e "${YELLOW}Committing files${NC}"
git commit -m "Initial commit: Stock Market Anomaly Detection System (ADS)

Complete data science project for detecting anomalies in stock market data using:
- yfinance for price data
- NewsAPI for news headlines  
- SQLite for local storage
- scikit-learn for ML models
- VADER for sentiment analysis
- Plotly for visualization

Features:
- 3 anomaly detection methods (Z-score, Isolation Forest, LOF)
- Agreement scoring across methods
- 4-table SQLite schema
- Interactive Plotly dashboards
- Free tools only, no paid APIs"
echo -e "${GREEN}Files committed${NC}"

echo ""
echo -e "${BLUE}Step 4: GitHub Repository Setup${NC}"
echo "-----------------------------------------"

echo -e "${YELLOW}IMPORTANT: You need to create the GitHub repository first${NC}"
echo ""
echo "Follow these steps:"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: ${REPO_NAME}"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo "4. Copy the repository URL (it will look like: https://github.com/YOUR_USERNAME/ADS.git)"
echo ""
echo -e "${YELLOW}After creating the repository, you have two options:${NC}"
echo ""
echo -e "${GREEN}Option A: Using HTTPS (requires personal access token)${NC}"
echo "  git remote add origin https://github.com/YOUR_USERNAME/ADS.git"
echo "  git push -u origin main"
echo ""
echo -e "${GREEN}Option B: Using SSH (requires SSH key setup)${NC}"
echo "  git remote add origin git@github.com:YOUR_USERNAME/ADS.git"
echo "  git push -u origin main"
echo ""
echo -e "${YELLOW}If you get an error about 'main' branch, try:${NC}"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo -e "${BLUE}Step 5: GitHub Authentication${NC}"
echo "-----------------------------------------"

echo -e "${YELLOW}GitHub Personal Access Token Setup:${NC}"
echo ""
echo "1. Go to https://github.com/settings/tokens"
echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "3. Give it a name: 'ADS Project Upload'"
echo "4. Select scopes: repo (full control of private repositories)"
echo "5. Generate token and COPY IT (you won't see it again)"
echo ""
echo -e "${YELLOW}Using the token:${NC}"
echo ""
echo "When pushing, use this URL format:"
echo "  https://YOUR_TOKEN@github.com/YOUR_USERNAME/ADS.git"
echo ""
echo "Or set it as credential helper:"
echo "  git config --global credential.helper store"
echo "  git push https://github.com/YOUR_USERNAME/ADS.git"
echo "  (enter your username and use token as password)"
echo ""
echo -e "${BLUE}Step 6: Final Push Commands${NC}"
echo "-----------------------------------------"

echo -e "${GREEN}Complete push sequence:${NC}"
echo ""
echo "# Set your git identity if not already done"
echo "git config --global user.name \"Your Name\""
echo "git config --global user.email \"your.email@example.com\""
echo ""
echo "# Add remote (replace YOUR_USERNAME)"
echo "git remote add origin https://github.com/YOUR_USERNAME/ADS.git"
echo ""
echo "# Rename branch to main if needed"
echo "git branch -M main"
echo ""
echo "# Push to GitHub"
echo "git push -u origin main"
echo ""
echo -e "${YELLOW}If using a token:${NC}"
echo "git push https://YOUR_TOKEN@github.com/YOUR_USERNAME/ADS.git"
echo ""
echo -e "${BLUE}Step 7: Verify Upload${NC}"
echo "-----------------------------------------"

echo "After pushing, verify at:"
echo "  https://github.com/YOUR_USERNAME/ADS"
echo ""
echo "Your repository should contain:"
echo "  ✓ README.md"
echo "  ✓ .gitignore"
echo "  ✓ src/ directory with all Python modules"
echo "  ✓ requirements.txt"
echo "  ✓ Other project files"
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup Complete! Follow the steps above.${NC}"
echo -e "${GREEN}=========================================${NC}"

# Create a simple push script
cat > push_to_github.sh << 'EOF'
#!/bin/bash
# Script to push ADS project to GitHub

echo "Pushing ADS project to GitHub..."
echo ""

# Check remote
if ! git remote | grep -q origin; then
    echo "Please set your GitHub remote first:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/ADS.git"
    echo ""
    echo "Or with SSH:"
    echo "  git remote add origin git@github.com:YOUR_USERNAME/ADS.git"
    exit 1
fi

# Check branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Current branch: $CURRENT_BRANCH"
    echo "Switching to main branch..."
    git checkout -b main 2>/dev/null || git branch -M main
fi

# Push
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📁 View your repository: https://github.com/YOUR_USERNAME/ADS"
else
    echo ""
    echo "❌ Push failed. Possible issues:"
    echo "  1. No GitHub remote configured"
    echo "  2. Authentication failed (need token or SSH key)"
    echo "  3. Repository doesn't exist on GitHub"
    echo ""
    echo "Solutions:"
    echo "  1. Create repo at: https://github.com/new"
    echo "  2. Use token: git push https://TOKEN@github.com/YOUR_USERNAME/ADS.git"
    echo "  3. Check remote: git remote -v"
fi
EOF

chmod +x push_to_github.sh
echo -e "${GREEN}Created push script: ./push_to_github.sh${NC}"
echo ""
echo -e "${YELLOW}Run ./push_to_github.sh when ready to push${NC}"