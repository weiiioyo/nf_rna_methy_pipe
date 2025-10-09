# Docker Build and Deployment Guide

This project contains automated Docker image build and check workflows.

## Automated Workflows

### GitHub Actions Workflows

The project includes the following GitHub Actions workflows:

1. **Docker Build & Test** (`.github/workflows/docker-build.yml`)
   - Automatically build Docker images
   - Run security scans (Trivy)
   - Execute quality checks
   - Push images to GitHub Container Registry

2. **Dockerfile Lint** (`.github/workflows/docker-lint.yml`)
   - Check Dockerfile syntax using Hadolint
   - Upload check results to GitHub Security tab

### Trigger Conditions

Workflows are automatically triggered in the following cases:
- Push to `main`, `master`, or `develop` branches
- Create Pull Requests to these branches
- Manual trigger (workflow_dispatch)

## Local Development and Testing

### Testing with Docker Compose

```bash
# Test base image
docker-compose -f docker-compose.test.yml --profile test up test-base

# Test SeekSoulMethyl image
docker-compose -f docker-compose.test.yml --profile test up test-seeksoulmethy

# Start development environment (base image)
docker-compose -f docker-compose.test.yml --profile dev up -d dev-base

# Start development environment (SeekSoulMethyl image)
docker-compose -f docker-compose.test.yml --profile dev up -d dev-seeksoulmethy
```

### Manual Image Building

```bash
# Build base image
docker build -f dockfile/Dockerfile -t nf-rna-methy-pipe:base .

# Build SeekSoulMethyl image
docker build -f dockfile/Dockerfile.env_seeksoulmethy -t nf-rna-methy-pipe:seeksoulmethy .
```

### Local Dockerfile Checking

```bash
# Install Hadolint
# macOS: brew install hadolint
# Linux: Download binary or use Docker

# Check Dockerfile
hadolint dockfile/Dockerfile
hadolint dockfile/Dockerfile.env_seeksoulmethy
```

## Image Registry

Built images are automatically pushed to GitHub Container Registry:
- `ghcr.io/[username]/nf-rna-methy-pipe:base`
- `ghcr.io/[username]/nf-rna-methy-pipe:seeksoulmethy`

## Security Scanning

The project uses Trivy for security vulnerability scanning:
- Scan results are uploaded to GitHub Security tab
- Build fails when high-severity vulnerabilities are found

## Configuration Files

- `.dockerignore`: Defines files to ignore during build
- `.hadolint.yaml`: Hadolint check rules configuration
- `docker-compose.test.yml`: Local testing and development configuration

## Troubleshooting

### Common Issues

1. **Build Failure**
   - Check Dockerfile syntax
   - Confirm base image availability
   - Review GitHub Actions logs

2. **Security Scan Failure**
   - Update base image versions
   - Fix known vulnerabilities
   - Review Trivy scan reports

3. **Push Failure**
   - Confirm GitHub token permissions
   - Check repository settings
   - Verify image tag format

### Debug Commands

```bash
# View image information
docker images
docker inspect <image_name>

# Run container for debugging
docker run -it --rm <image_name> /bin/bash

# View build history
docker history <image_name>
```