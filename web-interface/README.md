# LED Matrix Web Interface

A web-based interface for controlling the RGB LED matrix display remotely. This allows you to select GIF files and adjust brightness settings from any web browser.

## Features

- 🎨 **Web-based Control**: Access from any device with a web browser
- 📁 **GIF Selection**: Browse and select from available GIF files
- 🔆 **Brightness Control**: Adjust LED brightness from 1-100%
- ⚡ **Real-time Status**: Live status updates and process monitoring
- 🐳 **Docker Support**: Easy containerized deployment
- 🔧 **Process Management**: Automatic subprocess handling for led-image-viewer

## Quick Start

### Prerequisites

- Raspberry Pi with RGB LED matrix hardware
- Docker and Docker Compose installed
- GIF files stored in `/data/gifs` directory

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
   cd rpi-rgb-led-matrix/web-interface
   ```

2. **Create GIFs directory and add files**:
   ```bash
   sudo mkdir -p /data/gifs
   # Copy your GIF files to /data/gifs/
   ```

3. **Start the web interface**:
   ```bash
   ./start.sh
   ```

4. **Access the interface**:
   Open your browser and navigate to:
   - `http://localhost:5000` (from the Pi)
   - `http://YOUR_PI_IP:5000` (from other devices)

## Usage

### Web Interface

1. **Select a GIF**: Click on any GIF file from the list
2. **Adjust Brightness**: Use the slider to set brightness (1-100%)
3. **Start Display**: Click "Start Display" to begin showing the selected GIF
4. **Stop Display**: Click "Stop Display" to stop the current display

### Manual Docker Commands

If you prefer to use Docker directly:

```bash
# Build the container
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Direct Python Usage (without Docker)

If you prefer to run directly on the host:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Ensure the led-image-viewer is built
make -C ../utils led-image-viewer

# Run the web server
sudo python3 app.py
```

## Configuration

### Environment Variables

- `LED_ROWS`: Number of LED rows (default: 64)
- `LED_COLS`: Number of LED columns (default: 64)  
- `GIF_DIRECTORY`: Path to GIF files (default: /data/gifs)
- `LED_VIEWER_PATH`: Path to led-image-viewer binary

### Matrix Parameters

The web interface uses these default parameters for the LED matrix:
- Rows: 64
- Columns: 64
- Brightness: 100% (adjustable)
- Loop: Forever (-f flag)

These can be modified in the `LEDController` class in `app.py`.

## API Endpoints

The web interface provides a RESTful API:

- `GET /api/status` - Get current status
- `GET /api/gifs` - List available GIF files
- `POST /api/start` - Start displaying a GIF
- `POST /api/stop` - Stop current display
- `POST /api/brightness` - Update brightness

### API Examples

```bash
# Get status
curl http://localhost:5000/api/status

# Start displaying a GIF
curl -X POST -H "Content-Type: application/json" \
     -d '{"gif":"example.gif","brightness":75}' \
     http://localhost:5000/api/start

# Update brightness
curl -X POST -H "Content-Type: application/json" \
     -d '{"brightness":50}' \
     http://localhost:5000/api/brightness

# Stop display
curl -X POST http://localhost:5000/api/stop
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**:
   - Make sure the container runs with `privileged: true`
   - Ensure the user has sudo access for GPIO operations

2. **No GIF files found**:
   - Verify GIF files are in `/data/gifs`
   - Check file permissions and ownership

3. **Matrix not responding**:
   - Verify hardware connections
   - Check that you're running on a Raspberry Pi
   - Ensure no other processes are using the GPIO pins

4. **Container fails to start**:
   ```bash
   # Check logs for detailed error messages
   docker-compose logs
   ```

### Logs

View application logs:
```bash
# Docker logs
docker-compose logs -f led-web-interface

# Or if running directly
sudo journalctl -f -u led-matrix-web
```

## File Structure

```
web-interface/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface HTML
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Docker Compose configuration
├── start.sh            # Quick start script
└── README.md           # This file
```

## Development

### Local Development

For development without Docker:

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Build the led-image-viewer:
   ```bash
   make -C ../utils led-image-viewer
   ```

3. Run with debug mode:
   ```bash
   sudo python3 app.py
   ```

### Customization

- **Matrix size**: Modify `led_rows` and `led_cols` in `LEDController.__init__()`
- **GIF directory**: Change `gif_directory` path
- **Styling**: Edit the CSS in `templates/index.html`
- **Additional features**: Extend the Flask API in `app.py`

## Security Considerations

- The container runs in privileged mode for GPIO access
- The web interface is accessible on all network interfaces (0.0.0.0)
- Consider using a reverse proxy with authentication for production use
- GIF directory is mounted read-only for security

## License

This project follows the same license as the main rpi-rgb-led-matrix project (GPL v2).