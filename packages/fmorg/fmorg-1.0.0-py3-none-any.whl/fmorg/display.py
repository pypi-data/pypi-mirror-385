"""
Display module for colored terminal output and tabulated data.

This module provides utilities for displaying information in a user-friendly
format with colors and proper formatting for both bash and zsh.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

try:
    from colorama import init, Fore, Back, Style
    # Initialize colorama (autoreset resets colors after each print)
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback if colorama is not available
    COLORAMA_AVAILABLE = False
    class Fore:
        LIGHTGREEN_EX = GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = RESET = ''
    class Back:
        RESET = ''
    class Style:
        RESET_ALL = BRIGHT = DIM = NORMAL = ''


class DisplayManager:
    """Manages colored terminal output and tabulated display."""

    def __init__(self, use_colors: bool = True):
        """
        Initialize the display manager.

        Args:
            use_colors: Whether to use colored output
        """
        self.use_colors = use_colors and COLORAMA_AVAILABLE
        self.term_width = self._get_terminal_width()

    def _get_terminal_width(self) -> int:
        """Get the terminal width for proper formatting."""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except:
            return 80  # Default fallback

    def colorize(self, text: str, color: str, style: str = '') -> str:
        """
        Apply color to text if colors are enabled.

        Args:
            text: Text to colorize
            color: Color name (e.g., 'green', 'red', 'yellow')
            style: Style (e.g., 'bright', 'dim')

        Returns:
            Colorized text or original text if colors disabled
        """
        if not self.use_colors:
            return text

        # Map color names to colorama constants
        color_map = {
            'green': Fore.LIGHTGREEN_EX,
            'lightgreen': Fore.LIGHTGREEN_EX,
            'red': Fore.RED,
            'yellow': Fore.YELLOW,
            'orange': Fore.YELLOW,  # Colorama doesn't have orange, use yellow
            'cyan': Fore.CYAN,
            'magenta': Fore.MAGENTA,
            'white': Fore.WHITE,
            'reset': Fore.RESET
        }

        # Map style names to colorama constants
        style_map = {
            'bright': Style.BRIGHT,
            'dim': Style.DIM,
            'normal': Style.NORMAL,
            'reset': Style.RESET_ALL
        }

        # Apply style and color
        result = text
        if style in style_map:
            result = style_map[style] + result
        if color in color_map:
            result = color_map[color] + result

        return result

    def print_header(self, text: str, color: str = 'cyan'):
        """
        Print a header with proper formatting.

        Args:
            text: Header text
            color: Color for the header
        """
        separator = '=' * min(len(text), self.term_width - 4)
        colored_text = self.colorize(text, color, 'bright')
        colored_separator = self.colorize(separator, color)

        print()
        print(colored_separator)
        print(colored_text)
        print(colored_separator)
        print()

    def print_section(self, title: str, color: str = 'magenta'):
        """
        Print a section title.

        Args:
            title: Section title
            color: Color for the section
        """
        colored_title = self.colorize(f"--- {title} ---", color)
        print(colored_title)

    def display_file_analysis(self, grouped_files: Dict[str, List[Tuple[Path, str]]]):
        """
        Display file analysis results in a tabulated format.

        Args:
            grouped_files: Files grouped by title
        """
        if not grouped_files:
            print(self.colorize("No files found to analyze.", 'yellow'))
            return

        print(self.colorize("File Analysis Results:", 'cyan', 'bright'))
        print()

        # Sort titles alphabetically
        sorted_titles = sorted(grouped_files.keys())

        # Calculate column widths
        max_title_width = max(len(title) for title in sorted_titles) if sorted_titles else 0
        max_title_width = max(max_title_width, len("Title"))
        file_count_width = 5  # Width for "Count" column

        # Print header
        header_format = f"{{:<{max_title_width}}}  {{:>{file_count_width}}}  {{:<{self.term_width - max_title_width - file_count_width - 10}}}"
        print(header_format.format("Title", "Count", "Files"))
        print(self.colorize("-" * self.term_width, 'cyan'))

        # Print each group
        for title in sorted_titles:
            files = grouped_files[title]
            file_count = len(files)

            # Get the first few filenames as examples
            file_examples = [f[1] for f in files[:3]]
            if len(files) > 3:
                file_examples.append(f"... and {len(files) - 3} more")
            files_str = ", ".join(file_examples)

            # Truncate if too long
            available_width = self.term_width - max_title_width - file_count_width - 10
            if len(files_str) > available_width:
                files_str = files_str[:available_width - 3] + "..."

            # Color based on file count
            title_color = 'lightgreen' if file_count >= 1 else 'yellow'
            colored_title = self.colorize(title, title_color)

            print(header_format.format(colored_title, str(file_count), files_str))

        print()

    def display_organization_plan(self, plan: List[Tuple[Path, Path]], base_directory: Path,
                                 existing_folders: set[Path] = None, new_folders: set[Path] = None):
        """
        Display the organization plan in a tabulated format.

        Args:
            plan: List of (source, target) tuples
            base_directory: Base directory for organization
            existing_folders: Set of folders that already exist
            new_folders: Set of folders that will be created
        """
        if not plan:
            print(self.colorize("No files to organize.", 'yellow'))
            return

        print(self.colorize("Organization Plan:", 'cyan', 'bright'))
        print(self.colorize(f"Base Directory: {base_directory}", 'white'))
        print()

        # Group by target folder for better organization
        folder_groups = defaultdict(list)
        folder_paths = {}
        for source, target in plan:
            folder_name = target.parent.name
            folder_path = target.parent
            folder_groups[folder_name].append((source, target))
            folder_paths[folder_name] = folder_path

        # Sort folders alphabetically
        sorted_folders = sorted(folder_groups.keys())

        for folder_name in sorted_folders:
            files = folder_groups[folder_name]
            file_count = len(files)
            folder_path = folder_paths[folder_name]

            # Determine folder color based on whether it exists or will be created
            if new_folders and folder_path in new_folders:
                # New folder to be created - light green
                folder_color = 'lightgreen'
                folder_indicator = "📁"
            elif existing_folders and folder_path in existing_folders:
                # Existing folder - no color (default)
                folder_color = None
                folder_indicator = "📁"
            else:
                # Default/unknown - yellow
                folder_color = 'yellow'
                folder_indicator = "📁"

            # Print folder header
            if folder_color:
                colored_folder = self.colorize(f"{folder_indicator} {folder_name}/", folder_color, 'bright')
                colored_separator = self.colorize("-" * (len(folder_name) + 3), folder_color)
            else:
                colored_folder = f"{folder_indicator} {folder_name}/"
                colored_separator = "-" * (len(folder_name) + 3)

            print(colored_folder)
            print(colored_separator)

            # Print files in this folder (just the filename)
            # Files being moved are always green, regardless of folder status
            for source, target in files:
                colored_file = self.colorize(f"  📄 {source.name}", 'lightgreen')
                print(colored_file)

            print()

    def display_skipped_files(self, skipped_files: List[Tuple[Path, str]], min_files_threshold: int = 1):
        """
        Display files that were skipped or not properly detected.

        Args:
            skipped_files: List of (file_path, reason) tuples
            min_files_threshold: The minimum file threshold that was applied
        """
        if not skipped_files:
            return

        print(self.colorize("Files Not Organized:", 'orange', 'bright'))
        print(self.colorize("=" * len("Files Not Organized:"), 'orange'))

        # Group by reason for better organization
        reason_groups = defaultdict(list)
        for file_path, reason in skipped_files:
            reason_groups[reason].append(file_path)

        # Sort reasons and display
        for reason in sorted(reason_groups.keys()):
            files = reason_groups[reason]

            print(self.colorize(f"📋 {reason}:", 'orange'))

            # Sort files alphabetically
            for file_path in sorted(files, key=lambda x: x.name):
                colored_file = self.colorize(f"  📄 {file_path.name}", 'orange')
                print(colored_file)

            print()

        if min_files_threshold > 1:
            notice = self.colorize(f"Note: Files below minimum threshold of {min_files_threshold} per folder were skipped.", 'yellow')
            print(notice)
            print()

    def display_operation_summary(self, summary: Dict):
        """
        Display a summary of operations.

        Args:
            summary: Operation summary dictionary
        """
        print(self.colorize("Operation Summary:", 'cyan', 'bright'))
        print()

        # Statistics
        stats = [
            ("Files to organize:", summary['planned_moves'], 'lightgreen'),
            ("Successful operations:", summary['successful_operations'], 'lightgreen'),
            ("Failed operations:", summary['failed_operations'], 'red'),
            ("Folders to create:", summary['folders_to_create'], 'cyan'),
            ("Total files found:", summary['total_files_found'], 'white')
        ]

        for label, count, color in stats:
            colored_label = self.colorize(label, color)
            print(f"{colored_label} {count}")

        print()

        # Failed operations (if any)
        if summary['failed_files']:
            print(self.colorize("Failed Operations:", 'red', 'bright'))
            for file_path, error in summary['failed_files']:
                colored_file = self.colorize(f"  ❌ {file_path.name}", 'red')
                colored_error = self.colorize(f"({error})", 'yellow')
                print(f"{colored_file} {colored_error}")
            print()

    def prompt_confirmation(self, message: str, default: bool = True) -> bool:
        """
        Prompt user for confirmation with proper formatting.

        Args:
            message: Confirmation message
            default: Default answer if user just presses Enter

        Returns:
            True if user confirms, False otherwise
        """
        if default:
            prompt_suffix = "[Y/n]"
        else:
            prompt_suffix = "[y/N]"

        colored_message = self.colorize(message, 'cyan', 'bright')
        colored_suffix = self.colorize(prompt_suffix, 'yellow')

        while True:
            try:
                response = input(f"{colored_message} {colored_suffix}: ").strip().lower()

                if not response:
                    return default

                if response in ['y', 'yes', 'ye']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print(self.colorize("Please enter 'y' or 'n'.", 'red'))

            except (KeyboardInterrupt, EOFError):
                print()
                print(self.colorize("Operation cancelled.", 'red'))
                return False

    def print_success(self, message: str):
        """Print a success message."""
        colored_message = self.colorize(f"✅ {message}", 'lightgreen', 'bright')
        print(colored_message)

    def print_error(self, message: str):
        """Print an error message."""
        colored_message = self.colorize(f"❌ {message}", 'red', 'bright')
        print(colored_message)

    def print_warning(self, message: str):
        """Print a warning message."""
        colored_message = self.colorize(f"⚠️  {message}", 'yellow', 'bright')
        print(colored_message)

    def print_info(self, message: str):
        """Print an info message."""
        colored_message = self.colorize(f"ℹ️  {message}", 'cyan', 'bright')
        print(colored_message)

    def print_dry_run_notice(self):
        """Print a dry run notice."""
        notice = self.colorize("🔍 DRY RUN MODE - No files will be moved", 'yellow', 'bright')
        print(notice)
        print(self.colorize("-" * len("DRY RUN MODE - No files will be moved"), 'yellow'))
        print()

    def print_progress_bar(self, current: int, total: int, width: int = 50):
        """
        Print a simple progress bar.

        Args:
            current: Current progress
            total: Total items
            width: Width of the progress bar
        """
        if total == 0:
            return

        percentage = current / total
        filled = int(width * percentage)
        bar = '█' * filled + '░' * (width - filled)

        colored_bar = self.colorize(bar, 'lightgreen')
        colored_percentage = self.colorize(f"{percentage:.1%}", 'cyan')

        print(f"\rProgress: |{colored_bar}| {colored_percentage} ({current}/{total})", end='')

        if current == total:
            print()  # New line when complete