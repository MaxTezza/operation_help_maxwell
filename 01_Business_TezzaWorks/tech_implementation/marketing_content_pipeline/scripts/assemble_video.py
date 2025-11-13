#!/usr/bin/env python3
"""
Video Assembly Module
Assembles final videos using FFmpeg from voiceovers, music, and footage.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import json
import subprocess
import yaml
from dataclasses import dataclass

from parse_script import ScriptParser, VideoScript, Scene, OnScreenText

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VideoSegment:
    """Represents a segment of the final video"""
    order: int
    duration: float
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    music_path: Optional[str] = None
    text_overlay: Optional[str] = None
    fade_in: bool = False
    fade_out: bool = False


class VideoAssembler:
    """Assemble videos using FFmpeg"""

    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the video assembler"""
        self.config = self._load_config(config_path)
        self._check_ffmpeg()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'video': {
                'resolution': '1920x1080',
                'framerate': 30,
                'output_format': 'mp4',
                'video_codec': 'libx264',
                'audio_codec': 'aac',
                'audio_bitrate': '192k',
                'default_scene_duration': 5,
                'fade_duration': 0.5
            },
            'text_overlay': {
                'font': 'Arial',
                'font_size': 48,
                'font_color': 'white',
                'stroke_color': 'black',
                'stroke_width': 2,
                'position': 'bottom',
                'padding': 50
            },
            'paths': {
                'assets_voiceovers': 'assets/voiceovers',
                'assets_music': 'assets/music',
                'assets_footage': 'assets/footage',
                'output_videos': 'output',
                'temp': 'temp'
            }
        }

    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("FFmpeg is available")
            else:
                logger.warning("FFmpeg may not be properly installed")
        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")

    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of an audio file in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")

        # Default fallback
        return self.config['video']['default_scene_duration']

    def create_color_clip(
        self,
        duration: float,
        color: str = 'black',
        resolution: str = None
    ) -> str:
        """
        Create a solid color video clip

        Args:
            duration: Duration in seconds
            color: Color name or hex code
            resolution: Video resolution (e.g., '1920x1080')

        Returns:
            Path to the generated video file
        """
        if not resolution:
            resolution = self.config['video']['resolution']

        temp_dir = self.config['paths']['temp']
        os.makedirs(temp_dir, exist_ok=True)

        output_path = os.path.join(temp_dir, f'color_{color}_{duration}s.mp4')

        # Skip if already exists
        if os.path.exists(output_path):
            return output_path

        framerate = self.config['video']['framerate']

        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'color=c={color}:s={resolution}:d={duration}:r={framerate}',
            '-c:v', self.config['video']['video_codec'],
            '-t', str(duration),
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            logger.info(f"Created color clip: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error creating color clip: {e}")
            return None

    def add_text_overlay(
        self,
        video_path: str,
        text: str,
        output_path: str,
        position: str = None
    ) -> str:
        """
        Add text overlay to a video

        Args:
            video_path: Input video path
            text: Text to overlay
            output_path: Output video path
            position: Text position ('top', 'center', 'bottom')

        Returns:
            Path to the output video
        """
        if not position:
            position = self.config['text_overlay']['position']

        font_size = self.config['text_overlay']['font_size']
        font_color = self.config['text_overlay']['font_color']
        padding = self.config['text_overlay']['padding']

        # Escape text for FFmpeg
        text = text.replace(':', r'\:').replace("'", r"'\''")

        # Position mapping
        if position == 'bottom':
            y_pos = f'h-th-{padding}'
        elif position == 'top':
            y_pos = str(padding)
        else:  # center
            y_pos = '(h-th)/2'

        x_pos = '(w-tw)/2'  # Centered horizontally

        filter_text = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:x={x_pos}:y={y_pos}:borderw=2:bordercolor=black"

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_text,
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            logger.info(f"Added text overlay to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error adding text overlay: {e}")
            return video_path

    def merge_audio_tracks(
        self,
        voiceover_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.3
    ) -> str:
        """
        Merge voiceover and background music

        Args:
            voiceover_path: Path to voiceover audio
            music_path: Path to background music
            output_path: Output audio path
            music_volume: Volume level for music (0.0-1.0)

        Returns:
            Path to merged audio
        """
        cmd = [
            'ffmpeg',
            '-i', voiceover_path,
            '-i', music_path,
            '-filter_complex',
            f'[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first',
            '-c:a', self.config['video']['audio_codec'],
            '-b:a', self.config['video']['audio_bitrate'],
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            logger.info(f"Merged audio tracks: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error merging audio: {e}")
            return voiceover_path

    def create_video_segment(
        self,
        segment: VideoSegment,
        output_path: str
    ) -> str:
        """
        Create a single video segment

        Args:
            segment: VideoSegment object
            output_path: Output video path

        Returns:
            Path to created segment
        """
        # Use provided video or create black background
        if segment.video_path and os.path.exists(segment.video_path):
            video_source = segment.video_path
        else:
            video_source = self.create_color_clip(segment.duration)

        # Add text overlay if provided
        if segment.text_overlay:
            temp_dir = self.config['paths']['temp']
            os.makedirs(temp_dir, exist_ok=True)
            text_output = os.path.join(temp_dir, f'segment_{segment.order}_text.mp4')
            video_source = self.add_text_overlay(video_source, segment.text_overlay, text_output)

        # Merge audio tracks if both exist
        audio_source = segment.audio_path
        if segment.audio_path and segment.music_path:
            temp_dir = self.config['paths']['temp']
            os.makedirs(temp_dir, exist_ok=True)
            merged_audio = os.path.join(temp_dir, f'segment_{segment.order}_audio.mp3')
            audio_source = self.merge_audio_tracks(
                segment.audio_path,
                segment.music_path,
                merged_audio
            )
        elif segment.music_path:
            audio_source = segment.music_path

        # Combine video and audio
        if audio_source:
            cmd = [
                'ffmpeg',
                '-i', video_source,
                '-i', audio_source,
                '-c:v', 'copy',
                '-c:a', self.config['video']['audio_codec'],
                '-shortest',
                '-y',
                output_path
            ]
        else:
            # Just copy video if no audio
            cmd = [
                'ffmpeg',
                '-i', video_source,
                '-c:v', 'copy',
                '-y',
                output_path
            ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            logger.info(f"Created video segment: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error creating video segment: {e}")
            return None

    def concatenate_segments(
        self,
        segment_paths: List[str],
        output_path: str
    ) -> str:
        """
        Concatenate multiple video segments

        Args:
            segment_paths: List of video segment paths
            output_path: Output video path

        Returns:
            Path to final video
        """
        temp_dir = self.config['paths']['temp']
        os.makedirs(temp_dir, exist_ok=True)

        # Create concat file
        concat_file = os.path.join(temp_dir, 'concat_list.txt')
        with open(concat_file, 'w') as f:
            for segment_path in segment_paths:
                f.write(f"file '{os.path.abspath(segment_path)}'\n")

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Concatenated video: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error concatenating segments: {e}")
            return None

    def assemble_from_script(
        self,
        script: VideoScript,
        voiceover_results: List[Dict],
        music_results: List[Dict],
        output_path: Optional[str] = None
    ) -> str:
        """
        Assemble a complete video from a script

        Args:
            script: Parsed VideoScript object
            voiceover_results: List of voiceover generation results
            music_results: List of music generation results
            output_path: Output video path

        Returns:
            Path to assembled video
        """
        if not output_path:
            output_dir = self.config['paths']['output_videos']
            os.makedirs(output_dir, exist_ok=True)
            safe_title = "".join(c for c in script.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            output_path = os.path.join(output_dir, f'{safe_title}.mp4')

        logger.info(f"Assembling video: {script.title}")

        # Create segments
        segments: List[VideoSegment] = []
        voiceover_map = {v['order']: v for v in voiceover_results}
        music_map = {m['order']: m for m in music_results}
        text_map = {t.order: t.content for t in script.get_text_overlays()}

        # Process each element in order
        for element in script.elements:
            segment = VideoSegment(order=element.order, duration=5.0)

            # Add voiceover if available
            if element.order in voiceover_map:
                segment.audio_path = voiceover_map[element.order]['audio_path']
                segment.duration = self.get_audio_duration(segment.audio_path)

            # Add music if available
            if element.order in music_map:
                segment.music_path = music_map[element.order]['audio_path']

            # Add text overlay if available
            if element.order in text_map:
                segment.text_overlay = text_map[element.order]

            segments.append(segment)

        # Create individual segment videos
        temp_dir = self.config['paths']['temp']
        os.makedirs(temp_dir, exist_ok=True)

        segment_paths = []
        for i, segment in enumerate(segments):
            segment_output = os.path.join(temp_dir, f'segment_{i:03d}.mp4')
            created_segment = self.create_video_segment(segment, segment_output)
            if created_segment:
                segment_paths.append(created_segment)

        # Concatenate all segments
        if segment_paths:
            final_video = self.concatenate_segments(segment_paths, output_path)
            logger.info(f"Video assembly complete: {output_path}")
            return final_video
        else:
            logger.error("No segments created")
            return None


def main():
    """Command-line interface for video assembly"""
    import argparse

    parser = argparse.ArgumentParser(description='Assemble videos from generated assets')
    parser.add_argument('script_file', help='Input markdown script file')
    parser.add_argument('voiceover_json', help='JSON file with voiceover results')
    parser.add_argument('music_json', help='JSON file with music results')
    parser.add_argument('-o', '--output', help='Output video path')
    parser.add_argument('-s', '--script', help='Script ID to process (e.g., D, E, F)')
    parser.add_argument('-c', '--config', help='Config file path', default='config.yaml')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load results
    with open(args.voiceover_json, 'r') as f:
        voiceover_results = json.load(f)

    with open(args.music_json, 'r') as f:
        music_results = json.load(f)

    # Parse scripts
    script_parser = ScriptParser()
    scripts = script_parser.parse_multiple_scripts(args.script_file)

    # Filter by script ID if specified
    if args.script:
        scripts = [s for s in scripts if args.script in s.title]

    if not scripts:
        logger.error("No scripts found to process")
        return

    # Assemble videos
    assembler = VideoAssembler(config_path=args.config)

    for script in scripts:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {script.title}")
        logger.info(f"{'='*60}")

        output_path = args.output
        video_path = assembler.assemble_from_script(
            script,
            voiceover_results,
            music_results,
            output_path
        )

        if video_path:
            print(f"\nVideo created: {video_path}")


if __name__ == '__main__':
    main()
