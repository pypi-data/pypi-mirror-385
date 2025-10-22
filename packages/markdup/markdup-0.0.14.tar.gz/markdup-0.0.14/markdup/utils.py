"""
Utility functions for BAM deduplication.

This module contains utility functions for handling BAM files, fragments,
and reads, as well as for calculating quality metrics.

Author: Ye Chang
Date: 2025-01-27
"""

from dataclasses import dataclass
from functools import lru_cache

import jellyfish
import pysam


@lru_cache(maxsize=65536)
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings with caching.

    Uses jellyfish library for optimized performance (13-113x faster than custom implementation).
    Results are cached using LRU cache (65536 entries) to avoid recomputing distances for the same UMI pairs.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance between the strings
    """
    return jellyfish.levenshtein_distance(s1, s2)


@dataclass
class Fragment:
    """Represents a DNA fragment (single-end or paired-end)."""

    query_name: str
    read1: pysam.AlignedSegment
    read2: pysam.AlignedSegment | None = None
    is_paired: bool = False
    umi: str | None = None
    processed: bool = (
        False  # Track if fragment has been processed in overlapping windows
    )

    def __post_init__(self):
        """Initialize fragment properties after creation."""
        if self.read2 is not None:
            self.is_paired = True
        else:
            self.is_paired = False

    @property
    def start(self) -> int:
        """Get the start position of the fragment."""
        return self.get_leftmost_start()

    @property
    def end(self) -> int:
        """Get the end position of the fragment."""
        return self.get_rightmost_end()

    def get_leftmost_start(self) -> int:
        """Get the leftmost start position of the fragment."""
        if self.is_paired and self.read2:
            return min(self.read1.reference_start, self.read2.reference_start)
        return self.read1.reference_start

    def get_rightmost_end(self) -> int:
        """Get the rightmost end position of the fragment."""
        if self.is_paired and self.read2:
            read1_end = self.read1.reference_end
            read2_end = self.read2.reference_end
            return max(read1_end, read2_end)
        return self.read1.reference_end

    def get_fragment_position(self) -> tuple[int, int, bool]:
        """Get the fragment position as (start, end, is_reverse)."""
        return (
            self.get_leftmost_start(),
            self.get_rightmost_end(),
            self.read1.is_reverse,
        )

    def get_fragment_length(self) -> int:
        """Get the fragment length."""
        return self.get_rightmost_end() - self.get_leftmost_start()

    def get_strand(self) -> str:
        """Get the fragment strand (+ or -)."""
        return "-" if self.read1.is_reverse else "+"

    def get_biological_position(
        self, start_only: bool = False, end_only: bool = False
    ) -> int:
        """Get biological position for single-end reads based on strand."""
        if self.is_paired:
            # For paired-end reads, use regular fragment position
            start, end, _ = self.get_fragment_position()
            return start if start_only else end if end_only else start
        # For single-end reads: use biological positioning
        if start_only:
            # Biological start: 5' end of the read
            if self.read1.is_reverse:
                # Reverse strand: biological start is the 3' end (reference_end)
                return self.read1.reference_end
            # Forward strand: biological start is the 5' end (reference_start)
            return self.read1.reference_start
        if end_only:
            # Biological end: 3' end of the read
            if self.read1.is_reverse:
                # Reverse strand: biological end is the 5' end (reference_start)
                return self.read1.reference_start
            # Forward strand: biological end is the 3' end (reference_end)
            return self.read1.reference_end
        # Default: use regular fragment position
        start, end, _ = self.get_fragment_position()
        return start

    def get_cluster_name(
        self, method: str = "umi", start_only: bool = False, end_only: bool = False
    ) -> str:
        """Get cluster name for deduplication."""
        strand = self.get_strand()

        # Always use biological positioning for proper strand-aware coordinates
        if start_only:
            bio_pos = self.get_biological_position(start_only=True, end_only=False)
            # Convert to 1-based coordinates for user-friendly display
            position = bio_pos + 1
        elif end_only:
            bio_pos = self.get_biological_position(start_only=False, end_only=True)
            # Convert to 1-based coordinates for user-friendly display
            position = bio_pos + 1
        else:
            # Default: use biological start and end positions
            bio_start = self.get_biological_position(start_only=True, end_only=False)
            bio_end = self.get_biological_position(start_only=False, end_only=True)
            # Convert to 1-based coordinates for user-friendly display
            # Always show coordinates in ascending genomic order (left-to-right)
            start_1based = bio_start + 1  # Convert start from 0-based to 1-based
            end_1based = bio_end  # End is already 1-based (exclusive in 0-based)
            if start_1based <= end_1based:
                position = f"{start_1based}-{end_1based}"
            else:
                position = f"{end_1based}-{start_1based}"

        if method == "umi" and self.umi:
            return f"{self.read1.reference_name}:{position}:{strand}:{self.umi}"
        return f"{self.read1.reference_name}:{position}:{strand}"

    def is_in_window(self, window_start: int, window_end: int) -> bool:
        """Check if fragment overlaps with a window."""
        frag_start = self.get_leftmost_start()
        frag_end = self.get_rightmost_end()
        return frag_start < window_end and frag_end > window_start

    def is_in_overlap_region(self, window_end: int, max_pair_dist: int) -> bool:
        """Check if fragment is in the overlap region for paired-end reads."""
        if not self.is_paired:
            return False

        frag_start = self.get_leftmost_start()
        frag_end = self.get_rightmost_end()

        # Check if fragment spans the overlap region
        overlap_start = window_end - max_pair_dist
        return frag_start < window_end and frag_end > overlap_start

    def get_combined_qualities(self) -> list[int]:
        """Get combined quality scores from all reads in the fragment."""
        if self.is_paired and self.read2:
            return list(self.read1.query_qualities) + list(self.read2.query_qualities)
        return list(self.read1.query_qualities)

    def get_min_mapq(self) -> int:
        """Get the minimum mapping quality from all reads in the fragment."""
        if self.is_paired and self.read2:
            return min(self.read1.mapping_quality, self.read2.mapping_quality)
        return self.read1.mapping_quality

    def is_secondary(self) -> bool:
        """Check if any read in the fragment is secondary."""
        if self.is_paired and self.read2:
            return self.read1.is_secondary or self.read2.is_secondary
        return self.read1.is_secondary


def get_read_position(read):
    """Get read position as (start, end, is_reverse) for all reads."""
    read_start = read.reference_start
    read_end = read.reference_end
    return (read_start, read_end, read.is_reverse)


def extract_umi(read, umi_tag=None, umi_sep="_"):
    """
    Extract UMI from read based on provided parameters.

    Args:
        read: pysam AlignedSegment object
        umi_tag: BAM tag name for UMI (e.g., 'UB'). If provided, extracts from tag.
        umi_sep: Separator used to split UMI from query name (default: '_').
                 Only used if umi_tag is None.

    Returns:
        str: Extracted UMI sequence, or empty string if not found
    """
    # If umi_tag is provided, extract from BAM tag
    if umi_tag and read.has_tag(umi_tag):
        return read.get_tag(umi_tag)

    # If umi_tag is None or not found, extract from query name using umi_sep
    if umi_sep and umi_sep in read.query_name:
        return read.query_name.rsplit(umi_sep, 1)[-1]

    return ""


def calculate_average_base_quality(qualities):
    """
    Calculate average base quality from quality scores.

    Args:
        qualities: List of quality scores (integers)

    Returns:
        float: Average quality score, or 0 if no qualities provided
    """
    if not qualities:
        return 0
    return sum(qualities) / len(qualities) if qualities else 0


def cluster_umis_by_edit_distance(umi_groups, max_dist_frac):
    """
    Cluster UMIs by edit distance within each position using frequency-aware clustering.

    This function implements a more realistic clustering approach that considers UMI frequency:
    - UMIs are sorted by frequency (number of fragments) in descending order
    - Only smaller UMIs can be merged into larger ones (not vice versa)
    - This prevents unrealistic merging of high-frequency UMIs into low-frequency ones

    Args:
        umi_groups: Dictionary mapping UMI -> list of fragments
        max_dist_frac: Minimum edit distance as fraction of UMI length

    Returns:
        List of lists, where each inner list contains fragments from the same cluster
    """
    if not umi_groups:
        return []

    # Get all UMIs sorted by frequency (number of fragments) in descending order
    umi_freq_pairs = [(umi, len(fragments)) for umi, fragments in umi_groups.items()]
    umi_freq_pairs.sort(
        key=lambda x: x[1], reverse=True
    )  # Sort by frequency descending
    umis = [pair[0] for pair in umi_freq_pairs]

    if len(umis) <= 1:
        return [list(umi_groups.values())[0]] if umis else []

    clusters = []
    used_umis = set()

    for i, umi1 in enumerate(umis):
        if umi1 in used_umis:
            continue

        # Start a new cluster with this UMI
        cluster_fragments = list(umi_groups[umi1])
        used_umis.add(umi1)

        # Find other UMIs that are within edit distance
        # Only check UMIs that come after this one (smaller frequency)
        for j, umi2 in enumerate(umis[i + 1 :], i + 1):
            if umi2 in used_umis:
                continue

            # Calculate edit distance threshold
            max_dist = int(max_dist_frac * min(len(umi1), len(umi2)))
            if max_dist == 0:  # If threshold is 0, only exact matches
                if umi1 == umi2:
                    cluster_fragments.extend(umi_groups[umi2])
                    used_umis.add(umi2)
            else:
                dist = levenshtein_distance(umi1, umi2)
                if dist <= max_dist:
                    # Only merge smaller UMI into larger one (frequency-based)
                    # This prevents unrealistic merging of high-frequency UMIs
                    cluster_fragments.extend(umi_groups[umi2])
                    used_umis.add(umi2)

        clusters.append(cluster_fragments)

    return clusters


def cluster_umis_by_edit_distance_frequency_aware(
    umi_groups, max_dist_frac, max_frequency_ratio=0.1
):
    """
    Cluster UMIs by edit distance with frequency-aware logic to prevent unrealistic merging.

    This function implements a more sophisticated clustering approach that considers both
    edit distance and UMI frequency to make more realistic clustering decisions:

    - UMIs are sorted by frequency (number of fragments) in descending order
    - A smaller UMI can only be merged into a larger one if:
      1. Edit distance is within the threshold, AND
      2. The smaller UMI's frequency is below a minimum ratio of the larger UMI's frequency
    - This prevents merging of two high-frequency UMIs that are likely distinct biological entities

    Args:
        umi_groups: Dictionary mapping UMI -> list of fragments
        max_dist_frac: Minimum edit distance as fraction of UMI length
        max_frequency_ratio: Maximum ratio of smaller UMI frequency to larger UMI frequency
                            for merging to be allowed (default: 0.1 = 10%)

    Returns:
        List of lists, where each inner list contains fragments from the same cluster
    """
    if not umi_groups:
        return []

    # Early return for single UMI
    if len(umi_groups) == 1:
        return [list(umi_groups.values())[0]]

    # Get all UMIs sorted by frequency (number of fragments) in descending order
    umi_freq_pairs = [(umi, len(fragments)) for umi, fragments in umi_groups.items()]
    umi_freq_pairs.sort(
        key=lambda x: x[1], reverse=True
    )  # Sort by frequency descending
    umis = [pair[0] for pair in umi_freq_pairs]
    umi_frequencies = {pair[0]: pair[1] for pair in umi_freq_pairs}

    clusters = []
    used_umis = set()

    for i, umi1 in enumerate(umis):
        if umi1 in used_umis:
            continue

        # Start a new cluster with this UMI
        cluster_fragments = list(umi_groups[umi1])
        used_umis.add(umi1)
        cluster_frequency = umi_frequencies[umi1]

        # Pre-calculate minimum frequency threshold for potential merging
        # UMIs below this frequency could potentially be merged into this cluster
        min_merge_frequency = cluster_frequency * max_frequency_ratio

        # Find other UMIs that are within edit distance and frequency criteria
        # Only check UMIs that come after this one (smaller or equal frequency)
        for j, umi2 in enumerate(umis[i + 1 :], i + 1):
            if umi2 in used_umis:
                continue

            umi2_frequency = umi_frequencies[umi2]

            # Early exit: if umi2 frequency is too high, skip distance calculation
            # All subsequent UMIs will have even lower frequency, but we still need to check them
            # since cluster_frequency grows as we merge
            if umi2_frequency > min_merge_frequency:
                continue

            # Early exit: if umi1 frequency is too small compared to remaining UMIs,
            # stop checking (no more UMIs will be small enough to merge)
            # This happens when cluster_frequency becomes too small
            if umi2_frequency > cluster_frequency * max_frequency_ratio:
                # All remaining UMIs have frequency <= umi2_frequency
                # If umi2 is too large, all subsequent ones might also be too large
                # But we can't break here because cluster_frequency changes
                continue

            # Calculate edit distance threshold
            max_dist = int(max_dist_frac * min(len(umi1), len(umi2)))
            if max_dist == 0:  # If threshold is 0, only exact matches
                if umi1 == umi2:
                    cluster_fragments.extend(umi_groups[umi2])
                    used_umis.add(umi2)
                    cluster_frequency += umi2_frequency
                    min_merge_frequency = cluster_frequency * max_frequency_ratio
            else:
                # Only calculate expensive distance if frequency check passes
                dist = levenshtein_distance(umi1, umi2)
                if dist <= max_dist:
                    # Frequency ratio already checked above, so we can merge
                    cluster_fragments.extend(umi_groups[umi2])
                    used_umis.add(umi2)
                    # Update cluster frequency and threshold for subsequent merges
                    cluster_frequency += umi2_frequency
                    min_merge_frequency = cluster_frequency * max_frequency_ratio

        clusters.append(cluster_fragments)

    return clusters


def select_best_read(read_tuples, best_read_by):
    if best_read_by == "mapq":
        return max(
            read_tuples,
            key=lambda t: (t[1], calculate_average_base_quality(t[2])),
        )
    return max(
        read_tuples,
        key=lambda t: (calculate_average_base_quality(t[2]), t[1]),
    )


def select_best_fragment(fragments, best_read_by):
    """Select the best fragment based on quality metrics."""
    if best_read_by == "mapq":
        return max(
            fragments,
            key=lambda f: (
                f.get_min_mapq(),
                calculate_average_base_quality(f.get_combined_qualities()),
            ),
        )
    return max(
        fragments,
        key=lambda f: (
            calculate_average_base_quality(f.get_combined_qualities()),
            f.get_min_mapq(),
        ),
    )
