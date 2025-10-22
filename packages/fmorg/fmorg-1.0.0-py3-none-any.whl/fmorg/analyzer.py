"""
Improved filename analyzer - fundamentally redesigned approach.

This module implements a position-based, context-aware approach
that focuses on where technical metadata begins rather than individual word analysis.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional


class FilenameAnalyzer:
    """
    Improved analyzer using position-based and contextual analysis.

    Core principle: Stop at the first major technical metadata pattern,
    then extract everything before it as the title.
    """

    # Regex pattern constants for testing compatibility
    TV_SERIES_PATTERN = re.compile(r'[._-]?[Ss]\d{1,3}[Ee]\d{1,3}\b')
    YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
    VIDEO_QUALITY_PATTERN = re.compile(r'\b(480p|576p|720p|1080p|1440p|2160p)\b')
    VIDEO_SOURCE_PATTERN = re.compile(r'\b(WEB-DL|BluRay|BRRip|DVDRip|HDTV|PDTV|CAM|TS)\b')
    VIDEO_CODEC_PATTERN = re.compile(r'\b(x264|x265|H264|H265|HEVC|AVC|XVID|DivX)\b')
    AUDIO_CODEC_PATTERN = re.compile(r'\b(AAC|AC3|DTS|MP3|FLAC|E-AC-3|TrueHD|Atmos)\b')
    HDR_PATTERN = re.compile(r'\b(HDR|HDR10|DV|Dolby\s*Vision)\b')
    RELEASE_GROUP_PATTERN = re.compile(r'-[A-Za-z0-9]+$')
    RESOLUTION_PATTERN = re.compile(r'\b\d+[Kk]\b')
    FRAME_RATE_PATTERN = re.compile(r'\b\d+fps\b')
    FILE_SIZE_PATTERN = re.compile(r'\b\d+(\.\d+)?\s*(GB|MB|KB)\b')
    LANGUAGE_PATTERN = re.compile(r'\b(ENG|JPN|CHI|KOR|FRE|GER|SPA|ITA)\b')
    TECHNICAL_TERMS_PATTERN = re.compile(r'\b(' + '|'.join([
        'dolby', 'sony', 'thx', 'dts', 'eac3', 'truehd',
        'netflix', 'nf', 'amazon', 'amz', 'disney', 'hbo', 'hulu', 'paramount',
        'universal', 'warner', 'fox', 'bbc', 'itv',
        'webdl', 'web', 'dl', 'blu', 'ray', 'brrip', 'dvdrip', 'hdtv', 'cam',
        'telesync', 'sync', 'proper', 'repack', 'internal',
        'extended', 'uncut', 'unrated', 'directors',
        'cut', 'theatrical', 'imax', 'edition',
        'scene', 'p2p', 'rip', 'encode', 'remux',
        'hfr', 'hdr10', 'dolbyvision', 'atmos',
        'remastered', 'restored', 'digitally', 'mastered',
        'anamorphic', 'widescreen', 'fullscreen',
        'dual', 'mono', 'stereo', 'surround',
        'technical', 'metadata', 'info', 'data', 'spec',
        'ai', 'hq', 'hbr', 'rmst', 'max'
    ]) + r')\b')
    SEPARATOR_PATTERN = re.compile(r'[._\-+]+')
    LATIN_LETTERS_PATTERN = re.compile(r'[a-zA-Z]+')

    # Technical boundary patterns - these indicate where technical metadata begins
    BOUNDARY_PATTERNS = [
        # Episode patterns (highest priority)
        r'[._-]?[Ss]\d{1,3}[Ee]\d{1,3}\b',  # Allow preceding separators
        r'\bEpisode\s*\d+\b',
        r'[._-]?\bEpisode\b',  # Standalone "Episode" word with optional preceding separator
        r'[._-]?\b(Special|OVA|Bonus|Extra|Prologue|Epilogue)\b',  # Special episode types
        r'EP?\d+',    # EP01, E01, etc. (without word boundary requirement)
        r'[._-]?S\d+',    # Allow preceding separators for S3, S01, etc.
        r'-\s*\d+',   # Hyphen followed by numbers (e.g., "- 01", "-01")
        r'-\s*EP?\d+',   # Hyphen followed by EP01 (e.g., "- EP01")
        r'\(S\d+\)',  # Season in parentheses like (S01)
        r'\(EP?\d+\)',  # Episode in parentheses like (EP01)

        # Year patterns - handled by contextual analysis for better accuracy
        # r'\b(19|20)\d{2}\b',  # Years (19xx, 20xx) - handled in contextual analysis

        # Technical acronyms (check before quality indicators to avoid partial matches)
        r'\b\d*(KAI|HDR|AI|HFR|RMST|HBR|HQ)',  # Technical acronyms with optional preceding number

        # Quality indicators (very reliable)
        r'\b(480p|576p|720p|1080p|1440p|2160p)\b',
        r'\b(4K|8K|HD|FHD|UHD)\b',
        r'\b\d+[Kk](?=[^a-zA-Z]|$)',  # Match 4K, 8K but not 4KAI
        r'\b\d+[Pp]\b',  # Match 720p, 1080p in any case

        # Source indicators
        r'\b(WEB-DL|BluRay|BRRip|DVDRip|HDTV|PDTV|CAM|TS)\b',
        r'\b(NF|AMZON|AMZ|HBO|MAX|DISNEY|HULU)\b',  # Streaming service abbreviations

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
        # Companies/brands - streaming services
        'dolby', 'sony', 'thx', 'dts', 'eac3', 'truehd',
        'netflix', 'nf', 'amazon', 'amz', 'disney', 'hbo', 'hulu', 'paramount',
        'universal', 'warner', 'fox', 'bbc', 'itv',

        # Technical specifications
        'webdl', 'web', 'dl', 'blu', 'ray', 'brrip', 'dvdrip', 'hdtv', 'cam',
        'telesync', 'sync', 'proper', 'repack', 'internal',
        'extended', 'uncut', 'unrated', 'directors',
        'cut', 'theatrical', 'imax', 'edition',

        # Release groups/common technical terms
        'scene', 'p2p', 'rip', 'encode', 'remux',
        'hfr', 'hdr10', 'dolbyvision', 'atmos',

        # Quality indicators
        'remastered', 'restored', 'digitally', 'mastered',
        'anamorphic', 'widescreen', 'fullscreen',
        'dual', 'mono', 'stereo', 'surround',

        # Content type indicators (when they're technical, not title)
        'technical', 'metadata', 'info', 'data', 'spec',

        # Additional common abbreviations
        'ai', 'hq', 'hbr', 'rmst', 'max',
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
        2. Extract only Latin characters
        3. Try to extract title from different segments
        4. Clean and format the result
        """
        # Step 1: Extract only the filename (not full path) - handle special characters
        import os
        try:
            filename_only = os.path.basename(filename)
            # If basename returns empty due to invalid path characters, use the original
            if not filename_only:
                filename_only = filename
        except (ValueError, OSError):
            filename_only = filename

        # Step 2: Remove file extension
        filename_no_ext = self._remove_extension(filename_only)

        # Step 3: Extract only Latin characters
        latin_content = self._extract_latin_content(filename_no_ext)

        # Step 4: Try different extraction strategies

        # Strategy A: Extract from before the first boundary (most common case)
        boundary_index = self._find_technical_boundary(latin_content)
        title_before_boundary = latin_content[:boundary_index].strip()

        # Strategy B: If no meaningful title before boundary, try extracting from between patterns
        # This handles cases like "[Group] S01E001 Title Here [Technical]"
        meaningful_before_boundary = (
            title_before_boundary and
            len(title_before_boundary) >= 2 and
            not all(c in '._- ' for c in title_before_boundary) and
            not re.match(r'^[._-]*[Ss]\d+', title_before_boundary.strip('._- '))  # Not just season info
        )

        if not meaningful_before_boundary:
            title_between_patterns = self._extract_between_episode_and_technical(latin_content)
            if title_between_patterns:
                return self._clean_and_format(title_between_patterns)

        # Step 4: Clean and format the primary title
        clean_title = self._clean_and_format(title_before_boundary, title_before_boundary)

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

        # Special case: If content starts with technical metadata, boundary is at 0
        leading_patterns = [
            r'^(480p|576p|720p|1080p|1440p|2160p)',  # Quality at start
            r'^(4K|8K|HD|FHD|UHD)',  # Common quality terms at start
            r'^(19|20)\d{2}\b',  # Years at start
        ]

        for pattern in leading_patterns:
            if re.match(pattern, content_lower, re.IGNORECASE):
                return 0  # Entire content is technical metadata

        # Find the earliest occurrence of any boundary pattern
        earliest_boundary = len(content)  # Default to end

        # First pass: Check explicit boundary patterns
        for pattern in self.BOUNDARY_PATTERNS:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                boundary_index = match.start()
                # Only update if this is earlier than current boundary
                if boundary_index < earliest_boundary:
                    # Additional check: Ensure there's meaningful content before this boundary
                    before_boundary = content[:boundary_index].strip()

                    # Special case: If boundary is very early (position < 10) and content before is very short
                    # it might be technical metadata appearing before the actual title
                    if boundary_index < 10 and len(before_boundary) < 5:
                        # Check if there's meaningful content after this pattern that looks like a title
                        after_pattern = content[match.end():match.end() + 20].strip()
                        if len(after_pattern) > 5:  # There's substantial content after
                            # This might be technical metadata before the title, don't set boundary here
                            continue

                    # If there's meaningful content before the boundary, use it
                    if len(before_boundary) >= 2:  # At least 2 characters of meaningful content
                        # But if it's just separators, don't treat as boundary
                        if not all(c in '._- ' for c in before_boundary):
                            earliest_boundary = boundary_index

        # Second pass: Check underscore-separated technical patterns
        # This handles cases like "Movie.Title_2024_1080p"
        underscore_patterns = [
            r'_(19|20)\d{2}[_-]',  # Years with underscores or hyphens
            r'_(480p|576p|720p|1080p|1440p|2160p)_',  # Quality with underscores
            r'_(4K|8K|HD|FHD|UHD)_',  # Common quality terms with underscores
            r'_\d{4}[_-]',  # Any 4-digit number with underscores or hyphens (year-like)
            r'_\d{1,3}(_|$|-)',  # Isolated numbers with separators (episode numbers, etc.)
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
        # Use dot-separated analysis for better pattern detection
        words = content_lower.replace('.', ' ').split()

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

            # Check for 4-digit years with context awareness
            # Note: Years are now handled by boundary patterns, but we keep this for edge cases
            if re.match(r'19|20\d{2}', word) and len(word) == 4:
                # Get context words
                prev_word = words[i-1] if i > 0 else ''
                next_word = words[i+1] if i < len(words)-1 else ''

                # Check if there's meaningful title content between year and technical metadata
                words_after_year = words[i+1:] if i+1 < len(words) else []

                # Find the first technical word after the year
                first_tech_index = None
                meaningful_before_tech = []

                for j, w in enumerate(words_after_year):
                    if (w in self.TECHNICAL_TERMS or
                        any(tech in w.lower() for tech in ['480p', '720p', '1080p', '2160p', '4k', '8k', 'hd', 'uhd', 'web-dl', 'bluray'])):
                        first_tech_index = j
                        break
                    else:
                        meaningful_before_tech.append(w)

                # If there's meaningful content before the technical content, don't set boundary at year
                if first_tech_index is not None and len(meaningful_before_tech) > 0:
                    # Set boundary at the first technical content instead, allowing meaningful title content to pass through
                    tech_word = words_after_year[first_tech_index]
                    # Find this technical word in the original content
                    tech_match = re.search(r'\b' + tech_word + r'\b', content_lower)
                    if tech_match and tech_match.start() < earliest_boundary:
                        earliest_boundary = tech_match.start()
                elif first_tech_index is None:
                    # No technical content after year, don't treat year as boundary
                    continue
                else:
                    # Only technical content immediately after year, treat year as boundary
                    year_match = re.search(r'\b' + word + r'\b', content_lower)
                    if year_match and year_match.start() < earliest_boundary:
                        earliest_boundary = year_match.start()

        return earliest_boundary

    def _extract_between_episode_and_technical(self, content: str) -> str:
        """
        Extract title that appears between episode patterns and technical metadata.
        This handles cases like "[Group] S01E001 Title Here [Technical]"
        """
        content_lower = content.lower()

        # Find episode patterns
        episode_patterns = [
            r'[._-]?[Ss]\d{1,3}[Ee]\d{1,3}\b',
            r'\bEpisode\s*\d+\b',
            r'[._-]?\b(Special|OVA|Bonus|Extra|Prologue|Epilogue)\b',
            r'EP?\d+',
            r'-\s*\d+',
            r'\(S\d+\)',
            r'\(EP?\d+\)',
        ]

        # Find technical patterns (after the title)
        technical_patterns = [
            r'\[.*?\]',  # Any bracket content
            r'\b(480p|576p|720p|1080p|1440p|2160p)\b',
            r'\b(4K|8K|HD|FHD|UHD)\b',
            r'\b(WEB-DL|BluRay|BRRip|DVDRip|HDTV|PDTV|CAM|TS)\b',
            r'\b(x264|x265|H264|H265|HEVC|AVC|XVID|DivX)\b',
            r'\b(HDR|HDR10|DV|Dolby\s*Vision)\b',
            r'\b\d+fps\b',
        ]

        # Find the first episode pattern
        earliest_episode_end = None
        for pattern in episode_patterns:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                episode_end = match.end()
                if earliest_episode_end is None or episode_end < earliest_episode_end:
                    earliest_episode_end = episode_end

        if earliest_episode_end is None:
            return ""

        # Find the first technical pattern after the episode
        earliest_tech_start = len(content)
        for pattern in technical_patterns:
            match = re.search(pattern, content[earliest_episode_end:], re.IGNORECASE)
            if match:
                tech_start = earliest_episode_end + match.start()
                if tech_start < earliest_tech_start:
                    earliest_tech_start = tech_start

        # Extract content between episode and technical patterns
        if earliest_episode_end < earliest_tech_start:
            title_candidate = content[earliest_episode_end:earliest_tech_start].strip()
            # Clean up separators
            title_candidate = re.sub(r'^[._\s-]+', '', title_candidate)  # Remove leading separators
            title_candidate = re.sub(r'[._\s-]+$', '', title_candidate)  # Remove trailing separators

            return title_candidate

        return ""

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

    def _clean_and_format(self, raw_title: str, original_context: str = None) -> str:
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

        # Filter out obvious non-title content
        filtered_words = []
        for i, word in enumerate(words):
            # Skip isolated years (very likely metadata unless it's the main title)
            if re.match(r'19|20\d{2}', word) and len(word) == 4:
                # Only keep year if it's likely the actual title (e.g., "1984" by itself)
                # or part of a well-known title with the year (very rare)
                if len(words) == 1:
                    # Single word title that's just a year - keep it
                    filtered_words.append(word)
                else:
                    # Year with other content - likely metadata, skip it
                    continue

            # Handle repeated numbers (like "300.300" -> should become just "300")
            if word.isdigit():
                # Check if this number appears multiple times in the title
                word_indices = [j for j, w in enumerate(words) if w == word]
                if len(word_indices) > 1:
                    # This number repeats - keep only the first occurrence
                    if i == word_indices[0]:
                        filtered_words.append(word)
                    continue
                else:
                    # Single occurrence of a number - keep it
                    filtered_words.append(word)
                continue

            # Filter single letters
            if len(word) == 1:
                # Keep 'A' and 'I' as they're meaningful words
                if word in {'a', 'i'}:
                    filtered_words.append(word)
                else:
                    # For other single letters, only keep if between meaningful words
                    words_before = words[:i]
                    words_after = words[i+1:]
                    meaningful_before = sum(1 for w in words_before if len(w) > 2 and w.isalpha())
                    meaningful_after = sum(1 for w in words_after if len(w) > 2 and w.isalpha())

                    if meaningful_before >= 1 and meaningful_after >= 1:
                        filtered_words.append(word)
                continue

            # Keep everything else
            filtered_words.append(word)

        # Apply title case with small words handling
        formatted_words = []

        for i, word in enumerate(filtered_words):
            # Get the original word from the same position in the original words list
            # This helps maintain context for capitalization decisions
            original_word = words[i] if i < len(words) else word
            if i == 0:
                # First word always capitalized
                formatted_words.append(word.capitalize())
            elif word in self.SMALL_WORDS:
                # Small words should stay lowercase unless they are the first word
                # Only capitalize the first word or if the word is part of a proper noun/acronym
                if i == 0:
                    formatted_words.append(word.capitalize())
                elif word.upper() in {'A', 'I'}:  # Personal pronouns that should be capitalized
                    formatted_words.append(word.upper())
                elif word == 'the' and self._should_capitalize_the(filtered_words, i):
                    # Capitalize 'the' when it starts a major title phrase
                    formatted_words.append(word.capitalize())
                elif word == 'a' and self._should_capitalize_a(filtered_words, i):
                    # Only capitalize 'a' in very specific cases like "A Tale of Two Cities"
                    formatted_words.append(word.capitalize())
                else:
                    # All other small words stay lowercase
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

        # Final validation - if it's all technical or all numbers, return empty
        if self._is_mostly_technical(final_title):
            return ""

        # Check if title is all numbers (no meaningful content)
        # Allow single numbers that aren't recognized as years (e.g., "300", "24")
        if final_title and all(word.isdigit() for word in final_title.split()):
            # If it's a single word that's not a 4-digit year, keep it
            words = final_title.split()
            if len(words) == 1 and len(words[0]) != 4:
                return final_title
            return ""

        return final_title

    def is_tv_series_episode(self, filename: str) -> bool:
        """
        Check if the filename contains a TV series episode pattern.

        Args:
            filename: The filename to check

        Returns:
            True if the filename contains a TV series episode pattern
        """
        # Check for standard S##E## patterns
        if self.TV_SERIES_PATTERN.search(filename):
            return True

        # Check for other episode patterns
        episode_patterns = [
            r'\bEpisode\s*\d+\b',
            r'[._-]?\b(Special|OVA|Bonus|Extra|Prologue|Epilogue)\b',
            r'EP?\d+',
            r'-\s*\d+',
            r'\(S\d+\)',
            r'\(EP?\d+\)',
        ]

        for pattern in episode_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True

        return False

    def is_hidden_file(self, filepath) -> bool:
        """
        Check if a file is a hidden file (starts with a dot).

        Hidden files in Unix/Linux/macOS start with a dot and are typically
        system files, configuration files, or temporary files that should
        not be processed by the file organizer.

        Args:
            filepath: Path to the file (can be string or Path object)

        Returns:
            True if the file is hidden, False otherwise
        """
        # Convert to Path object if it's a string
        path_obj = Path(filepath) if not isinstance(filepath, Path) else filepath

        # Get just the filename (not the full path)
        filename = path_obj.name

        # Skip special directory references (.) and (..) - they're not hidden files
        if filename in ('.', '..'):
            return False

        # Check if filename starts with a dot
        return filename.startswith('.')

        # Note: We could also check for other hidden file indicators:
        # - Windows hidden files (but this requires filesystem access)
        # - Files in hidden directories (like .git/config)
        # But for cross-platform safety, we'll stick to the dot prefix rule

    def get_file_category(self, filepath: Path) -> str:
        """
        Determine the file category based on its extension.

        Args:
            filepath: Path to the file

        Returns:
            String representing the file category
        """
        suffix = filepath.suffix.lower()

        # Video files
        video_extensions = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.m4v', '.3gp', '.ogv', '.ts', '.mts', '.m2ts'
        }

        # Audio files
        audio_extensions = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            '.opus', '.aiff', '.au', '.ra', '.amr'
        }

        # Document files
        document_extensions = {
            '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
            '.xls', '.xlsx', '.ppt', '.pptx', '.odp', '.key', '.csv'
        }

        # Image files
        image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.svg', '.ico', '.psd', '.raw', '.heic'
        }

        # Archive files
        archive_extensions = {
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
            '.ace', '.lha', '.sit', '.dmg', '.iso', '.img'
        }

        if suffix in video_extensions:
            return "Videos"
        elif suffix in audio_extensions:
            return "Audio"
        elif suffix in document_extensions:
            return "Documents"
        elif suffix in image_extensions:
            return "Images"
        elif suffix in archive_extensions:
            return "Archives"
        else:
            return "Other"

    def analyze_file(self, filepath: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Analyze a file and return its title, category, and original name.

        Args:
            filepath: Path to the file to analyze

        Returns:
            Tuple of (title, category, original_name)

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Skip hidden files (starting with a dot) - return None to silently ignore
        if self.is_hidden_file(filepath):
            return None, None, None

        # Extract title from filename
        title = self.extract_title(filepath.name)

        # Get file category
        category = self.get_file_category(filepath)

        # Get original name
        original_name = filepath.name

        return title, category, original_name

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

    def _should_capitalize_a(self, filtered_words: List[str], position: int) -> bool:
        """
        Determine if 'a' should be capitalized based on context.

        Only capitalizes 'a' in very specific cases like when it starts a title
        is part of a well-known phrase, or is between proper nouns.

        Args:
            filtered_words: List of filtered words
            position: Position of the word 'a' in the list

        Returns:
            True if 'a' should be capitalized, False otherwise
        """
        # Don't capitalize 'a' in the middle of normal titles
        if position == 0:
            return True

        # Very specific cases only - be conservative
        # Check if this 'a' is between two proper-looking words
        if position > 0 and position < len(filtered_words) - 1:
            prev_word = filtered_words[position - 1]
            next_word = filtered_words[position + 1]

            # Only capitalize if both surrounding words are capitalized-like proper nouns
            # and this looks like a title pattern
            if (prev_word and next_word and
                prev_word[0].isupper() and next_word[0].isupper() and
                len(prev_word) > 2 and len(next_word) > 2):
                return True

        return False

    def _should_capitalize_the(self, filtered_words: List[str], position: int) -> bool:
        """
        Determine if 'the' should be capitalized based on context.

        Capitalizes 'the' when it appears to start a major title phrase
        or is part of a well-known title construction.

        Args:
            filtered_words: List of filtered words
            position: Position of the word 'the' in the list

        Returns:
            True if 'the' should be capitalized, False otherwise
        """
        # Don't capitalize 'the' if it's the first word (already handled)
        if position == 0:
            return False

        # Be very conservative about capitalizing 'the'
        # Only capitalize when it clearly starts a major title phrase
        if position > 0 and position < len(filtered_words) - 1:
            prev_word = filtered_words[position - 1]
            next_word = filtered_words[position + 1]

            # Capitalize 'the' only if it follows a word that clearly ends a title/phrase
            # AND is followed by multiple substantial words suggesting a new title phrase
            if (len(prev_word) >= 4 and  # Previous word must be substantial (4+ chars)
                len(next_word) >= 4 and  # Next word must be substantial (4+ chars)
                next_word.isalpha() and
                position < len(filtered_words) - 2):  # Must have at least 2 words after

                # Check if there are meaningful words after 'the'
                next_words = filtered_words[position + 1:position + 4]  # Check next 3 words

                # Count substantial words (4+ chars) and allow one small word
                substantial_count = 0
                has_small_word = False

                for w in next_words:
                    if len(w) > 3 and w.isalpha():
                        substantial_count += 1
                    elif w in self.SMALL_WORDS:
                        has_small_word = True

                # Be restrictive but allow cases where 'the' clearly starts a subtitle
                # Check if we have substantial content after AND good context before
                if (position >= 4):              # There's good context before it

                    # Allow cases with 1+ substantial word + small words (common in titles)
                    if (substantial_count >= 1 and has_small_word and
                        (len(prev_word) >= 5 or position >= 6)):
                        return True
                    # Or cases with 2+ substantial words (clear title phrases)
                    elif substantial_count >= 2:
                        return True

        return False