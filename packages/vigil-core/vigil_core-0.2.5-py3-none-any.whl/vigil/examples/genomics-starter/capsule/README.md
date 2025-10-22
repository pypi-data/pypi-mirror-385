# Genomics Capsule - Container Build Instructions

This directory contains the recipe for building the genomics analysis capsule (Docker container) used by Vigil for reproducible NGS workflows.

## What's Included

### System Tools
- **samtools** (v1.18): SAM/BAM/CRAM manipulation
- **bcftools** (v1.18): VCF/BCF manipulation
- **tabix**: Indexing for compressed files
- **bedtools**: Genome arithmetic operations

### Python Libraries
- **pandas, numpy, pyarrow**: Data manipulation and Parquet support
- **pysam**: Python interface to samtools/bcftools
- **cyvcf2**: Fast VCF parsing
- **biopython**: Sequence analysis tools
- **snakemake**: Workflow management
- **scikit-learn, scipy**: Statistical analysis and machine learning

## Building the Capsule

### Option 1: Local Build

```bash
# From this directory
docker build -t genomics-capsule:latest .

# Tag for your organization
docker tag genomics-capsule:latest ghcr.io/YOUR_ORG/genomics-capsule:v1.0.0

# Push to registry
docker push ghcr.io/YOUR_ORG/genomics-capsule:v1.0.0

# Get the digest
docker inspect ghcr.io/YOUR_ORG/genomics-capsule:v1.0.0 --format='{{.RepoDigests}}'
```

### Option 2: GitHub Actions (Recommended)

Create `.github/workflows/build-capsule.yml`:

```yaml
name: Build Genomics Capsule

on:
  push:
    branches: [main]
    paths:
      - 'capsule/**'
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/genomics-capsule
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./capsule
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}/genomics-capsule:latest
          format: spdx-json
          output-file: sbom.spdx.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json
```

## Updating vigil.yaml

After building and pushing, update `vigil.yaml` with the digest:

```yaml
capsule:
  image: ghcr.io/YOUR_ORG/genomics-capsule@sha256:ACTUAL_DIGEST_HERE
  extensions:
    - ms-python.python@2024.6.0
```

**Important**: Always use the digest (`@sha256:...`), not tags (`:v1.0.0` or `:latest`), to ensure reproducibility.

## Testing the Capsule

```bash
# Run interactively
docker run -it --rm -v $(pwd):/workspace genomics-capsule:latest bash

# Test samtools
docker run --rm genomics-capsule:latest samtools --version

# Test bcftools
docker run --rm genomics-capsule:latest bcftools --version

# Test Python environment
docker run --rm genomics-capsule:latest python3 -c "import pandas, pysam; print('OK')"
```

## Customizing the Capsule

### Adding New Tools

Edit `Dockerfile` to add more genomics tools:

```dockerfile
RUN apt-get update && apt-get install -y \
    samtools \
    bcftools \
    # Add your tools here
    bwa \           # Alignment
    gatk \          # Variant calling
    picard-tools \  # BAM manipulation
    && rm -rf /var/lib/apt/lists/*
```

### Adding Python Packages

Edit `requirements.txt`:

```
# Add your packages
scikit-bio>=0.6.0
intervaltree>=3.1.0
pybedtools>=0.9.0
```

### Adding Custom Scripts

Create a `scripts/` directory and copy it into the container:

```dockerfile
COPY scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*.py
```

## Size Optimization

The base image is ~500MB. To reduce size:

### 1. Use Multi-Stage Builds

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim-bookworm AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim-bookworm
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

### 2. Clean Up APT Cache

```dockerfile
RUN apt-get update && apt-get install -y ... \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
```

### 3. Use Smaller Base Images

```dockerfile
# Instead of python:3.11-slim (130MB)
FROM python:3.11-alpine (50MB)

# Trade-off: Alpine requires more work for genomics tools
```

## Security Best Practices

### 1. Run as Non-Root User

Already implemented:

```dockerfile
RUN useradd -m -u 1000 vigil
USER vigil
```

### 2. Scan for Vulnerabilities

```bash
# Install Trivy
brew install trivy

# Scan image
trivy image genomics-capsule:latest

# Scan in CI/CD
- name: Scan for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/${{ github.repository }}/genomics-capsule:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### 3. Pin Base Image Digest

```dockerfile
# Instead of: FROM python:3.11-slim-bookworm
FROM python:3.11-slim-bookworm@sha256:DIGEST_HERE
```

## Troubleshooting

### Issue: Capsule image not found

**Error**: `Error response from daemon: pull access denied`

**Solution**: Make sure you're logged in to the container registry:

```bash
docker login ghcr.io -u YOUR_USERNAME
# Or use GitHub token:
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Issue: Permission denied in container

**Error**: `Permission denied: '/workspace/data'`

**Solution**: The container runs as user `vigil` (UID 1000). Make sure your local files are accessible:

```bash
# Option 1: Run as root (not recommended)
docker run --user root ...

# Option 2: Change ownership (recommended)
chown -R 1000:1000 /path/to/data

# Option 3: Run with your UID
docker run --user $(id -u):$(id -g) ...
```

### Issue: Out of memory

**Error**: `Killed` or `Out of memory`

**Solution**: Increase Docker memory limit:

```bash
# Docker Desktop: Settings → Resources → Memory
# Or run with explicit limit:
docker run --memory=16g ...
```

## Advanced: GPU Support

For GPU-accelerated tools (e.g., DeepVariant, Parabricks):

```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Install CUDA-aware tools
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    && rm -rf /var/lib/apt/lists/*
```

Run with GPU:

```bash
docker run --gpus all genomics-capsule:latest nvidia-smi
```

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Genomics in Docker](https://bio-it.embl.de/software/docker-containers/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Trivy Security Scanning](https://aquasecurity.github.io/trivy/)

## License

Apache-2.0
