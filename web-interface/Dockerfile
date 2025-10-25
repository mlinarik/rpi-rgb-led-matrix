FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgraphicsmagick++-dev \
    libwebp-dev \
    sudo \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone and build the RGB LED Matrix library
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix
WORKDIR /opt/rpi-rgb-led-matrix
RUN make -C lib && make -C utils

# Copy application files
WORKDIR /app
COPY . .

# Create data directory for GIFs
RUN mkdir -p /data/gifs

# Create a non-root user but allow sudo for GPIO access
RUN useradd -m -s /bin/bash leduser && \
    echo "leduser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Set proper permissions
RUN chown -R leduser:leduser /app /data/gifs
USER leduser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/status || exit 1

# Start the application
CMD ["python", "app.py"]