# Use the official NVIDIA CUDA 11.6.1 development image as the base
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
    nano \
    curl \
    build-essential \
    pkg-config \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools

# Create a working directory inside the container
WORKDIR /app

# Set environment variable so that the virtual environment is used by default
ENV PYTHONPATH="/app/xmr4el"

# Verify installation
RUN python3 --version && pip --version

# Default command
CMD ["/bin/bash"]
