#!/bin/bash

# Repository configuration
REPO_NAME="timekpr-manager"
# Please update your username here if it's different
GITHUB_USER="joachim" 

echo "Initializing Git repository in /home/joachim/develop/time/..."
cd /home/joachim/develop/time/

# Initialize if not already a git repo
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized."
fi

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: TimeKpr Network Manager - Universal Linux Application"

# Set branch to main
git branch -M main

# Add remote (replaces if already exists)
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "--------------------------------------------------------"
echo "Ready to push! Use the command below to upload:"
echo "git push -u origin main"
echo "--------------------------------------------------------"
