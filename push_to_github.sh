#!/bin/bash
# Script to push code to GitHub repository
# Run this script from the mcp-coding-agent directory

set -e

echo "🚀 Preparing to push to GitHub..."

# Check if .env exists and warn if it contains real token
if [ -f .env ]; then
    if grep -q "github_pat_\|ghp_" .env 2>/dev/null; then
        echo "⚠️  Warning: .env file contains a token. Make sure it's in .gitignore!"
    fi
fi

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Add remote
echo "🔗 Setting up remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/AI-Castle-Labs/mcp-coding-agent.git

# Stage files (excluding .env)
echo "📝 Staging files..."
git add .env.template .gitignore README.md requirements.txt src/ test/ asset/ agents.md .claude/ 2>/dev/null || true

# Check for any .env files being staged
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ Error: .env file is being staged! Removing it..."
    git reset HEAD .env 2>/dev/null || true
fi

# Commit
echo "💾 Committing changes..."
git commit -m "Initial commit: MCP Coding Agent with AST analysis and dependency tracking" || echo "No changes to commit"

# Push
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main --force

echo "✅ Done! Code pushed to https://github.com/AI-Castle-Labs/mcp-coding-agent.git"

