#!/bin/bash
# Complete GitHub Upload Script for ADS Project
# Guides you through the entire process step by step

echo "=================================================="
echo "COMPLETE GITHUB UPLOAD FOR ADS PROJECT"
echo "=================================================="
echo ""
echo "This script will guide you through uploading your"
echo "Stock Market Anomaly Detection System to GitHub."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 YOUR PROJECT IS READY!${NC}"
echo "----------------------------------------"
echo "Project: Stock Market Anomaly Detection System (ADS)"
echo "Location: $(pwd)"
echo "Files: 18 files committed to git"
echo ""

echo -e "${BLUE}📋 WHAT'S BEEN PREPARED:${NC}"
echo "----------------------------------------"
echo "✅ Git repository initialized"
echo "✅ Comprehensive README.md created"
echo "✅ .gitignore configured for Python/DS projects"
echo "✅ All source code committed"
echo "✅ Database schema (4 SQLite tables)"
echo "✅ 3 anomaly detection methods"
echo "✅ Visualization module with Plotly"
echo "✅ Requirements.txt for dependencies"
echo ""

echo -e "${YELLOW}=================================================================${NC}"
echo -e "${YELLOW}STEP 1: CREATE GITHUB REPOSITORY${NC}"
echo -e "${YELLOW}=================================================================${NC}"
echo ""
echo "1. Open your browser and go to:"
echo -e "   ${GREEN}https://github.com/new${NC}"
echo ""
echo "2. Fill in the form:"
echo "   - Repository name: ${GREEN}ADS${NC}"
echo "   - Description: Stock Market Anomaly Detection System"
echo "   - Visibility: Public (recommended for academic projects)"
echo ""
echo "3. ${RED}IMPORTANT:${NC} DO NOT check any of these:"
echo "   - ☐ Add a README file"
echo "   - ☐ Add .gitignore"
echo "   - ☐ Choose a license"
echo ""
echo "4. Click ${GREEN}'Create repository'${NC}"
echo ""
read -p "Press Enter when you've created the repository..."

echo ""
echo -e "${YELLOW}=================================================================${NC}"
echo -e "${YELLOW}STEP 2: GET GITHUB PERSONAL ACCESS TOKEN${NC}"
echo -e "${YELLOW}=================================================================${NC}"
echo ""
echo "1. Go to:"
echo -e "   ${GREEN}https://github.com/settings/tokens${NC}"
echo ""
echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
echo ""
echo "3. Configure token:"
echo "   - Note: 'ADS Project Upload'"
echo "   - Expiration: 90 days (recommended)"
echo "   - Select scopes: ${GREEN}repo (Full control)${NC}"
echo ""
echo "4. Click ${GREEN}'Generate token'${NC}"
echo ""
echo "5. ${RED}COPY THE TOKEN NOW!${NC} You won't see it again."
echo "   It looks like: ghp_abc123def456ghi789..."
echo ""
read -p "Press Enter when you have your token copied..."

echo ""
echo -e "${YELLOW}=================================================================${NC}"
echo -e "${YELLOW}STEP 3: CONFIGURE GIT (One-time setup)${NC}"
echo -e "${YELLOW}=================================================================${NC}"
echo ""
echo "Setting your git identity..."
echo ""
read -p "Enter your name (for git commits): " USER_NAME
read -p "Enter your email (for git commits): " USER_EMAIL

git config --global user.name "$USER_NAME"
git config --global user.email "$USER_EMAIL"
echo -e "${GREEN}✓ Git identity configured${NC}"
echo ""

echo -e "${YELLOW}=================================================================${NC}"
echo -e "${YELLOW}STEP 4: PUSH TO GITHUB${NC}"
echo -e "${YELLOW}=================================================================${NC}"
echo ""
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your GitHub token (starts with ghp_): " GITHUB_TOKEN

echo ""
echo -e "${BLUE}🚀 Pushing to GitHub...${NC}"
echo ""

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add remote with token
REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/ADS.git"
echo "Adding remote: ${REMOTE_URL//${GITHUB_TOKEN}/********}"
git remote add origin "$REMOTE_URL"

# Rename branch to main
echo "Renaming branch to 'main'..."
git branch -M main

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================================${NC}"
    echo -e "${GREEN}🎉 SUCCESS! PROJECT UPLOADED TO GITHUB!${NC}"
    echo -e "${GREEN}==================================================${NC}"
    echo ""
    echo "Your repository is now live at:"
    echo -e "   ${GREEN}https://github.com/${GITHUB_USER}/ADS${NC}"
    echo ""
    echo "What's been uploaded:"
    echo "  ✓ README.md - Project documentation"
    echo "  ✓ src/ - All Python source code"
    echo "  ✓ requirements.txt - Dependencies"
    echo "  ✓ Database schema (4 SQLite tables)"
    echo "  ✓ 3 anomaly detection methods"
    echo "  ✓ Visualization module"
    echo "  ✓ Setup scripts and guides"
    echo ""
    echo -e "${BLUE}📊 FOR YOUR COURSE SUBMISSION:${NC}"
    echo "----------------------------------------"
    echo "Submit this GitHub URL:"
    echo "  https://github.com/${GITHUB_USER}/ADS"
    echo ""
    echo "The repository includes:"
    echo "  1. Complete source code"
    echo "  2. Installation instructions"
    echo "  3. Usage examples"
    echo "  4. Methodology documentation"
    echo "  5. Free tools justification"
    echo ""
    echo -e "${GREEN}✅ YOUR DATA SCIENCE PROJECT IS READY FOR GRADING!${NC}"
else
    echo ""
    echo -e "${RED}==================================================${NC}"
    echo -e "${RED}❌ PUSH FAILED${NC}"
    echo -e "${RED}==================================================${NC}"
    echo ""
    echo "Possible issues:"
    echo "  1. Repository not created at https://github.com/new"
    echo "  2. Invalid token or username"
    echo "  3. Network issues"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify repository exists: https://github.com/${GITHUB_USER}/ADS"
    echo "  2. Regenerate token if needed"
    echo "  3. Try manual commands:"
    echo "     git remote add origin https://TOKEN@github.com/USER/ADS.git"
    echo "     git branch -M main"
    echo "     git push -u origin main"
fi

echo ""
echo -e "${YELLOW}=================================================================${NC}"
echo -e "${YELLOW}ADDITIONAL COMMANDS (if needed)${NC}"
echo -e "${YELLOW}=================================================================${NC}"
echo ""
echo "To clone your repository elsewhere:"
echo "  git clone https://github.com/${GITHUB_USER}/ADS.git"
echo ""
echo "To add more files later:"
echo "  git add ."
echo "  git commit -m 'Your message'"
echo "  git push"
echo ""
echo "To view your repository:"
echo "  https://github.com/${GITHUB_USER}/ADS"
echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}PROJECT COMPLETE! GOOD LUCK WITH YOUR COURSE! 🎓${NC}"
echo -e "${GREEN}==================================================${NC}"