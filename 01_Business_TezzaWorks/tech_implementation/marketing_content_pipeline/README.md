# TezzaWorks AI Marketing Content Generation System

An automated pipeline that transforms video scripts into finished marketing videos using AI tools including ElevenLabs for voice generation, Suno AI for background music, and FFmpeg for video assembly.

## Features

- **Script Parsing**: Automatically extract narration, audio cues, scenes, and text overlays from markdown scripts
- **AI Voiceover Generation**: Generate professional voiceovers using ElevenLabs API with multiple voice profiles
- **Background Music Generation**: Create custom background music using Suno AI based on script audio cues
- **Automated Video Assembly**: Assemble complete videos with FFmpeg including voiceovers, music, and text overlays
- **Web Interface**: User-friendly Flask web application for non-technical users
- **Batch Processing**: Process multiple scripts and manage video generation jobs
- **API Integration**: Secure API key management with environment variables

## Project Structure

```
marketing_content_pipeline/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.yaml                  # Configuration file
├── .env.example                 # Environment variables template
├── scripts/                     # Core processing scripts
│   ├── parse_script.py         # Script parsing module
│   ├── generate_voiceover.py   # ElevenLabs integration
│   ├── generate_music.py       # Suno AI integration
│   └── assemble_video.py       # FFmpeg video assembly
├── web_interface/               # Flask web application
│   ├── app.py                  # Flask application
│   ├── templates/              # HTML templates
│   │   └── index.html
│   └── static/                 # CSS and JavaScript
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── input_scripts/               # Upload directory for scripts
├── output/                      # Generated videos
├── assets/                      # Generated assets
│   ├── voiceovers/             # Generated voiceover files
│   ├── music/                  # Generated music files
│   └── footage/                # Stock footage (optional)
└── temp/                        # Temporary files
```

## Prerequisites

### System Requirements

- Python 3.9 or higher
- FFmpeg (for video processing)
- 4GB RAM minimum (8GB recommended)
- 5GB disk space for assets and temporary files

### API Keys Required

1. **ElevenLabs API Key**
   - Sign up at: https://elevenlabs.io
   - Get your API key from: https://elevenlabs.io/app/settings
   - Pricing: https://elevenlabs.io/pricing

2. **Suno AI API Key**
   - Sign up at: https://suno.ai
   - Get your API key from account settings
   - Note: Suno API integration is hypothetical - adjust as needed

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /home/mtez/operation_help_maxwell/01_Business_TezzaWorks/tech_implementation/marketing_content_pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or with a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

Verify installation:
```bash
ffmpeg -version
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# ElevenLabs API Key
ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key_here

# Suno API Key
SUNO_API_KEY=your_actual_suno_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=generate_a_random_secret_key_here
FLASK_ENV=production
```

To generate a secure Flask secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Verify Configuration

```bash
python3 scripts/parse_script.py --help
```

## Usage

### Option 1: Web Interface (Recommended)

Start the web server:

```bash
cd web_interface
python3 app.py
```

Then open your browser to: **http://localhost:5000**

The web interface allows you to:
- Upload video scripts
- View parsed script details
- Generate videos with one click
- Monitor processing jobs
- Download finished videos

### Option 2: Command Line Interface

#### Step 1: Parse a Script

```bash
python3 scripts/parse_script.py input_scripts/business_video_scripts.md -s D -o parsed_script.json
```

This will parse Script D and output the structured data.

#### Step 2: Generate Voiceovers

```bash
python3 scripts/generate_voiceover.py input_scripts/business_video_scripts.md -s D -o assets/voiceovers
```

This generates voiceover MP3 files for all narrator sections.

#### Step 3: Generate Background Music

```bash
python3 scripts/generate_music.py input_scripts/business_video_scripts.md -s D -o assets/music
```

This generates background music based on audio cues.

#### Step 4: Assemble Video

```bash
python3 scripts/assemble_video.py \
    input_scripts/business_video_scripts.md \
    voiceover_results.json \
    music_results.json \
    -s D \
    -o output/script_d_video.mp4
```

This assembles the final video with all components.

## Configuration

Edit `config.yaml` to customize:

### Voice Settings

```yaml
elevenlabs:
  voice_profiles:
    narrator: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    narrator_male: "ErXwobaYiN019PkySvjV"  # Antoni
    internal_monologue: "EXAVITQu4vr4xnSDxMaL"  # Bella
  voice_settings:
    stability: 0.75
    similarity_boost: 0.75
```

### Video Settings

```yaml
video:
  resolution: "1920x1080"
  framerate: 30
  output_format: "mp4"
  video_codec: "libx264"
  audio_codec: "aac"
```

### Music Styles

```yaml
suno:
  music_styles:
    corporate_uplifting: "uplifting corporate background music"
    warm_acoustic: "warm acoustic music, guitar"
    dramatic: "dramatic cinematic music"
```

## Script Format

Scripts should be in markdown format with specific tags:

```markdown
### **Script D: The End of the Boring Corporate Gift**

**Concept:** A classic "problem-agitate-solution" marketing video.
**Style:** Professional, cinematic, and persuasive.

**[SCENE]:** A stylized shot of a generic gift basket.

**[AUDIO]:** Muted, generic corporate background music.

**[NARRATOR]:** You want to show your team you appreciate them...

**[ON-SCREEN TEXT]:** Stop giving stuff. Start giving experiences.
```

See `input_scripts/business_video_scripts.md` for complete examples.

## Example: Processing Script D

### Using the Web Interface

1. Start the web server: `python3 web_interface/app.py`
2. Open http://localhost:5000
3. Upload `business_video_scripts.md`
4. Click "View Details" on the uploaded script
5. Select "Script D: The End of the Boring Corporate Gift"
6. Click "Generate Video for This Script"
7. Monitor progress in the "Processing Jobs" tab
8. Download the finished video from "Generated Videos" tab

### Using Command Line

```bash
# Navigate to scripts directory
cd scripts

# Generate all assets for Script D
python3 generate_voiceover.py ../input_scripts/business_video_scripts.md -s D
python3 generate_music.py ../input_scripts/business_video_scripts.md -s D

# Note: For full video assembly, you'll need to collect the results
# from the generation steps and pass them to assemble_video.py
```

## Troubleshooting

### FFmpeg Not Found

**Error:** `ffmpeg: command not found`

**Solution:** Install FFmpeg following the installation instructions above.

### API Key Errors

**Error:** `ELEVENLABS_API_KEY not found`

**Solution:** Ensure `.env` file exists with valid API keys and is in the project root.

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'elevenlabs'`

**Solution:** Install dependencies: `pip install -r requirements.txt`

### Memory Issues

**Error:** Out of memory during video processing

**Solution:**
- Reduce video resolution in `config.yaml`
- Process scripts with fewer scenes
- Increase system RAM

### Web Interface Not Starting

**Error:** Port 5000 already in use

**Solution:**
- Change port in `config.yaml` under `web.port`
- Or kill process using port 5000: `lsof -ti:5000 | xargs kill -9`

## API Endpoints

If using the web interface programmatically:

- `GET /api/scripts` - List all scripts
- `POST /api/scripts/upload` - Upload a new script
- `GET /api/scripts/<filename>` - Get script details
- `DELETE /api/scripts/<filename>` - Delete a script
- `POST /api/generate` - Start video generation
- `GET /api/jobs/<job_id>` - Get job status
- `GET /api/jobs` - List all jobs
- `GET /api/videos` - List generated videos
- `GET /api/videos/<filename>` - Download video
- `GET /api/config` - Get system configuration
- `GET /health` - Health check

## Performance Optimization

### For Faster Processing

1. **Use faster voice models** (adjust in config.yaml)
2. **Reduce video resolution** for drafts (720p instead of 1080p)
3. **Enable GPU acceleration** in FFmpeg (if available)
4. **Process multiple scripts in parallel** (requires Celery setup)

### For Production Deployment

1. **Use Redis + Celery** for background job processing
2. **Add nginx** as reverse proxy
3. **Use gunicorn** instead of Flask development server
4. **Set up monitoring** with logging aggregation
5. **Add authentication** to web interface

## Advanced Features

### Batch Processing Multiple Scripts

```bash
# Process all scripts in a file
python3 scripts/generate_voiceover.py input_scripts/business_video_scripts.md -o assets/voiceovers
```

### Custom Voice Profiles

Edit `config.yaml` to add custom ElevenLabs voice IDs:

```yaml
elevenlabs:
  voice_profiles:
    custom_voice: "your_voice_id_here"
```

### Using Stock Footage

Place video files in `assets/footage/` and reference them by name in the assembly script.

## Security Considerations

- **Never commit `.env` file** to version control
- **Use environment variables** for all sensitive data
- **Restrict file upload types** in web interface
- **Validate all user inputs** before processing
- **Use HTTPS** in production deployments
- **Add authentication** for web interface in production

## Limitations

- **Suno API integration is hypothetical** - adjust based on actual API
- **Video assembly uses black backgrounds** by default (add footage for visuals)
- **Text overlay customization** is limited (edit FFmpeg filters for advanced styling)
- **Synchronous processing** in web interface (use Celery for production)

## Future Enhancements

- Add support for real-time preview
- Implement video editing timeline
- Add stock footage library integration
- Support for multiple languages
- Custom transition effects
- Audio normalization and enhancement
- Automated subtitle generation
- Cloud storage integration (S3, GCS)
- REST API with authentication
- Docker containerization

## Support

For issues and questions:
1. Check the Troubleshooting section above
2. Review FFmpeg documentation: https://ffmpeg.org/documentation.html
3. ElevenLabs API docs: https://docs.elevenlabs.io
4. File an issue or contact support

## License

This project is proprietary to TezzaWorks. All rights reserved.

## Credits

- **ElevenLabs** - AI Voice Generation
- **Suno AI** - Music Generation
- **FFmpeg** - Video Processing
- **Flask** - Web Framework
- **Python** - Core Language

---

**Version:** 1.0.0
**Last Updated:** November 2025
**Author:** TezzaWorks Technical Team
