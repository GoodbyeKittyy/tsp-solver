# Git Repository Setup Guide

This guide will walk you through creating a Git repository and pushing your TSP Solver project to GitHub.

## Prerequisites

1. **Install Git**: Download from [git-scm.com](https://git-scm.com/downloads)
2. **Create GitHub Account**: Sign up at [github.com](https://github.com)

## Step 1: Configure Git (First-Time Setup)

Open your terminal and configure your Git identity:

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

## Step 2: Create Project Directory Structure

```bash
# Create project directory
mkdir tsp-solver
cd tsp-solver

# Create subdirectories
mkdir tests docs examples

# Your project structure should look like:
# tsp-solver/
# ├── tsp_solver.py
# ├── tsp_visualizer.py
# ├── tsp_benchmark.py
# ├── tsp_api.py
# ├── tsp_cli.py
# ├── requirements.txt
# ├── .gitignore
# ├── README.md
# ├── LICENSE
# ├── tests/
# ├── docs/
# └── examples/
```

## Step 3: Copy Your Files

Copy all the Python files, README, and configuration files into the `tsp-solver` directory.

## Step 4: Initialize Git Repository

```bash
# Navigate to project directory
cd tsp-solver

# Initialize Git repository
git init

# Check status
git status
```

You should see all your files listed as "Untracked files".

## Step 5: Add Files to Git

```bash
# Add all files to staging area
git add .

# Or add files individually
git add tsp_solver.py
git add README.md
# ... etc

# Check what will be committed
git status
```

## Step 6: Create First Commit

```bash
# Commit with descriptive message
git commit -m "Initial commit: Add TSP solver with multiple algorithms"

# View commit history
git log
```

## Step 7: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to [github.com](https://github.com)
2. Click the "+" icon → "New repository"
3. Enter repository name: `tsp-solver`
4. Add description: "Production-grade TSP solver with multiple algorithms"
5. Choose "Public" or "Private"
6. **DO NOT** initialize with README (you already have one)
7. Click "Create repository"

### Option B: Via GitHub CLI (if installed)

```bash
# Install GitHub CLI first: https://cli.github.com/
gh auth login
gh repo create tsp-solver --public --source=. --remote=origin --push
```

## Step 8: Connect Local Repository to GitHub

After creating the repository on GitHub, connect your local repo:

```bash
# Add remote repository (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/tsp-solver.git

# Verify remote was added
git remote -v

# You should see:
# origin  https://github.com/USERNAME/tsp-solver.git (fetch)
# origin  https://github.com/USERNAME/tsp-solver.git (push)
```

## Step 9: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main

# Enter your GitHub credentials when prompted
```

### If Using Personal Access Token (PAT)

GitHub now requires personal access tokens instead of passwords:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token
5. Use token as password when pushing

## Step 10: Verify Upload

1. Go to `https://github.com/USERNAME/tsp-solver`
2. You should see all your files!

## Common Git Commands

### Daily Workflow

```bash
# Check status of files
git status

# Add changes to staging
git add filename.py
# or add all changes
git add .

# Commit changes
git commit -m "Add feature X"

# Push to GitHub
git push

# Pull latest changes
git pull
```

### Branching

```bash
# Create new branch
git branch feature-new-algorithm

# Switch to branch
git checkout feature-new-algorithm

# Create and switch in one command
git checkout -b feature-new-algorithm

# List all branches
git branch

# Merge branch into main
git checkout main
git merge feature-new-algorithm

# Delete branch
git branch -d feature-new-algorithm
```

### Viewing History

```bash
# View commit history
git log

# View last 5 commits
git log -5

# View commits with file changes
git log --stat

# View specific file history
git log -- tsp_solver.py
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- filename.py

# Unstage file (undo git add)
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## Complete Terminal Session Example

Here's a complete example session from start to finish:

```bash
# 1. Create and navigate to project directory
mkdir tsp-solver
cd tsp-solver

# 2. Copy your files here
# (manually copy all Python files, README.md, etc.)

# 3. Initialize Git
git init

# 4. Add .gitignore file
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
venv/
*.png
*.json
.DS_Store
EOF

# 5. Add all files
git add .

# 6. Create first commit
git commit -m "Initial commit: Production-grade TSP solver

- Implemented Held-Karp (exact DP algorithm)
- Implemented Christofides (1.5-approximation)
- Implemented Nearest Neighbor and 2-opt heuristics
- Added visualization tools
- Added REST API with Flask
- Added CLI interface
- Added comprehensive benchmarking suite
- Handles 1000+ cities with real-time metrics"

# 7. Create repo on GitHub (do this via website or GitHub CLI)

# 8. Add remote
git remote add origin https://github.com/YOUR_USERNAME/tsp-solver.git

# 9. Push to GitHub
git branch -M main
git push -u origin main
```

## Tips and Best Practices

### Commit Messages

**Good commit messages:**
```bash
git commit -m "Add Christofides algorithm implementation"
git commit -m "Fix 2-opt infinite loop for edge case"
git commit -m "Update README with API documentation"
```

**Bad commit messages:**
```bash
git commit -m "updates"
git commit -m "fix"
git commit -m "asdf"
```

### When to Commit

- After completing a feature
- After fixing a bug
- Before trying something experimental
- At the end of your work session

### .gitignore Tips

Always add these to `.gitignore`:
- `__pycache__/` and `*.pyc` (Python bytecode)
- `venv/` or `.venv/` (virtual environments)
- `.env` (environment variables with secrets)
- Output files (`.png`, `.json`, etc.)
- IDE settings (`.vscode/`, `.idea/`)

## Troubleshooting

### Error: "fatal: remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/USERNAME/tsp-solver.git
```

### Error: "Updates were rejected"

```bash
# Pull changes first
git pull origin main --rebase

# Then push
git push origin main
```

### Error: "Permission denied"

Make sure you're using the correct GitHub credentials or personal access token.

### Forgot to add .gitignore

```bash
# Remove tracked files that should be ignored
git rm -r --cached __pycache__
git rm --cached *.pyc

# Commit the removal
git commit -m "Remove ignored files from tracking"
```

## Next Steps

1. **Add a LICENSE file**: Choose from [choosealicense.com](https://choosealicense.com/)
2. **Add CI/CD**: Set up GitHub Actions for automated testing
3. **Add badges**: Add status badges to your README
4. **Write documentation**: Add detailed API docs in `docs/` folder
5. **Create releases**: Tag versions with `git tag v1.0.0`

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Pro Git Book](https://git-scm.com/book/en/v2) (Free online)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

## Quick Reference Card

```bash
# Setup
git init                              # Initialize repo
git clone <url>                       # Clone existing repo

# Basic workflow
git status                            # Check status
git add <file>                        # Stage file
git add .                             # Stage all files
git commit -m "message"               # Commit changes
git push                              # Push to remote

# Branches
git branch                            # List branches
git branch <name>                     # Create branch
git checkout <branch>                 # Switch branch
git merge <branch>                    # Merge branch

# Remote
git remote add origin <url>           # Add remote
git remote -v                         # View remotes
git push -u origin main               # Push with upstream
git pull                              # Pull changes

# History
git log                               # View commits
git diff                              # View changes
git show <commit>                     # View commit details

# Undo
git checkout -- <file>                # Discard changes
git reset HEAD <file>                 # Unstage file
git reset --hard HEAD                 # Discard all changes
```

---

**You're all set!** Your TSP Solver is now version-controlled and hosted on GitHub. 🎉
