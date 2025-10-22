#!/bin/bash
# Build script for QINA Security Editor

echo "🔨 Building QINA Security Editor package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf qina_security_editor.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel build twine

# Build the package
echo "🏗️ Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
python -m twine check dist/*

echo "✅ Build complete!"
echo "📦 Package files created in dist/"
echo ""
echo "To test locally:"
echo "  pip install dist/qina_security_editor-1.0.0-py3-none-any.whl"
echo ""
echo "To upload to PyPI:"
echo "  python -m twine upload dist/*"
