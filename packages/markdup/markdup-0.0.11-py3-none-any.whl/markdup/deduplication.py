#!/usr/bin/env python3
"""
Unified Deduplication Logic - Clean & Simple Architecture

This module provides a clean, unified approach to BAM deduplication with:
- Single reader object with sequential window processing
- Thread-safe writer object for parallel output
- Single processor for both UMI and coordinate methods
- Minimal code duplication

Author: Ye Chang
Date: 2025-01-27
"""

import logging
import os
import tempfile
import threading
import time
from collections import defaultdict
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

import pysam
from rich.progress import Progress, TimeElapsedColumn, TimeRemainingColumn

from .utils import (
    Fragment,
    calculate_average_base_quality,
    cluster_umis_by_edit_distance_frequency_aware,
    extract_umi,
    get_read_position,
)

# Set up logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Only show warnings and errors by default

# Globals used inside worker processes (set by pool initializer)
WORKER_READER = None
WORKER_WRITER = None
WORKER_SHARD_PATH = None


def _worker_initializer(bam_path: str, shard_dir: str):
    """Initializer for ProcessPool workers: open per-process reader and writer.

    Each process opens one AlignmentFile for reading and one shard BAM for writing.
    """
    import atexit as _atexit
    import os as _os

    import pysam as _pysam

    global WORKER_READER, WORKER_WRITER, WORKER_SHARD_PATH
    # Only create reader once per worker process
    if WORKER_READER is None:
        WORKER_READER = _pysam.AlignmentFile(bam_path, "rb")
    pid = _os.getpid()
    WORKER_SHARD_PATH = _os.path.join(shard_dir, f"shard_{pid}.bam")
    # Defer writer creation until first write to avoid creating unused shards
    WORKER_WRITER = None

    # Ensure files are closed when the worker exits so BGZF EOF is written
    def _worker_cleanup():
        try:
            if WORKER_WRITER is not None:
                WORKER_WRITER.close()
        except Exception:
            pass
        try:
            if WORKER_READER is not None:
                WORKER_READER.close()
        except Exception:
            pass

    _atexit.register(_worker_cleanup)


def _worker_shutdown_task():
    """Special task to close worker files before process termination."""
    global WORKER_WRITER, WORKER_READER
    try:
        if WORKER_WRITER is not None:
            WORKER_WRITER.close()
            WORKER_WRITER = None
    except Exception:
        pass
    try:
        if WORKER_READER is not None:
            WORKER_READER.close()
            WORKER_READER = None
    except Exception:
        pass
    return {"shutdown": True}


# ============================================================================
# QUALITY SCORING FUNCTIONS
# ============================================================================


def calculate_fragment_quality_score(fragment, best_read_by):
    """
    Calculate quality score for a fragment based on the specified criteria.

    Args:
        fragment: Fragment object containing read(s)
        best_read_by: Quality criterion ('mapq' or 'avg_base_q')

    Returns:
        float: Quality score for the fragment
    """
    if best_read_by == "mapq":
        if fragment.is_paired and fragment.read2:
            # For paired-end: use average of both reads' mapping qualities
            return (fragment.read1.mapping_quality + fragment.read2.mapping_quality) / 2
        # For single-end: use read1 mapping quality
        return fragment.read1.mapping_quality
    if best_read_by == "avg_base_q":
        if fragment.is_paired and fragment.read2:
            # For paired-end: use average of both reads' base qualities
            read1_qual = (
                calculate_average_base_quality(fragment.read1.query_qualities)
                if fragment.read1.query_qualities
                else 0
            )
            read2_qual = (
                calculate_average_base_quality(fragment.read2.query_qualities)
                if fragment.read2.query_qualities
                else 0
            )
            return (read1_qual + read2_qual) / 2
        # For single-end: use read1 base quality
        if fragment.read1.query_qualities:
            return calculate_average_base_quality(fragment.read1.query_qualities)
        return 0
    # Default to mapping quality
    if fragment.is_paired and fragment.read2:
        return (fragment.read1.mapping_quality + fragment.read2.mapping_quality) / 2
    return fragment.read1.mapping_quality


# ============================================================================
# BAM READER CLASS
# ============================================================================


class BAMReader:
    """
    Unified BAM file reader that handles genomic window creation.

    This class provides a unified interface for reading BAM files and creating
    genomic windows for parallel processing. It supports different reading
    strategies and efficiently checks for reads in genomic regions.
    """

    def __init__(
        self,
        bam_file: str,
        window_size: int,
        max_pair_dist: int = 2000,
        start_only: bool = False,
        end_only: bool = False,
    ):
        self.bam_file = bam_file
        self.window_size = window_size
        self.max_pair_dist = max_pair_dist
        self.start_only = start_only
        self.end_only = end_only
        self._header = None

    def get_header(self):
        """Get BAM header."""
        if self._header is None:
            with pysam.AlignmentFile(self.bam_file, "rb") as f:
                self._header = f.header
        return self._header

    def _check_region_has_reads(self, f, chromosome: str, start: int, end: int) -> bool:
        """Check if a genomic region contains any reads."""
        try:
            for _ in f.fetch(chromosome, start, end):
                return True
            return False
        except (ValueError, OSError):
            # Handle pysam internal errors or file access issues silently
            return False

    def get_windows(self) -> Iterator[dict[str, Any]]:
        """Create and yield genomic windows for processing."""
        import time

        window_id = 0
        total_windows_created = 0
        start_time = time.time()

        header = self.get_header()
        all_chromosomes = list(header.references)

        print("📖 Creating genomic windows...")

        for chromosome in all_chromosomes:
            contig_len = header.get_reference_length(chromosome)
            if contig_len is None:
                continue

            if contig_len <= self.window_size:
                # Short chromosome - use whole chromosome
                yield self._create_window_data(
                    chromosome,
                    0,
                    contig_len,
                    0,
                    contig_len,
                    window_id,
                    True,
                )
                window_id += 1
                total_windows_created += 1
            else:
                # Long chromosome - split into windows
                for i in range(0, contig_len, self.window_size):
                    window_start = i
                    window_end = min(i + self.window_size, contig_len)
                    search_start = max(0, window_start)
                    search_end = min(contig_len, window_end + self.max_pair_dist)

                    # Determine if this is the first window
                    is_first_window = i == 0

                    yield self._create_window_data(
                        chromosome,
                        search_start,
                        search_end,
                        window_start,
                        window_end,
                        window_id,
                        is_first_window,
                    )
                    window_id += 1
                    total_windows_created += 1

        # Print completion with timing
        window_creation_time = time.time() - start_time
        print(
            f"✅ Created {total_windows_created} windows (⏱️ {window_creation_time:.2f}s)"
        )

    def _create_window_data(
        self,
        chromosome: str,
        search_start: int,
        search_end: int,
        window_start: int,
        window_end: int,
        window_id: int,
        is_first: bool,
    ) -> dict[str, Any]:
        """Create window data dictionary."""
        return {
            "window_id": f"{chromosome}_window_{window_id}",
            "contig": chromosome,
            "search_start": search_start,
            "search_end": search_end,
            "window_start": window_start,
            "window_end": window_end,
            "is_first_window": is_first,
            "start_only": self.start_only,
            "end_only": self.end_only,
        }


# ============================================================================
# THREAD-SAFE WRITER CLASS
# ============================================================================


class ThreadSafeWriter:
    """
    Thread-safe BAM writer using multiple temporary files.

    This class provides thread-safe writing capabilities by using separate
    temporary files for each thread, then merging them at the end. It uses
    persistent file handles for efficiency."""

    def __init__(self, bam_file: str, num_threads: int):
        self.bam_file = bam_file
        self.num_threads = num_threads
        self.write_locks = {}  # thread_id -> lock
        self.temp_files = {}  # thread_id -> temp_file_path
        self.file_handles = {}  # thread_id -> file_handle
        self.header = None
        self.temp_dir = None
        self._setup_temp_files()

    def _setup_temp_files(self):
        """Setup temp files for each thread and open persistent file handles."""
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="dedup_threads_")

        # Get header
        with pysam.AlignmentFile(self.bam_file, "rb") as input_file:
            self.header = input_file.header

        # Create temp files and open persistent file handles for each thread
        for thread_id in range(self.num_threads):
            temp_file = os.path.join(self.temp_dir, f"thread_{thread_id}.bam")
            self.temp_files[thread_id] = temp_file

            # Create write lock for this thread
            self.write_locks[thread_id] = threading.Lock()

            # Create empty BAM file with header and open persistent file handle
            with pysam.AlignmentFile(temp_file, "wb", header=self.header):
                pass  # Just create the file with header

            # Open persistent file handle for writing (use 'wb' mode and keep it open)
            self.file_handles[thread_id] = pysam.AlignmentFile(
                temp_file, "wb", header=self.header
            )

    def write_reads(self, reads: list[str], header: Any, thread_id: int = None):
        """Write reads to the temp file for the specified thread using persistent file handle."""
        if not reads:
            return

        # Use thread_id if provided, otherwise use current thread ID
        if thread_id is None:
            thread_id = threading.get_ident() % self.num_threads

        # Get the file handle and lock for this thread
        file_handle = self.file_handles[thread_id]
        write_lock = self.write_locks[thread_id]

        # Thread-safe writing to the persistent file handle
        with write_lock:
            for read_string in reads:
                read = pysam.AlignedSegment.fromstring(read_string, header)
                file_handle.write(read)
            file_handle.flush()  # Ensure data is written to disk

    def get_temp_files(self):
        """Get list of all temp files."""
        return list(self.temp_files.values())

    def close_all_files(self):
        """Close all file handles properly to ensure BAM files are complete."""
        for file_handle in self.file_handles.values():
            try:
                file_handle.close()
            except Exception as e:
                logger.warning(f"Error closing file handle: {e}")
        self.file_handles.clear()

    def cleanup(self):
        """Clean up all temp files and directory."""
        try:
            # Close all file handles first
            self.close_all_files()
        except Exception as e:
            logger.warning(f"Error closing file handles: {e}")
            print(f"⚠️  Warning: Error closing file handles: {e}")

        # Remove temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Could not remove temp directory {self.temp_dir}: {e}")
                print(
                    f"⚠️  Warning: Could not remove temp directory {self.temp_dir}: {e}"
                )
                # Try to remove individual files as fallback
                try:
                    for temp_file in self.temp_files.values():
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to cleanup individual temp files: {cleanup_error}"
                    )

        # Clear references to help with garbage collection
        self.temp_files.clear()
        self.file_handles.clear()
        self.write_locks.clear()


# ============================================================================
# WINDOW PROCESSING FUNCTIONS
# ============================================================================


def process_window(window_data: dict[str, Any]) -> dict[str, Any]:
    """
    Process a single genomic window for deduplication.

    Args:
        window_data: Dictionary containing window parameters and configuration

    Returns:
        Dict containing processing results and statistics
    """
    try:
        # Extract parameters
        input_bam = window_data["input_bam"]
        contig = window_data["contig"]
        search_start = window_data["search_start"]
        search_end = window_data["search_end"]
        window_start = window_data["window_start"]
        window_end = window_data["window_end"]
        min_edit_dist_frac = window_data["min_edit_dist_frac"]
        min_frequency_ratio = window_data.get("min_frequency_ratio", 0.1)
        umi_tag = window_data.get("umi_tag")
        umi_sep = window_data.get("umi_sep", "_")
        no_umi = window_data["no_umi"]
        keep_duplicates = window_data["keep_duplicates"]
        best_read_by = window_data["best_read_by"]
        max_pair_dist = window_data["max_pair_dist"]
        fragment_paired = window_data["fragment_paired"]
        fragment_mapped = window_data["fragment_mapped"]
        start_only = window_data["start_only"]
        end_only = window_data["end_only"]
        is_first_window = window_data["is_first_window"]
        window_id = window_data.get("window_id", "unknown")
        thread_id = window_data.get("thread_id", 0)

        # Read BAM: fetch extended region but assign fragments by core window start
        global WORKER_READER
        extended_reads = []
        for read in WORKER_READER.fetch(contig, search_start, search_end):
            extended_reads.append(read)

        if not extended_reads:
            return {
                "window_id": window_id,
                "original_reads": 0,
                "deduplicated_reads": 0,
                "duplicates_removed": 0,
                "deduplication_rate": 0.0,
                "success": True,
                "has_reads": False,
                "reads": [],
                "read_stats": {"properly_paired": 0, "paired": 0, "single_end": 0},
                "thread_id": thread_id,
            }

        # Group extended reads by fragment (query_name)
        reads_by_name = defaultdict(list)
        for r in extended_reads:
            reads_by_name[r.query_name].append(r)

        # Select core fragments whose fragment start is within [window_start, window_end)
        core_names = set()
        for name, group in reads_by_name.items():
            frag_start = min(r.reference_start for r in group)
            if window_start <= frag_start < window_end:
                core_names.add(name)

        # Assemble final read set: for each core fragment, include anchor and its mate (if any),
        # plus any other alignments for the same query (avoid duplicates)
        reads = []
        seen_ids = set()
        for name in core_names:
            group = reads_by_name.get(name, [])
            if not group:
                continue
            # Choose earliest alignment as anchor
            anchor = min(group, key=lambda r: r.reference_start)
            mate = find_mate(anchor, group, max_pair_dist)
            for r in ([anchor] + ([mate] if mate else []) + group):
                obj_id = id(r)
                if obj_id in seen_ids:
                    continue
                seen_ids.add(obj_id)
                reads.append(r)

        # Early exit for empty windows - no need to process further
        if not reads:
            return {
                "window_id": window_id,
                "original_reads": 0,
                "deduplicated_reads": 0,
                "duplicates_removed": 0,
                "deduplication_rate": 0.0,
                "success": True,
                "has_reads": False,
                "reads": [],
                "read_stats": {"properly_paired": 0, "paired": 0, "single_end": 0},
                "thread_id": thread_id,
            }

        # Build fragment objects upfront
        fragments: list[Fragment] = []
        # Assemble fragments by query_name from the reads we selected
        group_by_name = defaultdict(list)
        for r in reads:
            group_by_name[r.query_name].append(r)
        for name, group in group_by_name.items():
            # pick earliest as read1
            r1 = min(group, key=lambda r: r.reference_start)
            mate = find_mate(r1, group, max_pair_dist)
            umi_value = None if no_umi else extract_umi(r1, umi_tag, umi_sep)
            fragments.append(
                Fragment(query_name=name, read1=r1, read2=mate, umi=umi_value)
            )

        # Deduplicate based on method (filtering happens at fragment level inside deduplication functions)
        method = "coordinate" if no_umi else "umi"
        if method == "coordinate":
            # Coordinate-based deduplication (fragment API)
            deduplicated_reads, read_stats = deduplicate_fragments_by_coordinate(
                fragments,
                max_pair_dist,
                start_only,
                end_only,
                best_read_by,
                keep_duplicates,
                fragment_paired,
                fragment_mapped,
            )
        else:
            # UMI-based deduplication (fragment API)
            deduplicated_reads, read_stats = deduplicate_fragments_by_umi(
                fragments,
                max_pair_dist,
                start_only,
                end_only,
                min_edit_dist_frac,
                min_frequency_ratio,
                best_read_by,
                keep_duplicates,
                fragment_paired,
                fragment_mapped,
            )

        # Write directly to per-process shard writer; ensure reference_name present
        global WORKER_WRITER
        # Lazily create writer only when we have output
        if deduplicated_reads and WORKER_WRITER is None:
            WORKER_WRITER = pysam.AlignmentFile(
                WORKER_SHARD_PATH, "wb", header=WORKER_READER.header
            )

        for r in deduplicated_reads:
            WORKER_WRITER.write(r)

        # Calculate statistics
        original_count = len(reads)
        deduplicated_count = len(deduplicated_reads)
        duplicates_removed = original_count - deduplicated_count

        # Calculate duplicates detected (for keep_duplicates mode)
        duplicates_detected = 0
        if keep_duplicates:
            # Count reads marked as duplicates
            duplicates_detected = sum(
                1 for read in deduplicated_reads if read.is_duplicate
            )

        # Calculate appropriate rate based on keep_duplicates setting
        if keep_duplicates:
            deduplication_rate = (
                (duplicates_detected / original_count * 100)
                if original_count > 0
                else 0
            )
        else:
            deduplication_rate = (
                (duplicates_removed / original_count * 100) if original_count > 0 else 0
            )

        return {
            "window_id": window_id,
            "original_reads": original_count,
            "deduplicated_reads": deduplicated_count,
            "duplicates_removed": duplicates_removed,
            "duplicates_detected": duplicates_detected,
            "deduplication_rate": deduplication_rate,
            "success": True,
            "has_reads": len(deduplicated_reads) > 0,
            "reads": [],
            "read_stats": read_stats,
            "thread_id": thread_id,
        }

    except Exception as e:
        logger.error(
            f"Error processing window {window_data.get('window_id', 'unknown')}: {e}"
        )
        return {
            "window_id": window_data.get("window_id", "unknown"),
            "error": str(e),
            "success": False,
            "has_reads": False,
            "reads": [],
            "read_stats": {"properly_paired": 0, "paired": 0, "single_end": 0},
            "thread_id": window_data.get("thread_id", 0),
        }


# ============================================================================
# UNIFIED PROCESSOR CLASS
# ============================================================================


class UnifiedProcessor:
    """
    Unified processor for all deduplication approaches and methods.

    This class provides a unified interface for processing BAM files with
    different deduplication methods (UMI-based and coordinate-based) and
    various configuration options. It handles parallel processing, window
    management, and result aggregation.
    """

    def __init__(
        self,
        bam_file: str,
        output_file: str,
        method: str = "umi",
        umi_tag: str = "UB",
        window_size: int = 1000,
        max_processes: int = None,
        max_pair_dist: int = 2000,
        umi_sep: str = "_",
        min_edit_dist_frac: float = 0.1,
        min_frequency_ratio: float = 0.1,
        keep_duplicates: bool = False,
        best_read_by: str = "avg_base_q",
        fragment_paired: bool = False,
        fragment_mapped: bool = False,
        start_only: bool = False,
        end_only: bool = False,
    ):
        self.bam_file = bam_file
        self.output_file = output_file
        self.method = method
        self.umi_tag = umi_tag
        self.window_size = window_size
        self.max_processes = max_processes or min(os.cpu_count(), 8)
        self.max_pair_dist = max_pair_dist
        self.umi_sep = umi_sep
        self.min_edit_dist_frac = min_edit_dist_frac
        self.min_frequency_ratio = min_frequency_ratio
        self.keep_duplicates = keep_duplicates
        self.best_read_by = best_read_by
        self.fragment_paired = fragment_paired
        self.fragment_mapped = fragment_mapped
        self.start_only = start_only
        self.end_only = end_only
        self.temp_bam_file = None  # Will be set if SAM file was converted

        # Statistics
        self.stats = {
            "total_reads_processed": 0,
            "total_duplicates_removed": 0,
            "total_duplicates_detected": 0,
            "total_windows_processed": 0,
            "total_windows_skipped": 0,
            "total_chromosomes_processed": 0,
            "processing_time": 0,
            "deduplication_rate": 0.0,
            "parallel_time": 0.0,
            "sorting_time": 0.0,
            "properly_paired": 0,
            "paired": 0,
            "single_end": 0,
        }

        # Writer for thread-safe output (will be created with correct thread count)
        self.writer = None

    def process_bam(self) -> bool:
        """Process BAM file using sequential reading and parallel window processing."""
        start_time = time.time()
        # Processing will be shown via progress bars

        try:
            # Create shard directory for per-process writers
            print("📝 Creating per-process shard directory...")
            self.shard_dir = tempfile.mkdtemp(prefix="dedup_shards_")

            # Create reader
            print("📖 Creating BAM reader...")
            reader = BAMReader(
                self.bam_file,
                self.window_size,
                self.max_pair_dist,
                self.start_only,
                self.end_only,
            )

            # Get windows for processing
            windows = list(reader.get_windows())  # Convert to list to know total

            # Process windows in parallel
            self._process_windows_parallel(windows)

            # Clean up temporary BAM file if it was created from SAM (no longer needed)
            if self.temp_bam_file and os.path.exists(self.temp_bam_file):
                print("🧹 Cleaning up temporary BAM file...")
                os.remove(self.temp_bam_file)
                # Also remove the index file
                index_file = self.temp_bam_file + ".bai"
                if os.path.exists(index_file):
                    os.remove(index_file)

            # Final sorting and cleanup
            self._final_sort_and_cleanup()

            # Calculate final statistics
            self._calculate_final_stats(time.time() - start_time)

            # Clean up temporary files before showing completion message
            if hasattr(self, "writer") and self.writer:
                self.writer.cleanup()

            # Create two separate panels: Progress and Statistics
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()

            # Clean, organized output
            console.print()
            # Human-readable duration formatter
            duration_seconds = self.stats["processing_time"]

            def _format_duration(sec: float) -> str:
                if sec < 60:
                    return f"{sec:.2f}s"
                if sec < 3600:
                    minutes = int(sec // 60)
                    seconds = int(round(sec % 60))
                    return f"{minutes}m {seconds}s"
                hours = int(sec // 3600)
                rem = sec % 3600
                minutes = int(rem // 60)
                seconds = int(round(rem % 60))
                return f"{hours}h {minutes}m {seconds}s"

            console.print(
                f"✅ Processing completed successfully! (⏱️ {_format_duration(duration_seconds)})",
                style="bold green",
            )

            # Panel 2: Statistics (table format)
            stats_table = Table(show_header=False, box=None, padding=(0, 1))
            stats_table.add_column(style="bold blue", justify="right", width=25)
            stats_table.add_column(style="white", justify="left")

            stats_table.add_row("Method:", self.method)
            stats_table.add_row("Window size:", f"{self.window_size:,}")
            stats_table.add_row("Threads:", str(self.max_processes or "auto"))
            stats_table.add_row("Best read by:", self.best_read_by)
            stats_table.add_row("", "")  # Empty row for spacing
            stats_table.add_row(
                "Total reads processed:", f"{self.stats['total_reads_processed']:,}"
            )

            # Show appropriate duplicate statistic based on keep_duplicates setting
            if self.keep_duplicates:
                stats_table.add_row(
                    "Duplicates detected:",
                    f"{self.stats['total_duplicates_detected']:,}",
                )
            else:
                stats_table.add_row(
                    "Duplicates removed:", f"{self.stats['total_duplicates_removed']:,}"
                )
            stats_table.add_row(
                "Chromosomes processed:", f"{self.stats['total_chromosomes_processed']}"
            )
            stats_table.add_row(
                "Deduplication rate:", f"{self.stats['deduplication_rate']:.2f}%"
            )
            stats_table.add_row("", "")  # Empty row for spacing
            stats_table.add_row("Read Types:", "")
            stats_table.add_row(
                "  Properly paired:", f"{self.stats['properly_paired']:,}"
            )
            stats_table.add_row("  Paired-end (no mate):", f"{self.stats['paired']:,}")
            stats_table.add_row("  Single-end:", f"{self.stats['single_end']:,}")

            stats_panel = Panel(
                stats_table,
                title="[bold green]📊 PROCESSING STATISTICS[/bold green]",
                border_style="green",
                padding=(1, 2),
            )

            console.print()
            console.print(stats_panel)

            return True

        except KeyboardInterrupt:
            print("\n⚠️  Processing interrupted by user (Ctrl+C)")
            return False
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            # Cleanup is now handled before statistics display
            pass

    def _process_windows_parallel(self, windows: list[dict[str, Any]]):
        """Process windows in parallel with progress tracking."""
        import time

        total_windows = len(windows)
        start_time = time.time()

        with Progress(
            "[progress.description]{task.description}",
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[cyan]{task.fields[windows_processed]}/{task.fields[total_windows]} windows",
            "[blue]{task.fields[chromosomes_processed]} chromosomes",
            "[green]{task.fields[reads_processed]:,} reads",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            expand=False,
        ) as progress:
            window_task = progress.add_task(
                "🔄 [cyan]Processing genomic windows...",
                total=total_windows,
                windows_processed=0,
                reads_processed=0,
                chromosomes_processed=0,
                total_windows=total_windows,
            )

            with ProcessPoolExecutor(
                max_workers=self.max_processes,
                initializer=_worker_initializer,
                initargs=(self.bam_file, self.shard_dir),
            ) as executor:
                # Submit all windows for processing
                future_to_window = {}
                for i, window in enumerate(windows):
                    # Add thread_id to window data
                    window["thread_id"] = i % self.max_processes
                    window.update(
                        {
                            "input_bam": self.bam_file,
                            "method": self.method,
                            "min_edit_dist_frac": self.min_edit_dist_frac,
                            "min_frequency_ratio": self.min_frequency_ratio,
                            "umi_sep": self.umi_sep,
                            "umi_tag": self.umi_tag,
                            "no_umi": (self.method == "coordinate"),
                            "keep_duplicates": self.keep_duplicates,
                            "best_read_by": self.best_read_by,
                            "max_pair_dist": self.max_pair_dist,
                            "fragment_paired": self.fragment_paired,
                            "fragment_mapped": self.fragment_mapped,
                            "start_only": self.start_only,
                            "end_only": self.end_only,
                        }
                    )
                    future = executor.submit(process_window, window)
                    future_to_window[future] = window

                # Process results as they complete
                windows_processed = 0
                total_windows_skipped = 0
                total_reads_processed = 0
                total_duplicates_removed = 0
                total_duplicates_detected = 0
                chromosomes_processed = set()
                total_properly_paired = 0
                total_paired = 0
                total_single_end = 0

                for future in as_completed(future_to_window):
                    result = future.result()
                    windows_processed += 1

                    # Track unique chromosomes
                    window_data = future_to_window[future]
                    chromosomes_processed.add(window_data.get("contig", "unknown"))

                    # Count skipped windows
                    if not result.get("has_reads", False):
                        total_windows_skipped += 1

                    # Count duplicates detected
                    total_duplicates_detected += result.get("duplicates_detected", 0)

                    # No parent-side writing; workers wrote to shard files

                    # Update statistics
                    total_reads_processed += result.get("original_reads", 0)
                    total_duplicates_removed += result.get("duplicates_removed", 0)
                    total_duplicates_detected += result.get("duplicates_detected", 0)

                    # Update read type statistics
                    read_stats = result.get("read_stats", {})
                    total_properly_paired += read_stats.get("properly_paired", 0)
                    total_paired += read_stats.get("paired", 0)
                    total_single_end += read_stats.get("single_end", 0)

                    # Update progress
                    progress.update(
                        window_task,
                        advance=1,
                        windows_processed=windows_processed,
                        reads_processed=total_reads_processed,
                        chromosomes_processed=len(chromosomes_processed),
                    )

                # Store statistics
                self.windows_processed = windows_processed
                self.total_reads_processed = total_reads_processed
                self.total_duplicates_removed = total_duplicates_removed
                self.total_duplicates_detected = total_duplicates_detected
                self.chromosomes_processed = len(chromosomes_processed)
                self.total_properly_paired = total_properly_paired
                self.total_paired = total_paired
                self.total_single_end = total_single_end

                # Print summary of skipped windows
                if total_windows_skipped > 0:
                    print(
                        f"⚡ Skipped {total_windows_skipped} empty windows during processing"
                    )

                # Calculate timing and update progress bar to show completion with timing
                parallel_time = time.time() - start_time
                progress.update(
                    window_task,
                    description=f"✅ Processed {windows_processed}/{total_windows} windows (⏱️ {parallel_time:.2f}s)",
                    completed=windows_processed,
                    windows_processed=windows_processed,
                    reads_processed=total_reads_processed,
                    chromosomes_processed=len(chromosomes_processed),
                )

                # Store timing for statistics
                self.stats["parallel_time"] = parallel_time

                # Submit shutdown tasks to all workers to ensure files are closed
                shutdown_futures = []
                for _ in range(self.max_processes):
                    shutdown_futures.append(executor.submit(_worker_shutdown_task))

                # Wait for all shutdowns to complete
                for future in as_completed(shutdown_futures):
                    try:
                        future.result()
                    except Exception:
                        pass

        # Progress completed - will be shown in final comprehensive panel
        pass

    def _final_sort_and_cleanup(self):
        """Final sorting and cleanup - merge N temp files and sort."""
        import time

        start_time = time.time()
        # Close all file handles before merging to ensure data is flushed
        # Shard writers are closed on worker exit; collect shard files by pid name
        temp_files = []
        if os.path.isdir(self.shard_dir):
            for name in os.listdir(self.shard_dir):
                if name.endswith(".bam"):
                    temp_files.append(os.path.join(self.shard_dir, name))
        if not temp_files:
            print("⚠️  No temp files to process - creating empty output")
            # Create an empty BAM file with header only
            with pysam.AlignmentFile(self.bam_file, "rb") as _hfsrc:
                header = _hfsrc.header
            with pysam.AlignmentFile(
                self.output_file, "wb", header=header
            ) as empty_bam:
                pass  # Write header only
            return

        with Progress(
            "[progress.description]{task.description}",
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            expand=False,
        ) as progress:
            sort_task = progress.add_task(
                "🔄 Sorting and merging temporary files...",
                total=100,
            )

            try:
                # Update progress for merging
                progress.update(
                    sort_task,
                    completed=25,
                    description=f"🔄 Merging {len(temp_files)} temporary files...",
                )

                # Merge all temp files into one using samtools merge (much faster)
                merged_temp_fd, merged_temp_file = tempfile.mkstemp(
                    suffix=".bam", prefix="dedup_merged_"
                )
                os.close(merged_temp_fd)

                # Wait for shards to be complete BAMs (BGZF EOF present)
                def _is_valid_bam(path: str) -> bool:
                    try:
                        with pysam.AlignmentFile(path, "rb"):
                            return True
                    except Exception:
                        return False

                valid_temp_files = []
                deadline = time.time() + 15.0
                while time.time() < deadline:
                    valid_temp_files = []
                    for temp_file in temp_files:
                        if (
                            os.path.exists(temp_file)
                            and os.path.getsize(temp_file) > 0
                            and _is_valid_bam(temp_file)
                        ):
                            valid_temp_files.append(temp_file)
                    # If we have at least one valid shard and no invalid ones remain, proceed
                    if len(valid_temp_files) == len(
                        [
                            p
                            for p in temp_files
                            if os.path.exists(p) and os.path.getsize(p) > 0
                        ]
                    ):
                        break
                    time.sleep(0.1)

                if not valid_temp_files:
                    print(
                        "⚠️  No valid temp files found after waiting - creating empty output"
                    )
                    # Create an empty BAM file with header only
                    with pysam.AlignmentFile(self.bam_file, "rb") as _hfsrc:
                        header = _hfsrc.header
                    with pysam.AlignmentFile(
                        merged_temp_file, "wb", header=header
                    ) as empty_bam:
                        pass  # Write header only
                elif len(valid_temp_files) == 1:
                    # For single file, just copy it
                    import shutil

                    shutil.copy2(valid_temp_files[0], merged_temp_file)
                else:
                    # Use pysam.cat for efficient concatenation
                    pysam.cat(
                        "-o", merged_temp_file, *valid_temp_files, catch_stdout=False
                    )

                # Update progress for sorting
                progress.update(
                    sort_task,
                    completed=50,
                    description=f"🔀 Sorting BAM file with {self.max_processes} threads...",
                )

                # Sort the merged temp file using pysam.sort with memory optimization
                # Use 1GB per thread for faster sorting without excessive memory pressure
                memory_per_thread = "1G"
                pysam.sort(
                    "-@",
                    str(self.max_processes),
                    "-m",
                    memory_per_thread,
                    "-o",
                    self.output_file,
                    merged_temp_file,
                )

                # Update progress for cleanup
                progress.update(
                    sort_task,
                    completed=75,
                    description="🧹 Cleaning up temporary files...",
                )

                # Clean up merged temp file
                if os.path.exists(merged_temp_file):
                    try:
                        os.unlink(merged_temp_file)
                    except Exception:
                        pass

                # Final completion with timing
                sort_time = time.time() - start_time
                progress.update(
                    sort_task,
                    completed=100,
                    description=f"✅ Wrote sorted results to {self.output_file} (⏱️ {sort_time:.2f}s)",
                )

                # Store sorting time
                self.stats["sort_time"] = sort_time
                # Cleanup shard dir
                try:
                    import shutil as _shutil

                    _shutil.rmtree(self.shard_dir)
                except Exception:
                    pass

            except Exception as e:
                print(f"❌ Error during sorting: {e}")
                raise e

    def _calculate_final_stats(self, total_time: float):
        """Calculate final statistics."""
        self.stats["processing_time"] = total_time
        self.stats["total_windows_processed"] = getattr(self, "windows_processed", 0)
        self.stats["total_chromosomes_processed"] = getattr(
            self, "chromosomes_processed", 0
        )
        self.stats["total_reads_processed"] = getattr(self, "total_reads_processed", 0)
        self.stats["total_duplicates_removed"] = getattr(
            self, "total_duplicates_removed", 0
        )
        self.stats["total_duplicates_detected"] = getattr(
            self, "total_duplicates_detected", 0
        )
        self.stats["properly_paired"] = getattr(self, "total_properly_paired", 0)
        self.stats["paired"] = getattr(self, "total_paired", 0)
        self.stats["single_end"] = getattr(self, "total_single_end", 0)

        # Calculate deduplication rate
        if self.stats["total_reads_processed"] > 0:
            if self.keep_duplicates:
                # When keeping duplicates, show detection rate
                self.stats["deduplication_rate"] = (
                    self.stats["total_duplicates_detected"]
                    / self.stats["total_reads_processed"]
                    * 100
                )
            else:
                # When removing duplicates, show removal rate
                self.stats["deduplication_rate"] = (
                    self.stats["total_duplicates_removed"]
                    / self.stats["total_reads_processed"]
                    * 100
                )


def find_mate(read, reads_with_same_name, max_pair_dist):
    """Find the mate of a paired-end read using name-based lookup."""
    for candidate in reads_with_same_name:
        if candidate != read and candidate.query_name == read.query_name:
            # Calculate distance between reads
            distance = abs(candidate.reference_start - read.reference_start)

            if distance <= max_pair_dist:
                return candidate
    return None


# ============================================================================
# DEDUPLICATION FUNCTIONS
# ============================================================================


def deduplicate_fragments_by_umi(
    fragments,
    max_pair_dist=2000,
    start_only=False,
    end_only=False,
    min_edit_dist_frac=0.1,
    min_frequency_ratio=0.1,
    best_read_by="avg_base_q",
    keep_duplicates=False,
    fragment_paired=False,
    fragment_mapped=False,
):
    """
    Deduplicate reads using UMI-based clustering with edit distance.

    This function groups reads by UMI and fragment position, then clusters
    similar UMIs using edit distance to identify duplicates. Uses frequency-aware
    clustering to prevent unrealistic merging of high-frequency UMIs.

    Args:
        reads: List of pysam.AlignedSegment objects
        max_pair_dist: Maximum distance for paired-end reads
        start_only: Use only fragment start position for grouping
        end_only: Use only fragment end position for grouping
        min_edit_dist_frac: Minimum edit distance as fraction of UMI length
        min_frequency_ratio: Minimum ratio of smaller UMI frequency to larger UMI frequency for merging
        best_read_by: Quality criterion for selecting best read ('mapq' or 'avg_base_q')
        keep_duplicates: Whether to keep duplicate reads and mark them
        fragment_paired: Keep only fragments with both reads present
        fragment_mapped: Keep only fragments where both reads are mapped

    Returns:
        Tuple of (deduplicated_reads, read_stats)
    """
    # Compute stats from provided fragments
    properly_paired = sum(1 for f in fragments if f.is_paired and f.read2 is not None)
    single_end = sum(1 for f in fragments if not f.is_paired or f.read2 is None)
    paired = 0 if properly_paired == 0 else 0

    # Apply fragment-level filtering
    if fragment_paired or fragment_mapped:
        filtered_fragments = []
        for fragment in fragments:
            if should_keep_fragment(fragment, fragment_paired, fragment_mapped):
                filtered_fragments.append(fragment)
        fragments = filtered_fragments

    # Group fragments by position first, then cluster UMIs within each position
    fragments_by_position = defaultdict(list)
    for fragment in fragments:
        if start_only and not fragment.is_paired:
            # For single-end reads: use biological start position based on strand
            # Forward strand: 5' end (reference_start) is biological start
            # Reverse strand: 3' end (reference_end) is biological start
            if fragment.read1.is_reverse:
                # Reverse strand: biological start is the 3' end
                bio_start = fragment.read1.reference_end
            else:
                # Forward strand: biological start is the 5' end
                bio_start = fragment.read1.reference_start
            position_key = (bio_start, fragment.read1.is_reverse)
        elif end_only and not fragment.is_paired:
            # For single-end reads: use biological end position
            if fragment.read1.is_reverse:
                # Reverse strand: biological end is the 5' end
                bio_end = fragment.read1.reference_start
            else:
                # Forward strand: biological end is the 3' end
                bio_end = fragment.read1.reference_end
            position_key = (bio_end, fragment.read1.is_reverse)
        else:
            # For UMI-based deduplication: group by start position and strand only
            # This allows UMI clustering within the same genomic region
            if fragment.is_paired:
                # For paired-end reads: use fragment start position and strand
                frag_start, _, is_reverse = fragment.get_fragment_position()
                position_key = (frag_start, is_reverse)
            else:
                # For single-end reads: use biological start position and strand
                bio_start = fragment.get_biological_position(
                    start_only=True, end_only=False
                )
                position_key = (bio_start, fragment.read1.is_reverse)

        fragments_by_position[position_key].append(fragment)

    # Apply edit distance clustering within each position
    deduplicated_reads = []
    for position, fragments_at_position in fragments_by_position.items():
        if len(fragments_at_position) > 1:
            # Group by UMI first (always)
            fragments_by_umi = defaultdict(list)
            for fragment in fragments_at_position:
                fragments_by_umi[fragment.umi].append(fragment)

            if min_edit_dist_frac > 0:
                # Fast path: if every UMI is unique (one fragment per UMI), skip clustering
                if sum(len(v) for v in fragments_by_umi.values()) == len(fragments_by_umi):
                    clustered_fragment_groups = [[frag] for frag in fragments_at_position]
                else:
                    # Apply frequency-aware edit distance clustering across UMIs
                    clustered_fragment_groups = (
                        cluster_umis_by_edit_distance_frequency_aware(
                            fragments_by_umi, min_edit_dist_frac, min_frequency_ratio
                        )
                    )
            else:
                # No edit distance clustering - exact UMI groups
                clustered_fragment_groups = list(fragments_by_umi.values())
        else:
            # Single fragment - no clustering needed
            clustered_fragment_groups = [fragments_at_position]

        # Process each cluster
        for fragment_group in clustered_fragment_groups:
            if len(fragment_group) == 1:
                # Single fragment - add cluster tags
                fragment = fragment_group[0]
                cluster_name = fragment.get_cluster_name("umi", start_only, end_only)
                fragment.read1.set_tag("cn", cluster_name)
                fragment.read1.set_tag("cs", 1)
                deduplicated_reads.append(fragment.read1)
                if fragment.read2:
                    fragment.read2.set_tag("cn", cluster_name)
                    fragment.read2.set_tag("cs", 1)
                    deduplicated_reads.append(fragment.read2)
            else:
                # Multiple fragments - handle based on keep_duplicates setting
                if keep_duplicates:
                    # Keep all fragments but mark non-best as duplicates
                    best_fragment = max(
                        fragment_group,
                        key=lambda f: calculate_fragment_quality_score(f, best_read_by),
                    )
                    cluster_name = best_fragment.get_cluster_name(
                        "umi", start_only, end_only
                    )

                    for fragment in fragment_group:
                        is_best = fragment == best_fragment
                        fragment.read1.set_tag("cn", cluster_name)
                        fragment.read1.set_tag("cs", len(fragment_group))
                        if not is_best:
                            fragment.read1.is_duplicate = True
                        deduplicated_reads.append(fragment.read1)

                        if fragment.read2:
                            fragment.read2.set_tag("cn", cluster_name)
                            fragment.read2.set_tag("cs", len(fragment_group))
                            if not is_best:
                                fragment.read2.is_duplicate = True
                            deduplicated_reads.append(fragment.read2)
                else:
                    # Select best fragment only
                    best_fragment = max(
                        fragment_group,
                        key=lambda f: calculate_fragment_quality_score(f, best_read_by),
                    )
                    cluster_name = best_fragment.get_cluster_name(
                        "umi", start_only, end_only
                    )
                    best_fragment.read1.set_tag("cn", cluster_name)
                    best_fragment.read1.set_tag("cs", len(fragment_group))
                    deduplicated_reads.append(best_fragment.read1)
                    if best_fragment.read2:
                        best_fragment.read2.set_tag("cn", cluster_name)
                        best_fragment.read2.set_tag("cs", len(fragment_group))
                        deduplicated_reads.append(best_fragment.read2)

    # Return reads and statistics
    stats = {
        "properly_paired": properly_paired,
        "paired": paired,
        "single_end": single_end,
    }
    return deduplicated_reads, stats


def deduplicate_fragments_by_coordinate(
    fragments,
    max_pair_dist=2000,
    start_only=False,
    end_only=False,
    best_read_by="avg_base_q",
    keep_duplicates=False,
    fragment_paired=False,
    fragment_mapped=False,
):
    """
    Deduplicate reads using coordinate-based clustering.

    This function groups reads by fragment position and selects the best
    read from each group based on quality criteria.

    Args:
        reads: List of pysam.AlignedSegment objects
        max_pair_dist: Maximum distance for paired-end reads
        start_only: Use only fragment start position for grouping
        end_only: Use only fragment end position for grouping
        best_read_by: Quality criterion for selecting best read ('mapq' or 'avg_base_q')
        fragment_paired: Keep only fragments with both reads present
        fragment_mapped: Keep only fragments where both reads are mapped

    Returns:
        Tuple of (deduplicated_reads, read_stats)
    """
    if not fragments:
        return [], {"properly_paired": 0, "paired": 0, "single_end": 0}

    # Track read type statistics
    properly_paired = sum(1 for f in fragments if f.is_paired and f.read2 is not None)
    single_end = sum(1 for f in fragments if not f.is_paired or f.read2 is None)
    paired = 0 if properly_paired == 0 else 0

    # Process single-end reads first
    # fragments provided: skip building from reads

    # Apply fragment-level filtering
    if fragment_paired or fragment_mapped:
        filtered_fragments = []
        for fragment in fragments:
            if should_keep_fragment(fragment, fragment_paired, fragment_mapped):
                filtered_fragments.append(fragment)
        fragments = filtered_fragments

    # Group fragments by position based on options
    fragments_by_position = defaultdict(list)
    for fragment in fragments:
        # Determine position key based on options
        if start_only and not fragment.is_paired:
            # For single-end fragments: use biological start position
            if fragment.read1.is_reverse:
                # Reverse strand: biological start is the 3' end
                bio_start = fragment.read1.reference_end
            else:
                # Forward strand: biological start is the 5' end
                bio_start = fragment.read1.reference_start
            pos = (bio_start, fragment.read1.is_reverse)
        elif end_only and not fragment.is_paired:
            # For single-end fragments: use biological end position
            if fragment.read1.is_reverse:
                # Reverse strand: biological end is the 5' end
                bio_end = fragment.read1.reference_start
            else:
                # Forward strand: biological end is the 3' end
                bio_end = fragment.read1.reference_end
            pos = (bio_end, fragment.read1.is_reverse)
        else:
            # For paired-end fragments or default: use full fragment position
            frag_pos = fragment.get_fragment_position()
            pos = frag_pos  # frag_pos is already (start, end, strand)

        fragments_by_position[pos].append(fragment)

    # Keep best fragment from each position group and add cluster tags
    deduplicated_reads = []
    for pos, fragment_group in fragments_by_position.items():
        if len(fragment_group) == 1:
            # Single fragment - add cluster tags
            fragment = fragment_group[0]
            cluster_name = fragment.get_cluster_name("coordinate", start_only, end_only)
            fragment.read1.set_tag("cn", cluster_name)
            fragment.read1.set_tag("cs", 1)
            deduplicated_reads.append(fragment.read1)
            if fragment.read2:
                fragment.read2.set_tag("cn", cluster_name)
                fragment.read2.set_tag("cs", 1)
                deduplicated_reads.append(fragment.read2)
        else:
            # Multiple fragments - handle based on keep_duplicates setting
            if keep_duplicates:
                # Keep all fragments but mark non-best as duplicates
                best_fragment = max(
                    fragment_group,
                    key=lambda f: calculate_fragment_quality_score(f, best_read_by),
                )
                cluster_name = best_fragment.get_cluster_name(
                    "coordinate", start_only, end_only
                )

                for fragment in fragment_group:
                    is_best = fragment == best_fragment
                    fragment.read1.set_tag("cn", cluster_name)
                    fragment.read1.set_tag("cs", len(fragment_group))
                    if not is_best:
                        fragment.read1.is_duplicate = True
                    deduplicated_reads.append(fragment.read1)

                    if fragment.read2:
                        fragment.read2.set_tag("cn", cluster_name)
                        fragment.read2.set_tag("cs", len(fragment_group))
                        if not is_best:
                            fragment.read2.is_duplicate = True
                        deduplicated_reads.append(fragment.read2)
            else:
                # Select best fragment only
                best_fragment = max(
                    fragment_group,
                    key=lambda f: calculate_fragment_quality_score(f, best_read_by),
                )
                cluster_name = best_fragment.get_cluster_name(
                    "coordinate", start_only, end_only
                )
                best_fragment.read1.set_tag("cn", cluster_name)
                best_fragment.read1.set_tag("cs", len(fragment_group))
                deduplicated_reads.append(best_fragment.read1)
                if best_fragment.read2:
                    best_fragment.read2.set_tag("cn", cluster_name)
                    best_fragment.read2.set_tag("cs", len(fragment_group))
                    deduplicated_reads.append(best_fragment.read2)

    # Return deduplicated reads and statistics
    stats = {
        "properly_paired": properly_paired,
        "paired": paired,
        "single_end": single_end,
    }
    return deduplicated_reads, stats


def should_keep_fragment(fragment, fragment_paired, fragment_mapped):
    """Determine if a fragment should be kept based on fragment-level filtering options."""
    # fragment_paired: Keep only fragments with both reads present
    if fragment_paired and fragment.read2 is None:
        return False

    # fragment_mapped: Keep only fragments where both reads are mapped
    if fragment_mapped:
        if fragment.read1 and fragment.read1.is_unmapped:
            return False
        if fragment.read2 and fragment.read2.is_unmapped:
            return False

    return True


# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================


def process_bam(
    input_bam: str,
    output_bam: str,
    method: str = "umi",
    umi_tag: str = "UB",
    window_size: int = 1000,
    max_processes: int = None,
    max_pair_dist: int = 2000,
    umi_sep: str = "_",
    min_edit_dist_frac: float = 0.1,
    min_frequency_ratio: float = 0.1,
    keep_duplicates: bool = False,
    best_read_by: str = "avg_base_q",
    fragment_paired: bool = False,
    fragment_mapped: bool = False,
    start_only: bool = False,
    end_only: bool = False,
) -> bool:
    """
    Process BAM file using sequential reading and parallel window processing.

    This function provides a unified interface for BAM deduplication with both
    UMI-based and coordinate-based methods. It includes comprehensive input
    validation, error handling, and progress reporting.

    Args:
        input_bam: Path to input BAM file
        output_bam: Path to output BAM file
        method: Deduplication method ('umi' or 'coordinate')
        umi_tag: UMI tag name for BAM tags (default: 'UB')
        window_size: Genomic window size for processing (default: 1000)
        max_processes: Maximum number of parallel processes (default: auto)
        max_pair_dist: Maximum distance for paired-end reads (default: 2000)
        umi_sep: Separator for extracting UMIs from read names (default: '_')
        min_edit_dist_frac: Minimum edit distance as fraction of UMI length (default: 0.1)
        min_frequency_ratio: Minimum frequency ratio for UMI merging (default: 0.1)
        keep_duplicates: Whether to keep duplicate reads and mark them (default: False)
        best_read_by: Quality criterion for selecting best read (default: 'avg_base_q')
        fragment_paired: Keep only fragments with both reads present (default: False)
        fragment_mapped: Keep only fragments where both reads are mapped (default: False)
        start_only: Use only start position for grouping (default: False)
        end_only: Use only end position for grouping (default: False)

    Returns:
        bool: True if processing succeeded, False otherwise

    Raises:
        ValueError: If input parameters are invalid
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If processing fails
    """
    import signal
    import sys

    # Validate input parameters
    if not os.path.exists(input_bam):
        print(f"❌ Input file '{input_bam}' does not exist!")
        return False

    if not input_bam.endswith((".bam", ".sam")):
        print(f"❌ Input file '{input_bam}' is not a BAM/SAM file!")
        return False

    if not output_bam.endswith((".bam", ".sam")):
        print(f"❌ Output file '{output_bam}' must be a BAM/SAM file!")
        return False

    # Handle SAM files by converting to temporary BAM
    temp_bam_file = None
    if input_bam.endswith(".sam"):
        import tempfile

        print("📝 Converting SAM to temporary BAM file...")
        temp_bam_file = tempfile.mktemp(suffix=".bam")

        try:
            # Convert SAM to BAM
            with pysam.AlignmentFile(input_bam, "r") as sam_file:
                with pysam.AlignmentFile(
                    temp_bam_file, "wb", header=sam_file.header
                ) as bam_file:
                    for read in sam_file:
                        bam_file.write(read)

            # Create index for the temporary BAM file using threads
            pysam.index(temp_bam_file, "-@", str(max_processes or 1))
            input_bam = temp_bam_file  # Use the temporary BAM file for processing
            print("✅ SAM file converted to temporary BAM and indexed")
        except Exception as e:
            print(f"❌ Error converting SAM to BAM: {e}")
            return False

    # Validate method parameter
    valid_methods = ["umi", "coordinate"]
    if method not in valid_methods:
        print(
            f"❌ Invalid method '{method}'. Valid methods are: {', '.join(valid_methods)}"
        )
        return False

    # Validate quality criteria
    valid_quality_criteria = ["mapq", "avg_base_q"]
    if best_read_by not in valid_quality_criteria:
        print(
            f"❌ Invalid quality criteria '{best_read_by}'. Valid criteria are: {', '.join(valid_quality_criteria)}"
        )
        return False

    # Validate numeric parameters
    if window_size <= 0:
        print(f"❌ Window size must be positive, got: {window_size}")
        return False

    if max_pair_dist <= 0:
        print(f"❌ Max pair distance must be positive, got: {max_pair_dist}")
        return False

    if not 0 <= min_edit_dist_frac <= 1:
        print(
            f"❌ Min edit distance fraction must be between 0 and 1, got: {min_edit_dist_frac}"
        )
        return False

    if not 0 <= min_frequency_ratio <= 1:
        print(
            f"❌ Min frequency ratio must be between 0 and 1, got: {min_frequency_ratio}"
        )
        return False

    processor = None

    def signal_handler(sig, frame):
        print("\n⚠️  Processing interrupted by user (Ctrl+C)")
        if processor and hasattr(processor, "writer") and processor.writer:
            print("🧹 Cleaning up temporary files...")
            processor.writer.cleanup()
        sys.exit(1)

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        processor = UnifiedProcessor(
            bam_file=input_bam,
            output_file=output_bam,
            method=method,
            umi_tag=umi_tag,
            window_size=window_size,
            max_processes=max_processes,
            max_pair_dist=max_pair_dist,
            umi_sep=umi_sep,
            min_edit_dist_frac=min_edit_dist_frac,
            min_frequency_ratio=min_frequency_ratio,
            keep_duplicates=keep_duplicates,
            best_read_by=best_read_by,
            fragment_paired=fragment_paired,
            fragment_mapped=fragment_mapped,
            start_only=start_only,
            end_only=end_only,
        )

        # Set temp BAM file if it was created from SAM
        if temp_bam_file:
            processor.temp_bam_file = temp_bam_file

        result = processor.process_bam()

        return result
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user (Ctrl+C)")
        if processor and hasattr(processor, "writer") and processor.writer:
            print("🧹 Cleaning up temporary files...")
            processor.writer.cleanup()
        # Clean up temporary BAM file
        if temp_bam_file and os.path.exists(temp_bam_file):
            print("🧹 Cleaning up temporary BAM file...")
            os.remove(temp_bam_file)
            index_file = temp_bam_file + ".bai"
            if os.path.exists(index_file):
                os.remove(index_file)
        return False
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"❌ Processing failed: {e}")
        if processor and hasattr(processor, "writer") and processor.writer:
            print("🧹 Cleaning up temporary files...")
            processor.writer.cleanup()
        # Clean up temporary BAM file
        if temp_bam_file and os.path.exists(temp_bam_file):
            print("🧹 Cleaning up temporary BAM file...")
            os.remove(temp_bam_file)
            index_file = temp_bam_file + ".bai"
            if os.path.exists(index_file):
                os.remove(index_file)
        return False
