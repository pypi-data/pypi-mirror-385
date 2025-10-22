"""
Tests for international filename extraction.

This module tests the advanced title extraction system with complex
international filenames that mix Latin content with Chinese characters,
technical metadata, and various naming conventions.
"""

import pytest
from fmorg.analyzer import FilenameAnalyzer


class TestInternationalFilenames:
    """Test cases for international filename extraction."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.analyzer = FilenameAnalyzer()

    @pytest.mark.parametrize("filename,expected", [
        # Complex multi-word titles with TV episodes
        ("[HRS].S01E001.Urban Miracle Doctor.都市古仙医.[1080p.vFTKEPR.HL].mkv",
         "Urban Miracle Doctor"),
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

        # International filenames with English translations
        ("[Blue Rain] 恶魔法则 - Law of Devil (S01) - EP01 [4K RMST] [E-AC-3,AAC][Anon].mkv",
         "Law of Devil"),
        ("[JRx7] 斩神之凡尘神域 Slay the Gods - 01 [4K HEVC][HBR][HQ][10bit][E-AC-3.AAC].mkv",
         "Slay the Gods"),
        ("[JRx7] 宗门里除了我都是卧底 Spy x Sect - 01 [4K HEVC][RMST][10Bit][E-AC-3.AAC].mkv",
         "Spy x Sect"),
        ("[JRx7] 吞天记 Swallowing the Heavens - 01 [4K HEVC][HBR][RMST][10bit][E-AC-3.AAC].mkv",
         "Swallowing the Heavens"),

        # Bracket-encoded group tags
        ("[Hall_of_C] Xue Ying Ling Zhu S3 - Episode_01_(53).mkv",
         "Xue Ying Ling Zhu"),
        ("[FSP DN] 剑来 Sword of Coming - 01 [4K HEVC][HBR][HQ][10Bit][E-AC-3.AAC].v2.mkv",
         "Sword of Coming"),
        ("Tales Of Dark River - 01 [4K HEVC][HQ.10Bit][JRx7].mkv",
         "Tales of Dark River"),

        # Complex mixed format titles
        ("Zhen_Dao_Ge_13_Special.mkv",
         "Zhen Dao Ge"),
        ("Spare Me, Great Lord! - 01 [4K AI] [4217DA69].mkv",
         "Spare Me, Great Lord"),
        ("[JRx7] Baozou Xia Ri - 01 [4K AVC].mp4",
         "Baozou Xia Ri"),
        ("Tales.of.Demons.and.Gods.(Yao.Shen.Ji).4KAI.10Bit.S01E01.(001).mkv",
         "Tales of Demons and Gods"),
    ])
    def test_extract_title_international_filenames(self, filename, expected):
        """Test title extraction from international filenames."""
        result = self.analyzer.extract_title(filename)
        assert result == expected, f"Expected '{expected}', got '{result}' for '{filename}'"

    def test_mixed_chinese_english_punctuation(self):
        """Test handling of mixed Chinese/English with various punctuation."""
        test_cases = [
            # Hyphen separators
            ("Legend-of-Dragons.S01E01.2024.1080p.mkv", "Legend of Dragons"),
            ("Sword-and-Magic.E01.2024.720p.mp4", "Sword and Magic"),

            # Underscore separators
            ("Cultivation_World_S01E01.2024.1080p.mkv", "Cultivation World"),
            ("Martial_Arts_Master_E01.2024.720p.mp4", "Martial Arts Master"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_bracket_group_tags_recognition(self):
        """Test that bracket group tags are properly identified and ignored."""
        test_cases = [
            # Various group tag formats
            ("[Team] Show.Name.S01E01.2024.1080p.mkv", "Show Name"),
            ("[Group] Title.S01E01.2024.720p.mp4", "Title"),
            ("[Encoding_Group] Series.Name.S01E01.2024.4K.mkv", "Series Name"),

            # Multiple brackets
            ("[Group1][Group2] Title.S01E01.2024.1080p.mkv", "Title"),
            ("[HDR] [4K] Title.2024.2160p.mkv", "Title"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_chinese_character_filtering(self):
        """Test that Chinese characters are properly filtered out."""
        test_cases = [
            # Chinese characters before English title
            ("仙逆 Battle Through the Heavens.S01E01.2024.1080p.mkv",
             "Battle Through the Heavens"),
            ("凡人修仙座 A Record of Mortals Journey to Immortality.S01E01.2024.1080p.mkv",
             "A Record of Mortals Journey to Immortality"),

            # Chinese characters after English title
            ("Cultivation Chat 修仙聊天室.S01E01.2024.1080p.mkv", "Cultivation Chat"),
            ("Martial Arts World 武侠世界.S01E01.2024.720p.mp4", "Martial Arts World"),

            # Chinese characters mixed throughout
            ("仙魔.道 Chinese.Demons.Path.S01E01.2024.1080p.mkv", "Chinese Demons Path"),
            ("神.魔.界 God.Demon.Realm.S01E01.2024.4K.mkv", "God Demon Realm"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_technical_metadata_patterns(self):
        """Test recognition of various technical metadata patterns."""
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

    def test_episode_number_formats(self):
        """Test various episode number formats."""
        test_cases = [
            # Standard formats
            ("Show.Name.S01E01.2024.1080p.mkv", "Show Name"),
            ("Show.Name.S1E1.2024.720p.mp4", "Show Name"),
            ("Show.Name.S01.E01.2024.1080p.mkv", "Show Name"),

            # Episode formats
            ("Show.Name.Episode.01.2024.1080p.mkv", "Show Name"),
            ("Show.Name.Ep01.2024.720p.mp4", "Show Name"),
            ("Show.Name.Episode.1.2024.480p.mp4", "Show Name"),

            # Special episodes
            ("Show.Name.S00E01.2024.1080p.mkv", "Show Name"),
            ("Show.Name.Special.01.2024.1080p.mkv", "Show Name"),
            ("Show.Name.OVA.01.2024.720p.mp4", "Show Name"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_year_filtering(self):
        """Test that years are properly filtered from titles."""
        test_cases = [
            # Years in different positions
            ("Title.2024.1080p.mkv", "Title"),
            ("Title.1999.1080p.mkv", "Title"),
            # 2000s is not recognized as a year
            ("Title.2000s.1080p.mkv", "Title 2000s"),

            # Multiple years
            ("Title.1999-2000.1080p.mkv", "Title"),
            ("Title.2023.2024.1080p.mkv", "Title"),

            # Years within title
            ("History.2024.A.Deeper.Look.1080p.mkv", "History A Deeper Look"),
            ("Future.2050.The.Next.Generation.4K.mkv", "Future the Next Generation"),
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected

    def test_edge_cases_and_boundaries(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            # Very short titles
            ("Go.2024.1080p.mkv", "Go"),
            ("It.2024.1080p.mkv", "It"),
            ("I.2024.1080p.mkv", "I"),

            # Very long titles
            ("The.Very.Long.And.Complicated.Title.That.Goes.On.And.On.And.On.S01E01.2024.1080p.mkv",
             "The Very Long and Complicated Title That Goes on and on and on"),

            # Single character with technical content
            ("A.2024.1080p.mkv", "A"),
            ("I.2024.1080p.mkv", "I"),

            # Numbers in titles
            ("1984.1984.1080p.mkv", ""),  # Both are years
            ("300.300.1080p.mkv", "300"),   # Not recognized as year
            ("24.24.1080p.mkv", "24"),     # Not recognized as year
        ]

        for filename, expected in test_cases:
            result = self.analyzer.extract_title(filename)
            assert result == expected
