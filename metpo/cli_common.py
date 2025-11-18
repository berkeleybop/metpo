"""Shared Click CLI option decorators for consistent command-line interface.

This module provides standardized Click option decorators to ensure consistency
across all METPO CLI tools. Use these decorators instead of creating custom
@click.option() definitions.

Example:
    from metpo.cli_common import input_file_option, output_option

    @click.command()
    @input_file_option()
    @output_option()
    def my_command(input_file, output):
        # Your code here
        pass
"""

import click

# =============================================================================
# File I/O Options
# =============================================================================


def input_file_option(required=True, help_text="Input file path"):
    """Standard single input file option.

    Args:
        required: Whether the option is required (default: True)
        help_text: Custom help text (default: 'Input file path')

    Returns:
        Click option decorator for --input-file, -i
    """
    return click.option(
        "--input-file",
        "-i",
        type=click.Path(exists=True, dir_okay=False, path_type=str),
        required=required,
        help=help_text,
    )


def input_csv_option(required=True, help_text="Input CSV/TSV file path"):
    """Standard CSV/TSV input file option.

    Args:
        required: Whether the option is required (default: True)
        help_text: Custom help text

    Returns:
        Click option decorator for --input-file, -i
    """
    return click.option(
        "--input-file",
        "-i",
        type=click.Path(exists=True, dir_okay=False, path_type=str),
        required=required,
        help=help_text,
    )


def output_option(required=False, default=None, help_text="Output file path"):
    """Standard output file option.

    Args:
        required: Whether the option is required (default: False)
        default: Default output path (default: None)
        help_text: Custom help text (default: 'Output file path')

    Returns:
        Click option decorator for --output, -o
    """
    return click.option(
        "--output",
        "-o",
        type=click.Path(dir_okay=False, path_type=str),
        required=required,
        default=default,
        help=help_text,
    )


def output_dir_option(required=False, default=None, help_text="Output directory path"):
    """Standard output directory option.

    Args:
        required: Whether the option is required (default: False)
        default: Default output directory (default: None)
        help_text: Custom help text

    Returns:
        Click option decorator for --output-dir
    """
    return click.option(
        "--output-dir",
        type=click.Path(exists=True, file_okay=False, path_type=str),
        required=required,
        default=default,
        help=help_text,
    )


# =============================================================================
# Database Connection Options
# =============================================================================


def chroma_path_option(default="./chroma_db", help_text="ChromaDB storage directory path"):
    """Standard ChromaDB storage path option.

    Args:
        default: Default ChromaDB path (default: './chroma_db')
        help_text: Custom help text

    Returns:
        Click option decorator for --chroma-path
    """
    return click.option(
        "--chroma-path", type=click.Path(path_type=str), default=default, help=help_text
    )


def db_path_option(required=True, help_text="SQLite database file path"):
    """Standard SQLite database path option.

    Args:
        required: Whether the option is required (default: True)
        help_text: Custom help text

    Returns:
        Click option decorator for --db-path
    """
    return click.option(
        "--db-path",
        type=click.Path(exists=True, dir_okay=False, path_type=str),
        required=required,
        help=help_text,
    )


def mongo_uri_option(default="mongodb://localhost:27017/", help_text="MongoDB connection URI"):
    """Standard MongoDB URI option.

    Args:
        default: Default MongoDB URI
        help_text: Custom help text

    Returns:
        Click option decorator for --mongo-uri
    """
    return click.option("--mongo-uri", default=default, help=help_text)


def database_option(default="bactotraits", help_text="Database name"):
    """Standard database name option.

    Args:
        default: Default database name
        help_text: Custom help text

    Returns:
        Click option decorator for --database, -d
    """
    return click.option("--database", "-d", default=default, help=help_text)


def collection_option(default="bactotraits", help_text="Collection name"):
    """Standard collection name option.

    Args:
        default: Default collection name
        help_text: Custom help text

    Returns:
        Click option decorator for --collection, -c
    """
    return click.option("--collection", "-c", default=default, help=help_text)


# =============================================================================
# Processing Options
# =============================================================================


def batch_size_option(default=1000, help_text="Batch processing size"):
    """Standard batch size option.

    Args:
        default: Default batch size (default: 1000)
        help_text: Custom help text

    Returns:
        Click option decorator for --batch-size
    """
    return click.option("--batch-size", type=int, default=default, help=help_text)


def limit_option(default=None, help_text="Limit number of items to process"):
    """Standard limit option.

    Args:
        default: Default limit (default: None for unlimited)
        help_text: Custom help text

    Returns:
        Click option decorator for --limit
    """
    return click.option("--limit", type=int, default=default, help=help_text)


def offset_option(default=0, help_text="Starting offset for processing"):
    """Standard offset option.

    Args:
        default: Default offset (default: 0)
        help_text: Custom help text

    Returns:
        Click option decorator for --offset
    """
    return click.option("--offset", type=int, default=default, help=help_text)


# =============================================================================
# Threshold Options
# =============================================================================


def distance_threshold_option(default=0.35, help_text="Distance threshold for matching"):
    """Standard distance threshold option.

    Args:
        default: Default threshold value (default: 0.35)
        help_text: Custom help text

    Returns:
        Click option decorator for --distance-threshold
    """
    return click.option("--distance-threshold", type=float, default=default, help=help_text)


def confidence_threshold_option(default=0.9, help_text="Confidence threshold"):
    """Standard confidence threshold option.

    Args:
        default: Default threshold value (default: 0.9)
        help_text: Custom help text

    Returns:
        Click option decorator for --confidence-threshold
    """
    return click.option("--confidence-threshold", type=float, default=default, help=help_text)


# =============================================================================
# Behavioral Flags
# =============================================================================


def verbose_option(help_text="Enable verbose output"):
    """Standard verbose flag option.

    Args:
        help_text: Custom help text

    Returns:
        Click option decorator for --verbose, -v
    """
    return click.option("--verbose", "-v", is_flag=True, default=False, help=help_text)


def debug_option(help_text="Enable debug mode"):
    """Standard debug flag option.

    Args:
        help_text: Custom help text

    Returns:
        Click option decorator for --debug
    """
    return click.option("--debug", is_flag=True, default=False, help=help_text)


def dry_run_option(help_text="Dry run mode (preview only) / Execute mode (write changes)"):
    """Standard dry-run/execute flag option.

    Args:
        help_text: Custom help text

    Returns:
        Click option decorator for --dry-run/--execute
    """
    return click.option("--dry-run/--execute", default=True, help=help_text)


# =============================================================================
# Format Options
# =============================================================================


def format_option(default="text", formats=None, help_text="Output format"):
    """Standard format selection option.

    Args:
        default: Default format (default: 'text')
        formats: List of valid formats (default: ['text', 'yaml', 'json', 'csv'])
        help_text: Custom help text

    Returns:
        Click option decorator for --format, -f
    """
    if formats is None:
        formats = ["text", "yaml", "json", "csv"]

    return click.option(
        "--format",
        "-f",
        type=click.Choice(formats, case_sensitive=False),
        default=default,
        help=help_text,
    )
