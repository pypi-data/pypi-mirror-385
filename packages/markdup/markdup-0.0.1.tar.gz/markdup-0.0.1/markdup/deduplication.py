#!/usr/bin/env python3
"""
Unified Deduplication Logic - Clean & Simple Architecture

This module provides a clean, unified approach to BAM deduplication with:
- Single reader object with 3 reading strategies
- Thread-safe writer object for shared temp file
- Single processor for both UMI and coordinate methods
- Minimal code duplication

Author: Ye Chang
Date: 2025-01-27
"""

import os
import tempfile
import threading
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, Iterator, List

import pysam
from rich.progress import Progress, TimeElapsedColumn, TimeRemainingColumn

# Import utility functions
from .utils import (
    Fragment,
    calculate_average_base_quality,
    cluster_umis_by_edit_distance_frequency_aware,
    get_read_position,
    extract_umi_from_query_name,
)


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
        approach: str = "sequential",
        start_only: bool = False,
        end_only: bool = False,
    ):
        self.bam_file = bam_file
        self.window_size = window_size
        self.max_pair_dist = max_pair_dist
        self.approach = approach
        self.start_only = start_only
        self.end_only = end_only
        self._windows = None
        self._header = None
        self._chromosomes_with_reads = None

    def get_header(self):
        """Get BAM header."""
        if self._header is None:
            with pysam.AlignmentFile(self.bam_file, "rb") as f:
                self._header = f.header
        return self._header

    def _check_region_has_reads(self, f, chromosome: str, start: int, end: int) -> bool:
        """Check if a genomic region contains any reads."""
        for _ in f.fetch(chromosome, start, end):
            return True
        return False

    def get_windows(self) -> Iterator[Dict[str, Any]]:
        """Get all windows for processing based on approach."""
        if self.approach == "sequential":
            yield from self._create_sequential_windows()
        elif self.approach == "fetch":
            yield from self._create_fetch_windows()
        elif self.approach == "whole":
            yield from self._create_whole_windows()
        else:
            raise ValueError(f"Unknown approach: {self.approach}")

    def _create_sequential_windows(self) -> Iterator[Dict[str, Any]]:
        """Create genomic windows for sequential processing with proper overlapping."""
        import time

        from rich.progress import Progress, TimeElapsedColumn, TimeRemainingColumn

        window_id = 0
        total_windows_created = 0
        total_windows_skipped = 0
        start_time = time.time()

        header = self.get_header()
        all_chromosomes = list(header.references)

        # Create progress bar for window creation
        with Progress(
            "[green]{task.description}",
            "[green]{task.fields[windows_created]} windows created",
            "[green]{task.fields[windows_skipped]} empty windows skipped",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            expand=False,
        ) as progress:
            window_task = progress.add_task(
                "🗂️ Creating genomic windows...",
                total=len(all_chromosomes),
                windows_created=0,
                windows_skipped=0,
            )

            # Creating genomic windows with progress bar
            with pysam.AlignmentFile(self.bam_file, "rb") as f:
                for chromosome in all_chromosomes:
                    contig_len = header.get_reference_length(chromosome)
                    if contig_len is None:
                        continue

                    if contig_len <= self.window_size:
                        # Short chromosome - use whole chromosome
                        if self._check_region_has_reads(f, chromosome, 0, contig_len):
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
                            total_windows_skipped += 1
                    else:
                        # Long chromosome - split into overlapping windows
                        # Step by window_size, with search region extended by max_pair_dist
                        for i in range(0, contig_len, self.window_size):
                            window_start = i
                            window_end = min(i + self.window_size, contig_len)
                            search_start = max(0, window_start)
                            search_end = min(
                                contig_len, window_end + self.max_pair_dist
                            )

                            # Fast check if window has reads using fetch
                            if self._check_region_has_reads(
                                f, chromosome, search_start, search_end
                            ):
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
                            else:
                                total_windows_skipped += 1

                    # Update progress
                    progress.update(
                        window_task,
                        advance=1,
                        windows_created=total_windows_created,
                        windows_skipped=total_windows_skipped,
                    )

            # Update progress bar to show completion with timing
            window_creation_time = time.time() - start_time
            progress.update(
                window_task,
                description=f"✅ Created {total_windows_created} windows, skipped {total_windows_skipped} empty windows (⏱️ {window_creation_time:.2f}s)",
                completed=len(all_chromosomes),
                windows_created=total_windows_created,
                windows_skipped=total_windows_skipped,
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
    ) -> Dict[str, Any]:
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

    def write_reads(self, reads: List[str], header: Any, thread_id: int = None):
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
            except Exception:
                pass
        self.file_handles.clear()

    def cleanup(self):
        """Clean up all temp files and directory."""
        try:
            # Close all file handles first
            self.close_all_files()
        except Exception as e:
            print(f"⚠️  Warning: Error closing file handles: {e}")

        # Remove temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(
                    f"⚠️  Warning: Could not remove temp directory {self.temp_dir}: {e}"
                )
                # Try to remove individual files as fallback
                try:
                    for temp_file in self.temp_files.values():
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                except Exception:
                    pass


# ============================================================================
# WINDOW PROCESSING FUNCTIONS
# ============================================================================

def process_window(window_data: Dict[str, Any]) -> Dict[str, Any]:
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
        umi_sep = window_data["umi_sep"]
        no_umi = window_data["no_umi"]
        keep_duplicates = window_data["keep_duplicates"]
        best_read_by = window_data["best_read_by"]
        max_pair_dist = window_data["max_pair_dist"]
        remove_unpaired = window_data["remove_unpaired"]
        remove_chimeric = window_data["remove_chimeric"]
        remove_unmapped = window_data["remove_unmapped"]
        start_only = window_data["start_only"]
        end_only = window_data["end_only"]
        is_first_window = window_data["is_first_window"]
        window_id = window_data.get("window_id", "unknown")

        # Read BAM file and extract reads for this window
        reads = []
        with pysam.AlignmentFile(input_bam, "rb") as f:
            for read in f.fetch(contig, search_start, search_end):
                if (
                    read.reference_start >= window_start
                    and read.reference_start < window_end
                ):
                    reads.append(read)

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
            }

        # Apply filtering
        filtered_reads = []
        for read in reads:
            if should_keep_read(
                read, remove_unpaired, remove_chimeric, remove_unmapped
            ):
                filtered_reads.append(read)

        # Deduplicate based on method
        method = "coordinate" if no_umi else "umi"
        if method == "coordinate":
            # Coordinate-based deduplication
            deduplicated_reads, read_stats = deduplicate_reads_by_coordinate(
                filtered_reads, max_pair_dist, start_only, end_only, best_read_by, keep_duplicates
            )
        else:
            # UMI-based deduplication
            deduplicated_reads, read_stats = deduplicate_reads_by_umi(
                filtered_reads,
                max_pair_dist,
                start_only,
                end_only,
                min_edit_dist_frac,
                min_frequency_ratio,
                best_read_by,
                keep_duplicates,
            )

        # Convert reads to strings for thread-safe writing
        read_strings = []
        for read in deduplicated_reads:
            read_strings.append(read.to_string())

        # Calculate statistics
        original_count = len(filtered_reads)
        deduplicated_count = len(deduplicated_reads)
        duplicates_removed = original_count - deduplicated_count
        
        # Calculate duplicates detected (for keep_duplicates mode)
        duplicates_detected = 0
        if keep_duplicates:
            # Count reads marked as duplicates
            duplicates_detected = sum(1 for read in deduplicated_reads if read.is_duplicate)
        
        # Calculate appropriate rate based on keep_duplicates setting
        if keep_duplicates:
            deduplication_rate = (
                (duplicates_detected / original_count * 100) if original_count > 0 else 0
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
            "has_reads": len(read_strings) > 0,
            "reads": read_strings,
            "read_stats": read_stats,
        }

    except Exception as e:
        return {
            "window_id": window_data.get("window_id", "unknown"),
            "error": str(e),
            "success": False,
            "has_reads": False,
            "reads": [],
            "read_stats": {"properly_paired": 0, "paired": 0, "single_end": 0},
        }




def _write_reads_to_file(reads: List[str], temp_file_path: str, header: Any):
    """Write reads to a specific temp file (called from worker process)."""
    if not reads or not temp_file_path:
        return

    # Read existing reads from temp file
    existing_reads = []
    if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
        try:
            with pysam.AlignmentFile(temp_file_path, "rb") as temp_file:
                for read in temp_file:
                    existing_reads.append(read)
        except Exception:
            existing_reads = []

    # Write all reads (existing + new) to temp file
    with pysam.AlignmentFile(temp_file_path, "wb", header=header) as temp_file:
        # Write existing reads
        for read in existing_reads:
            temp_file.write(read)

        # Write new reads
        for read_string in reads:
            read = pysam.AlignedSegment.fromstring(read_string, header)
            temp_file.write(read)


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
        remove_unpaired: bool = False,
        remove_chimeric: bool = False,
        remove_unmapped: bool = False,
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
        self.remove_unpaired = remove_unpaired
        self.remove_chimeric = remove_chimeric
        self.remove_unmapped = remove_unmapped
        self.start_only = start_only
        self.end_only = end_only

        # Statistics
        self.stats = {
            "total_reads_processed": 0,
            "total_duplicates_removed": 0,
            "total_windows_processed": 0,
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

        # Global processed reads tracker to avoid duplication across overlapping windows
        self.processed_reads_global = set()

        # Auto-detect UMI method if needed
        if method == "umi":
            self.method = self._detect_umi_method(umi_sep, umi_tag)
        else:
            self.method = method

    def _detect_umi_method(self, umi_sep: str, umi_tag: str) -> str:
        """Auto-detect if UMI exists in query names or tags."""
        try:
            with pysam.AlignmentFile(self.bam_file, "rb") as f:
                reads_checked = 0
                umi_in_qname_count = 0
                umi_in_tag_count = 0

                for read in f:
                    if reads_checked >= 10:
                        break
                    reads_checked += 1

                    # Check if UMI exists in query name (after umi_sep)
                    if umi_sep in read.query_name:
                        potential_umi = read.query_name.split(umi_sep)[-1]
                        # Check if potential UMI contains only valid bases
                        if all(base in "ATGC" for base in potential_umi.upper()):
                            umi_in_qname_count += 1

                    # Check if UMI exists in tags
                    if read.has_tag(umi_tag):
                        umi_in_tag_count += 1

                # Decision logic
                if umi_in_qname_count >= 8:  # 80% of reads have UMI in query name
                    print(f"🔍 Detected UMI in query names (separator: '{umi_sep}')")
                    return "umi"
                if umi_in_tag_count >= 8:  # 80% of reads have UMI in tags
                    print(f"🔍 Detected UMI in BAM tags (tag: '{umi_tag}')")
                    return "umi"
                print("🔍 No UMI detected, using coordinate-based deduplication")
                return "coordinate"

        except Exception as e:
            print(f"⚠️  Error detecting UMI: {e}, using coordinate-based deduplication")
            return "coordinate"

    def process_bam(self) -> bool:
        """Process BAM file using sequential reading and parallel window processing."""
        start_time = time.time()
        # Processing will be shown via progress bars

        try:
            # Create writer with correct thread count
            print("📝 Creating thread-safe writer...")
            self.writer = ThreadSafeWriter(self.bam_file, self.max_processes)

            # Create reader for sequential approach
            print("📖 Creating BAM reader...")
            reader = BAMReader(
                self.bam_file,
                self.window_size,
                self.max_pair_dist,
                "sequential",
                self.start_only,
                self.end_only,
            )

            # Get windows for processing
            windows = list(reader.get_windows())  # Convert to list to know total

            # Process windows in parallel
            self._process_windows_parallel(windows)

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
            console.print("✅ Processing completed successfully!", style="bold green")
            console.print(f"📁 Input file: {self.bam_file}", style="blue")
            console.print(f"📁 Output file: {self.output_file}", style="blue")
            console.print(
                f"⏱️ Processing time: {self.stats['processing_time']:.2f}s", style="blue"
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
                    "Duplicates detected:", f"{self.stats['total_duplicates_detected']:,}"
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

    def _process_windows_parallel(self, windows: List[Dict[str, Any]]):
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

            with ProcessPoolExecutor(max_workers=self.max_processes) as executor:
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
                            "no_umi": (self.method == "coordinate"),
                            "keep_duplicates": self.keep_duplicates,
                            "best_read_by": self.best_read_by,
                            "max_pair_dist": self.max_pair_dist,
                            "remove_unpaired": self.remove_unpaired,
                            "remove_chimeric": self.remove_chimeric,
                            "remove_unmapped": self.remove_unmapped,
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

                    # Write processed reads to appropriate temp file using persistent file handle
                    if result.get("has_reads", False) and result.get("reads"):
                        # Get header once instead of opening BAM file repeatedly
                        if not hasattr(self, "_cached_header"):
                            with pysam.AlignmentFile(self.bam_file, "rb") as f:
                                self._cached_header = f.header

                        thread_id = result.get("thread_id", 0)
                        self.writer.write_reads(
                            result["reads"], self._cached_header, thread_id
                        )

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

        # Progress completed - will be shown in final comprehensive panel
        pass

    def _final_sort_and_cleanup(self):
        """Final sorting and cleanup - merge N temp files and sort."""
        import time

        start_time = time.time()
        # Close all file handles before merging to ensure data is flushed
        self.writer.close_all_files()

        temp_files = self.writer.get_temp_files()
        if not temp_files:
            print("⚠️  No temp files to process")
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

                # Filter out empty or non-existent temp files
                valid_temp_files = []
                for temp_file in temp_files:
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        valid_temp_files.append(temp_file)

                if not valid_temp_files:
                    print("⚠️  No valid temp files to merge")
                    return

                # Use samtools cat for efficient concatenation (faster than merge)
                # cat is better for concatenating BAM files, merge is for merging overlapping regions
                try:
                    if len(valid_temp_files) == 1:
                        # For single file, just copy it
                        import shutil

                        shutil.copy2(valid_temp_files[0], merged_temp_file)
                    else:
                        # Use samtools cat for multiple files (faster than merge)
                        # First, create a header file
                        header_file = tempfile.mktemp(suffix=".sam")
                        try:
                            with open(header_file, "w") as hf:
                                hf.write(str(self.writer.header))

                            pysam.cat(
                                "-h",
                                header_file,
                                "-o",
                                merged_temp_file,
                                *valid_temp_files,
                                catch_stdout=False,
                            )
                        finally:
                            # Clean up header file
                            if os.path.exists(header_file):
                                os.unlink(header_file)
                except Exception as e:
                    print(
                        f"⚠️  Error using samtools cat, falling back to Python merging: {e}"
                    )
                    # Fallback to Python merging if samtools fails
                    with pysam.AlignmentFile(
                        merged_temp_file, "wb", header=self.writer.header
                    ) as merged_file:
                        for i, temp_file in enumerate(valid_temp_files):
                            try:
                                with pysam.AlignmentFile(temp_file, "rb") as temp_bam:
                                    for read in temp_bam:
                                        merged_file.write(read)
                            except Exception as e:
                                print(
                                    f"⚠️  Skipping corrupted temp file {temp_file}: {e}"
                                )
                                continue

                # Update progress for sorting
                progress.update(
                    sort_task,
                    completed=50,
                    description=f"🔀 Sorting BAM file with {self.max_processes} threads...",
                )

                # Sort the merged temp file using pysam.sort
                pysam.sort(
                    "-@",
                    str(self.max_processes),
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

    def _print_final_stats(self):
        """Print final processing statistics using rich panels."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Create statistics table
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column(style="bold blue", justify="right")
        stats_table.add_column(style="white", justify="left")

        stats_table.add_row(
            "Total reads processed:", f"{self.stats['total_reads_processed']:,}"
        )
        
        # Show appropriate duplicate statistic based on keep_duplicates setting
        if self.keep_duplicates:
            stats_table.add_row(
                "Duplicates detected:", f"{self.stats['total_duplicates_detected']:,}"
            )
        else:
            stats_table.add_row(
                "Duplicates removed:", f"{self.stats['total_duplicates_removed']:,}"
            )
        stats_table.add_row(
            "Chromosomes processed:", f"{self.stats['total_chromosomes_processed']}"
        )
        stats_table.add_row(
            "Windows processed:", f"{self.stats['total_windows_processed']}"
        )
        stats_table.add_row(
            "Deduplication rate:", f"{self.stats['deduplication_rate']:.2f}%"
        )
        stats_table.add_row("", "")  # Empty row for spacing
        stats_table.add_row("Read Types:", "")
        stats_table.add_row("  Properly paired:", f"{self.stats['properly_paired']:,}")
        stats_table.add_row("  Paired-end (no mate):", f"{self.stats['paired']:,}")
        stats_table.add_row("  Single-end:", f"{self.stats['single_end']:,}")

        # Create the statistics panel
        stats_panel = Panel(
            stats_table,
            title="[bold green]📊 FINAL PROCESSING STATISTICS[/bold green]",
            border_style="green",
            padding=(1, 2),
        )

        console.print()
        console.print(stats_panel)


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

def deduplicate_reads_by_umi(
    reads,
    max_pair_dist=2000,
    start_only=False,
    end_only=False,
    min_edit_dist_frac=0.1,
    min_frequency_ratio=0.1,
    best_read_by="avg_base_q",
    keep_duplicates=False,
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
        
    Returns:
        Tuple of (deduplicated_reads, read_stats)
    """
    if not reads:
        return reads, {"properly_paired": 0, "paired": 0, "single_end": 0}

    # Track read type statistics
    properly_paired = 0
    paired = 0
    single_end = 0

    # Group reads by position first (like in process_genomic_chunk)
    reads_by_position = defaultdict(list)
    for read in reads:
        if not read.is_unmapped:
            read_position = get_read_position(read)
            reads_by_position[read_position].append(read)

    # Create a lookup dictionary for faster mate finding
    reads_by_name = defaultdict(list)
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            reads_by_name[read.query_name].append(read)

    # Create fragments from reads
    fragments = []
    processed_reads = set()

    # Process single-end reads first
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            if not read.is_paired and read.query_name not in processed_reads:
                # Single-end read
                fragment = Fragment(
                    query_name=read.query_name,
                    read1=read,
                    umi=extract_umi_from_query_name(read.query_name, "_"),
                )
                fragments.append(fragment)
                processed_reads.add(read.query_name)
                single_end += 1

    # Process paired-end reads with optimized mate finding
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            if read.is_paired and read.query_name not in processed_reads:
                # Find the mate using the lookup dictionary
                mate_read = find_mate(
                    read, reads_by_name[read.query_name], max_pair_dist
                )

                if mate_read:
                    # Found a pair - create paired fragment
                    fragment = Fragment(
                        query_name=read.query_name,
                        read1=read,
                        read2=mate_read,
                        umi=extract_umi_from_query_name(read.query_name, "_"),
                    )
                    fragments.append(fragment)
                    processed_reads.add(read.query_name)
                    properly_paired += 1
                else:
                    # No mate found - treat as single-end
                    fragment = Fragment(
                        query_name=read.query_name,
                        read1=read,
                        umi=extract_umi_from_query_name(read.query_name, "_"),
                    )
                    fragments.append(fragment)
                    processed_reads.add(read.query_name)
                    paired += 1

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
                bio_start = fragment.get_biological_position(start_only=True, end_only=False)
                position_key = (bio_start, fragment.read1.is_reverse)

        fragments_by_position[position_key].append(fragment)

    # Apply edit distance clustering within each position
    deduplicated_reads = []
    for position, fragments_at_position in fragments_by_position.items():
        if len(fragments_at_position) > 1:
            if min_edit_dist_frac > 0:
                # Group by UMI first, then cluster by edit distance
                fragments_by_umi = defaultdict(list)
                for fragment in fragments_at_position:
                    fragments_by_umi[fragment.umi].append(fragment)

                # Apply frequency-aware edit distance clustering
                clustered_fragment_groups = cluster_umis_by_edit_distance_frequency_aware(
                    fragments_by_umi, min_edit_dist_frac, min_frequency_ratio
                )
            else:
                # No edit distance clustering - group by exact UMI
                fragments_by_umi = defaultdict(list)
                for fragment in fragments_at_position:
                    fragments_by_umi[fragment.umi].append(fragment)
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
                    cluster_name = best_fragment.get_cluster_name("umi", start_only, end_only)
                    
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
                    cluster_name = best_fragment.get_cluster_name("umi", start_only, end_only)
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


def deduplicate_reads_by_coordinate(
    reads,
    max_pair_dist=2000,
    start_only=False,
    end_only=False,
    best_read_by="avg_base_q",
    keep_duplicates=False,
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
        
    Returns:
        Tuple of (deduplicated_reads, read_stats)
    """
    if not reads:
        return reads, {"properly_paired": 0, "paired": 0, "single_end": 0}

    # Track read type statistics
    properly_paired = 0
    paired = 0
    single_end = 0

    # Group reads by position first (like in process_genomic_chunk)
    reads_by_position = defaultdict(list)
    for read in reads:
        if not read.is_unmapped:
            read_position = get_read_position(read)
            reads_by_position[read_position].append(read)

    # Create a lookup dictionary for faster mate finding
    reads_by_name = defaultdict(list)
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            reads_by_name[read.query_name].append(read)

    # Create fragments from reads
    fragments = []
    processed_reads = set()

    # Process single-end reads first
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            if not read.is_paired and read.query_name not in processed_reads:
                # Single-end read
                fragment = Fragment(
                    query_name=read.query_name,
                    read1=read,
                    umi=extract_umi_from_query_name(read.query_name, "_"),
                )
                fragments.append(fragment)
                processed_reads.add(read.query_name)
                single_end += 1

    # Process paired-end reads with optimized mate finding
    for read_position, reads_at_position in reads_by_position.items():
        for read in reads_at_position:
            if read.is_paired and read.query_name not in processed_reads:
                # Find the mate using the lookup dictionary
                mate_read = find_mate(
                    read, reads_by_name[read.query_name], max_pair_dist
                )

                if mate_read:
                    # Found a pair - create paired fragment
                    fragment = Fragment(
                        query_name=read.query_name,
                        read1=read,
                        read2=mate_read,
                        umi=extract_umi_from_query_name(read.query_name, "_"),
                    )
                    fragments.append(fragment)
                    processed_reads.add(read.query_name)
                    properly_paired += 1
                else:
                    # No mate found - treat as single-end
                    fragment = Fragment(
                        query_name=read.query_name,
                        read1=read,
                        umi=extract_umi_from_query_name(read.query_name, "_"),
                    )
                    fragments.append(fragment)
                    processed_reads.add(read.query_name)
                    paired += 1

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
                cluster_name = best_fragment.get_cluster_name("coordinate", start_only, end_only)
                
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
                cluster_name = best_fragment.get_cluster_name("coordinate", start_only, end_only)
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


def should_keep_read(read, remove_unpaired, remove_chimeric, remove_unmapped):
    """Determine if a read should be kept based on filtering options."""
    if remove_unmapped and read.is_unmapped:
        return False
    if remove_chimeric and read.is_supplementary:
        return False
    # Note: unpaired filtering is handled at the pair level, not individual read level
    return True


def process_genomic_chunk(
    input_bam: str,
    contig: str,
    search_start: int,
    search_end: int,
    chunk_start: int,
    chunk_end: int,
    min_edit_dist_frac: float,
    umi_sep: str,
    no_umi: bool,
    keep_duplicates: bool,
    best_read_by: str,
    max_pair_dist: int,
    remove_unpaired: bool,
    remove_chimeric: bool,
    remove_unmapped: bool,
    start_only: bool,
    end_only: bool,
    is_first_chunk: bool,
    processed_reads_global: set,
) -> Dict[str, Any]:
    """Process a genomic chunk for deduplication."""
    try:
        # Read BAM file and extract reads for this chunk
        reads = []
        with pysam.AlignmentFile(input_bam, "rb") as f:
            for read in f.fetch(contig, search_start, search_end):
                if (
                    read.reference_start >= chunk_start
                    and read.reference_start < chunk_end
                ):
                    reads.append(read)

        # Early exit for empty chunks
        if not reads:
            return {
                "input_fragments": 0,
                "output_fragments": 0,
                "has_reads": False,
                "reads": [],
            }

        # Apply filtering
        filtered_reads = []
        for read in reads:
            if should_keep_read(
                read, remove_unpaired, remove_chimeric, remove_unmapped
            ):
                filtered_reads.append(read)

        # Deduplicate based on method
        if no_umi:
            # Coordinate-based deduplication
            deduplicated_reads, read_stats = deduplicate_reads_coordinate(
                filtered_reads, max_pair_dist, start_only, end_only, best_read_by
            )
        else:
            # UMI-based deduplication
            deduplicated_reads, read_stats = deduplicate_reads_umi(
                filtered_reads,
                max_pair_dist,
                start_only,
                end_only,
                min_edit_dist_frac,
                best_read_by,
            )

        # Convert reads to strings for thread-safe writing
        read_strings = []
        for read in deduplicated_reads:
            read_strings.append(read.to_string())

        return {
            "input_fragments": len(filtered_reads),
            "output_fragments": len(deduplicated_reads),
            "has_reads": len(read_strings) > 0,
            "reads": read_strings,
            "read_stats": read_stats,
        }

    except Exception as e:
        return {
            "input_fragments": 0,
            "output_fragments": 0,
            "has_reads": False,
            "reads": [],
            "error": str(e),
        }


# Convenience functions for each approach - ALL SHARE THE SAME CODE!
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
    remove_unpaired: bool = False,
    remove_chimeric: bool = False,
    remove_unmapped: bool = False,
    prefilter: bool = False,
    start_only: bool = False,
    end_only: bool = False,
) -> bool:
    """Process BAM file using sequential reading and parallel window processing."""
    import signal
    import sys

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
            remove_unpaired=remove_unpaired,
            remove_chimeric=remove_chimeric,
            remove_unmapped=remove_unmapped,
            start_only=start_only,
            end_only=end_only,
        )
        return processor.process_bam()
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user (Ctrl+C)")
        if processor and hasattr(processor, "writer") and processor.writer:
            print("🧹 Cleaning up temporary files...")
            processor.writer.cleanup()
        return False
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        if processor and hasattr(processor, "writer") and processor.writer:
            print("🧹 Cleaning up temporary files...")
            processor.writer.cleanup()
        return False
