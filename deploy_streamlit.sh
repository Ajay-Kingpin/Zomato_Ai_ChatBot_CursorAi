#!/bin/bash

# Streamlit Deployment Script for Zomato AI Recommendation System

echo "🚀 Deploying Zomato AI Recommendation System to Streamlit..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📁 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Add Streamlit deployment files

- Add streamlit_app.py with modern UI
- Add .streamlit/config.toml for styling
- Add requirements_streamlit.txt
- Add README_STREAMLIT.md with deployment guide
- Update .gitignore for Streamlit deployment"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please add your GitHub remote:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/zomato-ai-recommendation.git"
    echo "Then run this script again."
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

echo "✅ Ready for Streamlit deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://streamlit.io"
echo "2. Click 'New app'"
echo "3. Connect your GitHub repository"
echo "4. Select 'streamlit_app.py' as main file"
echo "5. Set environment variable: GOOGLE_STUDIO_API_KEY"
echo "6. Click 'Deploy'!"
echo ""
echo "🎉 Your app will be live at: https://your-username-zomato-recommendation.streamlit.app"
