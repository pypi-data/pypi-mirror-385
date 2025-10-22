"""
Tests for the filename analyzer module.

This module contains comprehensive tests for the FilenameAnalyzer class,
including edge cases and various filename patterns.
"""

import pytest
from pathlib import Path
from fmorg.analyzer import FilenameAnalyzer


class TestFilenameAnalyzer:
    """Test cases for FilenameAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.analyzer = FilenameAnalyzer()

    @pytest.mark.parametrize("filename,expected", [
        # Basic cases
        ("Divine.Love.Deep.Blue.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv", "Divine Love Deep Blue"),
        ("The.Matrix.1999.1080p.BluRay.x264.AC3-XYZ", "The Matrix"),
        ("Inception.2010.720p.WEB-DL.x264.AAC-ABC", "Inception"),

        # Multiple dots
        ("Breaking.Bad.S01E01.2008.HDTV.x264-LOL", "Breaking Bad"),
        ("Game.of.Thrones.S08E06.2019.1080p.HBO.WEB-DL.DD5.1.H.264", "Game of Thrones"),

        # Underscores
        ("The_Walking_Dead_S01E01_2010_HDTV_x264", "The Walking Dead"),
        ("Stranger_Things_S04E09_2022_Netflix_4K", "Stranger Things"),

        # Hyphens
        ("House-of-Cards-S01E01-2013-Netflix-1080p", "House of Cards"),
        ("The-Crown-S04E10-2020-Netflix-4K", "The Crown"),

        # Mixed separators
        ("The.Big.Bang.Theory_S01E01-2007_HDTV", "The Big Bang Theory"),
        ("Friends.S01E01_1994-NBC_HDTV", "Friends"),

        # Complex patterns
        ("The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.Extended.Edition.2160p.UHD.BluRay.x265.HDR.Atmos-EVO", "The Lord of the Rings The Fellowship of the Ring"),
        ("Avengers.Endgame.2019.4K.Ultra.HD.BluRay.HDR.DTS-HD.MA.7.1", "Avengers Endgame"),

        # No TV series pattern
        ("Joker.2019.1080p.BluRay.x264.DTS-HD.MA.5.1", "Joker"),
        ("Parasite.2019.1080p.BluRay.x264.AAC5.1", "Parasite"),

        # Edge cases
        ("A.Beautiful.Day.in.the.Neighborhood.2019.1080p.WEB-DL.DD5.1.H264", "A Beautiful Day in the Neighborhood"),
        ("The.Good.the.Bad.and.the.Ugly.1966.Remastered.1080p.BluRay.x264", "The Good the Bad and the Ugly"),
    ])
    def test_extract_title_various_patterns(self, filename, expected):
        """Test title extraction from various filename patterns."""
        result = self.analyzer.extract_title(filename)
        assert result == expected

    @pytest.mark.parametrize("filename,expected", [
        ("S01E01", True),
        ("S1E1", True),
        ("S12E34", True),
        ("s01e01", True),
        ("S01E01.Episode.Title", True),
        ("Movie.Title.2023.1080p", False),
        ("No.Episode.Here", False),
        ("Season.01.Episode.01", False),  # Not S##E## format
    ])
    def test_is_tv_series_episode(self, filename, expected):
        """Test TV series episode detection."""
        result = self.analyzer.is_tv_series_episode(filename)
        assert result == expected

    @pytest.mark.parametrize("filename,expected_category", [
        ("movie.mp4", "Videos"),
        ("episode.mkv", "Videos"),
        ("song.mp3", "Audio"),
        ("album.flac", "Audio"),
        ("document.pdf", "Documents"),
        ("spreadsheet.xlsx", "Documents"),
        ("photo.jpg", "Images"),
        ("image.png", "Images"),
        ("archive.zip", "Archives"),
        ("backup.tar.gz", "Archives"),
        ("unknown.xyz", "Other"),
    ])
    def test_get_file_category(self, filename, expected_category):
        """Test file categorization based on extension."""
        filepath = Path(filename)
        result = self.analyzer.get_file_category(filepath)
        assert result == expected_category

    def test_extract_title_empty_string(self):
        """Test title extraction from empty string."""
        result = self.analyzer.extract_title("")
        assert result == ""

    def test_extract_title_only_technical_terms(self):
        """Test title extraction from filename with only technical terms."""
        filename = "1080p.WEB-DL.x264.AAC-HDTV"
        result = self.analyzer.extract_title(filename)
        assert result == ""

    def test_extract_title_special_characters(self):
        """Test title extraction with special characters."""
        filename = "Movie.Title@#$%^&*()_+={}[]|\\:;\"'<>?,./"
        result = self.analyzer.extract_title(filename)
        assert result == "Movie Title"

    def test_extract_title_numbers_only(self):
        """Test title extraction with only numbers."""
        filename = "12345.67890.24680"
        result = self.analyzer.extract_title(filename)
        assert result == ""

    def test_extract_title_mixed_languages(self):
        """Test title extraction with mixed language characters."""
        filename = "Movie.标题.Movie.タイトル.2023.1080p"
        result = self.analyzer.extract_title(filename)
        assert result == "Movie Movie"

    def test_extract_title_case_preservation(self):
        """Test that title case is properly applied."""
        filename = "the.lord.of.the.rings.2001.1080p"
        result = self.analyzer.extract_title(filename)
        assert result == "The Lord of the Rings"

    def test_extract_title_small_words(self):
        """Test handling of small words (a, an, the, etc.)."""
        filename = "a.beautiful.day.in.the.neighborhood.2019.1080p"
        result = self.analyzer.extract_title(filename)
        assert result == "A Beautiful Day in the Neighborhood"

    def test_analyze_file_nonexistent(self):
        """Test analyzing a non-existent file."""
        filepath = Path("/nonexistent/file.mp4")
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file(filepath)

    def test_analyze_file_success(self, tmp_path):
        """Test successful file analysis."""
        # Create a test file
        test_file = tmp_path / "test.movie.2023.1080p.mp4"
        test_file.write_text("test content")

        title, category, original_name = self.analyzer.analyze_file(test_file)

        assert title == "Test Movie"
        assert category == "Videos"
        assert original_name == test_file.name

    @pytest.mark.parametrize("filename", [
        "Movie.Title.2023.1080p.WEB-DL.H264.AAC",
        "TV.Show.S01E01.2023.HDTV.x264",
        "Documentary.Series.2022.4K.NF.WEB-DL",
        "Anime.Title.S01E01.2023.1080p.BluRay.x265",
        "Classic.Film.1950.Remastered.1080p.BluRay",
    ])
    def test_extract_title_consistency(self, filename):
        """Test that title extraction is consistent across multiple calls."""
        result1 = self.analyzer.extract_title(filename)
        result2 = self.analyzer.extract_title(filename)
        assert result1 == result2

    def test_extract_title_year_filtering(self):
        """Test that years are properly filtered out."""
        filename = "The.Matrix.1999.1080p.BluRay.x264"
        result = self.analyzer.extract_title(filename)
        assert "1999" not in result
        assert result == "The Matrix"

    def test_extract_title_quality_filtering(self):
        """Test that quality indicators are properly filtered out."""
        filename = "Movie.Title.2023.2160p.4K.UHD.BluRay.HDR"
        result = self.analyzer.extract_title(filename)
        assert "2160p" not in result
        assert "4K" not in result
        assert "UHD" not in result
        assert "HDR" not in result
        assert result == "Movie Title"

    def test_extract_title_codec_filtering(self):
        """Test that codec information is properly filtered out."""
        filename = "Movie.Title.2023.x264.H264.H265.HEVC.AAC.DTS"
        result = self.analyzer.extract_title(filename)
        assert "x264" not in result
        assert "H264" not in result
        assert "H265" not in result
        assert "HEVC" not in result
        assert "AAC" not in result
        assert "DTS" not in result
        assert result == "Movie Title"

    def test_extract_title_release_group_filtering(self):
        """Test that release groups are properly filtered out."""
        filename = "Movie.Title.2023.1080p.WEB-DL-ReleaseGroup"
        result = self.analyzer.extract_title(filename)
        assert "ReleaseGroup" not in result
        assert result == "Movie Title"

    def test_extract_title_multiple_years(self):
        """Test handling of multiple years in filename."""
        filename = "Movie.Title.2020-2023.1080p.BluRay"
        result = self.analyzer.extract_title(filename)
        assert "2020" not in result
        assert "2023" not in result
        assert result == "Movie Title"

    def test_extract_title_very_long_filename(self):
        """Test extraction from very long filename."""
        long_title = "A " * 100  # 100 words
        filename = f"{long_title}.2023.1080p.mp4"
        result = self.analyzer.extract_title(filename)
        assert result.startswith("A")
        assert len(result) < len(filename)

    def test_regex_patterns_compilation(self):
        """Test that all regex patterns compile successfully."""
        patterns = [
            self.analyzer.TV_SERIES_PATTERN,
            self.analyzer.YEAR_PATTERN,
            self.analyzer.VIDEO_QUALITY_PATTERN,
            self.analyzer.VIDEO_SOURCE_PATTERN,
            self.analyzer.VIDEO_CODEC_PATTERN,
            self.analyzer.AUDIO_CODEC_PATTERN,
            self.analyzer.HDR_PATTERN,
            self.analyzer.RELEASE_GROUP_PATTERN,
            self.analyzer.RESOLUTION_PATTERN,
            self.analyzer.FRAME_RATE_PATTERN,
            self.analyzer.FILE_SIZE_PATTERN,
            self.analyzer.LANGUAGE_PATTERN,
            self.analyzer.TECHNICAL_TERMS_PATTERN,
            self.analyzer.SEPARATOR_PATTERN,
            self.analyzer.LATIN_LETTERS_PATTERN,
        ]

        for pattern in patterns:
            assert pattern.pattern is not None
            assert pattern.flags >= 0


class TestHiddenFileHandling:
    """Test hidden file detection and handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FilenameAnalyzer()

    def test_is_hidden_file_with_strings(self):
        """Test hidden file detection with string paths."""
        # Test hidden files (should return True)
        hidden_files = [
            ".DS_Store",
            ".gitignore",
            ".bashrc",
            ".config",
            ".hidden_file.txt",
            ".movie.mp4",
            ".temporary"
        ]

        for filename in hidden_files:
            assert self.analyzer.is_hidden_file(filename), f"Failed to detect hidden file: {filename}"

        # Test regular files (should return False)
        regular_files = [
            "movie.mp4",
            "document.pdf",
            "image.jpg",
            "DS_Store",  # No dot prefix
            "gitignore",  # No dot prefix
            "file.txt",
            "normal_movie.mkv",
            ".",  # Current directory reference
            ".."  # Parent directory reference
        ]

        for filename in regular_files:
            assert not self.analyzer.is_hidden_file(filename), f"Incorrectly detected regular file as hidden: {filename}"

    def test_is_hidden_file_with_path_objects(self):
        """Test hidden file detection with Path objects."""
        # Test hidden files with Path objects
        hidden_paths = [
            Path("/home/user/.DS_Store"),
            Path("/tmp/.gitignore"),
            Path(".hidden_folder/.hidden_file"),
            Path("./.config")
        ]

        for path in hidden_paths:
            assert self.analyzer.is_hidden_file(path), f"Failed to detect hidden file: {path}"

        # Test regular files with Path objects
        regular_paths = [
            Path("/home/user/movie.mp4"),
            Path("/tmp/document.pdf"),
            Path("normal_file.txt"),
            Path("folder/subfolder/file.mkv"),
            Path("."),  # Current directory reference
            Path("..")  # Parent directory reference
        ]

        for path in regular_paths:
            assert not self.analyzer.is_hidden_file(path), f"Incorrectly detected regular file as hidden: {path}"

    def test_analyze_file_hidden_file_silently_ignored(self, tmp_path):
        """Test that analyze_file silently returns None for hidden files."""
        # Create a hidden file
        hidden_file = tmp_path / ".hidden_movie.mp4"
        hidden_file.write_text("content")

        # Should return None, None, None for hidden files (silently ignored)
        title, category, original_name = self.analyzer.analyze_file(hidden_file)
        assert title is None
        assert category is None
        assert original_name is None

    def test_analyze_file_regular_file_acceptance(self, tmp_path):
        """Test that analyze_file works normally for regular files."""
        # Create a regular file
        regular_file = tmp_path / "normal_movie.mp4"
        regular_file.write_text("content")

        # Should work normally for regular files
        title, category, original_name = self.analyzer.analyze_file(regular_file)

        assert title == "Normal Movie"
        assert category == "Videos"
        assert original_name == "normal_movie.mp4"

    def test_hidden_file_edge_cases(self):
        """Test edge cases for hidden file detection."""
        # Files that start with dot but have special considerations
        edge_cases = [
            (".", False),  # Current directory reference (not a hidden file)
            ("..", False),  # Parent directory reference (starts with two dots)
            (".hidden with spaces.txt", True),
            (".file-with-dashes.mkv", True),
            (".file.with.dots.mp4", True),
        ]

        for filename, expected in edge_cases:
            result = self.analyzer.is_hidden_file(filename)
            assert result == expected, f"Expected {expected} for {filename}, got {result}"

    def test_hidden_file_case_sensitivity(self):
        """Test that hidden file detection is case-sensitive."""
        # Unix/Linux is case-sensitive, but we only care about the dot prefix
        test_cases = [
            (".hidden", True),
            (".Hidden", True),  # Still hidden despite capital H
            (".HIDDEN", True),  # Still hidden despite uppercase
        ]

        for filename, expected in test_cases:
            result = self.analyzer.is_hidden_file(filename)
            assert result == expected, f"Expected {expected} for {filename}, got {result}"

    def test_hidden_file_path_vs_filename(self):
        """Test that only the filename matters, not the full path."""
        # Even if the path contains hidden directories, only the filename matters
        test_cases = [
            (Path("/home/user/.hidden_dir/normal_file.mp4"), False),  # Normal file in hidden directory
            (Path(".hidden_dir/.hidden_file.mp4"), True),  # Hidden file in hidden directory
            (Path("normal_dir/.hidden_file.mp4"), True),  # Hidden file in normal directory
        ]

        for path, expected in test_cases:
            result = self.analyzer.is_hidden_file(path)
            assert result == expected, f"Expected {expected} for {path}, got {result}"