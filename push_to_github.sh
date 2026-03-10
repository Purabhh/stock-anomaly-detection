#!/bin/bash
# Simple push script for ADS project

echo "🚀 Pushing ADS Project to GitHub"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo "❌ Error: Not in ADS project directory"
    echo "Run this script from: stock_anomaly_detection/"
    exit 1
fi

# Check git status
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    echo "Run: git init"
    exit 1
fi

echo "📊 Current git status:"
echo "---------------------"
git status --short

echo ""
echo "🔍 Checking remote..."
if git remote | grep -q origin; then
    echo "✓ Remote 'origin' configured"
    git remote -v
else
    echo "❌ No remote configured"
    echo ""
    echo "You need to add your GitHub remote first:"
    echo ""
    echo "1. Get your GitHub token from:"
    echo "   https://github.com/settings/tokens"
    echo ""
    echo "2. Add remote (replace YOUR_USERNAME and YOUR_TOKEN):"
    echo "   git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/ADS.git"
    echo ""
    echo "Or with SSH:"
    echo "   git remote add origin git@github.com:YOUR_USERNAME/ADS.git"
    echo ""
    exit 1
fi

echo ""
echo "🌿 Checking branch..."
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Renaming branch to 'main'..."
    git branch -M main
    CURRENT_BRANCH="main"
fi

echo ""
echo "📤 Pushing to GitHub..."
echo "----------------------"
git push -u origin "$CURRENT_BRANCH"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ✅ ✅ SUCCESS! ✅ ✅ ✅"
    echo ""
    echo "🎉 Your ADS project is now on GitHub!"
    echo ""
    echo "📁 View your repository:"
    echo "   https://github.com/YOUR_USERNAME/ADS"
    echo ""
    echo "📊 Project includes:"
    echo "   • README.md - Complete documentation"
    echo "   • src/ - All Python source code"
    echo "   • requirements.txt - Dependencies"
    echo "   • Database schema (4 SQLite tables)"
    echo "   • 3 anomaly detection methods"
    echo "   • Visualization with Plotly"
    echo ""
    echo "🎓 Ready for course submission!"
else
    echo ""
    echo "❌ ❌ ❌ PUSH FAILED ❌ ❌ ❌"
    echo ""
    echo "Possible issues:"
    echo "  1. Authentication failed (need valid token/SSH key)"
    echo "  2. Repository doesn't exist on GitHub"
    echo "  3. Network issues"
    echo ""
    echo "Solutions:"
    echo "  1. Create repo: https://github.com/new (name: ADS)"
    echo "  2. Get token: https://github.com/settings/tokens"
    echo "  3. Check remote: git remote -v"
    echo "  4. Try: git push https://TOKEN@github.com/USER/ADS.git"
    echo ""
fi