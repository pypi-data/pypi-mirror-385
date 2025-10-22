"""
Improved filename analyzer - fundamentally redesigned approach.

This module implements a position-based, context-aware approach
that focuses on where technical metadata begins rather than individual word analysis.
"""

import re
from pathlib import Path
from typing import List, Tuple


class ImprovedFilenameAnalyzer:
    """
    Improved analyzer using position-based and contextual analysis.

    Core principle: Stop at the first major technical metadata pattern,
    then extract everything before it as the title.
    """

    # Technical boundary patterns - these indicate where technical metadata begins
    BOUNDARY_PATTERNS = [
        # Episode patterns (highest priority)
        r'\b[Ss]\d{1,3}[Ee]\d{1,3}\b',
        r'\bEpisode\s*\d+\b',
        r'EP?\d+',    # EP01, E01, etc. (without word boundary requirement)
        r'\bS\d+',    # S3, S01, etc.
        r'-\s*\d+',   # Hyphen followed by numbers (e.g., "- 01", "-01")
        r'-\s*EP?\d+',   # Hyphen followed by EP01 (e.g., "- EP01")
        r'\(S\d+\)',  # Season in parentheses like (S01)
        r'\(EP?\d+\)',  # Episode in parentheses like (EP01)

        # Year patterns (very reliable)
        r'\b(19|20)\d{2}\b',

        # Technical acronyms (check before quality indicators to avoid partial matches)
        r'\b\d*(KAI|HDR|AI|HFR|RMST|HBR|HQ)',  # Technical acronyms with optional preceding number

        # Quality indicators (very reliable)
        r'\b(480p|576p|720p|1080p|1440p|2160p)\b',
        r'\b(4K|8K|HD|FHD|UHD)\b',
        r'\b\d+[Kk](?=[^a-zA-Z]|$)',  # Match 4K, 8K but not 4KAI
        r'\b\d+[Pp]\b',  # Match 720p, 1080p in any case

        # Source indicators
        r'\b(WEB-DL|BluRay|BRRip|DVDRip|HDTV|PDTV|CAM|TS)\b',

        # Codec indicators
        r'\b(x264|x265|H264|H265|HEVC|AVC|XVID|DivX)\b',
        r'\b(AAC|AC3|DTS|MP3|FLAC)\b',
        r'\b(E-AC-3|TrueHD|Atmos)\b',

        # HDR indicators
        r'\b(HDR|HDR10|DV|Dolby\s*Vision)\b',

        # Frame rates and technical specs
        r'\b\d+fps\b',
        r'\b\d+bit\b',
        r'\b\d+\.\d+\b',  # Version numbers like 2.0

        # File extensions
        r'\.(mkv|mp4|avi|mov|wmv|flv|webm)$',

        # Common technical terms that indicate metadata
        r'\b(remux|encode|rip|web-dl|hdtv|brrip|dvdrip)\b',
        r'\b(extended|uncut|unrated|directors.cut|theatrical)\b',
        r'\b(proper|repack|internal|limited)\b',
    ]

    # Common technical terms (brand names, etc.)
    TECHNICAL_TERMS = {
        # Companies/brands
        'dolby', 'sony', 'thx', 'dts', 'eac3', 'truehd',
        'netflix', 'amazon', 'disney', 'hbo', 'hulu', 'paramount',
        'universal', 'warner', 'fox', 'bbc', 'itv',

        # Technical specifications
        'webdl', 'blu', 'ray', 'brrip', 'dvdrip', 'hdtv', 'cam',
        'telesync', 'sync', 'proper', 'repack', 'internal',
        'extended', 'uncut', 'unrated', 'directors',
        'cut', 'theatrical', 'imax', 'edition',

        # Release groups/common technical terms
        'scene', 'p2p', 'web', 'dl', 'rip', 'encode', 'remux',
        'hfr', 'hdr10', 'dolbyvision', 'atmos',

        # File format indicators
        'video', 'audio', 'multimedia', 'media', 'format',

        # Quality indicators
        'remastered', 'restored', 'digitally', 'mastered',
        'anamorphic', 'widescreen', 'fullscreen',
        'dual', 'mono', 'stereo', 'surround',

        # Content type indicators (when they're technical, not title)
        'technical', 'metadata', 'info', 'data', 'spec',
    }

    # Small words that should stay lowercase in titles (except when first)
    SMALL_WORDS = {
        'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
        'at', 'by', 'for', 'from', 'in', 'into', 'of', 'on', 'onto',
        'out', 'over', 'to', 'up', 'with', 'as', 'per', 'via',
        'vs', 'vs.', 'etc', 'et', 'al', 'de', 'del', 'la', 'el'
    }

    def extract_title(self, filename: str) -> str:
        """
        Extract title using the improved position-based approach.

        Strategy:
        1. Remove file extension properly
        2. Find the first boundary where technical metadata begins
        3. Extract everything before that boundary
        4. Clean and format the result
        """
        # Step 1: Remove file extension
        filename_no_ext = self._remove_extension(filename)

        # Step 2: Extract only Latin characters
        latin_content = self._extract_latin_content(filename_no_ext)

        # Step 3: Find the first technical boundary
        boundary_index = self._find_technical_boundary(latin_content)

        # Step 4: Extract title portion
        title_portion = latin_content[:boundary_index].strip()

        # Step 5: Clean and format
        clean_title = self._clean_and_format(title_portion)

        return clean_title

    def _remove_extension(self, filename: str) -> str:
        """Remove file extension, handling complex extensions properly."""
        # Common video/media extensions
        known_extensions = {
            '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
        }

        # Check if the filename ends with a known extension
        for ext in known_extensions:
            if filename.lower().endswith(ext):
                return filename[:-len(ext)]

        return filename  # No clear extension found

    def _extract_latin_content(self, content: str) -> str:
        """Extract only Latin characters, properly handling brackets and other content."""
        # Remove entire bracket sections completely (including content inside)
        content = re.sub(r'\[[^\]]*\]', ' ', content)
        content = re.sub(r'<[^>]*>', ' ', content)
        content = re.sub(r'\([^)]*\)', ' ', content)
        content = re.sub(r'\{[^}]*\}', ' ', content)

        # Replace non-Latin characters with spaces
        latin_chars = []
        for char in content:
            if char.isascii() and (char.isalnum() or char.isspace() or char in '._-,'):
                latin_chars.append(char)
            else:
                latin_chars.append(' ')

        return ''.join(latin_chars)

    def _find_technical_boundary(self, content: str) -> int:
        """Find the index where technical metadata begins."""
        # Convert to lowercase for pattern matching
        content_lower = content.lower()

        # Find the earliest occurrence of any boundary pattern
        earliest_boundary = len(content)  # Default to end

        # First pass: Check explicit boundary patterns
        for pattern in self.BOUNDARY_PATTERNS:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                boundary_index = match.start()
                # Only update if this is earlier than current boundary
                if boundary_index < earliest_boundary:
                    earliest_boundary = boundary_index

        # Second pass: Check underscore-separated technical patterns
        # This handles cases like "Movie.Title_2024_1080p"
        underscore_patterns = [
            r'_(19|20)\d{2}_',  # Years with underscores
            r'_(480p|576p|720p|1080p|1440p|2160p)_',  # Quality with underscores
            r'_(4K|8K|HD|FHD|UHD)_',  # Common quality terms with underscores
            r'_\d{4}_',  # Any 4-digit number with underscores (year-like)
        ]

        for pattern in underscore_patterns:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                # Position is at the underscore + 1 (start of the actual technical content)
                boundary_index = match.start() + 1
                # Only update if this is earlier than current boundary
                if boundary_index < earliest_boundary:
                    earliest_boundary = boundary_index

        # Third pass: Check for contextual technical metadata
        words = content_lower.split()

        for i, word in enumerate(words):
            # If we find isolated numbers (likely episode numbers)
            if word.isdigit() and len(word) <= 3 and i > 0:
                # Check if the previous words look like a title
                prev_words = words[:i]
                if self._looks_like_title(prev_words):
                    # This number is likely an episode number
                    # Find its position in the original content
                    word_start = 0
                    for j in range(i):
                        word_start += len(words[j]) + 1  # +1 for space

                    if word_start < earliest_boundary:
                        earliest_boundary = word_start

            # Check for 4-digit years
            if re.match(r'19|20\d{2}', word) and len(word) == 4:
                # Find position
                word_start = 0
                for j in range(i):
                    word_start += len(words[j]) + 1

                if word_start < earliest_boundary:
                    earliest_boundary = word_start

        return earliest_boundary

    def _looks_like_title(self, words: list) -> bool:
        """Check if these words look like a title rather than technical terms."""
        if len(words) == 0:
            return False

        if len(words) == 1:
            # Single word - check if it's likely a title
            word = words[0]
            return (
                len(word) >= 2  # Not a single character
                and word not in self.TECHNICAL_TERMS
                and not word.isdigit()
                and not word.startswith('s')  # Not likely S01, etc.
            )

        # Multiple words - check if they're mostly meaningful
        title_like_count = 0
        for word in words:
            if (len(word) >= 2 and
                word not in self.TECHNICAL_TERMS and
                not word.isdigit() and
                not word.startswith('s')):
                title_like_count += 1

        # If more than half are title-like, consider it a title
        return title_like_count > len(words) / 2

    def _clean_and_format(self, raw_title: str) -> str:
        """Clean and format the raw title."""
        if not raw_title or not raw_title.strip():
            return ""

        # Replace separators with spaces, but preserve commas
        title = re.sub(r'[._\-]+', ' ', raw_title)

        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()

        # Split into words
        words = title.lower().split()
        if not words:
            return ""

        # Apply title case with small words handling
        formatted_words = []

        for i, word in enumerate(words):
            if i == 0:
                # First word always capitalized
                formatted_words.append(word.capitalize())
            elif word in self.SMALL_WORDS:
                # Small words stay lowercase
                formatted_words.append(word)
            elif len(word) == 1:
                # Single letters stay lowercase unless they're meaningful
                if word.upper() in {'A', 'I'}:  # Remove X - keep 'x' lowercase in contexts like "Spy x Sect"
                    formatted_words.append(word.upper())
                else:
                    formatted_words.append(word)
            else:
                # Regular words capitalized
                formatted_words.append(word.capitalize())

        # Join back together
        final_title = ' '.join(formatted_words)

        # Final validation - if it's all technical, return empty
        if self._is_mostly_technical(final_title):
            return ""

        return final_title

    def _is_mostly_technical(self, text: str) -> bool:
        """Check if the text is mostly technical terms."""
        if not text:
            return True

        words = text.lower().split()
        if not words:
            return True

        # Count technical words
        tech_count = sum(1 for word in words if word in self.TECHNICAL_TERMS)

        # If more than half are technical, consider it technical
        return tech_count > len(words) / 2