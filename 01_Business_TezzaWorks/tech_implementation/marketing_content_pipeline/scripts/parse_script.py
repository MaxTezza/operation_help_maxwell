#!/usr/bin/env python3
"""
Script Parser Module
Parses markdown video scripts to extract scenes, narrator sections, and audio cues.
"""

import re
import json
from typing import List, Dict, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScriptElement:
    """Base class for script elements"""
    def __init__(self, element_type: str, content: str, order: int):
        self.element_type = element_type
        self.content = content
        self.order = order

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.element_type,
            'content': self.content,
            'order': self.order
        }


class Scene(ScriptElement):
    """Represents a [SCENE] element"""
    def __init__(self, content: str, order: int):
        super().__init__('scene', content, order)


class Audio(ScriptElement):
    """Represents an [AUDIO] element"""
    def __init__(self, content: str, order: int, style: str = None):
        super().__init__('audio', content, order)
        self.style = style or self.infer_style(content)

    def infer_style(self, content: str) -> str:
        """Infer music style from content description"""
        content_lower = content.lower()

        if 'sad trombone' in content_lower:
            return 'sad_trombone'
        elif any(word in content_lower for word in ['warm', 'acoustic', 'authentic', 'laughter']):
            return 'warm_acoustic'
        elif any(word in content_lower for word in ['dramatic', 'cinematic', 'swell', 'emotional']):
            return 'dramatic'
        elif any(word in content_lower for word in ['generic', 'corporate', 'muted']):
            return 'generic_corporate'
        else:
            return 'corporate_uplifting'

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['style'] = self.style
        return data


class Narrator(ScriptElement):
    """Represents a [NARRATOR] element"""
    def __init__(self, content: str, order: int, voice_type: str = 'narrator'):
        super().__init__('narrator', content, order)
        self.voice_type = voice_type

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['voice_type'] = self.voice_type
        return data


class OnScreenText(ScriptElement):
    """Represents [ON-SCREEN TEXT] element"""
    def __init__(self, content: str, order: int):
        super().__init__('text', content, order)


class VideoScript:
    """Represents a complete parsed video script"""
    def __init__(self, title: str, concept: str, style: str):
        self.title = title
        self.concept = concept
        self.style = style
        self.elements: List[ScriptElement] = []

    def add_element(self, element: ScriptElement):
        """Add an element to the script"""
        self.elements.append(element)

    def get_narrations(self) -> List[Narrator]:
        """Get all narrator elements"""
        return [e for e in self.elements if isinstance(e, Narrator)]

    def get_audio_cues(self) -> List[Audio]:
        """Get all audio cues"""
        return [e for e in self.elements if isinstance(e, Audio)]

    def get_scenes(self) -> List[Scene]:
        """Get all scene descriptions"""
        return [e for e in self.elements if isinstance(e, Scene)]

    def get_text_overlays(self) -> List[OnScreenText]:
        """Get all on-screen text elements"""
        return [e for e in self.elements if isinstance(e, OnScreenText)]

    def to_dict(self) -> Dict[str, Any]:
        """Convert script to dictionary"""
        return {
            'title': self.title,
            'concept': self.concept,
            'style': self.style,
            'elements': [e.to_dict() for e in self.elements],
            'statistics': {
                'total_elements': len(self.elements),
                'narrations': len(self.get_narrations()),
                'audio_cues': len(self.get_audio_cues()),
                'scenes': len(self.get_scenes()),
                'text_overlays': len(self.get_text_overlays())
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert script to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class ScriptParser:
    """Parser for video script markdown files"""

    def __init__(self):
        # Regex patterns for different elements
        self.patterns = {
            'title': re.compile(r'###\s+\*\*(.+?)\*\*'),
            'concept': re.compile(r'\*\*Concept:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL),
            'style': re.compile(r'\*\*Style:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL),
            'scene': re.compile(r'\*\*\[SCENE\]:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL),
            'audio': re.compile(r'\*\*\[AUDIO\]:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL),
            'narrator': re.compile(r'\*\*\[NARRATOR(?:\s+\((.+?)\))?\]:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL),
            'text': re.compile(r'\*\*\[ON-SCREEN TEXT\]:\*\*\s+(.+?)(?=\n\*\*|\n\n|\Z)', re.DOTALL)
        }

    def parse_file(self, file_path: str) -> VideoScript:
        """Parse a video script file"""
        logger.info(f"Parsing script file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> VideoScript:
        """Parse video script content"""
        # Extract metadata
        title_match = self.patterns['title'].search(content)
        title = title_match.group(1) if title_match else "Untitled Script"

        concept_match = self.patterns['concept'].search(content)
        concept = concept_match.group(1).strip() if concept_match else ""

        style_match = self.patterns['style'].search(content)
        style = style_match.group(1).strip() if style_match else ""

        # Create script object
        script = VideoScript(title, concept, style)

        # Parse all elements in order
        order = 0

        # Find all matches with their positions
        all_matches = []

        for match in self.patterns['scene'].finditer(content):
            all_matches.append(('scene', match.start(), match.group(1).strip(), order))
            order += 1

        for match in self.patterns['audio'].finditer(content):
            all_matches.append(('audio', match.start(), match.group(1).strip(), order))
            order += 1

        for match in self.patterns['narrator'].finditer(content):
            voice_type = match.group(1) or 'narrator'
            text = match.group(2).strip()
            # Determine voice type from context
            if 'Internal Monologue' in voice_type:
                voice_type = 'internal_monologue'
            else:
                voice_type = 'narrator'
            all_matches.append(('narrator', match.start(), text, order, voice_type))
            order += 1

        for match in self.patterns['text'].finditer(content):
            all_matches.append(('text', match.start(), match.group(1).strip(), order))
            order += 1

        # Sort by position in document
        all_matches.sort(key=lambda x: x[1])

        # Create elements
        for match in all_matches:
            element_type = match[0]
            element_content = match[2]
            element_order = match[3]

            if element_type == 'scene':
                script.add_element(Scene(element_content, element_order))
            elif element_type == 'audio':
                script.add_element(Audio(element_content, element_order))
            elif element_type == 'narrator':
                voice_type = match[4] if len(match) > 4 else 'narrator'
                script.add_element(Narrator(element_content, element_order, voice_type))
            elif element_type == 'text':
                script.add_element(OnScreenText(element_content, element_order))

        logger.info(f"Parsed script: {title}")
        logger.info(f"Found {len(script.elements)} elements")

        return script

    def parse_multiple_scripts(self, file_path: str) -> List[VideoScript]:
        """Parse a file containing multiple scripts"""
        logger.info(f"Parsing multiple scripts from: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by script sections (marked by ###)
        script_sections = re.split(r'(?=###\s+\*\*Script\s+[A-Z]:)', content)

        scripts = []
        for section in script_sections:
            if section.strip() and '**[SCENE]:**' in section or '**[NARRATOR]:**' in section:
                try:
                    script = self.parse_content(section)
                    scripts.append(script)
                except Exception as e:
                    logger.error(f"Error parsing script section: {e}")

        logger.info(f"Parsed {len(scripts)} scripts")
        return scripts


def main():
    """Command-line interface for script parser"""
    import argparse

    parser = argparse.ArgumentParser(description='Parse video scripts from markdown files')
    parser.add_argument('input_file', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output JSON file (optional)')
    parser.add_argument('-s', '--script', help='Script ID to extract (e.g., D, E, F)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse scripts
    script_parser = ScriptParser()
    scripts = script_parser.parse_multiple_scripts(args.input_file)

    # Filter by script ID if specified
    if args.script:
        scripts = [s for s in scripts if args.script in s.title]

    # Output results
    if len(scripts) == 1:
        output_data = scripts[0].to_dict()
    else:
        output_data = {
            'scripts': [s.to_dict() for s in scripts]
        }

    output_json = json.dumps(output_data, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        logger.info(f"Output written to: {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
