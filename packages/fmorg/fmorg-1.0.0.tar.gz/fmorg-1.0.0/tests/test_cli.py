"""
Tests for the CLI module.

This module contains comprehensive tests for the CLI interface,
including argument parsing, command execution, and user interaction.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from fmorg.cli import cli, main_entry
from fmorg.display import DisplayManager


class TestCLI:
    """Test cases for CLI functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def create_test_files(self, filenames):
        """Create test files with given filenames."""
        files = []
        for filename in filenames:
            file_path = self.temp_dir / filename
            file_path.write_text(f"Content of {filename}")
            files.append(file_path)
        return files

    def test_main_command_basic(self):
        """Test basic main command execution."""
        # Create test files
        self.create_test_files([
            "Movie.Title.2023.1080p.mp4",
            "Movie.Title.2023.720p.mp4"
        ])

        # Run with dry-run to avoid actual file operations
        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0
        assert 'Dry run' in result.output or 'Found' in result.output

    def test_main_command_with_output_directory(self):
        """Test main command with custom output directory."""
        output_dir = self.temp_dir / "output"
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--output', str(output_dir),
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0

    def test_main_command_recursive(self):
        """Test main command with recursive scanning."""
        # Create subdirectory with files
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "Movie.Title.2023.1080p.mp4").write_text("content")

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--recursive',
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0

    def test_main_command_min_files_threshold(self):
        """Test main command with minimum files threshold."""
        self.create_test_files([
            "Movie.Title.2023.1080p.mp4",
            "Movie.Title.2023.720p.mp4",
            "Single.Movie.2023.1080p.mkv"
        ])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--min', '2',
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0

    def test_main_command_verbose(self):
        """Test main command with verbose output."""
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--verbose',
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0

    def test_main_command_quiet(self):
        """Test main command with quiet output."""
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--quiet',
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0
        # Quiet mode should have minimal output
        assert len(result.output.strip()) < 200

    def test_main_command_no_color(self):
        """Test main command with no color output."""
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--no-color',
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0

    def test_main_command_nonexistent_directory(self):
        """Test main command with nonexistent directory."""
        nonexistent_dir = self.temp_dir / "nonexistent"

        result = self.runner.invoke(cli, [str(nonexistent_dir)])

        assert result.exit_code != 0
        assert 'does not exist' in result.output.lower()

    def test_main_command_file_instead_of_directory(self):
        """Test main command with file instead of directory."""
        file_path = self.temp_dir / "file.txt"
        file_path.write_text("content")

        result = self.runner.invoke(cli, [str(file_path)])

        assert result.exit_code != 0
        assert 'is a file' in result.output.lower()

    def test_main_command_invalid_min_threshold(self):
        """Test main command with invalid minimum threshold."""
        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--min', '0'
        ])

        assert result.exit_code != 0
        assert 'at least 1' in result.output.lower()

    def test_main_command_empty_directory(self):
        """Test main command with empty directory."""
        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0
        assert 'no files found' in result.output.lower()

    @patch('fmorg.cli.display.DisplayManager.prompt_confirmation')
    def test_main_command_user_confirmation(self, mock_prompt):
        """Test main command with user confirmation."""
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        # Mock user to decline
        mock_prompt.return_value = False

        result = self.runner.invoke(cli, [str(self.temp_dir)])

        assert result.exit_code == 0
        assert 'cancelled' in result.output.lower()
        mock_prompt.assert_called_once()

    def test_main_command_keyboard_interrupt(self):
        """Test main command with keyboard interrupt."""
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        with patch('fmorg.cli.display.DisplayManager.prompt_confirmation', side_effect=KeyboardInterrupt()):
            result = self.runner.invoke(cli, [str(self.temp_dir)])

            assert result.exit_code == 1

    def test_cli_help_output(self):
        """Test CLI help output."""
        result = self.runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'DIRECTORY' in result.output
        assert '--min' in result.output
        assert '--recursive' in result.output

    def test_main_entry_no_arguments(self):
        """Test main_entry function with no arguments."""
        with patch('sys.argv', ['fmorg']):
            with patch('fmorg.cli.cli') as mock_cli:
                main_entry()
                mock_cli.assert_called_once()

    def test_cli_with_no_arguments_uses_current_directory(self):
        """Test CLI with no arguments uses current directory."""
        # Change to a temporary directory for the test
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            self.create_test_files(["Movie.Title.2023.1080p.mp4"])

            result = self.runner.invoke(cli, ['--dry-run', '--yes'])

            assert result.exit_code == 0
            assert 'Found' in result.output or 'files' in result.output
        finally:
            os.chdir(original_cwd)

    def test_main_entry_with_directory_argument(self):
        """Test main_entry function with directory argument."""
        import sys
        original_argv = sys.argv.copy()
        try:
            with patch('sys.argv', ['fmorg', '/some/path']):
                with patch('fmorg.cli.cli') as mock_cli:
                    main_entry()
                    # Should call cli()
                    mock_cli.assert_called_once()
                    # Check that sys.argv was not modified
                    assert sys.argv == ['fmorg', '/some/path']
        finally:
            sys.argv = original_argv

    def test_main_entry_keyboard_interrupt(self):
        """Test main_entry function with keyboard interrupt."""
        with patch('sys.argv', ['fmorg']):
            with patch('fmorg.cli.cli', side_effect=KeyboardInterrupt()):
                with pytest.raises(SystemExit):
                    main_entry()

    def test_main_entry_unexpected_error(self):
        """Test main_entry function with unexpected error."""
        with patch('sys.argv', ['fmorg']):
            with patch('fmorg.cli.cli', side_effect=Exception("Unexpected error")):
                with pytest.raises(SystemExit):
                    main_entry()

    def test_main_command_create_output_directory(self):
        """Test main command creates output directory if needed."""
        output_dir = self.temp_dir / "new_output_dir"
        self.create_test_files(["Movie.Title.2023.1080p.mp4"])

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--output', str(output_dir),
            '--dry-run',
            '--yes'
        ])

        assert result.exit_code == 0
        assert output_dir.exists()

    def test_main_command_complex_real_world_scenario(self):
        """Test main command with complex real-world file scenario."""
        # Create files in subdirectories
        for subdir in ["season1", "season2", "movies"]:
            (self.temp_dir / subdir).mkdir()

        test_files = [
            "Divine.Love.Deep.Blue.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "Divine.Love.Deep.Blue.S01E02.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "season1/Divine.Love.Deep.Blue.S01E03.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "season2/Divine.Love.Deep.Blue.S02E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "movies/The.Matrix.1999.1080p.BluRay.x264.AC3-XYZ.mp4",
            "movies/Inception.2010.720p.WEB-DL.x264.AAC-ABC.mkv"
        ]

        self.create_test_files(test_files)

        result = self.runner.invoke(cli, [
            str(self.temp_dir),
            '--recursive',
            '--min', '2',
            '--dry-run',
            '--verbose',
            '--yes'
        ])

        assert result.exit_code == 0
        assert 'Divine Love Deep Blue' in result.output
        assert '6 files found' in result.output or 'Found' in result.output

    def test_display_manager_color_detection(self):
        """Test that DisplayManager properly handles color settings."""
        # Test with colors enabled
        display = DisplayManager(use_colors=True)
        colored_text = display.colorize("test", "green")
        assert colored_text != "test"  # Should have color codes

        # Test with colors disabled
        display = DisplayManager(use_colors=False)
        colored_text = display.colorize("test", "green")
        assert colored_text == "test"  # Should be plain text

    def test_error_handling_in_file_operations(self):
        """Test error handling during file operations."""
        # Test with a nonexistent directory
        nonexistent_dir = "/tmp/nonexistent_directory_12345"

        result = self.runner.invoke(cli, [
            nonexistent_dir,
            '--dry-run',
            '--yes'
        ])

        # Should handle the error gracefully
        assert result.exit_code != 0

    def test_version_option(self):
        """Test version option."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output