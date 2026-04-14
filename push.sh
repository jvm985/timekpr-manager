#!/bin/bash

# Repository configuratie
REPO_NAME="timekpr-manager"
GITHUB_USER="jvm985" 

echo "Synchroniseren met GitHub: $GITHUB_USER/$REPO_NAME..."
cd /home/joachim/develop/time/

# Zorg dat alle wijzigingen zijn toegevoegd
git add .

# Maak een commit (als er wijzigingen zijn)
git commit -m "Update: $(date +'%Y-%m-%d %H:%M:%S')" || echo "Geen wijzigingen om te committen."

# Forceer de juiste SSH remote URL
git remote set-url origin "git@github.com:$GITHUB_USER/$REPO_NAME.git"

# Push naar de main branch
echo "Bezig met pushen naar GitHub via SSH..."
git push -u origin main

echo "--------------------------------------------------------"
echo "Klaar! Je code staat nu op: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "--------------------------------------------------------"
