#!/usr/bin/env python3
"""
BAM Deduplication CLI

Beautiful command-line interface for BAM file deduplication with multiple processing strategies.

Author: Ye Chang
Date: 2025-01-27
"""

import importlib.metadata
import os

import pysam
import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .deduplication import process_bam

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.ERRORS_SUGGESTION = (
    "Try running the '--help' flag for more information."
)
click.rich_click.ERRORS_EPILOGUE = "To find out more, visit [link=https://github.com/y9c/markdup]https://github.com/y9c/markdup[/link]"

console = Console()


def validate_bam_file(bam_file: str, threads: int = 1) -> bool:
    """Simple BAM/SAM file validation - check if sorted by coordinate and create/rebuild index if needed."""
    try:
        # Skip indexing for SAM files - they will be converted to BAM later
        if bam_file.endswith(".sam"):
            console.print(
                "📝 SAM file detected - will be converted to BAM for processing"
            )
            # Just check if it's a valid SAM file
            with pysam.AlignmentFile(bam_file, "r") as f:
                header = f.header
                if "HD" in header and "SO" in header["HD"]:
                    return header["HD"]["SO"] == "coordinate"
                return False
        else:
            # Check if index exists and is newer than BAM file
            index_file = bam_file + ".bai"
            bam_mtime = os.path.getmtime(bam_file)

            if not os.path.exists(index_file):
                console.print("📝 Creating BAM index...")
                pysam.index(bam_file, "-@", str(threads))
            else:
                # Check if index is older than BAM file
                index_mtime = os.path.getmtime(index_file)
                if index_mtime < bam_mtime:
                    console.print("🔄 BAM index is older than BAM file, rebuilding...")
                    pysam.index(bam_file, "-@", str(threads))

            # Check if sorted by coordinate
            with pysam.AlignmentFile(bam_file, "rb") as f:
                header = f.header
                if "HD" in header and "SO" in header["HD"]:
                    return header["HD"]["SO"] == "coordinate"
                return False
    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")
        return False


def detect_umi_method(bam_file: str, umi_sep: str, umi_tag: str) -> tuple[str, str]:
    """Auto-detect if UMI exists in query names or tags."""
    try:
        with pysam.AlignmentFile(bam_file, "rb") as f:
            reads_checked = 0
            umi_in_qname_count = 0
            umi_in_tag_count = 0

            for read in f:
                if reads_checked >= 10:
                    break
                reads_checked += 1

                # Check if UMI exists in query name (after umi_sep)
                if umi_sep and umi_sep in read.query_name:
                    potential_umi = read.query_name.rsplit(umi_sep, 1)[-1]
                    if potential_umi and all(
                        base in "ATGC" for base in potential_umi.upper()
                    ):
                        umi_in_qname_count += 1

                # Check if UMI exists in tags
                if umi_tag and read.has_tag(umi_tag):
                    umi_in_tag_count += 1

            # Prefer tag-based UMI if tag is specified and present
            if umi_tag and umi_in_tag_count > 0:
                return "umi", umi_tag
            # Otherwise use name-based UMI if separator is present in most reads
            if umi_in_qname_count >= 8:
                return "umi", None
            # Fallback to coordinate-based
            return "coordinate", None

    except Exception:
        return "coordinate", None


def print_banner():
    """Print beautiful tool banner."""
    banner_text = Text("🧬 Dedup - Efficient BAM File Deduplication", style="bold blue")
    console.print(Panel(banner_text, style="blue", padding=(1, 2)))


@click.command(
    name="markdup",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="""
[bold blue]Examples:[/bold blue]

[dim]# Basic usage[/dim]
[green]markdup input.bam output.bam[/green]

[dim]# Use custom window size and threads[/dim]
[green]markdup input.bam output.bam --window-size 2000000 -t 8[/green]

[dim]# UMI-based deduplication (extract from read names)[/dim]
[green]markdup input.bam output.bam --umi-sep _ --max-dist-frac 0.15[/green]

[dim]# UMI-based deduplication (extract from BAM tags)[/dim]
[green]markdup input.bam output.bam --umi-tag UB[/green]

[dim]# Coordinate-based deduplication (ignore UMIs)[/dim]
[green]markdup input.bam output.bam --no-umi[/green]

[dim]# Keep duplicates and mark them[/dim]
[green]markdup input.bam output.bam --keep-duplicates --best-read-by mapq[/green]

[dim]# Advanced filtering and processing[/dim]
[green]markdup input.bam output.bam --fragment-paired --fragment-mapped --keep-duplicates --best-read-by avg_base_q[/green]
    """,
)
@click.argument(
    "input_bam",
    type=click.Path(exists=True, path_type=str),
    metavar="INPUT_BAM",
)
@click.argument(
    "output_bam",
    type=click.Path(path_type=str),
    metavar="OUTPUT_BAM",
)
@click.option(
    "--no-umi",
    is_flag=True,
    help="[bold]Force coordinate-based deduplication[/bold] (ignore any detected UMIs). By default, the tool attempts UMI-based deduplication if UMIs are detected.",
)
@click.option(
    "--umi-tag",
    default=None,
    show_default=False,
    help="[bold]UMI tag name[/bold] for UMI-based deduplication. If not specified, extracts UMIs from read names using --umi-sep",
)
@click.option(
    "--umi-sep",
    default="_",
    show_default=True,
    help="[bold]Separator[/bold] for extracting UMIs from read names (default method when --umi-tag not specified)",
)
@click.option(
    "-e",
    "--max-dist-frac",
    type=float,
    default=0.1,
    show_default=True,
    help="[bold]Maximum UMI edit distance[/bold] as a fraction of UMI length",
)
@click.option(
    "--max-frequency-ratio",
    type=float,
    default=0.1,
    show_default=True,
    help="[bold]Maximum frequency ratio[/bold] for UMI merging (smaller UMI frequency / larger UMI frequency). Prevents merging of UMIs with too large frequency differences that are likely distinct biological entities.",
)
@click.option(
    "--keep-duplicates",
    is_flag=True,
    help="[bold]Keep duplicate reads[/bold] and mark them with the duplicate flag",
)
@click.option(
    "--best-read-by",
    type=click.Choice(["mapq", "avg_base_q"], case_sensitive=False),
    default="avg_base_q",
    show_default=True,
    help="[bold]Select best read[/bold] by mapping quality or average base quality",
)
@click.option(
    "--window-size",
    type=int,
    default=100_000,
    show_default=True,
    help="[bold]Genomic window size[/bold] for processing (in base pairs)",
)
# Min window size is always 1 - no CLI parameter needed
@click.option(
    "--max-pair-dist",
    type=int,
    default=2000,
    show_default=True,
    help="[bold]Maximum distance[/bold] between read pairs for overlapping windows (in base pairs)",
)
@click.option(
    "-t",
    "--threads",
    type=int,
    default=None,
    help="[bold]Number of threads[/bold] for parallel processing (default: auto-detect)",
)
@click.option(
    "--fragment-paired",
    is_flag=True,
    help="[bold]Keep only fragments with both reads present[/bold] (filter out fragments missing one read)",
)
@click.option(
    "--fragment-mapped",
    is_flag=True,
    help="[bold]Keep only fragments where both reads are mapped[/bold] (filter out fragments with unmapped reads)",
)
@click.option(
    "--start-only",
    is_flag=True,
    help="[bold]Use only start position[/bold] for grouping reads (like UMICollapse). By default, uses both start and end positions.",
)
@click.option(
    "--end-only",
    is_flag=True,
    help="[bold]Use only end position[/bold] for grouping reads (useful when reads are reverse-complemented before mapping).",
)
@click.option(
    "--force",
    is_flag=True,
    help="[bold]Overwrite output file[/bold] without prompting",
)
@click.version_option(importlib.metadata.version("markdup"), "--version", "-v")
def main(
    input_bam: str,
    output_bam: str,
    no_umi: bool,
    umi_tag: str,
    umi_sep: str,
    max_dist_frac: float,
    max_frequency_ratio: float,
    keep_duplicates: bool,
    best_read_by: str,
    window_size: int,
    max_pair_dist: int,
    threads: int | None,
    fragment_paired: bool,
    fragment_mapped: bool,
    start_only: bool,
    end_only: bool,
    force: bool,
):
    """
    [bold blue]🧬 Dedup - Efficient BAM File Deduplication[/bold blue]

    A powerful tool for deduplicating BAM files using UMI tags or alignment coordinates
    with multiple processing strategies and advanced filtering options.

    [bold]Key Features:[/bold]
    • [bold green]Multiple deduplication methods[/bold green]: UMI-based and coordinate-based
    • [bold green]Flexible processing approaches[/bold green]: Sequential, fetch, and whole-file
    • [bold green]Advanced filtering options[/bold green]: Remove unpaired, chimeric, or unmapped reads
    • [bold green]Parallel processing[/bold green]: Multi-threaded with automatic thread detection
    • [bold green]Memory efficient[/bold green]: Streaming processing for large files
    • [bold green]Rich output[/bold green]: Beautiful progress bars and detailed statistics

    [bold]Input Requirements:[/bold]
    • Input BAM file must be [bold]coordinate-sorted[/bold]
    • BAM index (.bai) will be created automatically if missing
    """

    # Banner removed - will be shown in progress panel

    # Determine deduplication method
    if no_umi:
        method = "coordinate"
        print("🔧 Using coordinate-based deduplication (--no-umi specified)")
    else:
        # Default: Auto-detect UMI presence
        method, umi_tag = detect_umi_method(input_bam, umi_sep, umi_tag)
        # Silent detection; method is shown in the configuration panel

    # Build and display processing configuration BEFORE validation
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column(style="bold blue", justify="left")
    info_table.add_column(style="white", justify="left")

    info_table.add_row("Method:", f"{method} (auto-detected)" if not no_umi else method)
    info_table.add_row("Window size:", f"{window_size:,}")
    info_table.add_row("Threads:", str(threads or "auto"))

    if method == "umi":
        info_table.add_row("UMI tag:", umi_tag or "N/A")
        info_table.add_row("UMI separator:", f"{umi_sep}")
        info_table.add_row("Min edit dist:", str(max_dist_frac))
        info_table.add_row("Max freq ratio:", str(max_frequency_ratio))

    if any([fragment_paired, fragment_mapped]):
        filters = []
        if fragment_mapped:
            filters.append("fragment-mapped")
        if fragment_paired:
            filters.append("fragment-paired")
        info_table.add_row("Filters:", ", ".join(filters))

    if keep_duplicates:
        info_table.add_row("Keep duplicates:", "Yes (marked with duplicate flag)")

    if start_only:
        info_table.add_row("Position:", "Start only (biological start)")
    elif end_only:
        info_table.add_row("Position:", "End only")
    else:
        info_table.add_row("Position:", "Start + end")

    info_table.add_row("Best read by:", best_read_by)

    console.print(
        Panel(
            info_table,
            title="[bold green]Processing configuration[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Validate input file exists
    if not os.path.exists(input_bam):
        console.print(f"[red]❌ Input file '{input_bam}' does not exist![/red]")
        return

    # Check output directory exists
    output_dir = os.path.dirname(output_bam)
    if output_dir and not os.path.exists(output_dir):
        console.print(f"[red]❌ Output directory '{output_dir}' does not exist![/red]")
        return

    # Check if output file already exists
    if os.path.exists(output_bam):
        if not force:
            response = console.input(
                f"[yellow]⚠️  Output file '{output_bam}' already exists. Overwrite? (y/N): [/yellow]"
            )
            if response.lower() != "y":
                console.print("[yellow]Operation cancelled.[/yellow]")
                return
        else:
            # Overwrite warning will be shown in progress panel
            pass

    # Validate options
    if start_only and end_only:
        console.print("[red]❌ Cannot specify both --start-only and --end-only![/red]")
        return

    # Validate numeric parameters
    if window_size <= 0:
        console.print(f"[red]❌ Window size must be positive, got: {window_size}[/red]")
        return

    if max_pair_dist <= 0:
        console.print(
            f"[red]❌ Max pair distance must be positive, got: {max_pair_dist}[/red]"
        )
        return

    if not 0 <= max_dist_frac <= 1:
        console.print(
            f"[red]❌ Min edit distance fraction must be between 0 and 1, got: {max_dist_frac}[/red]"
        )
        return

    if not 0 <= max_frequency_ratio <= 1:
        console.print(
            f"[red]❌ Max frequency ratio must be between 0 and 1, got: {max_frequency_ratio}[/red]"
        )
        return

    # Validate BAM file
    console.print("🔍 Validating BAM file...")
    if not validate_bam_file(input_bam, threads or 1):
        console.print("[red]❌ BAM file validation failed![/red]")
        return
    console.print("✅ BAM file validation passed")

    # Print processing information
    # Create processing information table

    # Process BAM file - all output will be shown in panels at the end
    console.print("🚀 Starting BAM processing...")

    try:
        # Always use sequential reading with parallel window processing
        try:
            success = process_bam(
                input_bam=input_bam,
                output_bam=output_bam,
                method=method,
                umi_tag=umi_tag,
                window_size=window_size,
                max_processes=threads,
                max_pair_dist=max_pair_dist,
                umi_sep=umi_sep,
                max_dist_frac=max_dist_frac,
                max_frequency_ratio=max_frequency_ratio,
                keep_duplicates=keep_duplicates,
                best_read_by=best_read_by,
                fragment_paired=fragment_paired,
                fragment_mapped=fragment_mapped,
                start_only=start_only,
                end_only=end_only,
            )
        except Exception as e:
            console.print(f"[red]❌ Error during BAM processing: {e}[/red]")
            import traceback

            traceback.print_exc()
            return

        if not success:
            console.print("[red]❌ Processing failed![/red]")
            return

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Processing interrupted by user[/yellow]")
        return

    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        import traceback

        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
