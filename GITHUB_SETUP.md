# GitHub Repository Setup Guide

Quick guide to push this repository to GitHub using GitHub CLI (`gh`).

## Prerequisites

Install GitHub CLI if not already installed:

```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh

# Or download from: https://cli.github.com/
```

## Step-by-Step Instructions

### 1. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts:
- Choose: **GitHub.com**
- Protocol: **HTTPS** or **SSH** (your preference)
- Authenticate: Choose **Login with a web browser** (easiest)
- Copy the one-time code and paste in browser

### 2. Create GitHub Repository

```bash
# Option A: Public repository (recommended for open source)
gh repo create Speed_test --public --source=. --remote=origin --push

# Option B: Private repository
gh repo create Speed_test --private --source=. --remote=origin --push
```

**Explanation of flags:**
- `Speed_test` - repository name
- `--public` or `--private` - visibility
- `--source=.` - use current directory
- `--remote=origin` - set remote name to 'origin'
- `--push` - push commits immediately

### 3. Verify Upload

```bash
# Check remote
git remote -v

# View on GitHub
gh repo view --web
```

## Alternative: Manual Steps

If you prefer step-by-step:

### 1. Authenticate
```bash
gh auth login
```

### 2. Create repository (without auto-push)
```bash
gh repo create Speed_test --public --source=.
```

### 3. Push manually
```bash
git remote add origin https://github.com/YOUR_USERNAME/Speed_test.git
git branch -M main
git push -u origin main
```

## Add Repository Description

```bash
gh repo edit --description "Internet speed testing tool with CLI, GUI (KivyMD), and KDE Plasma widget. Features automated testing, SQLite storage, and result validation."
```

## Add Topics/Tags

```bash
gh repo edit --add-topic speedtest,python,kivy,kde-plasma,network-testing,gui,cli
```

## Repository Settings

### Enable Issues and Wiki

```bash
gh repo edit --enable-issues --enable-wiki
```

### Add Homepage URL (if you have one)

```bash
gh repo edit --homepage "https://your-project-website.com"
```

## Create README Badge

After pushing, add status badges to README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20windows-lightgrey.svg)
```

## Quick Reference

```bash
# View repository on GitHub
gh repo view --web

# Clone repository (for testing)
gh repo clone YOUR_USERNAME/Speed_test

# Create release
gh release create v1.0.0 --title "Initial Release" --notes "First stable release"

# View repository info
gh repo view

# List your repositories
gh repo list
```

## Update .gitignore (already done)

The following files are already in `.gitignore`:
- `speedtest_history.db` - SQLite database with user results
- `speedtest_config.json` - User configuration
- Virtual environment directories (`speedtest_env/`, `ebv/`)

## Next Steps After Push

1. **Add README badges** - Update README.md with status badges
2. **Create releases** - Tag versions with `gh release create`
3. **Enable GitHub Actions** - Add CI/CD workflows (optional)
4. **Add CONTRIBUTING.md** - Guidelines for contributors
5. **Set up GitHub Pages** - For project website (optional)

## Common Commands

```bash
# Push changes
git push

# Pull changes
git pull

# Create new branch
git checkout -b feature-name

# Push branch to GitHub
git push -u origin feature-name

# Create pull request
gh pr create

# View pull requests
gh pr list

# Merge pull request
gh pr merge
```

## Troubleshooting

### Authentication Issues

```bash
# Check auth status
gh auth status

# Re-authenticate
gh auth login

# Use token
gh auth login --with-token < token.txt
```

### Remote Already Exists

```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/Speed_test.git
```

### Large Files Warning

If you get warnings about large files:
```bash
# Check file sizes
git ls-files -s | awk '{print $4 " " $2}' | sort -rn | head -20

# Use Git LFS for large files (if needed)
git lfs install
git lfs track "*.db"
```

---

**Ready to share your Speed Test tool with the world! 🚀**
