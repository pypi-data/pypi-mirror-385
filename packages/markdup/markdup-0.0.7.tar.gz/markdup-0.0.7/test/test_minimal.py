"""
Minimal working tests for BAM deduplication.

This module contains minimal tests that verify core functionality works correctly.

Author: Ye Chang
Date: 2025-01-27
"""

import pytest
import tempfile
import os
from unittest.mock import Mock
import pysam

from markdup.utils import (
    Fragment,
    levenshtein_distance,
    get_read_position,
    extract_umi,
    calculate_average_base_quality,
    cluster_umis_by_edit_distance,
    select_best_read,
    select_best_fragment,
)
from markdup.deduplication import (
    calculate_fragment_quality_score,
    find_mate,
    deduplicate_reads_by_umi,
    deduplicate_reads_by_coordinate,
)


class TestBasicFunctionality:
    """Test basic functionality."""
    
    def test_fragment_creation(self):
        """Test Fragment creation."""
        read = Mock()
        read.is_paired = False
        read.is_reverse = False
        read.reference_start = 1000
        read.reference_end = 1100
        read.reference_name = "chr1"
        read.query_name = "read1"
        read.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read)
        
        assert fragment.query_name == "read1"
        assert fragment.read1 == read
        assert fragment.read2 is None
        assert not fragment.is_paired
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("abc", "abc") == 0
        assert levenshtein_distance("abc", "ab") == 1
        assert levenshtein_distance("kitten", "sitting") == 3
    
    def test_get_read_position(self):
        """Test read position calculation."""
        read = Mock()
        read.reference_start = 1000
        read.reference_end = 1100
        read.is_reverse = False
        read.query_length = 100
        
        start, end, is_reverse = get_read_position(read)
        assert start == 1000
        assert end == 1100
        assert is_reverse == False
    
    def test_extract_umi_from_query_name(self):
        """Test UMI extraction from query names."""
        # Create mock read objects
        class MockRead:
            def __init__(self, query_name):
                self.query_name = query_name
                self.tags = {}
            
            def has_tag(self, tag):
                return tag in self.tags
            
            def get_tag(self, tag):
                return self.tags[tag]
        
        # Test query name extraction
        read1 = MockRead("read_UMI123")
        assert extract_umi(read1, None, "_") == "UMI123"
        
        read2 = MockRead("read_UMI123_extra")
        assert extract_umi(read2, None, "_") == "extra"
        
        read3 = MockRead("read")
        assert extract_umi(read3, None, "_") == ""  # No separator found, no UMI extracted
    
    def test_calculate_average_base_quality(self):
        """Test average base quality calculation."""
        assert calculate_average_base_quality([30, 35, 40]) == 35.0
        assert calculate_average_base_quality([]) == 0.0
        assert calculate_average_base_quality(None) == 0.0
    
    def test_cluster_umis_by_edit_distance(self):
        """Test UMI clustering by edit distance."""
        umi_groups = {
            "UMI1": [Mock()],
            "UMI2": [Mock()],
            "UMI3": [Mock()]
        }
        
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.1)
        assert len(clusters) >= 1
    
    def test_select_best_read(self):
        """Test best read selection."""
        reads = [
            (Mock(), 30, [25] * 100),  # read, mapq, qualities
            (Mock(), 40, [35] * 100),
            (Mock(), 20, [45] * 100)
        ]
        
        # Test by mapping quality
        best_read = select_best_read(reads, "mapq")
        assert best_read[1] == 40  # Highest mapping quality
        
        # Test by average base quality
        best_read = select_best_read(reads, "avg_base_q")
        assert best_read[1] == 20  # Highest average base quality (45)
    
    def test_select_best_fragment(self):
        """Test best fragment selection."""
        fragments = []
        for i in range(3):
            read1 = Mock()
            read1.mapping_quality = 20 + i * 10
            read1.query_qualities = [20 + i * 10] * 100
            read1.query_sequence = "A" * 100
            
            fragment = Fragment(query_name=f"read_{i}", read1=read1)
            fragments.append(fragment)
        
        # Test by mapping quality
        best_fragment = select_best_fragment(fragments, "mapq")
        assert best_fragment.read1.mapping_quality == 40  # Highest mapping quality
        
        # Test by average base quality
        best_fragment = select_best_fragment(fragments, "avg_base_q")
        assert best_fragment.read1.query_qualities[0] == 40  # Highest base quality


class TestDeduplication:
    """Test deduplication functionality."""
    
    def test_calculate_fragment_quality_score(self):
        """Test fragment quality score calculation."""
        read1 = Mock()
        read1.mapping_quality = 30
        read1.query_qualities = [30] * 100
        read1.query_sequence = "A" * 100
        
        fragment = Fragment(query_name="read1", read1=read1)
        
        score = calculate_fragment_quality_score(fragment, "mapq")
        assert score == 30.0
    
    def test_find_mate_success(self):
        """Test successful mate finding."""
        read1 = Mock()
        read1.query_name = "read1"
        read1.reference_name = "chr1"
        read1.reference_start = 1000
        read1.is_reverse = False
        
        read2 = Mock()
        read2.query_name = "read1"
        read2.reference_name = "chr1"
        read2.reference_start = 2000
        read2.is_reverse = True
        
        reads_with_same_name = [read1, read2]
        
        mate = find_mate(read1, reads_with_same_name, 2000)
        assert mate == read2
    
    def test_deduplicate_reads_by_umi_empty(self):
        """Test UMI deduplication with empty input."""
        deduplicated_reads, stats = deduplicate_reads_by_umi([])
        assert len(deduplicated_reads) == 0
        assert stats["single_end"] == 0
    
    def test_deduplicate_reads_by_umi_single_read(self):
        """Test UMI deduplication with single read."""
        read = Mock()
        read.is_paired = False
        read.is_reverse = False
        read.reference_start = 1000
        read.reference_end = 1100
        read.reference_name = "chr1"
        read.query_name = "read1_UMI1"
        read.mapping_quality = 30
        read.query_qualities = [30] * 100
        read.query_sequence = "A" * 100
        read.is_unmapped = False
        read.is_duplicate = False
        read.is_proper_pair = True
        read.query_length = 100
        # Set up UMI tag
        read.tags = {"UB": "UMI1"}
        read.has_tag = lambda tag: tag in read.tags
        read.get_tag = lambda tag: read.tags[tag]
        
        deduplicated_reads, stats = deduplicate_reads_by_umi([read])
        assert len(deduplicated_reads) == 1
        assert stats["single_end"] == 1
    
    def test_deduplicate_reads_by_umi_duplicates(self):
        """Test UMI deduplication with duplicate reads."""
        reads = []
        for i in range(3):
            read = Mock()
            read.is_paired = False
            read.is_reverse = False
            read.reference_start = 1000
            read.reference_end = 1100
            read.reference_name = "chr1"
            read.query_name = f"read_{i}_UMI1"  # Same UMI
            read.mapping_quality = 30
            read.query_qualities = [30] * 100
            read.query_sequence = "A" * 100
            read.is_unmapped = False
            read.is_duplicate = False
            read.is_proper_pair = True
            read.query_length = 100
            # Set up UMI tag
            read.tags = {"UB": "UMI1"}
            read.has_tag = lambda tag: tag in read.tags
            read.get_tag = lambda tag: read.tags[tag]
            reads.append(read)
        
        deduplicated_reads, stats = deduplicate_reads_by_umi(reads)
        assert len(deduplicated_reads) == 1  # Should deduplicate to 1
        assert stats["single_end"] == 3  # Original count
    
    def test_deduplicate_reads_by_coordinate_empty(self):
        """Test coordinate deduplication with empty input."""
        deduplicated_reads, stats = deduplicate_reads_by_coordinate([])
        assert len(deduplicated_reads) == 0
        assert stats["single_end"] == 0
    
    def test_deduplicate_reads_by_coordinate_single_read(self):
        """Test coordinate deduplication with single read."""
        read = Mock()
        read.is_paired = False
        read.is_reverse = False
        read.reference_start = 1000
        read.reference_end = 1100
        read.reference_name = "chr1"
        read.query_name = "read1"
        read.mapping_quality = 30
        read.query_qualities = [30] * 100
        read.query_sequence = "A" * 100
        read.is_unmapped = False
        read.is_duplicate = False
        read.is_proper_pair = True
        read.query_length = 100
        
        deduplicated_reads, stats = deduplicate_reads_by_coordinate([read])
        assert len(deduplicated_reads) == 1
        assert stats["single_end"] == 1
    
    def test_deduplicate_reads_by_coordinate_duplicates(self):
        """Test coordinate deduplication with duplicate reads."""
        reads = []
        for i in range(3):
            read = Mock()
            read.is_paired = False
            read.is_reverse = False
            read.reference_start = 1000  # Same position
            read.reference_end = 1100
            read.reference_name = "chr1"
            read.query_name = f"read_{i}"
            read.mapping_quality = 30
            read.query_qualities = [30] * 100
            read.query_sequence = "A" * 100
            read.is_unmapped = False
            read.is_duplicate = False
            read.is_proper_pair = True
            read.query_length = 100
            reads.append(read)
        
        deduplicated_reads, stats = deduplicate_reads_by_coordinate(reads)
        assert len(deduplicated_reads) == 1  # Should deduplicate to 1
        assert stats["single_end"] == 3  # Original count


class TestBAMFileHandling:
    """Test BAM file handling."""
    
    def test_create_valid_bam_file(self):
        """Test creating a valid BAM file."""
        with tempfile.NamedTemporaryFile(suffix='.bam', delete=False) as tmp:
            try:
                # Create a minimal valid BAM file
                header = {'HD': {'VN': '1.0'}, 'SQ': [{'SN': 'chr1', 'LN': 1000}]}
                with pysam.AlignmentFile(tmp.name, 'wb', header=header) as bam:
                    pass
                
                # Verify the file was created
                assert os.path.exists(tmp.name)
                
                # Verify it can be opened
                with pysam.AlignmentFile(tmp.name, 'rb') as bam:
                    assert bam.header is not None
                    
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main([__file__])