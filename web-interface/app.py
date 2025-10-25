#!/usr/bin/env python3
"""
LED Matrix Web Interface
A Flask web server for controlling the led-image-viewer remotely.
Allows selecting GIFs and brightness settings from a web browser.
"""

import os
import subprocess
import signal
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
import psutil
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class LEDController:
    def __init__(self):
        self.current_process = None
        self.current_gif = None
        self.current_brightness = 100
        self.led_rows = 64
        self.led_cols = 64
        self.gif_directory = "/data/gifs"
        self.led_viewer_path = "/opt/rpi-rgb-led-matrix/utils/led-image-viewer"
        self.status_lock = threading.Lock()
        
    def get_available_gifs(self):
        """Get list of available GIF files in the gif directory."""
        try:
            gif_files = []
            if os.path.exists(self.gif_directory):
                for file in os.listdir(self.gif_directory):
                    if file.lower().endswith('.gif'):
                        file_path = os.path.join(self.gif_directory, file)
                        file_size = os.path.getsize(file_path)
                        gif_files.append({
                            'name': file,
                            'size': self._format_file_size(file_size),
                            'path': file_path
                        })
                gif_files.sort(key=lambda x: x['name'])
            return gif_files
        except Exception as e:
            logger.error(f"Error getting GIF files: {e}")
            return []
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def is_running(self):
        """Check if led-image-viewer process is currently running."""
        with self.status_lock:
            if self.current_process is None:
                return False
            try:
                # Check if process is still alive
                return self.current_process.poll() is None
            except:
                return False
    
    def get_status(self):
        """Get current status of the LED display."""
        return {
            'running': self.is_running(),
            'current_gif': self.current_gif,
            'brightness': self.current_brightness,
            'led_rows': self.led_rows,
            'led_cols': self.led_cols,
            'available_gifs': self.get_available_gifs()
        }
    
    def stop_display(self):
        """Stop the currently running display."""
        with self.status_lock:
            if self.current_process and self.current_process.poll() is None:
                try:
                    # First try gentle termination
                    self.current_process.terminate()
                    try:
                        self.current_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # If it doesn't stop gracefully, force kill
                        self.current_process.kill()
                        self.current_process.wait()
                    logger.info("LED display stopped")
                except Exception as e:
                    logger.error(f"Error stopping display: {e}")
                finally:
                    self.current_process = None
                    self.current_gif = None
    
    def start_display(self, gif_filename, brightness=None):
        """Start displaying a GIF with specified brightness."""
        # Stop any currently running display
        self.stop_display()
        
        if brightness is not None:
            self.current_brightness = max(1, min(100, brightness))
        
        gif_path = os.path.join(self.gif_directory, gif_filename)
        
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        
        # Build the command
        cmd = [
            "sudo", self.led_viewer_path,
            gif_path,
            f"--led-rows={self.led_rows}",
            f"--led-cols={self.led_cols}",
            f"--led-brightness={self.current_brightness}",
            "-f"  # Loop forever
        ]
        
        try:
            with self.status_lock:
                # Start the process
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Create new process group
                )
                self.current_gif = gif_filename
            
            logger.info(f"Started displaying {gif_filename} at {self.current_brightness}% brightness")
            return True
            
        except Exception as e:
            logger.error(f"Error starting display: {e}")
            with self.status_lock:
                self.current_process = None
                self.current_gif = None
            raise
    
    def update_brightness(self, brightness):
        """Update brightness by restarting with new brightness value."""
        if self.current_gif and self.is_running():
            return self.start_display(self.current_gif, brightness)
        else:
            self.current_brightness = max(1, min(100, brightness))
            return True

# Global controller instance
led_controller = LEDController()

@app.route('/')
def index():
    """Main page with the control interface."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get current status."""
    return jsonify(led_controller.get_status())

@app.route('/api/gifs')
def api_gifs():
    """API endpoint to get available GIF files."""
    return jsonify(led_controller.get_available_gifs())

@app.route('/api/start', methods=['POST'])
def api_start():
    """API endpoint to start displaying a GIF."""
    try:
        data = request.get_json()
        gif_name = data.get('gif')
        brightness = data.get('brightness', led_controller.current_brightness)
        
        if not gif_name:
            return jsonify({'error': 'GIF name is required'}), 400
        
        led_controller.start_display(gif_name, brightness)
        return jsonify({'success': True, 'message': f'Started displaying {gif_name}'})
        
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error in start API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API endpoint to stop the current display."""
    try:
        led_controller.stop_display()
        return jsonify({'success': True, 'message': 'Display stopped'})
    except Exception as e:
        logger.error(f"Error in stop API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/brightness', methods=['POST'])
def api_brightness():
    """API endpoint to update brightness."""
    try:
        data = request.get_json()
        brightness = data.get('brightness')
        
        if brightness is None or not (1 <= brightness <= 100):
            return jsonify({'error': 'Brightness must be between 1 and 100'}), 400
        
        led_controller.update_brightness(brightness)
        return jsonify({'success': True, 'message': f'Brightness updated to {brightness}%'})
        
    except Exception as e:
        logger.error(f"Error in brightness API: {e}")
        return jsonify({'error': str(e)}), 500

# Cleanup on shutdown
def cleanup():
    """Clean up resources on shutdown."""
    led_controller.stop_display()

import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    # Check if running as root (required for GPIO access)
    if os.geteuid() != 0:
        logger.warning("Warning: Not running as root. LED matrix control may not work.")
    
    # Ensure gif directory exists
    os.makedirs(led_controller.gif_directory, exist_ok=True)
    
    logger.info("Starting LED Matrix Web Interface")
    logger.info(f"GIF Directory: {led_controller.gif_directory}")
    logger.info(f"LED Viewer Path: {led_controller.led_viewer_path}")
    
    app.run(host='0.0.0.0', port=5000, debug=False)