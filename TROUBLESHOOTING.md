# Troubleshooting Guide

This guide covers common issues and solutions for building and using the Blender wheel package.

---

## Table of Contents

1. [Build Issues](#build-issues)
2. [Installation Issues](#installation-issues)
3. [Runtime Issues](#runtime-issues)
4. [AWS Build Issues](#aws-build-issues)
5. [Performance Issues](#performance-issues)
6. [Getting Help](#getting-help)

---

## Build Issues

### Build Fails: "Insufficient disk space"

**Symptom:**
```
ERROR: Insufficient disk space!
  Required: 25GB
  Available: 15GB
```

**Solution:**
- Free up at least 25GB of disk space before starting the build
- Delete temporary files: `sudo apt clean && rm -rf ~/.cache/*`
- Check disk usage: `df -h`

---

### Build Fails: "python3.12-distutils" Package Not Found

**Symptom:**
```
E: Package 'python3.12-distutils' has no installation candidate
```

**Solution:**
This is expected! The build script no longer tries to install `python3.12-distutils` (removed in Python 3.12 per PEP 632). If you see this error, you may be using an outdated version of the build script. Pull the latest changes:

```bash
git pull origin main
```

---

### Build Fails: Commit Hash Mismatch

**Symptom:**
```
ERROR: Commit hash mismatch!
  Expected: abc123...
  Actual:   def456...
```

**Solution:**
This security check prevents building from unexpected Blender source. Either:

1. **Update the commit hash** to the latest:
   ```bash
   # Get current commit from official Blender repo
   git ls-remote https://projects.blender.org/blender/blender.git HEAD
   BLENDER_COMMIT_HASH=<new_hash> ./build_blender_wheel.sh --yes
   ```

2. **Skip verification** (not recommended):
   ```bash
   # Build without commit verification
   unset BLENDER_COMMIT_HASH
   ./build_blender_wheel.sh --yes
   ```

---

### Build Hangs at "Cloning Blender source"

**Symptom:**
Build appears frozen during git clone phase.

**Solution:**
- Check internet connection
- Blender repository is large (~2GB); may take 5-10 minutes on slow connections
- Try with verbose git output:
  ```bash
  export GIT_CURL_VERBOSE=1
  ./build_blender_wheel.sh --yes
  ```

---

### Build Fails: "make: *** [bpy] Error 2"

**Symptom:**
Compilation fails with C++ errors.

**Common Causes:**

1. **Insufficient RAM**
   - Blender compilation requires ~4GB+ RAM
   - Solution: Reduce parallel jobs
     ```bash
     # Instead of make bpy -j$(nproc), manually limit:
     make bpy -j2
     ```

2. **Missing dependencies**
   - Solution: Re-run dependency installation
     ```bash
     cd blender-source
     sudo ./build_files/build_environment/install_linux_packages.py --all
     ```

3. **Incompatible GCC version**
   - Blender requires GCC 9+
   - Check: `gcc --version`
   - Solution: Update build tools
     ```bash
     sudo apt install gcc-11 g++-11
     sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
     ```

---

### Build Succeeds But Verification Fails

**Symptom:**
```
✗ Wheel verification FAILED - cannot import bpy
```

**Solution:**

1. **Check Python version mismatch**
   ```bash
   python3.12 --version  # Ensure 3.12 is installed
   ```

2. **Check wheel filename**
   ```bash
   ls output/  # Should see blender_bpy_module-*.whl
   ```

3. **Manual verification**
   ```bash
   cd output
   python3.12 -m venv test_env
   source test_env/bin/activate
   pip install blender_bpy_module-*.whl
   python -c "import bpy; print(bpy.app.version_string)"
   ```

4. **Check for missing system libraries**
   ```bash
   ldd output/test_env/lib/python3.12/site-packages/bpy.so
   # Look for "not found" entries
   ```

---

## Installation Issues

### "ERROR: Could not find a version that satisfies the requirement"

**Symptom:**
```bash
pip install blender_bpy_module-4.4.0.whl
ERROR: blender_bpy_module-4.4.0.whl is not a supported wheel on this platform.
```

**Solution:**
- Wheel is built for Linux only (x86_64)
- For Windows/macOS: Use WSL (Windows) or consider Docker
- Check platform: `python -c "import platform; print(platform.system(), platform.machine())"`

---

### "ImportError: libGL.so.1: cannot open shared object file"

**Symptom:**
```python
import bpy
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

**Solution:**
Install OpenGL libraries:
```bash
sudo apt install libgl1-mesa-glx libglu1-mesa
```

For headless servers (no X11):
```bash
sudo apt install xvfb
xvfb-run python your_script.py
```

---

### "ImportError: No module named 'numpy'"

**Symptom:**
```python
import bpy
ImportError: No module named 'numpy'
```

**Solution:**
Install required dependencies:
```bash
pip install numpy==1.26.4 pillow==10.3.0
```

Or install from requirements:
```bash
pip install -r blender-demo/requirements.txt
```

---

## Runtime Issues

### Renders Are Blank/Black

**Common Causes:**

1. **No lights in scene**
   ```python
   import bpy
   # Add a sun light
   bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
   bpy.context.active_object.data.energy = 5.0
   ```

2. **Camera not set**
   ```python
   # Check if camera is active
   if bpy.context.scene.camera is None:
       print("No active camera!")
       # Set a camera
       camera = bpy.data.objects.get('Camera')
       if camera:
           bpy.context.scene.camera = camera
   ```

3. **Render engine not set**
   ```python
   bpy.context.scene.render.engine = 'CYCLES'
   ```

---

### "RuntimeError: Error: Cannot read file"

**Symptom:**
```python
bpy.ops.render.render(write_still=True)
RuntimeError: Error: Cannot read file '/path/to/output.png'
```

**Solution:**
1. **Ensure output directory exists**
   ```python
   import os
   os.makedirs('/path/to/output', exist_ok=True)
   ```

2. **Set render filepath**
   ```python
   bpy.context.scene.render.filepath = '/path/to/output.png'
   ```

3. **Check file permissions**
   ```bash
   ls -la /path/to/output/
   chmod 755 /path/to/output
   ```

---

### Rendering Is Very Slow

**Solutions:**

1. **Reduce render samples** (preview quality)
   ```python
   bpy.context.scene.cycles.samples = 32  # Default is 128+
   ```

2. **Reduce resolution**
   ```python
   bpy.context.scene.render.resolution_percentage = 50  # 50% of set resolution
   ```

3. **Enable denoising**
   ```python
   bpy.context.scene.cycles.use_denoising = True
   ```

4. **Use GPU rendering** (if available)
   ```python
   bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'  # or 'OPTIX'
   bpy.context.scene.cycles.device = 'GPU'
   ```

---

### "bpy.ops.*.* failed with result {'CANCELLED'}"

**Symptom:**
```python
result = bpy.ops.object.light_add(type='SUN')
print(result)  # {'CANCELLED'}
```

**Solution:**
Ensure context is correct:
```python
# Check if in correct mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Ensure scene exists
if bpy.context.scene is None:
    print("No active scene!")
```

Use the safe operation helper:
```python
from scripts.utils import safe_ops_call

# This will raise RuntimeError with details if it fails
light = safe_ops_call(bpy.ops.object.light_add, 'LIGHT', type='SUN', location=(0, 0, 5))
```

---

## AWS Build Issues

### CloudFormation Stack Creation Fails

**Symptom:**
```
CREATE_FAILED: Resource handler returned message: "Invalid request provided: ..."
```

**Common Causes:**

1. **S3 bucket doesn't exist**
   - Create bucket first: `aws s3 mb s3://your-bucket-name`

2. **Missing IAM permissions**
   - Ensure your AWS user has CloudFormation, CodeBuild, and IAM permissions
   - Required policies: `iam:CreateRole`, `codebuild:CreateProject`, `cloudformation:CreateStack`

3. **Invalid parameter values**
   - Check GitHub URL format: `https://github.com/user/repo.git`
   - Verify S3 bucket name follows AWS naming rules (lowercase, no underscores)

---

### CodeBuild Fails: "BuildSpec not found"

**Symptom:**
```
BUILD_PHASE_FAILURE: YAML_FILE_ERROR Message: YAML file does not exist
```

**Solution:**
This was a known issue (now fixed). Update CloudFormation template:
```yaml
# In cf/codebuild.yml, ensure BuildSpec points to correct path:
BuildSpec: buildspec.yml/blender-whl.yml
```

If using older template, update your stack:
```bash
aws cloudformation update-stack \
  --stack-name blender-wheel-build \
  --template-body file://cf/codebuild.yml \
  --parameters (same as before) \
  --capabilities CAPABILITY_IAM
```

---

### CodeBuild Times Out After 60 Minutes

**Symptom:**
```
BUILD_TIMEOUT: Build timed out after 60 minutes
```

**Solution:**
Increase timeout in CloudFormation template:
```yaml
# cf/codebuild.yml
BlenderWhlBuildProject:
  Type: AWS::CodeBuild::Project
  Properties:
    TimeoutInMinutes: 90  # Increase from 60
```

Or use larger compute instance for faster builds:
```yaml
Environment:
  ComputeType: BUILD_GENERAL1_2XLARGE  # Instead of BUILD_GENERAL1_LARGE
```

---

### Cannot Download Wheel from S3

**Symptom:**
```bash
aws s3 cp s3://my-bucket/blender_bpy_module.whl .
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
```

**Solution:**

1. **Check S3 permissions**
   ```bash
   aws s3 ls s3://my-bucket/  # Verify you can list bucket
   ```

2. **Verify file exists**
   - Check CodeBuild logs to confirm build succeeded
   - File location: `s3://bucket-name/blender_bpy_module-<version>.whl`

3. **Update IAM policy**
   ```json
   {
     "Effect": "Allow",
     "Action": ["s3:GetObject"],
     "Resource": "arn:aws:s3:::my-bucket/*"
   }
   ```

---

## Performance Issues

### Build Takes Longer Than Expected

**Expected Times:**
- Local build (4 cores): 50-70 minutes
- AWS CodeBuild (LARGE): 45-60 minutes
- AWS CodeBuild (2XLARGE): 30-40 minutes

**If significantly slower:**

1. **Check CPU usage**
   ```bash
   top  # During build, ensure high CPU usage (300%+ for 4 cores)
   ```

2. **Check I/O wait**
   ```bash
   iostat -x 5  # Look for high %iowait
   ```
   - If high: Consider using faster storage (SSD vs HDD)

3. **Network speed** (for git clone phase)
   ```bash
   # Test download speed
   wget -O /dev/null https://projects.blender.org/blender/blender.git
   ```

---

### Demo Scripts Run Slowly

**Benchmarks (1920x1080, 50%, 128 samples, 4-core CPU):**
- demo.py: 15-25 seconds
- animation_demo.py: 20-35 seconds per frame
- materials_demo.py: 25-45 seconds
- generate_scene_assets.py: 30-60 seconds

**If significantly slower:**

1. **Reduce samples for testing**
   ```python
   bpy.context.scene.cycles.samples = 32  # Fast preview
   ```

2. **Check render device**
   ```python
   print(bpy.context.scene.cycles.device)  # Should use GPU if available
   ```

3. **Monitor system resources**
   ```bash
   # CPU usage should be near 100% during rendering
   htop
   ```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review error messages carefully** - they often indicate the exact issue
3. **Search existing issues**: https://github.com/darkrelics/blender-wheel/issues
4. **Try with minimal example** - isolate the problem

### When Reporting Issues

Include:

1. **System information**
   ```bash
   uname -a
   python --version
   gcc --version
   df -h  # Disk space
   free -h  # RAM
   ```

2. **Build command used**
   ```bash
   ./build_blender_wheel.sh --yes  # or AWS stack params
   ```

3. **Error message** (full output)
   ```bash
   # Save full output to file
   ./build_blender_wheel.sh --yes 2>&1 | tee build.log
   ```

4. **Blender wheel version**
   ```bash
   ls output/blender_bpy_module-*.whl
   ```

5. **Python environment**
   ```bash
   pip list  # Show installed packages
   ```

### Getting Help

- **GitHub Issues**: https://github.com/darkrelics/blender-wheel/issues
- **Documentation**: See README.md, GETTING_STARTED.md, LOCAL_BUILD.md
- **Contributing**: See CONTRIBUTING.md for development setup

---

## Known Limitations

1. **Linux Only**: The wheel is built for Linux x86_64 only
   - Windows users: Use WSL or Docker
   - macOS users: Contribution welcome for macOS build script

2. **Python 3.12**: Wheel is built for Python 3.12
   - Other versions: Rebuild with `PYTHON_VERSION=3.11 ./build_blender_wheel.sh`

3. **Build Time**: Compiling Blender takes 45-60 minutes minimum
   - No incremental builds currently supported
   - Consider using pre-built wheels if available

4. **Disk Space**: Requires ~25GB during build
   - Temporary: 20GB (blender-source directory)
   - Final wheel: 200-400MB

5. **No GUI**: Blender built as Python module doesn't include GUI
   - Use for headless rendering and automation only
   - For interactive work, use Blender desktop application

---

## Quick Reference

### Build Commands

```bash
# Local build (interactive)
./build_blender_wheel.sh

# Local build (CI/CD - no prompts)
./build_blender_wheel.sh --yes

# Build with specific Python version
PYTHON_VERSION=3.11 ./build_blender_wheel.sh --yes

# Build with commit verification (secure)
BLENDER_COMMIT_HASH=abc123... ./build_blender_wheel.sh --yes

# Build to custom output directory
OUTPUT_DIR=/custom/path ./build_blender_wheel.sh --yes
```

### Installation Commands

```bash
# Install wheel
pip install output/blender_bpy_module-*.whl

# Install with dependencies
pip install output/blender_bpy_module-*.whl -r blender-demo/requirements.txt

# Verify installation
python -c "import bpy; print(bpy.app.version_string)"
```

### Running Demos

```bash
# Run from blender-demo directory
cd blender-demo
python demo.py

# Or set PYTHONPATH
PYTHONPATH=blender-demo python blender-demo/demo.py
```

---

**Last Updated**: 2025-11-16
**Version**: 1.0.0
