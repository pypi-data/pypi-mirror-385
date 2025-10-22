FROM python:3.11-slim

WORKDIR /workspace

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e .

# Default command
CMD ["bash"]
