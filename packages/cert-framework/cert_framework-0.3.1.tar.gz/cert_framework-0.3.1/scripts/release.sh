#!/bin/bash
set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh 0.2.0"
    exit 1
fi

echo "======================================"
echo "CERT Framework Release Process"
echo "Version: $VERSION"
echo "======================================"
echo ""

# Step 1: Update version
echo "Step 1: Updating version in cert/__init__.py..."
sed -i '' "s/__version__ = .*/__version__ = \"$VERSION\"/" cert/__init__.py
echo "✓ Version updated to $VERSION"
echo ""

# Step 2: Clean and build
echo "Step 2: Building distributions..."
rm -rf dist/ build/ *.egg-info
python3 -m build
echo "✓ Built distributions"
echo ""

# Step 3: List built files
echo "Built files:"
ls -lh dist/
echo ""

# Step 4: Test in clean environment
echo "Step 3: Testing built package..."
echo "Creating clean test environment..."
python3 -m venv /tmp/test-cert-release-$VERSION
source /tmp/test-cert-release-$VERSION/bin/activate

echo "Installing from wheel..."
pip install --quiet dist/cert_framework-${VERSION}-py3-none-any.whl

echo "Running tests..."
python3 -c "from cert import compare; print('✓ Import successful')"
python3 -c "from cert import compare; result = compare('hello', 'hello'); assert result.matched; print('✓ Basic test passed')"
python3 -c "from cert import __version__; assert __version__ == '$VERSION'; print(f'✓ Version correct: {__version__}')"

deactivate
rm -rf /tmp/test-cert-release-$VERSION
echo "✓ Package tests passed"
echo ""

# Step 5: Upload to TestPyPI
echo "Step 4: Uploading to TestPyPI..."
read -p "Press Enter to upload to TestPyPI (or Ctrl+C to cancel)..."
python3 -m twine upload --repository testpypi dist/*
echo "✓ Uploaded to TestPyPI"
echo ""

# Step 6: Test install from TestPyPI
echo "Step 5: Testing install from TestPyPI..."
echo "Run this command to test:"
echo ""
echo "  python3 -m venv /tmp/test-from-testpypi"
echo "  source /tmp/test-from-testpypi/bin/activate"
echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cert-framework"
echo "  python3 -c 'from cert import compare; print(\"✓ TestPyPI install works\")'"
echo "  deactivate"
echo ""
read -p "Press Enter after testing TestPyPI install to continue..."

# Step 7: Upload to production PyPI
echo "Step 6: Uploading to production PyPI..."
read -p "Press Enter to upload to PRODUCTION PyPI (or Ctrl+C to cancel)..."
python3 -m twine upload dist/*
echo "✓ Uploaded to PyPI"
echo ""

# Step 8: Verify production install
echo "Step 7: Verifying production install..."
echo "Run this command to verify:"
echo ""
echo "  python3 -m venv /tmp/test-from-pypi"
echo "  source /tmp/test-from-pypi/bin/activate"
echo "  pip install cert-framework"
echo "  python3 -c 'from cert import compare; print(\"✓ PyPI install works\")'"
echo "  deactivate"
echo ""
read -p "Press Enter after testing PyPI install to continue..."

# Step 9: Tag the release
echo "Step 8: Tagging the release..."
git add cert/__init__.py
git commit -m "Release version $VERSION"
git tag "v$VERSION"
git push origin master
git push origin "v$VERSION"
echo "✓ Tagged and pushed v$VERSION"
echo ""

echo "======================================"
echo "Release $VERSION Complete!"
echo "======================================"
echo ""
echo "Package is now available at:"
echo "  https://pypi.org/project/cert-framework/$VERSION/"
echo ""
echo "Users can install with:"
echo "  pip install cert-framework"
echo ""
