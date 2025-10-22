"""
Tests for the file organizer module.

This module contains comprehensive tests for the FileOrganizer class,
including file operations, directory management, and error handling.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from fmorg.organizer import FileOrganizer
from fmorg.analyzer import FilenameAnalyzer


class TestFileOrganizer:
    """Test cases for FileOrganizer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "base"
        self.base_dir.mkdir()
        self.organizer = FileOrganizer(base_directory=self.base_dir, min_files_per_folder=1)

    def teardown_method(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def create_test_files(self, filenames):
        """Create test files with given filenames."""
        files = []
        for filename in filenames:
            file_path = self.temp_dir / filename
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"Content of {filename}")
            files.append(file_path)
        return files

    def test_init_with_valid_directory(self):
        """Test initialization with valid directory."""
        assert self.organizer.base_directory == self.base_dir.resolve()
        assert self.organizer.min_files_per_folder == 1

    def test_init_with_nonexistent_directory(self):
        """Test initialization with nonexistent directory."""
        nonexistent_dir = self.temp_dir / "nonexistent"
        organizer = FileOrganizer(base_directory=nonexistent_dir)
        assert organizer.base_directory == nonexistent_dir.resolve()

    def test_init_with_min_files_threshold(self):
        """Test initialization with custom min files threshold."""
        organizer = FileOrganizer(base_directory=self.base_dir, min_files_per_folder=3)
        assert organizer.min_files_per_folder == 3

    def test_scan_directory_existing(self):
        """Test scanning an existing directory."""
        # Create test files
        test_files = self.create_test_files(["file1.txt", "file2.txt", "subdir/file3.txt"])

        # Scan non-recursive
        files = self.organizer.scan_directory(self.temp_dir, recursive=False)
        assert len(files) == 2
        assert test_files[0] in files
        assert test_files[1] in files

        # Scan recursive
        files = self.organizer.scan_directory(self.temp_dir, recursive=True)
        assert len(files) == 3
        assert all(f in files for f in test_files)

    def test_scan_directory_nonexistent(self):
        """Test scanning a nonexistent directory."""
        nonexistent_dir = self.temp_dir / "nonexistent"
        with pytest.raises(FileNotFoundError):
            self.organizer.scan_directory(nonexistent_dir)

    def test_scan_directory_not_directory(self):
        """Test scanning a path that is not a directory."""
        file_path = self.temp_dir / "file.txt"
        file_path.write_text("content")
        with pytest.raises(ValueError):
            self.organizer.scan_directory(file_path)

    def test_analyze_files_success(self):
        """Test successful file analysis."""
        test_files = self.create_test_files([
            "Movie.Title.2023.1080p.mp4",
            "Movie.Title.2023.720p.mp4",
            "Another.Movie.2023.1080p.mkv"
        ])

        grouped = self.organizer.analyze_files(test_files)

        assert len(grouped) == 2
        assert "Movie Title" in grouped
        assert "Another Movie" in grouped
        assert len(grouped["Movie Title"]) == 2
        assert len(grouped["Another Movie"]) == 1

    def test_analyze_files_with_empty_titles(self):
        """Test analyzing files that result in empty titles."""
        test_files = self.create_test_files([
            "1080p.WEB-DL.x264.AAC.mp4",  # No meaningful content
            "Another.1080p.mp4"  # Has some content
        ])

        grouped = self.organizer.analyze_files(test_files)

        assert len(grouped) == 1
        assert "Another" in grouped

        # Check that failed operations were recorded
        assert len(self.organizer.failed_operations) == 1

    def test_analyze_files_empty_list(self):
        """Test analyzing empty file list."""
        grouped = self.organizer.analyze_files([])
        assert grouped == {}

    def test_create_organization_plan_basic(self):
        """Test basic organization plan creation."""
        test_files = self.create_test_files([
            "Movie.Title.2023.1080p.mp4",
            "Movie.Title.2023.720p.mp4"
        ])

        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        assert len(plan) == 2
        for source, target in plan:
            assert source.exists()
            assert target.parent.name == "Movie Title"
            assert target.name == source.name

    def test_create_organization_plan_min_files_threshold(self):
        """Test organization plan with min files threshold."""
        organizer = FileOrganizer(base_directory=self.base_dir, min_files_per_folder=2)
        test_files = self.create_test_files([
            "Movie.Title.2023.1080p.mp4",
            "Movie.Title.2023.720p.WEB-DL.mkv"
        ])

        grouped = organizer.analyze_files(test_files)
        plan = organizer.create_organization_plan(grouped)

        # Both files should be in plan (they have the same title and meet min_files threshold)
        assert len(plan) == 2
        assert plan[0][1].parent.name == "Movie Title"

    def test_create_organization_plan_same_location(self):
        """Test plan creation when files are already in target location."""
        target_dir = self.base_dir / "Movie Title"
        target_dir.mkdir()

        test_file = target_dir / "Movie.Title.2023.1080p.mp4"
        test_file.write_text("content")

        grouped = {"Movie Title": [(test_file, test_file.name)]}
        plan = self.organizer.create_organization_plan(grouped)

        # File should not be moved (already in target location)
        assert len(plan) == 0

    def test_create_safe_folder_name_basic(self):
        """Test safe folder name creation."""
        safe_name = self.organizer._create_safe_folder_name("Movie Title")
        assert safe_name == "Movie Title"

    def test_create_safe_folder_name_with_special_chars(self):
        """Test safe folder name creation with special characters."""
        safe_name = self.organizer._create_safe_folder_name('Movie:Title/<>|?*')
        assert safe_name == "Movie_Title______"

    def test_create_safe_folder_name_empty(self):
        """Test safe folder name creation from empty string."""
        safe_name = self.organizer._create_safe_folder_name("")
        assert safe_name == "Untitled"

    def test_create_safe_folder_name_too_long(self):
        """Test safe folder name creation from very long string."""
        long_title = "A" * 300
        safe_name = self.organizer._create_safe_folder_name(long_title)
        assert len(safe_name) <= 255

    def test_resolve_conflicts_no_conflict(self):
        """Test conflict resolution when no conflict exists."""
        source = self.temp_dir / "source.txt"
        target = self.temp_dir / "target.txt"

        resolved = self.organizer._resolve_conflicts(source, target)
        assert resolved == target

    def test_resolve_conflicts_with_conflict(self):
        """Test conflict resolution when conflict exists."""
        source = self.temp_dir / "source.txt"
        target = self.temp_dir / "target.txt"

        # Create target file
        target.write_text("existing content")

        resolved = self.organizer._resolve_conflicts(source, target)
        assert resolved == self.temp_dir / "target_1.txt"

        # Test multiple conflicts
        target_1 = self.temp_dir / "target_1.txt"
        target_1.write_text("existing content")

        resolved = self.organizer._resolve_conflicts(source, target)
        assert resolved == self.temp_dir / "target_2.txt"

    def test_execute_plan_dry_run(self):
        """Test plan execution in dry run mode."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        success = self.organizer.execute_plan(plan, dry_run=True)

        assert success is True
        assert len(self.organizer.successful_operations) == 1
        assert len(self.organizer.failed_operations) == 0
        # Files should not be actually moved
        assert test_files[0].exists()

    def test_execute_plan_actual_execution(self):
        """Test actual plan execution."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        success = self.organizer.execute_plan(plan, dry_run=False)

        assert success is True
        assert len(self.organizer.successful_operations) == 1
        assert len(self.organizer.failed_operations) == 0

        # File should be moved
        assert not test_files[0].exists()
        target_path = self.base_dir / "Movie Title" / test_files[0].name
        assert target_path.exists()

    def test_execute_plan_empty_plan(self):
        """Test executing an empty plan."""
        success = self.organizer.execute_plan([])
        assert success is True

    def test_execute_plan_with_directory_creation(self):
        """Test plan execution that requires directory creation."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        # Target directory should not exist initially
        target_dir = plan[0][1].parent
        assert not target_dir.exists()

        success = self.organizer.execute_plan(plan, dry_run=False)

        assert success is True
        assert target_dir.exists()
        assert target_dir.is_dir()

    def test_execute_plan_with_permission_error(self):
        """Test plan execution with permission errors."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        # Mock shutil.move to raise permission error
        with patch('shutil.move', side_effect=PermissionError("Permission denied")):
            success = self.organizer.execute_plan(plan, dry_run=False)

        assert success is False
        assert len(self.organizer.successful_operations) == 0
        assert len(self.organizer.failed_operations) == 1

    def test_get_operation_summary(self):
        """Test operation summary generation."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        summary = self.organizer.get_operation_summary()

        assert 'planned_moves' in summary
        assert 'successful_operations' in summary
        assert 'failed_operations' in summary
        assert 'total_files_found' in summary
        assert 'folders_to_create' in summary
        assert summary['planned_moves'] == 1

    def test_validate_operations_success(self):
        """Test operation validation with valid operations."""
        test_files = self.create_test_files(["Movie.Title.2023.1080p.mp4"])
        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        errors = self.organizer.validate_operations()
        assert len(errors) == 0

    def test_validate_operations_nonexistent_source(self):
        """Test operation validation with nonexistent source file."""
        source = self.temp_dir / "nonexistent.txt"
        target = self.base_dir / "target.txt"
        plan = [(source, target)]

        self.organizer.planned_moves = plan
        errors = self.organizer.validate_operations()

        assert len(errors) == 1
        assert "does not exist" in errors[0][1]

    def test_validate_operations_same_source_target(self):
        """Test operation validation with same source and target."""
        source = self.temp_dir / "test.txt"
        source.write_text("content")
        plan = [(source, source)]

        self.organizer.planned_moves = plan
        errors = self.organizer.validate_operations()

        assert len(errors) == 1
        assert "same file" in errors[0][1]

    def test_reset_operations(self):
        """Test resetting operation tracking."""
        # Add some operations
        self.organizer.planned_moves = [(Path("a"), Path("b"))]
        self.organizer.successful_operations = [(Path("a"), Path("b"))]
        self.organizer.failed_operations = [(Path("a"), "error")]

        # Reset
        self.organizer.reset_operations()

        assert len(self.organizer.planned_moves) == 0
        assert len(self.organizer.successful_operations) == 0
        assert len(self.organizer.failed_operations) == 0

    def test_real_world_file_organization(self):
        """Test with real-world file names."""
        test_files = self.create_test_files([
            "Divine.Love.Deep.Blue.S01E01.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "Divine.Love.Deep.Blue.S01E02.2025.2160p.WEB-DL.H265.HDR.AAC-ColorTV.mkv",
            "The.Matrix.1999.1080p.BluRay.x264.AC3-XYZ.mp4",
            "Breaking.Bad.S01E01.2008.HDTV.x264-LOL.mkv",
            "Breaking.Bad.S01E02.2008.HDTV.x264-LOL.mkv",
            "Breaking.Bad.S01E03.2008.HDTV.x264-LOL.mkv"
        ])

        grouped = self.organizer.analyze_files(test_files)
        plan = self.organizer.create_organization_plan(grouped)

        # Should have 3 groups: Divine Love Deep Blue, The Matrix, Breaking Bad
        assert len(grouped) == 3
        assert "Divine Love Deep Blue" in grouped
        assert "The Matrix" in grouped
        assert "Breaking Bad" in grouped

        # Plan should include all files
        assert len(plan) == 6

        # Execute plan
        success = self.organizer.execute_plan(plan, dry_run=False)
        assert success is True

        # Verify files are in correct folders
        for title in ["Divine Love Deep Blue", "The Matrix", "Breaking Bad"]:
            folder = self.base_dir / title
            assert folder.exists()
            assert folder.is_dir()
            assert len(list(folder.iterdir())) > 0

    def test_hidden_files_are_skipped(self):
        """Test that hidden files are properly skipped during organization."""
        # Create a mix of regular and hidden files
        test_files = self.create_test_files([
            "Movie.Title.2023.1080p.mp4",  # Regular file
            ".DS_Store",  # macOS hidden file
            ".gitignore",  # Git hidden file
            ".hidden_folder/.hidden_movie.mkv",  # Hidden file in hidden folder
            "Another.Movie.2022.720p.mp4",  # Another regular file
            ".temporary.txt",  # Temporary hidden file
        ])

        # Analyze files
        grouped = self.organizer.analyze_files(test_files)

        # Should only have 2 groups (Movie Title and Another Movie)
        assert len(grouped) == 2
        assert "Movie Title" in grouped
        assert "Another Movie" in grouped

        # Hidden files are now silently ignored - no failed operations or skipped files
        assert len(self.organizer.failed_operations) == 0
        assert len(self.organizer.skipped_files) == 0  # Hidden files are not recorded as skipped

        # Create organization plan - should only include regular files
        plan = self.organizer.create_organization_plan(grouped)
        assert len(plan) == 2  # 2 regular files should be in plan

        # Verify all plan items are for regular files
        for source, target in plan:
            assert not source.name.startswith('.')

        # Execute plan
        success = self.organizer.execute_plan(plan, dry_run=False)
        assert success is True

        # Verify only regular files were moved
        for title in ["Movie Title", "Another Movie"]:
            folder = self.base_dir / title
            assert folder.exists()
            assert folder.is_dir()
            files_in_folder = list(folder.iterdir())
            assert len(files_in_folder) == 1
            assert not files_in_folder[0].name.startswith('.')

        # Verify hidden files are still in their original locations
        for file_path in test_files:
            if file_path.name.startswith('.'):
                assert file_path.exists()  # Hidden files should not be moved