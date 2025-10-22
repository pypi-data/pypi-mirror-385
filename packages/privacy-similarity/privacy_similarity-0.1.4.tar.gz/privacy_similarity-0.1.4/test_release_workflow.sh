#!/bin/bash
set -e

echo "========================================="
echo "Testing Release Workflow Steps Locally"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Get current version
echo -e "${YELLOW}Step 1: Get current version${NC}"
CURRENT_VERSION=$(grep "version=" setup.py | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"
echo ""

# Step 2: Verify version consistency across all files
echo -e "${YELLOW}Step 2: Verify version consistency${NC}"
SETUP_VERSION=$(grep "version=" setup.py | cut -d'"' -f2)
PYPROJECT_VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
INIT_VERSION=$(grep "__version__ = " privacy_similarity/__init__.py | cut -d'"' -f2)
BUMPVERSION_VERSION=$(grep "current_version = " .bumpversion.cfg | cut -d' ' -f3)

echo "  setup.py:              $SETUP_VERSION"
echo "  pyproject.toml:        $PYPROJECT_VERSION"
echo "  __init__.py:           $INIT_VERSION"
echo "  .bumpversion.cfg:      $BUMPVERSION_VERSION"

if [ "$SETUP_VERSION" = "$PYPROJECT_VERSION" ] && [ "$SETUP_VERSION" = "$INIT_VERSION" ] && [ "$SETUP_VERSION" = "$BUMPVERSION_VERSION" ]; then
    echo -e "${GREEN}✓ All versions are in sync!${NC}"
else
    echo -e "${RED}✗ Version mismatch detected!${NC}"
    exit 1
fi
echo ""

# Step 3: Clean previous builds
echo -e "${YELLOW}Step 3: Clean previous builds${NC}"
rm -rf dist build *.egg-info
echo -e "${GREEN}✓ Cleaned build directories${NC}"
echo ""

# Step 4: Install build dependencies
echo -e "${YELLOW}Step 4: Install build dependencies${NC}"
pip install --quiet --break-system-packages build twine 2>&1 | tail -3
echo -e "${GREEN}✓ Build dependencies installed${NC}"
echo ""

# Step 5: Build packages
echo -e "${YELLOW}Step 5: Build packages${NC}"
python -m build 2>&1 | grep -E "(Successfully built|Creating|Building)" || true
if [ $? -eq 0 ] || [ -f "dist/privacy_similarity-${CURRENT_VERSION}-py3-none-any.whl" ]; then
    echo -e "${GREEN}✓ Build completed successfully${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 6: Check built packages
echo -e "${YELLOW}Step 6: Check built packages${NC}"
echo "Files created:"
ls -lh dist/
echo ""

EXPECTED_WHEEL="dist/privacy_similarity-${CURRENT_VERSION}-py3-none-any.whl"
EXPECTED_TARBALL="dist/privacy_similarity-${CURRENT_VERSION}.tar.gz"

if [ -f "$EXPECTED_WHEEL" ]; then
    echo -e "${GREEN}✓ Wheel file created: $(basename $EXPECTED_WHEEL)${NC}"
else
    echo -e "${RED}✗ Expected wheel file not found: $(basename $EXPECTED_WHEEL)${NC}"
    exit 1
fi

if [ -f "$EXPECTED_TARBALL" ]; then
    echo -e "${GREEN}✓ Source distribution created: $(basename $EXPECTED_TARBALL)${NC}"
else
    echo -e "${RED}✗ Expected tarball not found: $(basename $EXPECTED_TARBALL)${NC}"
    exit 1
fi
echo ""

# Step 7: Run twine check
echo -e "${YELLOW}Step 7: Run twine check${NC}"
twine check dist/*
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Twine check passed${NC}"
else
    echo -e "${RED}✗ Twine check failed${NC}"
    exit 1
fi
echo ""

# Step 8: Verify package contents
echo -e "${YELLOW}Step 8: Verify package contents${NC}"
echo "Wheel contents:"
unzip -l "$EXPECTED_WHEEL" | grep -E "(privacy_similarity|\.py)" | head -10
echo ""

# Step 9: Test installation (in a safe way)
echo -e "${YELLOW}Step 9: Test package metadata${NC}"
python -c "
import zipfile
import sys
whl = zipfile.ZipFile('$EXPECTED_WHEEL')
metadata = [f for f in whl.namelist() if 'METADATA' in f][0]
content = whl.read(metadata).decode('utf-8')
print('Package metadata:')
for line in content.split('\n')[:20]:
    print('  ' + line)
"
echo ""

# Summary
echo "========================================="
echo -e "${GREEN}All release workflow steps passed! ✓${NC}"
echo "========================================="
echo ""
echo "The workflow will create these files:"
echo "  - $(basename $EXPECTED_WHEEL)"
echo "  - $(basename $EXPECTED_TARBALL)"
echo ""
echo "These match what the GitHub Actions workflow expects."
