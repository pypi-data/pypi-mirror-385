"""
BAM Deduplication Package

This package provides efficient BAM file deduplication functionality with multiple processing strategies.

Author: Ye Chang
Date: 2025-01-27
"""

from .deduplication import (
    deduplicate_fragments_by_coordinate,
    deduplicate_fragments_by_umi,
    process_bam,
)

__author__ = "Ye Chang"
__email__ = "yech1990@gmail.com"

__all__ = [
    "deduplicate_fragments_by_umi",
    "deduplicate_fragments_by_coordinate",
    "process_bam",
]
