#!/bin/bash
# Example script showing how to upload a skill to GitHub

echo "=== Uploading Skill to GitHub ==="
echo ""

# Step 1: Initialize git repository
echo "1. Initialize git repository:"
echo "   cd example_skill"
echo "   git init"
echo ""

# Step 2: Add all files
echo "2. Add files to git:"
echo "   git add ."
echo ""

# Step 3: Commit changes
echo "3. Commit the files:"
echo '   git commit -m "Initial commit: Weather skill from clawhub.com"'
echo ""

# Step 4: Rename branch to main (if needed)
echo "4. Rename branch to main:"
echo "   git branch -M main"
echo ""

# Step 5: Add remote repository
echo "5. Add GitHub remote (replace with your repository URL):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/openclaw-weather-skill.git"
echo ""

# Step 6: Push to GitHub
echo "6. Push to GitHub:"
echo "   git push -u origin main"
echo ""

# Alternative: Using GitHub CLI
echo "=== Alternative: Using GitHub CLI ==="
echo ""
echo "1. Create repository first:"
echo '   gh repo create openclaw-weather-skill --description "Weather skill for OpenClaw" --public --confirm'
echo ""
echo "2. Then push:"
echo "   git init"
echo "   git add ."
echo '   git commit -m "Initial commit"'
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "=== Manual GitHub Steps ==="
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create repository: openclaw-weather-skill"
echo "3. Copy the commands shown on GitHub"
echo "4. Run them in your skill directory"
echo ""

echo "=== Verify Upload ==="
echo ""
echo "After uploading, visit:"
echo "https://github.com/YOUR_USERNAME/openclaw-weather-skill"
echo ""

echo "=== Next Steps ==="
echo ""
echo "1. Add a LICENSE file"
echo "2. Create GitHub Releases"
echo "3. Set up GitHub Actions for testing"
echo "4. Add more documentation"
echo "5. Submit to clawhub.com"