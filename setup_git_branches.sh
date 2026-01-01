#!/bin/bash

# ============================================================================
# Git Branch Setup Script for Streamlit Cloud Deployment
# ============================================================================
# This script sets up separate branches for:
# - main: Full project (Streamlit + Backend)
# - streamlit-cloud: Only Streamlit app (no backend/)
# ============================================================================

echo "🚀 Setting up Git branches for Travel News Translator..."
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Add all files to main branch
echo "📝 Committing current state to main branch..."
git add .
git commit -m "Backend Phase 2 complete + Streamlit app" || echo "Nothing to commit or already committed"
echo ""

# Ensure we're on main branch
git branch -M main
echo "✅ Main branch ready"
echo ""

# Create streamlit-cloud branch
echo "🌿 Creating streamlit-cloud branch..."
git checkout -b streamlit-cloud 2>/dev/null || git checkout streamlit-cloud
echo ""

# Remove backend folder from streamlit-cloud branch
if [ -d "backend" ]; then
    echo "🗑️  Removing backend/ folder from streamlit-cloud branch..."
    git rm -r backend/ 2>/dev/null || echo "Backend already removed"
    git commit -m "Remove backend folder for Streamlit Cloud deployment" 2>/dev/null || echo "Already committed"
    echo "✅ Backend removed from streamlit-cloud branch"
else
    echo "ℹ️  No backend/ folder found (already removed or doesn't exist)"
fi
echo ""

# Switch back to main
echo "🔄 Switching back to main branch..."
git checkout main
echo ""

# Summary
echo "============================================================================"
echo "✅ Git branches set up successfully!"
echo "============================================================================"
echo ""
echo "📊 Branch Summary:"
echo "  • main branch:           Full project (Streamlit + Backend)"
echo "  • streamlit-cloud branch: Streamlit only (no backend/)"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/travel-news-translator.git"
echo "   git push -u origin main"
echo "   git push -u origin streamlit-cloud"
echo ""
echo "2. Deploy to Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io/"
echo "   - Select repository: travel-news-translator"
echo "   - Select branch: streamlit-cloud  ← IMPORTANT"
echo "   - Main file: app.py"
echo ""
echo "3. Switch between branches:"
echo "   git checkout main              # For backend development"
echo "   git checkout streamlit-cloud   # For Streamlit demo"
echo ""
echo "============================================================================"
echo "🎉 Setup complete! Current branch:"
git branch --show-current
echo "============================================================================"
