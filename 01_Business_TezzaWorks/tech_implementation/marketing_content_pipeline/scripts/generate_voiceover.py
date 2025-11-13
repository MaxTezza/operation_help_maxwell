#!/usr/bin/env python3
"""
Voiceover Generation Module
Integrates with ElevenLabs API to generate voiceovers from narrator text.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
import yaml
import time

# Try to import ElevenLabs client
try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
except ImportError:
    print("Warning: elevenlabs package not installed. Install with: pip install elevenlabs")
    ElevenLabs = None

from parse_script import ScriptParser, VideoScript, Narrator

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceoverGenerator:
    """Generate voiceovers using ElevenLabs API"""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the voiceover generator"""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('ELEVENLABS_API_KEY')

        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not found in environment variables")

        # Initialize ElevenLabs client
        if ElevenLabs and self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("ElevenLabs client not initialized")

        # Voice settings from config
        self.voice_settings = VoiceSettings(
            stability=self.config['elevenlabs']['voice_settings']['stability'],
            similarity_boost=self.config['elevenlabs']['voice_settings']['similarity_boost'],
            style=self.config['elevenlabs']['voice_settings'].get('style', 0.0),
            use_speaker_boost=self.config['elevenlabs']['voice_settings'].get('use_speaker_boost', True)
        ) if ElevenLabs else None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return default config
            return {
                'elevenlabs': {
                    'voice_profiles': {
                        'narrator': '21m00Tcm4TlvDq8ikWAM',
                        'narrator_male': 'ErXwobaYiN019PkySvjV',
                        'internal_monologue': 'EXAVITQu4vr4xnSDxMaL'
                    },
                    'voice_settings': {
                        'stability': 0.75,
                        'similarity_boost': 0.75,
                        'style': 0.0,
                        'use_speaker_boost': True
                    },
                    'output_format': 'mp3_44100_128'
                },
                'paths': {
                    'assets_voiceovers': 'assets/voiceovers'
                }
            }

    def get_voice_id(self, voice_type: str) -> str:
        """Get voice ID for a given voice type"""
        voice_profiles = self.config['elevenlabs']['voice_profiles']
        return voice_profiles.get(voice_type, voice_profiles['narrator'])

    def generate_voiceover(
        self,
        text: str,
        voice_type: str = 'narrator',
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a single voiceover from text

        Args:
            text: The text to convert to speech
            voice_type: Type of voice to use
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file
        """
        if not self.client:
            logger.error("ElevenLabs client not initialized")
            return self._generate_mock_voiceover(text, output_path)

        try:
            voice_id = self.get_voice_id(voice_type)
            logger.info(f"Generating voiceover with voice: {voice_type} ({voice_id})")

            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=self.voice_settings
            )

            # Collect audio data
            audio_data = b''
            for chunk in audio_generator:
                if chunk:
                    audio_data += chunk

            # Save to file
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"Saved voiceover to: {output_path}")
                return output_path

            return None

        except Exception as e:
            logger.error(f"Error generating voiceover: {e}")
            return self._generate_mock_voiceover(text, output_path)

    def _generate_mock_voiceover(self, text: str, output_path: Optional[str]) -> Optional[str]:
        """Generate a mock voiceover file for testing"""
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Create an empty file as placeholder
            with open(output_path, 'wb') as f:
                f.write(b'MOCK_AUDIO_DATA')
            logger.info(f"Created mock voiceover at: {output_path}")
            return output_path
        return None

    def generate_from_script(
        self,
        script: VideoScript,
        output_dir: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate all voiceovers from a video script

        Args:
            script: Parsed VideoScript object
            output_dir: Directory to save voiceover files

        Returns:
            List of dictionaries with voiceover information
        """
        if not output_dir:
            output_dir = self.config['paths']['assets_voiceovers']

        os.makedirs(output_dir, exist_ok=True)

        narrations = script.get_narrations()
        logger.info(f"Generating {len(narrations)} voiceovers for: {script.title}")

        results = []

        for i, narration in enumerate(narrations, 1):
            # Generate filename
            safe_title = "".join(c for c in script.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_narration_{i:02d}.mp3"
            output_path = os.path.join(output_dir, filename)

            # Generate voiceover
            logger.info(f"Processing narration {i}/{len(narrations)}")
            audio_path = self.generate_voiceover(
                text=narration.content,
                voice_type=narration.voice_type,
                output_path=output_path
            )

            result = {
                'order': narration.order,
                'text': narration.content,
                'voice_type': narration.voice_type,
                'audio_path': audio_path,
                'filename': filename
            }
            results.append(result)

            # Rate limiting - be nice to the API
            if i < len(narrations):
                time.sleep(0.5)

        logger.info(f"Generated {len(results)} voiceovers")
        return results

    def list_available_voices(self) -> List[Dict]:
        """List all available voices from ElevenLabs"""
        if not self.client:
            logger.error("ElevenLabs client not initialized")
            return []

        try:
            voices = self.client.voices.get_all()
            voice_list = []

            for voice in voices.voices:
                voice_list.append({
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category,
                    'labels': voice.labels
                })

            return voice_list

        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []


def main():
    """Command-line interface for voiceover generation"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Generate voiceovers from video scripts')
    parser.add_argument('input_file', help='Input markdown script file')
    parser.add_argument('-o', '--output-dir', help='Output directory for voiceovers',
                        default='assets/voiceovers')
    parser.add_argument('-s', '--script', help='Script ID to process (e.g., D, E, F)')
    parser.add_argument('-c', '--config', help='Config file path', default='config.yaml')
    parser.add_argument('--list-voices', action='store_true',
                        help='List available voices and exit')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize generator
    generator = VoiceoverGenerator(config_path=args.config)

    # List voices if requested
    if args.list_voices:
        voices = generator.list_available_voices()
        print(json.dumps(voices, indent=2))
        return

    # Parse scripts
    script_parser = ScriptParser()
    scripts = script_parser.parse_multiple_scripts(args.input_file)

    # Filter by script ID if specified
    if args.script:
        scripts = [s for s in scripts if args.script in s.title]

    if not scripts:
        logger.error("No scripts found to process")
        return

    # Generate voiceovers for each script
    for script in scripts:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {script.title}")
        logger.info(f"{'='*60}")

        results = generator.generate_from_script(script, args.output_dir)

        # Print summary
        print(f"\nGenerated {len(results)} voiceovers for: {script.title}")
        for result in results:
            print(f"  - {result['filename']}")


if __name__ == '__main__':
    main()
