#!/bin/bash

cd /home/ubuntu/bots/calculator_bot

# Add all changes
git add .

# Commit (ignore if nothing changed)
git commit -m "auto update $(date)" || echo "No changes"

# Push
git push origin main
