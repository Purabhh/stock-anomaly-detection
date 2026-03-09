# GitHub Skill Download and Upload Guide

This guide explains how to download skills from clawhub.com and upload them to GitHub repositories.

## Prerequisites

### 1. Install ClawHub CLI
```bash
npm install -g clawhub
```

### 2. Install Git
```bash
# On Ubuntu/Debian
sudo apt-get install git

# On macOS
brew install git
```

### 3. (Optional) Install GitHub CLI
For automatic repository creation and upload:
```bash
# On Ubuntu/Debian
sudo apt-get install gh

# On macOS
brew install gh

# Authenticate
gh auth login
```

## Methods

### Method 1: Using the Python Script (Recommended)

The `download_and_upload_skill.py` script provides a complete solution:

```bash
# Search for skills
python download_and_upload_skill.py search --query "weather"

# Download a skill
python download_and_upload_skill.py download --skill "weather"

# Download specific version
python download_and_upload_skill.py download --skill "weather" --version "1.0.0"

# Full process (download + upload to GitHub)
python download_and_upload_skill.py upload --skill "weather" --repo "openclaw-weather-skill"

# With organization
python download_and_upload_skill.py upload --skill "weather" --repo "weather-skill" --org "myorg" --private
```

### Method 2: Using the Bash Script

Simple bash script for downloading and preparing skills:

```bash
# Make script executable
chmod +x download_skill.sh

# Search for skills
./download_skill.sh search "weather"

# Download a skill
./download_skill.sh download "weather"

# Download with options
./download_skill.sh download "weather" --version "1.0.0" --dir "./my_skills"

# Prepare for GitHub
./download_skill.sh prepare ./downloaded_skills/weather "openclaw-weather"
```

### Method 3: Manual Process

#### Step 1: Search for Skills
```bash
clawhub search "query"
```

#### Step 2: Download a Skill
```bash
# Download to current directory
clawhub install skill-name

# Download specific version
clawhub install skill-name --version 1.0.0

# Download to specific directory
mkdir -p my_skills
cd my_skills
clawhub install skill-name
```

#### Step 3: Prepare for GitHub
```bash
# Navigate to skill directory
cd skill-name

# Create README.md (if missing)
cat > README.md << 'EOF'
# Skill Name

Description of the skill.

## Installation
```bash
clawhub install skill-name
```

## Usage
[Usage instructions]
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
node_modules/
.env
.DS_Store
EOF
```

#### Step 4: Upload to GitHub

**Option A: Using GitHub CLI (if installed)**
```bash
# Create repository
gh repo create skill-name --description "OpenClaw skill" --public --confirm

# Initialize git and push
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/skill-name.git
git push -u origin main
```

**Option B: Manual GitHub Upload**
1. Go to https://github.com/new
2. Create a new repository named `skill-name`
3. Follow the instructions to push an existing repository:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/skill-name.git
git push -u origin main
```

## Example: Download and Upload a Weather Skill

```bash
# 1. Search for weather skills
clawhub search "weather"

# 2. Download the weather skill
clawhub install weather

# 3. Navigate to the skill
cd weather

# 4. Check the skill structure
ls -la
cat SKILL.md

# 5. Prepare for GitHub
echo "# Weather Skill" > README.md
echo "" >> README.md
echo "OpenClaw skill for weather information." >> README.md

# 6. Create repository on GitHub.com
#    - Go to https://github.com/new
#    - Name: openclaw-weather-skill
#    - Description: Weather skill for OpenClaw

# 7. Upload to GitHub
git init
git add .
git commit -m "Initial commit: Weather skill from clawhub.com"
git branch -M main
git remote add origin https://github.com/yourusername/openclaw-weather-skill.git
git push -u origin main
```

## Available Skills on ClawHub

Here are some popular skills you can download:

1. **weather** - Get weather information
2. **github** - GitHub operations via CLI
3. **tmux** - Remote-control tmux sessions
4. **video-frames** - Extract frames from videos
5. **openai-image-gen** - Generate images with OpenAI
6. **openai-whisper-api** - Transcribe audio with Whisper
7. **skill-creator** - Create new skills
8. **healthcheck** - Security hardening checks
9. **agentmail** - Email integration

## Troubleshooting

### "clawhub: command not found"
```bash
npm install -g clawhub
```

### "gh: command not found"
Install GitHub CLI or use manual GitHub upload method.

### Skill not found
```bash
# Search for similar skills
clawhub search "partial-name"

# List all installed skills
clawhub list
```

### Permission errors
```bash
# Check permissions
ls -la downloaded_skills/

# Fix permissions
sudo chown -R $USER:$USER downloaded_skills/
```

## Best Practices

1. **Check SKILL.md** - Always review the skill documentation before uploading
2. **Add proper README** - Include installation and usage instructions
3. **Respect licenses** - Check if the skill has a license file
4. **Give credit** - Mention the original source (clawhub.com)
5. **Test locally** - Verify the skill works before uploading

## Script Reference

### Python Script (`download_and_upload_skill.py`)
```bash
# Full help
python download_and_upload_skill.py --help

# Search, download, and upload in one command
python download_and_upload_skill.py full --skill "weather" --repo "weather-skill"
```

### Bash Script (`download_skill.sh`)
```bash
# Show help
./download_skill.sh

# Download skill with all options
./download_skill.sh download "weather" --version "1.2.0" --dir "./custom_dir"
```

## Next Steps

After uploading a skill to GitHub, you can:

1. **Add CI/CD** - Set up GitHub Actions for testing
2. **Create releases** - Tag versions for stability
3. **Add documentation** - Expand README with examples
4. **Submit to clawhub** - Publish your own skills back to clawhub.com

```bash
# Publish to clawhub.com
clawhub publish ./skill-directory --slug "my-skill" --name "My Skill" --version "1.0.0"
```

## Resources

- [ClawHub Website](https://clawhub.com)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [GitHub CLI Documentation](https://cli.github.com)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)