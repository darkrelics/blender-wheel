# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

1. **Email**: Send details to the project maintainers (create an issue with "SECURITY" in title for contact)
2. **Include**:
   - Type of vulnerability
   - Affected component (build script, CloudFormation, demo code)
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: Next release cycle

### Disclosure Policy

- We follow responsible disclosure
- Vulnerabilities will be publicly disclosed after a fix is available
- Security advisories will be published on GitHub Security Advisories
- Credit will be given to reporters (unless they prefer to remain anonymous)

---

## Known Security Considerations

### Build Script Security Risks

⚠️ **The build script runs arbitrary code from the internet as root**

**Affected**: `build_blender_wheel.sh` and AWS CodeBuild

**Risk**:
```bash
# The script clones a git repository
git clone "$BLENDER_REPO_URL" blender-source

# Then runs Python scripts from it as root
sudo ./build_files/build_environment/install_linux_packages.py --all
```

**Mitigation**:
- Only use official Blender repository: `https://projects.blender.org/blender/blender.git`
- Verify `BLENDER_REPO_URL` before running script
- Consider running in isolated environment (Docker/VM)
- Script warns users about this risk

**Future Improvements**:
- [ ] Add GPG signature verification for Blender source
- [ ] Use Docker for build isolation
- [ ] Add checksum verification for dependencies

### CloudFormation IAM Permissions

**Risk**: CodeBuild has permissions to S3 and CloudWatch

**Current Permissions**:
- `s3:PutObject`
- `s3:GetObject`
- `s3:ListBucket`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

**Mitigation**:
- Permissions follow principle of least privilege
- Limited to specific S3 bucket
- No overly broad permissions

### Demo Scripts

**Risk**: Demo scripts execute Blender operations

**Mitigation**:
- All demos are read-only on the system
- No network access required
- All file operations are to user-specified output directories
- Error handling prevents crashes

### Dependencies

**Risk**: Python dependencies could have vulnerabilities

**Current Dependencies**:
- `numpy==1.26.4` (pinned)
- `pillow==10.3.0` (pinned)
- Dev: `pytest`, `pytest-cov`, `ruff`

**Mitigation**:
- All versions pinned for reproducibility
- Dependencies reviewed before updates
- Regular Dependabot alerts enabled

---

## Security Best Practices for Users

### Running the Build Script

1. **Review the script** before running:
   ```bash
   cat build_blender_wheel.sh
   ```

2. **Verify repository URL**:
   ```bash
   echo $BLENDER_REPO_URL  # Should be official Blender repo
   ```

3. **Run in isolated environment**:
   ```bash
   # Use Docker for isolation
   docker run -it --rm -v $(pwd):/workspace -w /workspace ubuntu:22.04 \
     bash -c "./build_blender_wheel.sh --yes"
   ```

4. **Check wheel integrity**:
   ```bash
   sha256sum -c blender_bpy_module-4.4.whl.sha256
   ```

### AWS Deployment

1. **Use least-privilege IAM**:
   - Review CloudFormation template before deploying
   - Create dedicated S3 bucket (don't use existing buckets with sensitive data)
   - Use separate AWS account for builds if possible

2. **Monitor builds**:
   - Review CloudWatch logs
   - Set up CloudWatch alarms for failures
   - Monitor S3 bucket access

3. **Secure artifacts**:
   - Enable S3 versioning
   - Enable S3 encryption at rest
   - Set up bucket policies to restrict access

### Using the Built Wheel

1. **Verify before installing**:
   ```bash
   sha256sum -c blender_bpy_module-4.4.whl.sha256
   pip install --require-hashes blender_bpy_module-4.4.whl
   ```

2. **Use in virtual environment**:
   ```bash
   python -m venv blender_env
   source blender_env/bin/activate
   pip install blender_bpy_module-4.4.whl
   ```

3. **Scan for vulnerabilities**:
   ```bash
   pip install safety
   safety check
   ```

---

## Security Checklist for Contributors

Before submitting code:

- [ ] No hardcoded credentials or secrets
- [ ] Input validation for all user-provided data
- [ ] Proper error handling (no silent failures)
- [ ] File operations use safe paths (no path traversal)
- [ ] Shell commands are properly escaped
- [ ] No use of `eval()` or similar dangerous functions
- [ ] Dependencies are pinned and reviewed

---

## Security Tools

### Recommended Tools

**For scanning code**:
```bash
# Install security scanners
pip install bandit safety

# Scan Python code for security issues
bandit -r blender-demo/

# Check dependencies for known vulnerabilities
safety check
```

**For Docker builds**:
```bash
# Scan Docker images
docker scan blender-wheel-builder
```

**For AWS**:
```bash
# Validate CloudFormation templates
cfn-lint cf/codebuild.yml

# Check for security issues
cfn-nag cf/codebuild.yml
```

---

## Past Security Issues

### v1.0.0 (2025-11-13)

**Fixed Issues**:
1. **Overly permissive S3 IAM policy**: Changed from `s3:*` to specific actions
2. **Missing input validation**: Added validation to critical functions
3. **Unsafe rm -rf**: Added safety checks before deletion

**Details**: See FIXES_SUMMARY.md

---

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 1.0.1)
- Documented in CHANGELOG.md
- Announced in GitHub Security Advisories
- Tagged with `security` label in releases

---

## Contact

For security concerns, please:
1. Open a GitHub issue with "SECURITY" in the title
2. Project maintainers will provide secure communication channel
3. Do not disclose details publicly until fix is available

---

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be recognized in:
- Security advisories
- CHANGELOG.md
- Release notes

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
