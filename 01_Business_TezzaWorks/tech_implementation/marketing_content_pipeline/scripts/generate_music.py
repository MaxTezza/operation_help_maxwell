#!/usr/bin/env python3
"""
Music Generation Module
Integrates with Suno API to generate background music from audio cues.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
import yaml
import time
import requests
import json

from parse_script import ScriptParser, VideoScript, Audio

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicGenerator:
    """Generate background music using Suno API"""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the music generator"""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('SUNO_API_KEY')

        if not self.api_key:
            logger.warning("SUNO_API_KEY not found in environment variables")

        self.api_base_url = "https://api.suno.ai/v1"  # Example URL - adjust as needed

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
                'suno': {
                    'default_duration': 30,
                    'music_styles': {
                        'corporate_uplifting': 'uplifting corporate background music',
                        'warm_acoustic': 'warm acoustic music, guitar',
                        'dramatic': 'dramatic cinematic music',
                        'sad_trombone': 'sad trombone sound effect',
                        'generic_corporate': 'generic corporate music'
                    },
                    'output_format': 'mp3'
                },
                'paths': {
                    'assets_music': 'assets/music'
                }
            }

    def get_music_prompt(self, style: str, description: str = "") -> str:
        """
        Generate a music prompt from style and description

        Args:
            style: Music style key from config
            description: Additional description from script

        Returns:
            Complete prompt for music generation
        """
        music_styles = self.config['suno']['music_styles']
        base_prompt = music_styles.get(style, music_styles['corporate_uplifting'])

        if description:
            # Extract key descriptive words from the script's audio cue
            additional_context = self._extract_context(description)
            if additional_context:
                base_prompt += f", {additional_context}"

        return base_prompt

    def _extract_context(self, description: str) -> str:
        """Extract additional context from audio description"""
        # Keywords to look for
        mood_keywords = [
            'happy', 'sad', 'energetic', 'calm', 'tense', 'relaxed',
            'uplifting', 'emotional', 'dramatic', 'gentle', 'intense'
        ]
        instrument_keywords = [
            'guitar', 'piano', 'strings', 'drums', 'synth', 'orchestra'
        ]

        description_lower = description.lower()
        found_keywords = []

        for keyword in mood_keywords + instrument_keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)

        return ", ".join(found_keywords[:3])  # Limit to 3 keywords

    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate music from a prompt

        Args:
            prompt: Text description of the music
            duration: Duration in seconds
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file
        """
        if not self.api_key:
            logger.warning("No API key available, generating mock music")
            return self._generate_mock_music(prompt, output_path)

        try:
            logger.info(f"Generating music: {prompt[:50]}...")

            # Note: Suno API is hypothetical - adjust based on actual API
            # This is a template implementation
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'prompt': prompt,
                'duration': duration,
                'format': self.config['suno']['output_format']
            }

            # Make API request
            response = requests.post(
                f"{self.api_base_url}/generate",
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()

                # Check if we need to poll for completion
                if 'job_id' in result:
                    audio_url = self._poll_generation(result['job_id'])
                else:
                    audio_url = result.get('audio_url')

                if audio_url and output_path:
                    # Download the audio file
                    self._download_audio(audio_url, output_path)
                    logger.info(f"Saved music to: {output_path}")
                    return output_path

            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return self._generate_mock_music(prompt, output_path)

        except Exception as e:
            logger.error(f"Error generating music: {e}")
            return self._generate_mock_music(prompt, output_path)

    def _poll_generation(self, job_id: str, max_attempts: int = 30) -> Optional[str]:
        """Poll for generation completion"""
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.api_base_url}/status/{job_id}",
                    headers=headers,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status')

                    if status == 'completed':
                        return result.get('audio_url')
                    elif status == 'failed':
                        logger.error(f"Generation failed: {result.get('error')}")
                        return None

                time.sleep(2)  # Wait 2 seconds between polls

            except Exception as e:
                logger.error(f"Error polling status: {e}")

        logger.error("Generation timed out")
        return None

    def _download_audio(self, url: str, output_path: str):
        """Download audio file from URL"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

    def _generate_mock_music(self, prompt: str, output_path: Optional[str]) -> Optional[str]:
        """Generate a mock music file for testing"""
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Create an empty file as placeholder
            with open(output_path, 'wb') as f:
                f.write(b'MOCK_MUSIC_DATA')
            logger.info(f"Created mock music at: {output_path}")
            return output_path
        return None

    def generate_from_script(
        self,
        script: VideoScript,
        output_dir: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate all music tracks from a video script

        Args:
            script: Parsed VideoScript object
            output_dir: Directory to save music files

        Returns:
            List of dictionaries with music information
        """
        if not output_dir:
            output_dir = self.config['paths']['assets_music']

        os.makedirs(output_dir, exist_ok=True)

        audio_cues = script.get_audio_cues()
        logger.info(f"Generating {len(audio_cues)} music tracks for: {script.title}")

        results = []
        default_duration = self.config['suno']['default_duration']

        for i, audio_cue in enumerate(audio_cues, 1):
            # Generate filename
            safe_title = "".join(c for c in script.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_music_{i:02d}.mp3"
            output_path = os.path.join(output_dir, filename)

            # Generate prompt
            prompt = self.get_music_prompt(audio_cue.style, audio_cue.content)

            # Generate music
            logger.info(f"Processing music track {i}/{len(audio_cues)}")
            logger.info(f"Style: {audio_cue.style}")
            logger.info(f"Prompt: {prompt}")

            audio_path = self.generate_music(
                prompt=prompt,
                duration=default_duration,
                output_path=output_path
            )

            result = {
                'order': audio_cue.order,
                'description': audio_cue.content,
                'style': audio_cue.style,
                'prompt': prompt,
                'audio_path': audio_path,
                'filename': filename
            }
            results.append(result)

            # Rate limiting
            if i < len(audio_cues):
                time.sleep(1)

        logger.info(f"Generated {len(results)} music tracks")
        return results


def main():
    """Command-line interface for music generation"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate background music from video scripts')
    parser.add_argument('input_file', help='Input markdown script file')
    parser.add_argument('-o', '--output-dir', help='Output directory for music',
                        default='assets/music')
    parser.add_argument('-s', '--script', help='Script ID to process (e.g., D, E, F)')
    parser.add_argument('-c', '--config', help='Config file path', default='config.yaml')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize generator
    generator = MusicGenerator(config_path=args.config)

    # Parse scripts
    script_parser = ScriptParser()
    scripts = script_parser.parse_multiple_scripts(args.input_file)

    # Filter by script ID if specified
    if args.script:
        scripts = [s for s in scripts if args.script in s.title]

    if not scripts:
        logger.error("No scripts found to process")
        return

    # Generate music for each script
    for script in scripts:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {script.title}")
        logger.info(f"{'='*60}")

        results = generator.generate_from_script(script, args.output_dir)

        # Print summary
        print(f"\nGenerated {len(results)} music tracks for: {script.title}")
        for result in results:
            print(f"  - {result['filename']} ({result['style']})")


if __name__ == '__main__':
    main()
