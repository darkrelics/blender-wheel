# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-04

### Added
- Automated testing infrastructure with pytest
- Project metadata in `pyproject.toml`
- Test suite covering imports, configuration validation, and unit tests
- Development dependencies for testing and code quality
- CHANGELOG.md for tracking changes
- Comprehensive project review documentation

### Fixed
- **CRITICAL**: Renamed `demo,py` to `demo.py` (filename typo)
- **CRITICAL**: Fixed CloudFormation template variable reference (`${S3BucketName}` → `${OutputBucketName}`)
- **SECURITY**: Restricted S3 IAM permissions from `s3:*` to specific actions (`s3:PutObject`, `s3:GetObject`, `s3:ListBucket`)

### Changed
- Pinned dependencies in `requirements.txt` for reproducibility (numpy==1.26.4, pillow==10.3.0)
- Updated README.md with correct file paths and development instructions

### Security
- Reduced IAM policy permissions to principle of least privilege
- Pinned all dependency versions to prevent supply chain attacks

## [0.1.0] - 2025-11-01

### Added
- Initial project setup for building Blender 4.4 as Python wheel
- AWS CodeBuild infrastructure with CloudFormation
- Demo applications (basic, animation, materials, batch rendering)
- Utility functions for common Blender operations
- Apache 2.0 license
- README documentation
