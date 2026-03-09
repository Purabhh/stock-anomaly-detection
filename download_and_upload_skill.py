#!/usr/bin/env python3
"""
Script to download a skill from clawhub.com and upload it to a GitHub repository.
"""

import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
import argparse
import tempfile


def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return result."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, cwd=cwd, 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def check_dependencies():
    """Check if required tools are installed."""
    tools = ['clawhub', 'git']
    
    for tool in tools:
        result = run_command(f"which {tool}", capture_output=True)
        if result is None or not result:
            print(f"❌ {tool} is not installed or not in PATH")
            return False
    
    print("✅ All dependencies are installed")
    return True


def search_skill(query, limit=10):
    """Search for skills on clawhub.com."""
    print(f"🔍 Searching for skills matching: '{query}'")
    
    cmd = f"clawhub search '{query}' --limit {limit}"
    result = run_command(cmd, capture_output=True)
    
    if result:
        print("Search results:")
        print(result)
        return True
    else:
        print("No results found or search failed")
        return False


def download_skill(skill_name, version=None, target_dir=None):
    """Download a skill from clawhub.com."""
    if target_dir is None:
        target_dir = os.path.join(os.getcwd(), "downloaded_skills")
    
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"📥 Downloading skill: {skill_name}")
    
    # Build download command
    cmd = f"clawhub install {skill_name}"
    if version:
        cmd += f" --version {version}"
    
    # Change to target directory
    original_cwd = os.getcwd()
    os.chdir(target_dir)
    
    try:
        result = run_command(cmd, capture_output=False)
        print(f"✅ Skill '{skill_name}' downloaded to: {target_dir}")
        
        # Find the downloaded skill directory
        skill_dir = os.path.join(target_dir, skill_name)
        if os.path.exists(skill_dir):
            return skill_dir
        else:
            # Check if it was installed in a skills subdirectory
            skills_dir = os.path.join(target_dir, "skills", skill_name)
            if os.path.exists(skills_dir):
                return skills_dir
            else:
                print("⚠️ Could not find downloaded skill directory")
                return None
                
    except Exception as e:
        print(f"❌ Failed to download skill: {e}")
        return None
    finally:
        os.chdir(original_cwd)


def prepare_for_github(skill_dir, repo_name=None):
    """Prepare skill directory for GitHub repository."""
    if not os.path.exists(skill_dir):
        print(f"❌ Skill directory not found: {skill_dir}")
        return None
    
    if repo_name is None:
        repo_name = os.path.basename(skill_dir)
    
    # Create a clean copy for GitHub
    github_dir = os.path.join(os.path.dirname(skill_dir), f"{repo_name}-github")
    
    if os.path.exists(github_dir):
        shutil.rmtree(github_dir)
    
    # Copy skill directory
    shutil.copytree(skill_dir, github_dir)
    
    # Create README.md if it doesn't exist
    readme_path = os.path.join(github_dir, "README.md")
    if not os.path.exists(readme_path):
        skill_name = os.path.basename(skill_dir)
        readme_content = f"""# {skill_name} Skill

This is an OpenClaw agent skill downloaded from clawhub.com.

## Description

[Add description here]

## Installation

```bash
clawhub install {skill_name}
```

## Usage

[Add usage instructions]

## Files

- `SKILL.md` - Skill definition and documentation
- `index.js` - Main skill implementation (if applicable)
- Other supporting files

## License

[Add license information]
"""
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"📝 Created README.md at: {readme_path}")
    
    # Create .gitignore
    gitignore_path = os.path.join(github_dir, ".gitignore")
    gitignore_content = """# Python
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

# Temporary files
*.tmp
*.temp
"""
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    
    print(f"✅ Prepared for GitHub: {github_dir}")
    return github_dir


def create_github_repo(repo_name, description="", private=False, org=None):
    """Create a new GitHub repository using gh CLI."""
    print(f"🔄 Creating GitHub repository: {repo_name}")
    
    # Build create command
    cmd = "gh repo create"
    cmd += f" {repo_name}"
    cmd += f" --description '{description}'"
    
    if private:
        cmd += " --private"
    else:
        cmd += " --public"
    
    if org:
        cmd += f" --org {org}"
    
    cmd += " --confirm"
    
    result = run_command(cmd, capture_output=True)
    
    if result:
        print(f"✅ GitHub repository created: {repo_name}")
        
        # Get the repository URL
        if org:
            repo_url = f"https://github.com/{org}/{repo_name}"
        else:
            # Try to get username
            username_cmd = "gh api user --jq '.login'"
            username = run_command(username_cmd, capture_output=True)
            if username:
                repo_url = f"https://github.com/{username}/{repo_name}"
            else:
                repo_url = f"https://github.com/{repo_name}"
        
        return repo_url
    else:
        print("❌ Failed to create GitHub repository")
        return None


def upload_to_github(local_dir, repo_url, commit_message="Initial commit"):
    """Upload local directory to GitHub repository."""
    print(f"📤 Uploading to GitHub: {repo_url}")
    
    # Initialize git repository
    run_command("git init", cwd=local_dir)
    run_command("git add .", cwd=local_dir)
    run_command(f'git commit -m "{commit_message}"', cwd=local_dir)
    
    # Add remote and push
    run_command(f"git remote add origin {repo_url}", cwd=local_dir)
    
    # Try to push, create main branch if needed
    push_result = run_command("git push -u origin main", cwd=local_dir, capture_output=True)
    if push_result is None:
        # Try with master branch
        run_command("git branch -M master", cwd=local_dir)
        push_result = run_command("git push -u origin master", cwd=local_dir, capture_output=True)
    
    if push_result:
        print(f"✅ Successfully uploaded to GitHub: {repo_url}")
        return True
    else:
        print("❌ Failed to upload to GitHub")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download skill from clawhub.com and upload to GitHub")
    parser.add_argument("action", choices=["search", "download", "upload", "full"],
                       help="Action to perform")
    parser.add_argument("--query", help="Search query for skills")
    parser.add_argument("--skill", help="Skill name to download")
    parser.add_argument("--version", help="Specific version to download")
    parser.add_argument("--repo", help="GitHub repository name")
    parser.add_argument("--description", default="OpenClaw skill from clawhub.com",
                       help="Repository description")
    parser.add_argument("--private", action="store_true",
                       help="Create private repository")
    parser.add_argument("--org", help="GitHub organization name")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies:")
        print("  - clawhub: npm install -g clawhub")
        print("  - git: Install git from https://git-scm.com/")
        print("  - gh: Install GitHub CLI from https://cli.github.com/")
        return
    
    if args.action == "search":
        if not args.query:
            print("❌ Please provide a search query with --query")
            return
        search_skill(args.query)
    
    elif args.action == "download":
        if not args.skill:
            print("❌ Please provide a skill name with --skill")
            return
        
        skill_dir = download_skill(args.skill, args.version)
        if skill_dir:
            print(f"\n📁 Skill downloaded to: {skill_dir}")
            print(f"\nTo prepare for GitHub, run:")
            print(f"  python {sys.argv[0]} upload --skill {args.skill}")
    
    elif args.action == "upload":
        if not args.skill:
            print("❌ Please provide a skill name with --skill")
            return
        
        # First download the skill
        skill_dir = download_skill(args.skill, args.version)
        if not skill_dir:
            return
        
        # Prepare for GitHub
        repo_name = args.repo or args.skill
        github_dir = prepare_for_github(skill_dir, repo_name)
        if not github_dir:
            return
        
        # Check if gh CLI is installed for GitHub operations
        gh_check = run_command("which gh", capture_output=True)
        if not gh_check:
            print("\n⚠️  GitHub CLI (gh) is not installed.")
            print("The skill has been prepared for GitHub at:")
            print(f"  {github_dir}")
            print("\nTo upload manually:")
            print(f"  1. Create a repository on GitHub: {repo_name}")
            print(f"  2. cd {github_dir}")
            print(f"  3. git init && git add . && git commit -m 'Initial commit'")
            print(f"  4. git remote add origin https://github.com/yourusername/{repo_name}.git")
            print(f"  5. git push -u origin main")
            return
        
        # Create GitHub repository
        repo_url = create_github_repo(repo_name, args.description, args.private, args.org)
        if not repo_url:
            return
        
        # Upload to GitHub
        upload_to_github(github_dir, repo_url)
        
        print(f"\n🎉 Success! Skill '{args.skill}' has been uploaded to GitHub:")
        print(f"   Repository: {repo_url}")
        print(f"   Local copy: {github_dir}")
    
    elif args.action == "full":
        if not args.skill:
            print("❌ Please provide a skill name with --skill")
            return
        
        # Search first
        if args.query:
            search_skill(args.query)
        
        # Then download and upload
        skill_dir = download_skill(args.skill, args.version)
        if not skill_dir:
            return
        
        repo_name = args.repo or args.skill
        github_dir = prepare_for_github(skill_dir, repo_name)
        if not github_dir:
            return
        
        gh_check = run_command("which gh", capture_output=True)
        if gh_check:
            repo_url = create_github_repo(repo_name, args.description, args.private, args.org)
            if repo_url:
                upload_to_github(github_dir, repo_url)
                print(f"\n🎉 Success! Repository: {repo_url}")
        else:
            print(f"\n📁 Skill prepared for GitHub at: {github_dir}")
            print("Install GitHub CLI (gh) to automatically create and upload the repository.")


if __name__ == "__main__":
    main()