#!/bin/bash
# publish.sh - Publish Datum DBT to PyPI using uv

set -e

cd /Users/zain/dev/datum-cli

echo "======================================"
echo "Publishing Datum DBT to PyPI with uv"
echo "======================================"
echo ""

# Step 1: Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf build/ dist/ *.egg-info

# Step 2: Build with uv
echo "🔨 Building package with uv..."
uv build

# Step 3: Check what was built
echo "✅ Built artifacts:"
ls -lh dist/

# Step 4: Upload with uv
echo ""
echo "📤 Uploading to PyPI with uv..."
echo "You will be asked for your PyPI credentials (or use API token)"
echo ""

uv publish

echo ""
echo "======================================"
echo "✅ PUBLISHED SUCCESSFULLY!"
echo "======================================"
echo ""
echo "Your package is now available at:"
echo "  https://pypi.org/project/datum-dbt/"
echo ""
echo "Users can install with:"
echo "  pip install datum-dbt"
echo "  or: uv pip install datum-dbt"
echo ""
echo "Test installation:"
echo "  uv pip install datum-dbt"
echo "  datum dbt --help"
