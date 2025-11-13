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
#   BLENDER_REPO_URL - Git URL for Blender source (default: official repo)
#   PYTHON_VERSION   - Python version to use (default: 3.12)
#   OUTPUT_DIR       - Where to place the built wheel (default: ./output)
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

# Clone Blender (shallow clone for faster download)
if [ -d "$BUILD_DIR" ]; then
    echo "Build directory exists. Removing..."
    # Double-check safety before rm -rf
    if [ -z "$BUILD_DIR" ] || [ "$BUILD_DIR" = "/" ]; then
        echo "ERROR: Refusing to remove invalid path: '$BUILD_DIR'"
        exit 1
    fi
    rm -rf "$BUILD_DIR"
fi

echo "Cloning from: $BLENDER_REPO_URL"
git clone --depth 1 "$BLENDER_REPO_URL" "$BUILD_DIR"

cd "$BUILD_DIR"

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

# Rename to standard name
OUTPUT_WHEEL="$OUTPUT_DIR/blender_bpy_module-4.4.whl"
mv "$WHEEL_FILE" "$OUTPUT_WHEEL"

echo "Wheel generated: $OUTPUT_WHEEL"
echo ""

# ============================================================================
# Phase 5: Generate Checksums
# ============================================================================
echo "Phase 5: Generating checksums..."

cd "$OUTPUT_DIR"

# SHA256
sha256sum blender_bpy_module-4.4.whl > blender_bpy_module-4.4.whl.sha256
echo "SHA256: $(cat blender_bpy_module-4.4.whl.sha256)"

# MD5
md5sum blender_bpy_module-4.4.whl > blender_bpy_module-4.4.whl.md5
echo "MD5:    $(cat blender_bpy_module-4.4.whl.md5)"

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
echo "  SHA256: $OUTPUT_DIR/blender_bpy_module-4.4.whl.sha256"
echo "  MD5:    $OUTPUT_DIR/blender_bpy_module-4.4.whl.md5"
echo ""
echo "File size: $(du -h $OUTPUT_WHEEL | cut -f1)"
echo ""
echo "To install:"
echo "  pip install $OUTPUT_WHEEL"
echo ""
echo "To verify integrity:"
echo "  sha256sum -c blender_bpy_module-4.4.whl.sha256"
echo ""
