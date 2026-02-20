#!/bin/bash

echo "🧹 Cleaning all cache files from the project..."

# Remove Python cache
echo "  → Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
echo "  → Removing .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove .pyo files
echo "  → Removing .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove .DS_Store files (macOS)
echo "  → Removing .DS_Store files..."
find . -name ".DS_Store" -delete 2>/dev/null

# Remove egg-info directories
echo "  → Removing .egg-info directories..."
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove pytest cache
echo "  → Removing pytest cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# Remove coverage files
echo "  → Removing coverage files..."
find . -type f -name ".coverage" -delete 2>/dev/null
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null

# Remove mypy cache
echo "  → Removing mypy cache..."
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null

echo ""
echo "✅ All cache files removed successfully!"
echo ""
echo "💡 Tip: Restart your Django server for changes to take effect"
