# Local Build Instructions

This guide shows how to build the Blender wheel **locally** without AWS.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04+ / Debian 11+ (or similar Linux)
- **CPU**: Multi-core recommended (build uses all cores)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: ~20GB free space
- **Time**: 45-60 minutes

### Required Software
- Python 3.12
- Git
- Sudo privileges (for installing dependencies)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/darkrelics/blender-wheel.git
cd blender-wheel
```

### 2. Run the Build Script

```bash
./build_blender_wheel.sh
```

The script will:
1. Install build dependencies (asks for sudo)
2. Clone Blender source code
3. Build Blender Python module (~45-60 min)
4. Generate Python wheel
5. Create checksums (SHA256, MD5)

### 3. Install the Wheel

```bash
pip install output/blender_bpy_module-4.4.whl
```

### 4. Verify Installation

```bash
python -c "import bpy; print(f'Blender {bpy.app.version_string}')"
```

Expected output: `Blender 4.4.0`

---

## Customization

### Environment Variables

Customize the build with environment variables:

```bash
# Use different Blender repository
export BLENDER_REPO_URL="https://github.com/blender/blender.git"

# Use different Python version
export PYTHON_VERSION="3.11"

# Change output directory
export OUTPUT_DIR="$HOME/blender-builds"

# Run the build
./build_blender_wheel.sh
```

### Manual Build Steps

If you prefer to run steps manually, see the script contents. Each phase is clearly marked:

1. **Phase 1**: Install dependencies
2. **Phase 2**: Clone and prepare source
3. **Phase 3**: Build Blender module
4. **Phase 4**: Generate wheel
5. **Phase 5**: Generate checksums

---

## Docker Build

For a fully isolated build environment:

```bash
# Build using Docker
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  bash -c "apt-get update && apt-get install -y sudo && ./build_blender_wheel.sh"
```

Or create a Dockerfile:

```dockerfile
FROM ubuntu:22.04

# Install base dependencies
RUN apt-get update && \
    apt-get install -y sudo git && \
    rm -rf /var/lib/apt/lists/*

# Copy build script
COPY build_blender_wheel.sh /build/
WORKDIR /build

# Run build
RUN chmod +x build_blender_wheel.sh && \
    ./build_blender_wheel.sh

# Output will be in /build/output/
```

Build the Docker image:
```bash
docker build -t blender-wheel-builder .
docker create --name temp-builder blender-wheel-builder
docker cp temp-builder:/build/output/blender_bpy_module-4.4.whl .
docker rm temp-builder
```

---

## Using in CI/CD

### GitHub Actions

```yaml
name: Build Blender Wheel

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - uses: actions/checkout@v4

    - name: Build Blender Wheel
      run: |
        chmod +x build_blender_wheel.sh
        ./build_blender_wheel.sh

    - name: Upload Wheel
      uses: actions/upload-artifact@v4
      with:
        name: blender-wheel
        path: output/blender_bpy_module-4.4.whl

    - name: Upload Checksums
      uses: actions/upload-artifact@v4
      with:
        name: checksums
        path: |
          output/*.sha256
          output/*.md5
```

### GitLab CI

```yaml
build-wheel:
  image: ubuntu:22.04

  before_script:
    - apt-get update
    - apt-get install -y sudo git

  script:
    - chmod +x build_blender_wheel.sh
    - ./build_blender_wheel.sh

  artifacts:
    paths:
      - output/blender_bpy_module-4.4.whl
      - output/*.sha256
      - output/*.md5
    expire_in: 1 week

  timeout: 2h
```

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh '''
                    chmod +x build_blender_wheel.sh
                    ./build_blender_wheel.sh
                '''
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'output/*.whl,output/*.sha256,output/*.md5'
            }
        }
    }
}
```

---

## Troubleshooting

### Build Fails: Missing Dependencies

**Error**: `Package 'xxx' has no installation candidate`

**Solution**: Update package lists first:
```bash
sudo apt-get update
sudo apt-get upgrade
```

### Build Fails: Out of Memory

**Error**: `c++: fatal error: Killed signal terminated program cc1plus`

**Solution**: Reduce parallel jobs:
```bash
# Edit build_blender_wheel.sh, line with "make bpy"
make bpy -j2  # Instead of -j$(nproc)
```

Or add swap space:
```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Build Fails: Python Version

**Error**: `python3.12: command not found`

**Solution**: Install Python 3.12:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.12 python3.12-dev python3.12-distutils
```

### Build Takes Forever

**Expected**: 45-60 minutes on 4-core CPU

**To speed up**:
- Use more CPU cores (the script auto-detects)
- Use faster SSD storage
- Use a more powerful machine

### Wheel Size is Huge

**Expected**: 500MB - 1.5GB

This is normal - Blender includes:
- Full rendering engine
- Python bindings
- All dependencies

---

## Comparison: Local vs AWS

| Aspect | Local Build | AWS CodeBuild |
|--------|-------------|---------------|
| **Cost** | Free (your hardware) | ~$0.50-$2 per build |
| **Speed** | Depends on your CPU | Consistent (BUILD_GENERAL1_LARGE) |
| **Setup** | Simple script | CloudFormation stack |
| **Dependencies** | Install on your machine | Managed by AWS |
| **Reproducibility** | Varies by system | Highly consistent |
| **Storage** | Local disk | S3 bucket |
| **Best For** | Personal use, testing | Team use, automation |

---

## Next Steps

After building:

1. **Install the wheel**: `pip install output/blender_bpy_module-4.4.whl`
2. **Run demos**: See [GETTING_STARTED.md](GETTING_STARTED.md)
3. **Generate assets**: `python blender-demo/generate_scene_assets.py`

---

## Additional Resources

- **Build Script**: `build_blender_wheel.sh`
- **AWS BuildSpec**: `buildspec.yml/blender-whl.yml` (same steps, different format)
- **Blender Build Docs**: https://developer.blender.org/docs/handbook/building_blender/
- **Python Module Docs**: https://developer.blender.org/docs/handbook/building_blender/python_module/

---

**Questions?** Open an issue: https://github.com/darkrelics/blender-wheel/issues
