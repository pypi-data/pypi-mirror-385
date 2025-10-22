"""
File organizer module for safe file operations and directory management.

This module contains logic for organizing files into folders based on
analysis results, with safe operations and proper error handling.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging
import re
from difflib import SequenceMatcher

from .analyzer import FilenameAnalyzer


class FileOrganizer:
    """Organizes files into folders based on analysis results."""

    def __init__(self, base_directory: Path, min_files_per_folder: int = 1):
        """
        Initialize the file organizer.

        Args:
            base_directory: Base directory where files should be organized
            min_files_per_folder: Minimum number of files required to create a folder
        """
        self.base_directory = Path(base_directory).resolve()
        self.min_files_per_folder = min_files_per_folder
        self.analyzer = FilenameAnalyzer()
        self.logger = logging.getLogger(__name__)

        # Track operations
        self.planned_moves: List[Tuple[Path, Path]] = []
        self.failed_operations: List[Tuple[Path, str]] = []
        self.successful_operations: List[Tuple[Path, Path]] = []
        self.skipped_files: List[Tuple[Path, str]] = []

        # Track folder creation status
        self.existing_folders_used: set[Path] = set()
        self.new_folders_to_create: set[Path] = set()

        # Track skipped files and their reasons
        self.skipped_files: List[Tuple[Path, str]] = []

    def scan_directory(self, directory: Path, recursive: bool = False) -> List[Path]:
        """
        Scan a directory for files to organize.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of file paths found
        """
        files = []
        directory = Path(directory).resolve()

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        if recursive:
            for item in directory.rglob('*'):
                if item.is_file():
                    files.append(item)
        else:
            for item in directory.iterdir():
                if item.is_file():
                    files.append(item)

        return sorted(files)

    def analyze_files(self, files: List[Path]) -> Dict[str, List[Tuple[Path, str]]]:
        """
        Analyze a list of files and group them by title.

        Args:
            files: List of file paths to analyze

        Returns:
            Dictionary mapping titles to list of (file_path, original_name) tuples
        """
        grouped_files = defaultdict(list)

        for file_path in files:
            try:
                title, category, original_name = self.analyzer.analyze_file(file_path)

                # Silently skip hidden files (returned as None, None, None)
                if title is None:
                    continue

                # Skip files with empty titles
                if not title.strip():
                    self.logger.warning(f"Could not extract title from: {file_path.name}")
                    self.skipped_files.append((file_path, "Could not extract title"))
                    self.failed_operations.append((file_path, "Could not extract title"))
                    continue

                grouped_files[title].append((file_path, original_name))

            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                self.skipped_files.append((file_path, f"Analysis error: {str(e)}"))
                self.failed_operations.append((file_path, f"Analysis error: {str(e)}"))

        return dict(grouped_files)

    def find_similar_existing_folder(self, desired_folder_name: str) -> Optional[Path]:
        """
        Find an existing folder with a similar name to avoid creating duplicates.

        This method looks for existing folders that contain the desired folder name
        or have very similar names, accounting for variations like additional
        information in parentheses, different capitalization, etc.

        Args:
            desired_folder_name: The ideal folder name we want to use

        Returns:
            Path to the existing similar folder if found, None otherwise
        """
        if not self.base_directory.exists():
            return None

        # Normalize the desired folder name for comparison
        normalized_desired = self._normalize_folder_name_for_matching(desired_folder_name)

        # Get all existing directories in the base directory
        existing_dirs = [d for d in self.base_directory.iterdir() if d.is_dir()]

        best_match = None
        best_score = 0.0

        for existing_dir in existing_dirs:
            existing_name = existing_dir.name
            normalized_existing = self._normalize_folder_name_for_matching(existing_name)

            # Calculate similarity score
            similarity = self._calculate_folder_similarity(normalized_desired, normalized_existing)

            # Check for exact match (high priority)
            if similarity >= 0.9:
                return existing_dir

            # Check if one name contains the other (medium priority)
            if (normalized_desired.lower() in normalized_existing.lower() or
                normalized_existing.lower() in normalized_desired.lower()):
                if similarity > best_score:
                    best_score = similarity
                    best_match = existing_dir

        # Return the best match if it's reasonably similar
        if best_score >= 0.6:  # 60% similarity threshold
            self.logger.info(f"Found similar existing folder: '{best_match.name}' for desired '{desired_folder_name}' (score: {best_score:.2f})")
            return best_match

        return None

    def _normalize_folder_name_for_matching(self, folder_name: str) -> str:
        """
        Normalize a folder name for fuzzy matching.

        This removes common patterns like years, parentheses content,
        special characters, and normalizes case for better matching.

        Args:
            folder_name: The folder name to normalize

        Returns:
            Normalized folder name for comparison
        """
        # Remove content in parentheses (like years, additional info)
        normalized = re.sub(r'\([^)]*\)', '', folder_name)

        # Remove common separators and replace with spaces
        normalized = re.sub(r'[._\-+]', ' ', normalized)

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Remove years and numbers
        normalized = re.sub(r'\b\d{4}\b', '', normalized)  # 4-digit years
        normalized = re.sub(r'\b\d{1,2}\b', '', normalized)  # other numbers

        # Remove special characters
        normalized = re.sub(r'[^\w\s]', '', normalized)

        # Normalize case and strip again
        normalized = normalized.lower().strip()

        return normalized

    def _calculate_folder_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two normalized folder names.

        Args:
            name1: First normalized folder name
            name2: Second normalized folder name

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use SequenceMatcher for basic string similarity
        base_similarity = SequenceMatcher(None, name1, name2).ratio()

        # Boost similarity if one contains the other
        if name1 in name2 or name2 in name1:
            base_similarity += 0.2

        # Word-based similarity
        words1 = set(name1.split())
        words2 = set(name2.split())

        if words1 and words2:
            word_similarity = len(words1 & words2) / len(words1 | words2)
            base_similarity = max(base_similarity, word_similarity)

        return min(base_similarity, 1.0)

    def create_organization_plan(self, grouped_files: Dict[str, List[Tuple[Path, str]]]) -> List[Tuple[Path, Path]]:
        """
        Create a plan for organizing files.

        Args:
            grouped_files: Files grouped by title from analyze_files()

        Returns:
            List of (source_path, destination_path) tuples
        """
        plan = []

        for title, files in grouped_files.items():
            # Skip if not enough files for this title
            if len(files) < self.min_files_per_folder:
                reason = f"Below minimum threshold ({len(files)} files, minimum: {self.min_files_per_folder})"
                self.logger.info(f"Skipping '{title}': {reason}")
                # Add these files to skipped files list
                for file_path, _ in files:
                    self.skipped_files.append((file_path, reason))
                continue

            # Create safe folder name
            desired_folder_name = self._create_safe_folder_name(title)

            # Try to find similar existing folder first
            existing_folder = self.find_similar_existing_folder(desired_folder_name)

            if existing_folder:
                target_folder = existing_folder
                self.existing_folders_used.add(target_folder)
                self.logger.debug(f"Using existing folder: '{existing_folder.name}' for files matching '{title}'")
            else:
                target_folder = self.base_directory / desired_folder_name
                self.new_folders_to_create.add(target_folder)

            for file_path, original_name in files:
                # Ensure we don't move files to their own location
                if file_path.parent == target_folder:
                    self.logger.debug(f"Skipping {file_path}: already in target location")
                    continue

                target_path = target_folder / original_name
                plan.append((file_path, target_path))

        self.planned_moves = plan
        return plan

    def _create_safe_folder_name(self, title: str) -> str:
        """
        Create a safe folder name from a title.

        Args:
            title: The title to convert

        Returns:
            Safe folder name
        """
        # Remove problematic characters
        safe_name = title

        # Replace problematic characters with underscores
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')

        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')

        # Ensure it's not empty
        if not safe_name:
            safe_name = "Untitled"

        # Limit length
        if len(safe_name) > 255:
            safe_name = safe_name[:255]

        return safe_name

    def execute_plan(self, plan: Optional[List[Tuple[Path, Path]]] = None, dry_run: bool = False) -> bool:
        """
        Execute the organization plan.

        Args:
            plan: Plan to execute (uses self.planned_moves if None)
            dry_run: If True, only simulate the operations

        Returns:
            True if all operations succeeded, False otherwise
        """
        if plan is None:
            plan = self.planned_moves

        if not plan:
            self.logger.info("No files to organize")
            return True

        success = True

        for source_path, target_path in plan:
            try:
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move: {source_path} -> {target_path}")
                    self.successful_operations.append((source_path, target_path))
                    continue

                # Create target directory if it doesn't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Handle file name conflicts
                final_target_path = self._resolve_conflicts(source_path, target_path)

                # Move the file
                shutil.move(str(source_path), str(final_target_path))
                self.logger.info(f"Moved: {source_path} -> {final_target_path}")
                self.successful_operations.append((source_path, final_target_path))

            except Exception as e:
                self.logger.error(f"Failed to move {source_path} to {target_path}: {e}")
                self.failed_operations.append((source_path, str(e)))
                success = False

        return success

    def _resolve_conflicts(self, source_path: Path, target_path: Path) -> Path:
        """
        Resolve file name conflicts by finding a unique name.

        Args:
            source_path: Source file path
            target_path: Target file path

        Returns:
            Unique target path
        """
        if not target_path.exists():
            return target_path

        # File exists, find a unique name
        stem = target_path.stem
        suffix = target_path.suffix
        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = target_path.parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def get_operation_summary(self) -> Dict:
        """
        Get a summary of planned and executed operations.

        Returns:
            Dictionary with operation statistics
        """
        return {
            'planned_moves': len(self.planned_moves),
            'successful_operations': len(self.successful_operations),
            'failed_operations': len(self.failed_operations),
            'total_files_found': len(self.planned_moves) + len(self.failed_operations),
            'folders_to_create': len(set(move[1].parent for move in self.planned_moves)),
            'failed_files': self.failed_operations,
            'successful_moves': self.successful_operations
        }

    def validate_operations(self) -> List[Tuple[Path, str]]:
        """
        Validate planned operations before execution.

        Returns:
            List of (path, error_message) for invalid operations
        """
        errors = []

        for source_path, target_path in self.planned_moves:
            # Check source exists
            if not source_path.exists():
                errors.append((source_path, "Source file does not exist"))
                continue

            # Check we have permission to read source
            if not os.access(source_path, os.R_OK):
                errors.append((source_path, "No read permission for source file"))
                continue

            # Check we have permission to write to target directory
            target_dir = target_path.parent
            if target_dir.exists() and not os.access(target_dir, os.W_OK):
                errors.append((target_path, f"No write permission for target directory: {target_dir}"))

            # Check if source and target are the same file
            try:
                if source_path.resolve() == target_path.resolve():
                    errors.append((source_path, "Source and target are the same file"))
            except Exception:
                # If we can't resolve paths, skip this check
                pass

        return errors

    def reset_operations(self):
        """Reset operation tracking."""
        self.planned_moves = []
        self.failed_operations = []
        self.successful_operations = []
        self.existing_folders_used.clear()
        self.new_folders_to_create.clear()
        self.skipped_files.clear()