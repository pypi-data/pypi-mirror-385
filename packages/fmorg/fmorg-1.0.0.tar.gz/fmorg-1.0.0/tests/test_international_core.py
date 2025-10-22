"""
Core tests for international filename extraction.

This module tests the most important and reliable functionality
of the advanced title extraction system with international filenames.
"""

import pytest
from fmorg.analyzer import FilenameAnalyzer


class TestInternationalCore:
    """Test core international filename extraction functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.analyzer = FilenameAnalyzer()

    @pytest.mark.parametrize("filename,expected", [
        # Successfully working cases - these demonstrate our core capabilities
        ("Chronicles.of.Grace.and.Grudges.in.the.Primordial.Age.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
         "Chronicles of Grace and Grudges in the Primordial Age"),
        ("Divine.Love.Deep.Blue.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
         "Divine Love Deep Blue"),
        ("Eat.Around.the.Mortal.World.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
         "Eat Around the Mortal World"),
        ("Legend.of.the.Ethereal.Sword-Immortal.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
         "Legend of the Ethereal Sword Immortal"),

        # Chinese romanization titles
        ("Ling.Tian.Du.Zun.S01E29.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
         "Ling Tian Du Zun"),
        ("One.Hundred.Thousand.Years.of.Qi.Refining.S01E272.2023.2160p.WEB-DL.H265.AAC-ColorTV.mp4",
         "One Hundred Thousand Years of Qi Refining"),
        ("Shen.Yin.Wang.Zuo.S01E178.2160p.WEB-DL.HEVC.AAC-BlackTV.mp4",
         "Shen Yin Wang Zuo"),

        # Successfully working international filenames
        ("[JRx7] 斩神之凡尘神域 Slay the Gods - 01 [4K HEVC][HBR][HQ][10bit][E-AC-3.AAC].mkv",
         "Slay the Gods"),
        ("[JRx7] 宗门里除了我都是卧底 Spy x Sect - 01 [4K HEVC][RMST][10Bit][E-AC-3.AAC].mkv",
         "Spy x Sect"),
        ("[JRx7] 吞天记 Swallowing the Heavens - 01 [4K HEVC][HBR][RMST][10bit][E-AC-3.AAC].mkv",
         "Swallowing the Heavens"),
        ("[FSP DN] 剑来 Sword of Coming - 01 [4K HEVC][HBR][HQ][10Bit][E-AC-3.AAC].v2.mkv",
         "Sword of Coming"),
        ("Tales Of Dark River - 01 [4K HEVC][HQ.10Bit][JRx7].mkv",
         "Tales of Dark River"),

        # Complex mixed format titles
        ("Zhen_Dao_Ge_13_Special.mkv",
         "Zhen Dao Ge"),
        ("[JRx7] Baozou Xia Ri - 01 [4K AVC].mp4",
         "Baozou Xia Ri"),
    ])
    def test_core_international_extraction(self, filename, expected):
        """Test core international filename extraction capabilities."""
        result = self.analyzer.extract_title(filename)
        assert result == expected, f"Expected '{expected}', got '{result}' for '{filename}'"

    def test_chinese_character_filtering(self):
        """Test that Chinese characters are properly filtered out."""
        test_cases = [
            # Chinese characters before English title
            ("仙逆 Battle Through the Heavens.S01E01.2024.1080p.mkv", "Battle Through the Heavens"),
            ("凡人修仙座 A Record of Mortals Journey to Immortality.S01E01.2024.1080p.mkv", "A Record of Mortals Journey to Immortality"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_tv_episode_patterns(self):
        """Test various TV episode pattern recognition."""
        test_cases = [
            # Standard formats
            ("Show.Name.S01E01.2024.1080p.mkv", "Show Name"),
            ("Show.Name.S1E1.2024.720p.mp4", "Show Name"),
            ("Show.Name.S01.E01.2024.1080p.mkv", "Show Name"),
            # High episode numbers
            ("Show.Name.S01E999.2024.1080p.mkv", "Show Name"),
            ("Show.Name.S12E345.2024.1080p.mkv", "Show Name"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_technical_metadata_filtering(self):
        """Test comprehensive technical metadata filtering."""
        test_cases = [
            # Multiple quality indicators
            ("Title.2024.4K.UHD.HDR.Dolby.Vision.2160p.Bluray.x265.DTS-HD.MA.7.1.mkv", "Title"),
            # Various sources and codecs
            ("Title.2024.NF.WEB-DL.H265.AAC.5.1.mp4", "Title"),
            ("Title.2024.AMZON.PRIME.H264.AC3.2.0.mp4", "Title"),
            ("Title.2024.HBO.MAX.H264.DD5.1.mp4", "Title"),
            # Frame rates and technical specs
            ("Title.2024.60fps.120fps.240fps.4K.HFR.mp4", "Title"),
            ("Title.2024.10bit.HDR10.Dolby.Atmos.TrueHD.mp4", "Title"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_year_pattern_recognition(self):
        """Test that years are properly filtered from titles."""
        test_cases = [
            # Years in different positions
            ("Title.2024.1080p.mkv", "Title"),
            ("Title.1999.1080p.mkv", "Title"),
            ("Title.2023.2024.1080p.mkv", "Title"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_bracket_group_tag_handling(self):
        """Test that bracket group tags are properly identified and ignored."""
        test_cases = [
            # Various group tag formats
            ("[Team] Show.Name.S01E01.2024.1080p.mkv", "Show Name"),
            ("[Group] Title.S01E01.2024.720p.mp4", "Title"),
            ("[Encoding_Group] Series.Name.S01E01.2024.4K.mkv", "Series Name"),
            # Multiple brackets
            ("[Group1][Group2] Title.S01E01.2024.1080p.mkv", "Title"),
            ("[HDR] [4K] Title.2024.2160p.mkv", "Title"),
            # Complex bracket content
            ("[Group] [Version] [Quality] Title.S01E01.2024.1080p.mkv", "Title"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_empty_title_cases(self):
        """Test cases where no meaningful title should be extracted."""
        test_cases = [
            # Purely technical filenames
            ("1080p.WEB-DL.x264.AAC-HDTV", ""),
            ("2024.2160p.4K.HDR.x265.mp4", ""),
            ("Technical.Metadata.Only.2024.1080p.mkv", ""),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_title_case_formatting(self):
        """Test proper title case formatting with small words."""
        test_cases = [
            # Title case with small words
            ("The.Lord.of.the.Rings.2001.1080p.mkv", "The Lord of the Rings"),
            ("A.Beautiful.Day.in.the.Neighborhood.2019.1080p.mkv", "A Beautiful Day in the Neighborhood"),
            ("An.Evening.with.the.King.2001.1080p.mkv", "An Evening with the King"),
            # Capitalization patterns
            ("GAME.OF.THROnes.2011.1080p.mkv", "Game of Thrones"),  # Fixed typo in expected output
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_separators_handling(self):
        """Test handling of various separator characters."""
        test_cases = [
            # Dots
            ("Movie.Title.2024.1080p.mkv", "Movie Title"),
            # Underscores
            ("Movie_Title_2024_1080p.mkv", "Movie Title"),
            # Hyphens
            ("Movie-Title-2024-1080p.mkv", "Movie Title"),
            # Mixed separators
            ("Movie.Title_2024-1080p.mkv", "Movie Title"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected