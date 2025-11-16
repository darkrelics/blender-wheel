#!/bin/bash
set -e  # Exit on error

#
# Blender Python Module Build Script
# ===================================
# This script builds Blender 4.4 as a Python wheel module.
# Based on AWS CodeBuild buildspec, but works anywhere (local, CI/CD, Docker).
#
# Requirements:
#   - Ubuntu/Debian Linux (or similar)
#   - Python 3.12
#   - sudo privileges (for apt-get)
#   - ~20GB disk space
#   - ~45-60 minutes build time
#
# Usage:
#   ./build_blender_wheel.sh [-y|--yes]
#
# Options:
#   -y, --yes        Skip confirmation prompts (for CI/CD)
#
# Environment Variables (optional):
#   BLENDER_REPO_URL    - Git URL for Blender source (default: official repo)
#   BLENDER_COMMIT_HASH - Trusted commit hash for verification (default: none, shows warning)
#   PYTHON_VERSION      - Python version to use (default: 3.12)
#   OUTPUT_DIR          - Where to place the built wheel (default: ./output)
#

echo "========================================"
echo "Blender Python Module Build Script"
echo "========================================"
echo ""

# Parse arguments
AUTO_YES=false
for arg in "$@"; do
    case $arg in
        -y|--yes)
            AUTO_YES=true
            shift
            ;;
    esac
done

# Configuration
BLENDER_REPO_URL="${BLENDER_REPO_URL:-https://projects.blender.org/blender/blender.git}"
BLENDER_COMMIT_HASH="${BLENDER_COMMIT_HASH:-}"  # Optional: specify trusted commit hash for verification
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
WITH_LIBS_PRECOMPILED="${WITH_LIBS_PRECOMPILED:-OFF}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/output}"
BUILD_DIR="$(pwd)/blender-source"

# Safety checks
if [ -z "$BUILD_DIR" ] || [ "$BUILD_DIR" = "/" ] || [ "$BUILD_DIR" = "/home" ]; then
    echo "ERROR: Invalid BUILD_DIR detected: '$BUILD_DIR'"
    echo "This would be dangerous. Aborting."
    exit 1
fi

echo "Configuration:"
echo "  Blender Repository: $BLENDER_REPO_URL"
echo "  Python Version:     $PYTHON_VERSION"
echo "  Output Directory:   $OUTPUT_DIR"
echo "  Build Directory:    $BUILD_DIR"
echo ""

# Check available disk space (require at least 25GB free)
echo "Checking disk space..."
REQUIRED_SPACE_GB=25
AVAILABLE_SPACE_KB=$(df -k "$(pwd)" | tail -1 | awk '{print $4}')
AVAILABLE_SPACE_GB=$((AVAILABLE_SPACE_KB / 1024 / 1024))

if [ "$AVAILABLE_SPACE_GB" -lt "$REQUIRED_SPACE_GB" ]; then
    echo "ERROR: Insufficient disk space!"
    echo "  Required: ${REQUIRED_SPACE_GB}GB"
    echo "  Available: ${AVAILABLE_SPACE_GB}GB"
    echo "  Please free up disk space before continuing."
    exit 1
fi

echo "✓ Disk space check passed (${AVAILABLE_SPACE_GB}GB available)"
echo ""

# ============================================================================
# Phase 1: Install Dependencies
# ============================================================================
echo "Phase 1: Installing build dependencies..."
echo "This requires sudo privileges and will install packages."
echo ""
echo "⚠️  WARNING: This script will:"
echo "  - Install system packages as root"
echo "  - Clone and execute code from: $BLENDER_REPO_URL"
echo "  - Run Blender's install_linux_packages.py as root"
echo ""
echo "Only continue if you trust the source repository!"
echo ""

if [ "$AUTO_YES" = false ]; then
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Updating package list..."
sudo apt-get update -y -q

echo "Installing Python ${PYTHON_VERSION}..."
sudo apt-get install -y -q \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev

echo "Installing build tools..."
sudo apt-get install -y -q \
    build-essential \
    git \
    cmake \
    ninja-build \
    git-lfs

echo "Dependencies installed."
echo ""

# ============================================================================
# Phase 2: Clone and Prepare Blender Source
# ============================================================================
echo "Phase 2: Cloning Blender source..."

# Initialize git-lfs
git lfs install --skip-smudge

# Safety check before any directory operations (validate BUILD_DIR hasn't been modified)
if [ -z "$BUILD_DIR" ] || [ "$BUILD_DIR" = "/" ] || [ "$BUILD_DIR" = "/home" ] || [ "$BUILD_DIR" = "$HOME" ]; then
    echo "ERROR: Invalid BUILD_DIR detected before directory removal: '$BUILD_DIR'"
    echo "This would be dangerous. Aborting."
    exit 1
fi

# Clone Blender (shallow clone for faster download)
if [ -d "$BUILD_DIR" ]; then
    echo "Build directory exists. Removing: $BUILD_DIR"
    rm -rf "$BUILD_DIR"
fi

echo "Cloning from: $BLENDER_REPO_URL"
git clone --depth 1 "$BLENDER_REPO_URL" "$BUILD_DIR"

cd "$BUILD_DIR"

# Verify commit hash if specified (security measure)
if [ -n "$BLENDER_COMMIT_HASH" ]; then
    echo "Verifying commit hash for security..."
    ACTUAL_COMMIT=$(git rev-parse HEAD)
    if [ "$ACTUAL_COMMIT" != "$BLENDER_COMMIT_HASH" ]; then
        echo "ERROR: Commit hash mismatch!"
        echo "  Expected: $BLENDER_COMMIT_HASH"
        echo "  Actual:   $ACTUAL_COMMIT"
        echo "  This could indicate a compromised repository or outdated hash."
        echo "  Aborting for security."
        exit 1
    fi
    echo "✓ Commit hash verified: $ACTUAL_COMMIT"
else
    ACTUAL_COMMIT=$(git rev-parse HEAD)
    echo "⚠️  WARNING: No commit hash verification enabled."
    echo "   Current commit: $ACTUAL_COMMIT"
    echo "   For security, consider setting BLENDER_COMMIT_HASH environment variable."
    echo "   Example: BLENDER_COMMIT_HASH=$ACTUAL_COMMIT ./build_blender_wheel.sh"
fi
echo ""

echo "Installing Linux build dependencies..."
sudo ./build_files/build_environment/install_linux_packages.py --all

echo "Updating build libraries..."
./build_files/utils/make_update.py --use-linux-libraries

echo "Source prepared."
echo ""

# ============================================================================
# Phase 3: Build Blender Python Module
# ============================================================================
echo "Phase 3: Building Blender Python module..."
echo "This will take 45-60 minutes on a typical machine."
echo ""

# Export build configuration
export PYTHON_VERSION="${PYTHON_VERSION}"
export WITH_LIBS_PRECOMPILED="${WITH_LIBS_PRECOMPILED}"

# Build using all available CPU cores
NPROC=$(nproc)
echo "Building with $NPROC parallel jobs..."

make bpy -j${NPROC}

echo "Build complete."
echo ""

# ============================================================================
# Phase 4: Generate Python Wheel
# ============================================================================
echo "Phase 4: Generating Python wheel..."

# Run Blender's wheel generation script
python${PYTHON_VERSION} ./build_files/utils/make_bpy_wheel.py ../build_linux_bpy/bin/

# Move wheel to output directory
cd ..
mkdir -p "$OUTPUT_DIR"

# Find the generated wheel
WHEEL_FILE=$(find . -name "bpy-*.whl" -type f -print -quit)

if [ -z "$WHEEL_FILE" ]; then
    echo "ERROR: Wheel file not found!"
    exit 1
fi

# Extract version from the wheel filename (e.g., bpy-4.4.0-cp312-cp312-linux_x86_64.whl)
WHEEL_BASENAME=$(basename "$WHEEL_FILE")
# Extract version: everything between "bpy-" and the first "-cp"
BLENDER_VERSION=$(echo "$WHEEL_BASENAME" | sed -n 's/bpy-\([^-]*\)-.*/\1/p')

if [ -z "$BLENDER_VERSION" ]; then
    echo "WARNING: Could not extract version from wheel filename, using 'unknown'"
    BLENDER_VERSION="unknown"
fi

echo "Detected Blender version: $BLENDER_VERSION"

# Rename to standard name with detected version
OUTPUT_WHEEL="$OUTPUT_DIR/blender_bpy_module-${BLENDER_VERSION}.whl"
mv "$WHEEL_FILE" "$OUTPUT_WHEEL"

echo "Wheel generated: $OUTPUT_WHEEL"
echo ""

# ============================================================================
# Phase 5: Generate Checksums
# ============================================================================
echo "Phase 5: Generating checksums..."

cd "$OUTPUT_DIR"

WHEEL_FILENAME=$(basename "$OUTPUT_WHEEL")

# SHA256
sha256sum "$WHEEL_FILENAME" > "${WHEEL_FILENAME}.sha256"
echo "SHA256: $(cat ${WHEEL_FILENAME}.sha256)"

# MD5
md5sum "$WHEEL_FILENAME" > "${WHEEL_FILENAME}.md5"
echo "MD5:    $(cat ${WHEEL_FILENAME}.md5)"

echo ""

# ============================================================================
# Phase 6: Verify Build (Optional but Recommended)
# ============================================================================
echo "Phase 6: Verifying wheel installation..."
echo ""

# Create temporary virtual environment for testing
TEMP_VENV="$OUTPUT_DIR/test_venv"
if [ -d "$TEMP_VENV" ]; then
    rm -rf "$TEMP_VENV"
fi

echo "Creating test virtual environment..."
python${PYTHON_VERSION} -m venv "$TEMP_VENV"

echo "Activating test environment..."
source "$TEMP_VENV/bin/activate"

echo "Installing wheel..."
pip install --quiet "$WHEEL_FILENAME"

echo "Testing bpy import..."
if python -c "import bpy; print(f'✓ Successfully imported bpy {bpy.app.version_string}')" 2>/dev/null; then
    echo "✓ Wheel verification PASSED"
    VERIFICATION_STATUS="PASSED"
else
    echo "✗ Wheel verification FAILED - cannot import bpy"
    VERIFICATION_STATUS="FAILED"
fi

# Cleanup
deactivate
rm -rf "$TEMP_VENV"

echo ""

# ============================================================================
# Complete
# ============================================================================
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Output files:"
echo "  Wheel:  $OUTPUT_WHEEL"
echo "  SHA256: ${OUTPUT_WHEEL}.sha256"
echo "  MD5:    ${OUTPUT_WHEEL}.md5"
echo ""
echo "File size: $(du -h $OUTPUT_WHEEL | cut -f1)"
echo ""
echo "Verification: $VERIFICATION_STATUS"
echo ""
echo "To install:"
echo "  pip install $OUTPUT_WHEEL"
echo ""
echo "To verify integrity:"
echo "  sha256sum -c $WHEEL_FILENAME.sha256"
echo ""

# Exit with error if verification failed
if [ "$VERIFICATION_STATUS" = "FAILED" ]; then
    echo "⚠️  WARNING: Build completed but verification failed!"
    echo "    The wheel may not be functional."
    exit 1
fi
