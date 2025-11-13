#!/usr/bin/env python3
"""
Flask Web Interface for AI Marketing Content Generation System
Provides a user-friendly interface for script management and video generation.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import yaml
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from parse_script import ScriptParser
from generate_voiceover import VoiceoverGenerator
from generate_music import MusicGenerator
from assemble_video import VideoAssembler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Set up paths
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
UPLOAD_FOLDER = os.path.join(BASE_DIR, CONFIG['paths']['input_scripts'])
OUTPUT_FOLDER = os.path.join(BASE_DIR, CONFIG['paths']['output_videos'])
VOICEOVER_FOLDER = os.path.join(BASE_DIR, CONFIG['paths']['assets_voiceovers'])
MUSIC_FOLDER = os.path.join(BASE_DIR, CONFIG['paths']['assets_music'])

# Create directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, VOICEOVER_FOLDER, MUSIC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'md', 'txt'}

# Job tracking
jobs = {}
job_counter = 0


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/scripts', methods=['GET'])
def list_scripts():
    """List all uploaded scripts"""
    try:
        scripts = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                stat = os.stat(file_path)
                scripts.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return jsonify({'success': True, 'scripts': scripts})
    except Exception as e:
        logger.error(f"Error listing scripts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scripts/upload', methods=['POST'])
def upload_script():
    """Upload a new script"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        logger.info(f"Script uploaded: {filename}")
        return jsonify({'success': True, 'filename': filename})

    except Exception as e:
        logger.error(f"Error uploading script: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scripts/<filename>', methods=['GET'])
def get_script(filename):
    """Get script details"""
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Script not found'}), 404

        # Parse script
        parser = ScriptParser()
        scripts = parser.parse_multiple_scripts(file_path)

        scripts_data = [script.to_dict() for script in scripts]

        return jsonify({
            'success': True,
            'filename': filename,
            'scripts': scripts_data
        })

    except Exception as e:
        logger.error(f"Error getting script: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scripts/<filename>', methods=['DELETE'])
def delete_script(filename):
    """Delete a script"""
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Script not found'}), 404

        os.remove(file_path)
        logger.info(f"Script deleted: {filename}")

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting script: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate video from script"""
    global job_counter

    try:
        data = request.json
        filename = data.get('filename')
        script_title = data.get('script_title')

        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        filename = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Script not found'}), 404

        # Create job
        job_counter += 1
        job_id = f"job_{job_counter}"

        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'filename': filename,
            'script_title': script_title,
            'created': datetime.now().isoformat(),
            'progress': 0,
            'message': 'Job queued'
        }

        # Start processing in background (in production, use Celery)
        # For now, we'll do it synchronously for simplicity
        process_video_generation(job_id, file_path, script_title)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Video generation started'
        })

    except Exception as e:
        logger.error(f"Error starting video generation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def process_video_generation(job_id, file_path, script_title):
    """Process video generation (should be async in production)"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['message'] = 'Parsing script...'
        jobs[job_id]['progress'] = 10

        # Parse script
        parser = ScriptParser()
        scripts = parser.parse_multiple_scripts(file_path)

        # Filter by title if specified
        if script_title:
            scripts = [s for s in scripts if script_title in s.title]

        if not scripts:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['message'] = 'Script not found'
            return

        script = scripts[0]

        # Generate voiceovers
        jobs[job_id]['message'] = 'Generating voiceovers...'
        jobs[job_id]['progress'] = 30

        voiceover_gen = VoiceoverGenerator(CONFIG_PATH)
        voiceover_results = voiceover_gen.generate_from_script(script, VOICEOVER_FOLDER)

        # Generate music
        jobs[job_id]['message'] = 'Generating background music...'
        jobs[job_id]['progress'] = 60

        music_gen = MusicGenerator(CONFIG_PATH)
        music_results = music_gen.generate_from_script(script, MUSIC_FOLDER)

        # Assemble video
        jobs[job_id]['message'] = 'Assembling video...'
        jobs[job_id]['progress'] = 80

        assembler = VideoAssembler(CONFIG_PATH)
        video_path = assembler.assemble_from_script(
            script,
            voiceover_results,
            music_results
        )

        if video_path:
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['message'] = 'Video generation complete'
            jobs[job_id]['progress'] = 100
            jobs[job_id]['video_path'] = os.path.basename(video_path)
        else:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['message'] = 'Video assembly failed'

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['message'] = f'Error: {str(e)}'


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'success': False, 'error': 'Job not found'}), 404

    return jsonify({
        'success': True,
        'job': jobs[job_id]
    })


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        'success': True,
        'jobs': list(jobs.values())
    })


@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all generated videos"""
    try:
        videos = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.mp4'):
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                stat = os.stat(file_path)
                videos.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return jsonify({'success': True, 'videos': videos})
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/videos/<filename>', methods=['GET'])
def download_video(filename):
    """Download a generated video"""
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(OUTPUT_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Video not found'}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    return jsonify({
        'success': True,
        'config': {
            'elevenlabs_configured': bool(os.getenv('ELEVENLABS_API_KEY')),
            'suno_configured': bool(os.getenv('SUNO_API_KEY')),
            'video_settings': CONFIG['video'],
            'available_voices': CONFIG['elevenlabs']['voice_profiles'],
            'music_styles': list(CONFIG['suno']['music_styles'].keys())
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    host = CONFIG.get('web', {}).get('host', '0.0.0.0')
    port = CONFIG.get('web', {}).get('port', 5000)
    debug = CONFIG.get('web', {}).get('debug', False)

    logger.info(f"Starting web interface on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
