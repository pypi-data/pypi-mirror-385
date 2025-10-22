#!/bin/bash
# Minimal build that avoids importing the package

set -e

echo "Building cert-framework 0.3.1 (minimal method)..."

# Set environment to prevent imports during build
export SETUPTOOLS_SCM_PRETEND_VERSION="0.3.1"
export CERT_SKIP_IMPORT="1"

# Clean
rm -rf dist/ build/ *.egg-info cert_framework.egg-info 2>/dev/null

# Create a temporary minimal setup.py that doesn't call get_version()
cat > setup_minimal.py << 'SETUP_EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cert-framework",
    version="0.3.1",
    author="Javier Marin",
    author_email="info@cert-framework.com",
    description="A framework to test your LLM application for reliability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Javihaus/cert-framework",
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.8",
    install_requires=[
        "sentence-transformers>=2.2.0,<3.0.0",
        "torch>=1.11.0",
        "transformers>=4.30.0",
        "numpy>=1.21.0",
        "typing-extensions>=4.0.0",
    ],
)
SETUP_EOF

# Build
echo "Building..."
python3 setup_minimal.py sdist

# Clean up temp file
rm setup_minimal.py

echo ""
echo "✓ Build complete!"
ls -lh dist/
echo ""
echo "Upload with: twine upload dist/*"
