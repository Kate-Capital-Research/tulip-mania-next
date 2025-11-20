#!/bin/bash
# quick-build.sh - Fast iteration script for CSS/content changes
# Usage: ./quick-build.sh [commit message]

set -e  # Exit on error

echo "=========================================="
echo "Quick Build & Deploy Script"
echo "=========================================="

# Get current branch
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

# Step 1: Pull latest changes
echo ""
echo "Step 1/5: Pulling latest changes..."
git pull origin "$BRANCH"

# Step 2: Build the book
echo ""
echo "Step 2/5: Building Jupyter Book..."
poetry run jupyter book build --html --all

# Step 3: Add changed files
echo ""
echo "Step 3/5: Adding changes..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
  echo "No changes to commit. Exiting."
  exit 0
fi

# Step 4: Commit with message
echo ""
echo "Step 4/5: Committing changes..."
if [ -z "$1" ]; then
  # Default commit message if none provided
  COMMIT_MSG="Quick build: CSS and content updates"
else
  COMMIT_MSG="$1"
fi
git commit -m "$COMMIT_MSG"

# Step 5: Push to remote
echo ""
echo "Step 5/5: Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo ""
echo "=========================================="
echo "✓ Done! Changes pushed to $BRANCH"
echo "=========================================="
