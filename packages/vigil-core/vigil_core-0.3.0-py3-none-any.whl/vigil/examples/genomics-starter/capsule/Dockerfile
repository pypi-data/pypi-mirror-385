# Genomics Capsule - Reproducible NGS Analysis Environment
# Base image: Python 3.11 with essential system libraries
FROM python:3.11-slim-bookworm

LABEL maintainer="Science Abundance <info@scienceabundance.org>"
LABEL description="Genomics analysis capsule with NGS tools and Python libraries"
LABEL version="1.0.0"

# Install system dependencies and genomics tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    ca-certificates \
    curl \
    git \
    wget \
    # Compression tools
    bzip2 \
    gzip \
    xz-utils \
    zlib1g-dev \
    # NGS tools
    samtools \
    bcftools \
    tabix \
    bedtools \
    # Other utilities
    vim \
    less \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy Python requirements
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Add genomics-specific environment variables
ENV BCFTOOLS_PLUGINS=/usr/lib/x86_64-linux-gnu/bcftools
ENV SAMTOOLS_VERSION=1.18
ENV BCFTOOLS_VERSION=1.18

# Create standard directories
RUN mkdir -p /workspace/data \
    /workspace/results \
    /workspace/logs \
    /workspace/.cache

# Set user to non-root for security
RUN useradd -m -u 1000 vigil && \
    chown -R vigil:vigil /workspace

USER vigil

# Default command
CMD ["/bin/bash"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Metadata
LABEL org.opencontainers.image.title="Vigil Genomics Capsule"
LABEL org.opencontainers.image.description="Containerized genomics analysis environment"
LABEL org.opencontainers.image.vendor="Science Abundance"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/science-abundance/vigil"
