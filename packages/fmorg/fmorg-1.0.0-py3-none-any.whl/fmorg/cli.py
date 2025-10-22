"""
Command-line interface for FMORG using click.

This module provides a user-friendly CLI for the file organization tool
with proper argument parsing, help text, and error handling.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import click

from .analyzer import FilenameAnalyzer
from .organizer import FileOrganizer
from .display import DisplayManager

# Create a display namespace for test compatibility
from . import display as display_module
display = display_module


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Setup logging configuration."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.command()
@click.argument('directory', type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    '--min', '-m',
    default=1,
    type=int,
    help='Minimum number of files required to create a folder (default: 1)'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output directory for organized files (default: same as input directory)'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Scan subdirectories recursively'
)
@click.option(
    '--dry-run', '-d',
    is_flag=True,
    help='Show what would be done without actually moving files'
)
@click.option(
    '--yes', '-y',
    is_flag=True,
    help='Skip confirmation prompt and execute operations'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Suppress non-error output'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Disable colored output'
)
@click.version_option(version='1.0.0', prog_name='fmorg')
def cli(
    directory: Optional[Path],
    min: int,
    output: Optional[Path],
    recursive: bool,
    dry_run: bool,
    yes: bool,
    verbose: bool,
    quiet: bool,
    no_color: bool
):
    """
    FMORG - Smart File Organization Tool

    Automatically organizes files into folders based on intelligent filename analysis.

    DIRECTORY: The directory containing files to organize (default: current directory)

    Examples:

        \b
        # Organize files in current directory
        fmorg .

        \b
        # Organize files with minimum 2 files per folder
        fmorg /path/to/files --min 2

        \b
        # Recursively scan subdirectories
        fmorg /path/to/files --recursive

        \b
        # Dry run to see what would be done
        fmorg /path/to/files --dry-run

        \b
        # Organize to a different output directory
        fmorg /path/to/source --output /path/to/target
    """
    # Setup logging
    setup_logging(verbose, quiet)

    # Initialize display manager
    use_colors = not no_color
    display = DisplayManager(use_colors=use_colors)

    # Handle default directory
    if directory is None:
        directory = Path('.')
    else:
        directory = Path(directory)

    # Validate arguments
    if min < 1:
        display.print_error("Minimum files per folder must be at least 1")
        sys.exit(1)

    if directory.is_file():
        display.print_error(f"'{directory}' is a file, not a directory")
        sys.exit(1)

    # Set output directory
    if output is None:
        output = directory

    try:
        output = output.resolve()
        if not output.exists():
            output.mkdir(parents=True, exist_ok=True)
            if not quiet:
                display.print_info(f"Created output directory: {output}")
    except Exception as e:
        display.print_error(f"Cannot create output directory '{output}': {e}")
        sys.exit(1)

    # Display startup information
    if not quiet:
        display.print_header("FMORG - Smart File Organization Tool")
        display.print_info(f"Scanning directory: {directory}")
        display.print_info(f"Output directory: {output}")
        display.print_info(f"Minimum files per folder: {min}")
        if recursive:
            display.print_info("Recursive scan: enabled")
        print()

        if dry_run:
            display.print_dry_run_notice()

    # Initialize organizer
    try:
        organizer = FileOrganizer(base_directory=output, min_files_per_folder=min)
    except Exception as e:
        display.print_error(f"Failed to initialize organizer: {e}")
        sys.exit(1)

    # Scan for files
    try:
        if not quiet:
            display.print_info("Scanning for files...")

        files = organizer.scan_directory(directory, recursive=recursive)

        if not files:
            display.print_warning("No files found to organize")
            sys.exit(0)

        if not quiet:
            display.print_success(f"Found {len(files)} files")
            print()

    except Exception as e:
        display.print_error(f"Failed to scan directory: {e}")
        sys.exit(1)

    # Analyze files
    try:
        if not quiet:
            display.print_info("Analyzing filenames...")

        grouped_files = organizer.analyze_files(files)

        if not grouped_files:
            display.print_warning("No files could be analyzed for organization")
            sys.exit(0)

        if not quiet:
            display.print_success(f"Analyzed {len(files)} files into {len(grouped_files)} groups")
            print()

            # Display analysis results
            display.display_file_analysis(grouped_files)

    except Exception as e:
        display.print_error(f"Failed to analyze files: {e}")
        sys.exit(1)

    # Create organization plan
    try:
        if not quiet:
            display.print_info("Creating organization plan...")

        plan = organizer.create_organization_plan(grouped_files)

        if not plan:
            display.print_warning("No files to organize (check minimum file threshold)")
            sys.exit(0)

        if not quiet:
            display.print_success(f"Planned to move {len(plan)} files")
            print()

            # Display organization plan
            display.display_organization_plan(plan, output,
                                             organizer.existing_folders_used,
                                             organizer.new_folders_to_create)

            # Display skipped files
            if organizer.skipped_files:
                print()
                display.display_skipped_files(organizer.skipped_files, organizer.min_files_per_folder)

    except Exception as e:
        display.print_error(f"Failed to create organization plan: {e}")
        sys.exit(1)

    # Validate operations
    try:
        validation_errors = organizer.validate_operations()
        if validation_errors:
            display.print_warning(f"Found {len(validation_errors)} potential issues:")
            for path, error in validation_errors:
                display.print_warning(f"  {path.name}: {error}")
            print()

    except Exception as e:
        display.print_error(f"Failed to validate operations: {e}")
        sys.exit(1)

    # Show operation summary
    if not quiet:
        summary = organizer.get_operation_summary()
        display.display_operation_summary(summary)

    # Get user confirmation (unless yes flag or dry run)
    if not dry_run and not yes:
        if not display.prompt_confirmation("Do you want to proceed with the organization?"):
            display.print_info("Operation cancelled by user")
            sys.exit(0)

    elif dry_run and not quiet:
        display.print_info("Dry run mode - not executing operations")

    # Execute the plan
    try:
        if not dry_run and not quiet:
            display.print_info("Executing organization plan...")

        success = organizer.execute_plan(dry_run=dry_run)

        if success:
            if not quiet:
                final_summary = organizer.get_operation_summary()
                if dry_run:
                    display.print_success("Dry run completed successfully")
                else:
                    display.print_success("File organization completed successfully")

                display.display_operation_summary(final_summary)
        else:
            display.print_error("Some operations failed")
            final_summary = organizer.get_operation_summary()
            display.display_operation_summary(final_summary)
            sys.exit(1)

    except KeyboardInterrupt:
        display.print_warning("Operation interrupted by user")
        sys.exit(1)

    except Exception as e:
        display.print_error(f"Failed to execute organization plan: {e}")
        sys.exit(1)


def main_entry():
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main_entry()