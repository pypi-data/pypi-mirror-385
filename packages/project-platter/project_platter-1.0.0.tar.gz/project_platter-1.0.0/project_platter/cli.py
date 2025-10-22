import os
import subprocess
import webbrowser
from pathlib import Path
import requests

# ==========================
# Utility Functions
# ==========================
def yes(val: str) -> bool:
    return val.strip().lower() in ['y', 'yes']

def safe_input(prompt, default=None):
    """
    Wrapper for input() to handle KeyboardInterrupt and provide a default value.
    """
    try:
        return input(prompt).strip() or default
    except KeyboardInterrupt:
        print("\n⚠️ Input interrupted by user.")
        return default
    except Exception as e:
        print(f"⚠️ Error reading input: {e}")
        return default

def check_git_installed():
    while True:
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("✅ Git is installed and ready.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Git is not installed or not found in PATH: {e}")
            if yes(safe_input("Open Git download page in your browser? (y/n): ", "n")):
                try:
                    webbrowser.open("https://git-scm.com/downloads")
                except Exception as ex:
                    print(f"⚠️ Could not open browser: {ex}")
            if yes(safe_input("Have you installed Git now and want to retry? (y/n): ", "n")):
                continue
            else:
                print("⚠️ Skipping Git setup...")
                return False

# --------------------------
# File/Folder Helpers
# --------------------------
def create_init_only(path):
    try:
        os.makedirs(path, exist_ok=True)
        init_file = Path(path) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Init file")
        print(f"📦 Created code folder: {path}")
    except Exception as e:
        print(f"⚠️ Failed to create init file in {path}: {e}")

def create_gitkeep_only(path):
    try:
        os.makedirs(path, exist_ok=True)
        gitkeep = Path(path) / ".gitkeep"
        gitkeep.write_text("")
        print(f"📁 Created asset/data folder: {path}")
    except Exception as e:
        print(f"⚠️ Failed to create .gitkeep in {path}: {e}")

def create_template_file(path, template_text):
    try:
        os.makedirs(path.parent, exist_ok=True)
        path.write_text(f"'''\n{template_text}\n'''")
        print(f"📝 Created template: {path}")
    except Exception as e:
        print(f"⚠️ Failed to create template file {path}: {e}")

def safe_create_file(path, content):
    try:
        if path.exists() and path.is_dir():
            print(f"⚠️ Skipping file creation for {path} (directory exists).")
            return
        create_template_file(path, content)
    except Exception as e:
        print(f"⚠️ Error in safe_create_file for {path}: {e}")

# --------------------------
# GitHub API Repo Creation
# --------------------------
def create_github_repo(project_name):
    try:
        print("\nℹ️ GitHub Personal Access Token (PAT) guidance:")
        print(" - Use a CLASSIC PAT for best compatibility: https://github.com/settings/tokens")
        print(" - Scopes: public_repo for public, repo for private repos")
        print(" - Fine-grained PATs often fail for repo creation.")
        username = safe_input("Your GitHub username: ")
        token = safe_input("Your GitHub Personal Access Token (PAT): ")
        repo_name = safe_input(f"Repository name [{project_name}]: ", project_name) or project_name
        private_repo = yes(safe_input("Make repository private? (y/n): ", "n"))
        url = "https://api.github.com/user/repos"
        payload = {"name": repo_name, "private": private_repo, "auto_init": False}
        headers = {"Accept": "application/vnd.github+json"}
        auth = (username, token)
        print("📡 Creating repository on GitHub...")
        r = requests.post(url, json=payload, headers=headers, auth=auth)
        if r.status_code == 201:
            repo_data = r.json()
            print(f"✅ Repository created: {repo_data['html_url']}")
            return repo_data["clone_url"]
        elif r.status_code == 403:
            print("❌ Permission denied: Token likely fine-grained without repo creation rights.")
            print("   Fix: Use a Classic PAT with 'repo' scope.")
            return None
        else:
            print(f"❌ Failed to create repository: {r.status_code} {r.text}")
            return None
    except Exception as e:
        print(f"⚠️ Error creating GitHub repo: {e}")
        return None

# --------------------------
# Git Initialization
# --------------------------
def init_git_repo(base_path, repo_url, git_location):
    if not check_git_installed():
        print("⚠️ Git setup skipped.")
        return

    repo_dir = base_path.parent if git_location == "parent" else base_path
    print(f"\n🔧 Initializing Git repository in: {repo_dir}")

    try:
        current_name = subprocess.run(["git", "config", "--global", "user.name"],
                                      capture_output=True, text=True).stdout.strip()
        current_email = subprocess.run(["git", "config", "--global", "user.email"],
                                       capture_output=True, text=True).stdout.strip()
    except Exception as e:
        print(f"⚠️ Error getting git config: {e}")
        current_name = current_email = ""

    if not current_name or not current_email:
        try:
            name = safe_input("Enter your Git username: ")
            email = safe_input("Enter your Git email: ")
            subprocess.run(["git", "config", "--global", "user.name", name])
            subprocess.run(["git", "config", "--global", "user.email", email])
            print(f"✅ Git identity set: {name} <{email}>")
        except Exception as e:
            print(f"⚠️ Error setting git identity: {e}")
    else:
        print(f"✅ Git identity set: {current_name} <{current_email}>")

    if not repo_url:
        if yes(safe_input("Auto-create GitHub repo now? (y/n): ", "n")):
            new_url = create_github_repo(base_path.name)
            if new_url:
                repo_url = new_url
        elif yes(safe_input("Enter remote repo URL now? (y/n): ", "n")):
            repo_url = safe_input("Remote URL (HTTPS or SSH): ")

    try:
        subprocess.run(["git", "init"], cwd=repo_dir)
        default_branch = safe_input("Enter default branch name [main]: ", "main")
        subprocess.run(["git", "checkout", "-b", default_branch], cwd=repo_dir)
    except Exception as e:
        print(f"⚠️ Git init or checkout failed: {e}")

    try:
        safe_create_file(repo_dir / ".gitignore", """
# Python ignore patterns
__pycache__/
*.py[cod]
*$py.class
venv/
.env/
.venv/
logs/
*.log
.ipynb_checkpoints
data/
outputs/
""")
    except Exception as e:
        print(f"⚠️ Error creating .gitignore: {e}")

    if repo_url:
        try:
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=repo_dir)
        except Exception as e:
            print(f"⚠️ Failed to add remote repo: {e}")

    try:
        subprocess.run(["git", "add", "."], cwd=repo_dir)
        subprocess.run(["git", "commit", "-m", "Initial project structure"], cwd=repo_dir)
    except Exception as e:
        print(f"⚠️ Git add/commit failed: {e}")

    if yes(safe_input("Create develop branch? (y/n): ", "n")):
        try:
            subprocess.run(["git", "checkout", "-b", "develop"], cwd=repo_dir)
        except Exception as e:
            print(f"⚠️ Failed to create develop branch: {e}")

    feat_name = None
    if yes(safe_input("Create feature branch? (y/n): ", "n")):
        feat_name = safe_input("Feature branch name (e.g., feature/login-api): ")
        if feat_name:
            try:
                subprocess.run(["git", "checkout", "-b", feat_name], cwd=repo_dir)
            except Exception as e:
                print(f"⚠️ Failed to create feature branch: {e}")

    if repo_url and yes(safe_input("Push ALL branches to remote now? (y/n): ", "n")):
        try:
            subprocess.run(["git", "push", "--all", "origin"], cwd=repo_dir)
            subprocess.run(["git", "push", "--tags", "origin"], cwd=repo_dir)
            print("🚀 All branches pushed to remote.")
        except Exception as e:
            print(f"⚠️ Git push failed: {e}")

    try:
        subprocess.run(["git", "log", "--graph", "--oneline", "--all", "--decorate"], cwd=repo_dir)
    except Exception as e:
        print(f"⚠️ Git log failed: {e}")

# --------------------------
# Main Project Init
# --------------------------
def init_project():
    try:
        print("🚀 GenAI/Agentic AI Project Bootstrapper")
        project_name = safe_input("Project name: ")
        base_path = Path(project_name)
        if base_path.exists():
            print(f"❌ Folder '{project_name}' exists.")
            return

        author = safe_input("Author name: ")
        repo_url = safe_input("GitHub repo URL (or leave blank): ")

        # Default industry-standard folder structure
        structure = [
            ("data", False),
            ("notebooks", False),
            ("src", True),
            ("src/agents", True),
            ("src/models", True),
            ("src/pipelines", True),
            ("src/utils", True),
            ("configs", False),
            ("tests", True),
            ("logs", False),
            ("prompts", False),
            ("outputs", False),
            ("docs", False),
            (".env", False)
        ]
        for folder, is_code in structure:
            path = base_path / folder
            if "." in folder:
                safe_create_file(path, "# Environment variables here")
            elif is_code:
                create_init_only(path)
            else:
                create_gitkeep_only(path)

        # Ask for extra folders/files
        while yes(safe_input("Add extra folder/file? (y/n): ", "n")):
            name = safe_input("Enter name (with extension for file or no extension for files like Dockerfile): ")
            path = base_path / name
            if "." in name or name.lower() in ["dockerfile", "makefile", "readme", "license"]:
                safe_create_file(path, f"# {name} placeholder")
            else:
                create_gitkeep_only(path)

        # Default templates
        safe_create_file(base_path / "Dockerfile", "FROM python:3.10\n# Add your steps here")
        safe_create_file(base_path / "docker-compose.yml", "version: '3'\n# Services here")
        safe_create_file(base_path / "README.md", f"# {project_name}\nAuthor: {author}")
        safe_create_file(base_path / "requirements.txt", "# Add dependencies here")
        safe_create_file(base_path / "config.yaml", "# Config values here")

        # Git init location choice
        git_location = "project"
        if yes(safe_input("Init Git in parent dir instead of project dir? (y/n): ", "n")):
            git_location = "parent"

        init_git_repo(base_path, repo_url, git_location)
        print(f"🎉 Project '{project_name}' created successfully.")
    except Exception as e:
        print(f"⚠️ Error in init_project: {e}")

def main():
    """Entry point for the GenAI Project Bootstrapper CLI"""
    try:
        from .cli import init_project
        init_project()
    except Exception as e:
        print(f"⚠️ CLI main execution failed: {e}")
