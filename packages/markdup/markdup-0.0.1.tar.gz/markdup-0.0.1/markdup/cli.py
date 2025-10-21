#!/usr/bin/env python3
"""
BAM Deduplication CLI

Beautiful command-line interface for BAM file deduplication with multiple processing strategies.

Author: Ye Chang
Date: 2025-01-27
"""

import os
from typing import Optional

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
    """Simple BAM file validation - check if sorted by coordinate and create/rebuild index if needed."""
    try:
        import os

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
[green]dedup input.bam output.bam --window-size 2000000 -t 8[/green]

[dim]# UMI-based deduplication with custom parameters[/dim]
[green]dedup input.bam output.bam --method umi --umi-sep _ --min-edit-dist-frac 0.15[/green]

[dim]# Coordinate-based deduplication with filtering[/dim]
[green]dedup input.bam output.bam --method coordinate --remove-unmapped --remove-chimeric[/green]

[dim]# Keep duplicates and mark them[/dim]
[green]dedup input.bam output.bam --keep-duplicates --best-read-by mapq[/green]

[dim]# Advanced filtering and processing[/dim]
[green]dedup input.bam output.bam --method umi --remove-unpaired --remove-chimeric --remove-unmapped --keep-duplicates --best-read-by avg_base_q[/green]
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
    "--auto",
    is_flag=True,
    help="[bold]Auto-detect UMI method[/bold] by checking first 10 reads for UMI patterns. When used, --method, --umi-sep, and --umi-tag options are ignored.",
)
@click.option(
    "--method",
    type=click.Choice(["umi", "coordinate"], case_sensitive=False),
    default="umi",
    show_default=True,
    help="[bold]Deduplication method[/bold]\n\n[dim]• [bold]umi[/bold]: Use UMI tags for deduplication (recommended for single-cell data)\n• [bold]coordinate[/bold]: Use alignment coordinates for deduplication[/dim]",
)
@click.option(
    "--umi-tag",
    default="UB",
    show_default=True,
    help="[bold]UMI tag name[/bold] for UMI-based deduplication",
)
@click.option(
    "--umi-sep",
    default="_",
    show_default=True,
    help="[bold]Separator[/bold] for extracting UMIs from read names",
)
@click.option(
    "-e",
    "--min-edit-dist-frac",
    type=float,
    default=0.1,
    show_default=True,
    help="[bold]Minimum UMI edit distance[/bold] as a fraction of UMI length",
)
@click.option(
    "--min-frequency-ratio",
    type=float,
    default=0.1,
    show_default=True,
    help="[bold]Minimum frequency ratio[/bold] for UMI merging (smaller UMI frequency / larger UMI frequency). Prevents merging of two high-frequency UMIs that are likely distinct biological entities.",
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
    "--remove-unpaired",
    is_flag=True,
    help="[bold]Remove unpaired reads[/bold] (only keep properly paired reads)",
)
@click.option(
    "--remove-chimeric",
    is_flag=True,
    help="[bold]Remove chimeric reads[/bold] (reads with supplementary alignments)",
)
@click.option(
    "--remove-unmapped",
    is_flag=True,
    help="[bold]Remove unmapped reads[/bold]",
)
@click.option(
    "--prefilter",
    is_flag=True,
    default=False,
    help="[bold]Enable pre-filtering[/bold] to skip empty windows (default: disabled)",
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
def main(
    input_bam: str,
    output_bam: str,
    auto: bool,
    method: str,
    umi_tag: str,
    umi_sep: str,
    min_edit_dist_frac: float,
    min_frequency_ratio: float,
    keep_duplicates: bool,
    best_read_by: str,
    window_size: int,
    max_pair_dist: int,
    threads: Optional[int],
    remove_unpaired: bool,
    remove_chimeric: bool,
    remove_unmapped: bool,
    prefilter: bool,
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

    # Auto-detect method only if --auto is explicitly used
    if auto:
        from .deduplication import UnifiedProcessor

        temp_processor = UnifiedProcessor(
            input_bam,
            output_bam,
            method,
            umi_tag,
            window_size,
            threads,
            max_pair_dist,
            umi_sep,
            min_edit_dist_frac,
            min_frequency_ratio,
            keep_duplicates,
            best_read_by,
            remove_unpaired,
            remove_chimeric,
            remove_unmapped,
        )
        method = temp_processor.method
        print(f"🔍 Auto-detected method: {method}")
    else:
        print(f"🔧 Using specified method: {method}")

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

    # Validate BAM file
    console.print("🔍 Validating BAM file...")
    if not validate_bam_file(input_bam, threads or 1):
        console.print("[red]❌ BAM file validation failed![/red]")
        return
    console.print("✅ BAM file validation passed")

    # Print processing information
    # Create processing information table

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column(style="bold blue", justify="right", width=20)
    info_table.add_column(style="white", justify="left")

    info_table.add_row("📁 Input file:", input_bam)
    info_table.add_row("📁 Output file:", output_bam)
    info_table.add_row("🔧 Method:", f"{method} (auto-detected)" if auto else method)
    info_table.add_row("📦 Window size:", f"{window_size:,}")
    info_table.add_row("⚡ Threads:", str(threads or "auto"))

    if method == "umi":
        info_table.add_row("🏷️  UMI tag:", umi_tag)
        info_table.add_row("🔗 UMI separator:", f"'{umi_sep}'")
        info_table.add_row("📏 Min edit distance:", str(min_edit_dist_frac))
        info_table.add_row("📊 Min frequency ratio:", str(min_frequency_ratio))

    if any([remove_unpaired, remove_chimeric, remove_unmapped]):
        filters = []
        if remove_unmapped:
            filters.append("unmapped")
        if remove_chimeric:
            filters.append("chimeric")
        if remove_unpaired:
            filters.append("unpaired")
        info_table.add_row("🔍 Filters:", ", ".join(filters))

    if keep_duplicates:
        info_table.add_row("📋 Keep duplicates:", "Yes (marked with duplicate flag)")

    if start_only:
        info_table.add_row(
            "📍 Position grouping:", "Start position only (biological start)"
        )
    elif end_only:
        info_table.add_row("📍 Position grouping:", "End position only")
    else:
        info_table.add_row("📍 Position grouping:", "Start + end position")

    info_table.add_row("🎯 Best read by:", best_read_by)

    # Process BAM file - all output will be shown in panels at the end
    console.print("🚀 Starting BAM processing...")

    try:
        # Always use sequential reading with parallel window processing
        if True:
            # Processing approach will be shown via progress bars
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
                    min_edit_dist_frac=min_edit_dist_frac,
                    min_frequency_ratio=min_frequency_ratio,
                    keep_duplicates=keep_duplicates,
                    best_read_by=best_read_by,
                    remove_unpaired=remove_unpaired,
                    remove_chimeric=remove_chimeric,
                    remove_unmapped=remove_unmapped,
                    prefilter=prefilter,
                    start_only=start_only,
                    end_only=end_only,
                )
            except Exception as e:
                console.print(f"[red]❌ Error in process_bam_sequential: {e}[/red]")
                import traceback

                traceback.print_exc()
                return
        # Only using sequential reading with parallel processing

        if success:
            # Processing completed successfully - no additional output needed
            pass
        else:
            pass

    except KeyboardInterrupt:
        pass

    except Exception:
        pass


if __name__ == "__main__":
    main()
