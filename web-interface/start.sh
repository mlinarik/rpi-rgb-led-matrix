#!/bin/bash

# LED Matrix Web Interface Startup Script
# This script builds and runs the LED matrix web interface container

set -e

echo "🎨 LED Matrix Web Interface Setup"
echo "================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi."
    echo "   The LED matrix may not work properly."
fi

# Check if /data/gifs directory exists
if [ ! -d "/data/gifs" ]; then
    echo "📁 Creating /data/gifs directory..."
    sudo mkdir -p /data/gifs
    sudo chmod 755 /data/gifs
    echo "   Directory created. Place your GIF files in /data/gifs/"
fi

# Check if there are any GIFs in the directory
gif_count=$(find /data/gifs -name "*.gif" -type f 2>/dev/null | wc -l)
if [ "$gif_count" -eq 0 ]; then
    echo "⚠️  Warning: No GIF files found in /data/gifs"
    echo "   Please add some GIF files to display"
else
    echo "✅ Found $gif_count GIF file(s) in /data/gifs"
fi

# Build and start the container
echo "🐳 Building Docker container..."
docker-compose build

echo "🚀 Starting LED Matrix Web Interface..."
docker-compose up -d

# Wait a moment for the service to start
sleep 3

# Check if the container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ LED Matrix Web Interface is running!"
    echo ""
    echo "🌐 Access the web interface at:"
    echo "   http://localhost:5000"
    echo "   http://$(hostname -I | cut -d' ' -f1):5000"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop service: docker-compose down"
    echo "   Restart: docker-compose restart"
else
    echo "❌ Failed to start the container. Check the logs:"
    docker-compose logs
    exit 1
fi