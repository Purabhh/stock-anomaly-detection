#!/bin/bash
# Simple script to download a skill from clawhub.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenClaw Skill Downloader${NC}"
echo "=============================="

# Check if clawhub is installed
if ! command -v clawhub &> /dev/null; then
    echo -e "${RED}Error: clawhub CLI is not installed${NC}"
    echo "Install it with: npm install -g clawhub"
    exit 1
fi

# Function to search for skills
search_skills() {
    echo -e "\n${YELLOW}Searching for skills matching: '$1'${NC}"
    clawhub search "$1" --limit 10
}

# Function to download a skill
download_skill() {
    local skill_name=$1
    local version=$2
    local target_dir=${3:-"./downloaded_skills"}
    
    echo -e "\n${YELLOW}Downloading skill: $skill_name${NC}"
    
    mkdir -p "$target_dir"
    cd "$target_dir"
    
    if [ -n "$version" ]; then
        clawhub install "$skill_name" --version "$version"
    else
        clawhub install "$skill_name"
    fi
    
    cd - > /dev/null
    
    # Find the downloaded skill
    local skill_dir="$target_dir/$skill_name"
    if [ ! -d "$skill_dir" ]; then
        skill_dir="$target_dir/skills/$skill_name"
    fi
    
    if [ -d "$skill_dir" ]; then
        echo -e "${GREEN}✅ Skill downloaded to: $skill_dir${NC}"
        echo -e "\nContents:"
        ls -la "$skill_dir/"
        
        # Check for SKILL.md
        if [ -f "$skill_dir/SKILL.md" ]; then
            echo -e "\n${YELLOW}Skill Description:${NC}"
            head -20 "$skill_dir/SKILL.md"
        fi
    else
        echo -e "${RED}❌ Could not find downloaded skill directory${NC}"
    fi
}

# Function to prepare for GitHub
prepare_for_github() {
    local skill_dir=$1
    local repo_name=${2:-$(basename "$skill_dir")}
    
    if [ ! -d "$skill_dir" ]; then
        echo -e "${RED}❌ Skill directory not found: $skill_dir${NC}"
        return 1
    fi
    
    local github_dir="$(dirname "$skill_dir")/${repo_name}-github"
    
    echo -e "\n${YELLOW}Preparing for GitHub: $github_dir${NC}"
    
    # Remove existing directory
    rm -rf "$github_dir"
    
    # Copy skill
    cp -r "$skill_dir" "$github_dir"
    
    # Create README.md if it doesn't exist
    if [ ! -f "$github_dir/README.md" ]; then
        cat > "$github_dir/README.md" << EOF
# $(basename "$skill_dir") Skill

This is an OpenClaw agent skill downloaded from clawhub.com.

## Description

[Add description here]

## Installation

\`\`\`bash
clawhub install $(basename "$skill_dir")
\`\`\`

## Usage

[Add usage instructions]

## Files

- \`SKILL.md\` - Skill definition and documentation
- \`index.js\` - Main skill implementation (if applicable)
- Other supporting files

## License

[Add license information]
EOF
        echo -e "${GREEN}📝 Created README.md${NC}"
    fi
    
    # Create .gitignore
    cat > "$github_dir/.gitignore" << EOF
# Python
__pycache__/
*.py[cod]
*\$py.class
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

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
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

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
    
    echo -e "${GREEN}✅ Prepared for GitHub: $github_dir${NC}"
    echo -e "\nTo upload to GitHub:"
    echo "  cd $github_dir"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    echo "  git remote add origin https://github.com/yourusername/$repo_name.git"
    echo "  git push -u origin main"
}

# Main script
if [ $# -eq 0 ]; then
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  search <query>      Search for skills on clawhub.com"
    echo "  download <name>     Download a skill by name"
    echo "  prepare <dir>       Prepare downloaded skill for GitHub"
    echo ""
    echo "Examples:"
    echo "  $0 search weather"
    echo "  $0 download weather"
    echo "  $0 prepare ./downloaded_skills/weather"
    exit 1
fi

command=$1
shift

case $command in
    "search")
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Please provide a search query${NC}"
            exit 1
        fi
        search_skills "$1"
        ;;
    
    "download")
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Please provide a skill name${NC}"
            exit 1
        fi
        
        skill_name=$1
        version=""
        target_dir="./downloaded_skills"
        
        # Parse optional arguments
        shift
        while [[ $# -gt 0 ]]; do
            case $1 in
                --version)
                    version=$2
                    shift 2
                    ;;
                --dir)
                    target_dir=$2
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        download_skill "$skill_name" "$version" "$target_dir"
        ;;
    
    "prepare")
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Please provide skill directory${NC}"
            exit 1
        fi
        
        skill_dir=$1
        repo_name=$2
        
        prepare_for_github "$skill_dir" "$repo_name"
        ;;
    
    *)
        echo -e "${RED}Error: Unknown command '$command'${NC}"
        exit 1
        ;;
esac