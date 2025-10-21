"""
Comprehensive utility function tests.

This module tests all utility functions with extensive coverage.

Author: Ye Chang
Date: 2025-01-27
"""

import pytest
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


class TestFragmentComprehensive:
    """Comprehensive tests for the Fragment dataclass."""
    
    def test_fragment_creation_single_end(self):
        """Test creating a single-end fragment."""
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
        assert fragment.umi is None
        assert not fragment.processed
    
    def test_fragment_creation_paired_end(self):
        """Test creating a paired-end fragment."""
        read1 = Mock()
        read1.is_paired = True
        read1.is_reverse = False
        read1.reference_start = 1000
        read1.reference_end = 1100
        read1.reference_name = "chr1"
        read1.query_name = "read1"
        read1.query_length = 100
        
        read2 = Mock()
        read2.is_paired = True
        read2.is_reverse = True
        read2.reference_start = 2000
        read2.reference_end = 2100
        read2.reference_name = "chr1"
        read2.query_name = "read1"
        read2.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2, umi="UMI123")
        
        assert fragment.query_name == "read1"
        assert fragment.read1 == read1
        assert fragment.read2 == read2
        assert fragment.is_paired
        assert fragment.umi == "UMI123"
        assert not fragment.processed
    
    def test_fragment_properties(self):
        """Test fragment properties."""
        read = Mock()
        read.reference_start = 1000
        read.reference_end = 1100
        read.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read)
        
        assert fragment.start == 1000
        assert fragment.end == 1100
    
    def test_fragment_get_leftmost_start(self):
        """Test getting leftmost start position."""
        read1 = Mock()
        read1.reference_start = 1000
        read1.query_length = 100
        
        read2 = Mock()
        read2.reference_start = 2000
        read2.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        
        assert fragment.get_leftmost_start() == 1000
    
    def test_fragment_get_rightmost_end(self):
        """Test getting rightmost end position."""
        read1 = Mock()
        read1.reference_start = 1000
        read1.reference_end = 1100
        read1.query_length = 100

        read2 = Mock()
        read2.reference_start = 2000
        read2.reference_end = 2100
        read2.query_length = 100

        fragment = Fragment(query_name="read1", read1=read1, read2=read2)

        assert fragment.get_rightmost_end() == 2100
    
    def test_fragment_get_fragment_position(self):
        """Test getting fragment position."""
        read1 = Mock()
        read1.reference_start = 1000
        read1.reference_end = 1100
        read1.query_length = 100
        read1.is_reverse = False
        
        read2 = Mock()
        read2.reference_start = 2000
        read2.reference_end = 2100
        read2.query_length = 100
        read2.is_reverse = True
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        
        start, end, strand = fragment.get_fragment_position()
        assert start == 1000
        assert end == 2100
        assert strand == 0  # Forward strand
    
    def test_fragment_get_strand(self):
        """Test getting fragment strand."""
        read = Mock()
        read.is_reverse = False
        
        fragment = Fragment(query_name="read1", read1=read)
        
        strand = fragment.get_strand()
        assert strand == "+"
        
        # Test reverse strand
        read.is_reverse = True
        strand = fragment.get_strand()
        assert strand == "-"
    
    def test_fragment_get_cluster_name(self):
        """Test getting cluster name."""
        read1 = Mock()
        read1.reference_start = 1000
        read1.reference_end = 1100
        read1.query_length = 100
        read1.is_reverse = False
        read1.reference_name = "chr1"
        
        fragment = Fragment(query_name="read1_UMI123", read1=read1)
        fragment.umi = "UMI123"
    
        cluster_name = fragment.get_cluster_name("umi")
        assert cluster_name == "chr1:1001-1100:+:UMI123"
        
        cluster_name = fragment.get_cluster_name("coordinate")
        assert cluster_name == "chr1:1001-1100:+"
    
    def test_fragment_get_fragment_length(self):
        """Test getting fragment length."""
        read1 = Mock()
        read1.reference_start = 1000
        read1.reference_end = 1100
        read1.query_length = 100
        
        read2 = Mock()
        read2.reference_start = 2000
        read2.reference_end = 2100
        read2.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        
        length = fragment.get_fragment_length()
        assert length == 1100  # 2100 - 1000
    
    def test_fragment_is_in_window(self):
        """Test checking if fragment is in window."""
        read = Mock()
        read.reference_start = 1000
        read.reference_end = 1100
        read.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read)
        
        # Fragment is in window
        assert fragment.is_in_window(500, 1500) == True
        # Fragment is not in window
        assert fragment.is_in_window(2000, 3000) == False
        # Fragment partially overlaps
        assert fragment.is_in_window(1050, 1200) == True
    
    def test_fragment_is_in_overlap_region(self):
        """Test checking if fragment is in overlap region."""
        read = Mock()
        read.reference_start = 1000
        read.reference_end = 1100
        read.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read)
        
        # Single-end fragment should return False
        assert fragment.is_in_overlap_region(1000, 2000) == False
        
        # Paired-end fragment
        read2 = Mock()
        read2.reference_start = 2000
        read2.reference_end = 2100
        read2.query_length = 100
        
        fragment = Fragment(query_name="read1", read1=read, read2=read2)
        
        # Fragment is in overlap region (window_end=2000, max_pair_dist=1000)
        assert fragment.is_in_overlap_region(2000, 1000) == True
        # Fragment is not in overlap region
        assert fragment.is_in_overlap_region(500, 1000) == False
    
    def test_fragment_get_combined_qualities(self):
        """Test getting combined qualities."""
        read1 = Mock()
        read1.query_qualities = [30, 35, 40]
        
        fragment = Fragment(query_name="read1", read1=read1)
        
        qualities = fragment.get_combined_qualities()
        assert qualities == [30, 35, 40]
        
        # Paired-end fragment
        read2 = Mock()
        read2.query_qualities = [25, 30, 35]
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        
        qualities = fragment.get_combined_qualities()
        assert qualities == [30, 35, 40, 25, 30, 35]
    
    def test_fragment_get_min_mapq(self):
        """Test getting minimum mapping quality."""
        read1 = Mock()
        read1.mapping_quality = 30
        
        fragment = Fragment(query_name="read1", read1=read1)
        
        min_mapq = fragment.get_min_mapq()
        assert min_mapq == 30
        
        # Paired-end fragment
        read2 = Mock()
        read2.mapping_quality = 40
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        
        min_mapq = fragment.get_min_mapq()
        assert min_mapq == 30  # Minimum of 30 and 40
    
    def test_fragment_is_secondary(self):
        """Test checking if fragment is secondary."""
        read1 = Mock()
        read1.is_secondary = False
        
        fragment = Fragment(query_name="read1", read1=read1)
        
        assert fragment.is_secondary() == False
        
        # Secondary read
        read1.is_secondary = True
        assert fragment.is_secondary() == True
        
        # Paired-end with one secondary
        read2 = Mock()
        read2.is_secondary = False
        
        fragment = Fragment(query_name="read1", read1=read1, read2=read2)
        assert fragment.is_secondary() == True


class TestUtilityFunctionsComprehensive:
    """Comprehensive tests for utility functions."""
    
    def test_levenshtein_distance_comprehensive(self):
        """Test Levenshtein distance calculation comprehensively."""
        # Basic cases
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("abc", "abc") == 0
        assert levenshtein_distance("abc", "ab") == 1
        assert levenshtein_distance("abc", "abcd") == 1
        assert levenshtein_distance("kitten", "sitting") == 3
        
        # UMI-specific cases
        assert levenshtein_distance("UMI1", "UMI2") == 1
        assert levenshtein_distance("ATCG", "GCTA") == 4
        assert levenshtein_distance("AAAA", "TTTT") == 4
        
        # Edge cases
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("a", "b") == 1
        assert levenshtein_distance("ab", "ba") == 2
    
    def test_get_read_position_comprehensive(self):
        """Test read position calculation comprehensively."""
        read = Mock()
        read.reference_start = 1000
        read.reference_end = 1100
        read.is_reverse = False
        read.query_length = 100
        
        start, end, is_reverse = get_read_position(read)
        assert start == 1000
        assert end == 1100
        assert is_reverse == False
        
        # Test reverse read
        read.is_reverse = True
        start, end, is_reverse = get_read_position(read)
        assert start == 1000
        assert end == 1100
        assert is_reverse == True
    
    # Removed read-level filtering tests; filtering is now fragment-level
    
    def test_extract_umi_from_query_name_comprehensive(self):
        """Test UMI extraction comprehensively."""
        # Create mock read objects
        class MockRead:
            def __init__(self, query_name):
                self.query_name = query_name
                self.tags = {}
            
            def has_tag(self, tag):
                return tag in self.tags
            
            def get_tag(self, tag):
                return self.tags[tag]
        
        # Test with underscore separator
        read1 = MockRead("read_UMI123")
        assert extract_umi(read1, None, "_") == "UMI123"
        
        read2 = MockRead("read_UMI123_extra")
        assert extract_umi(read2, None, "_") == "extra"
        
        read3 = MockRead("read_UMI123_extra_more")
        assert extract_umi(read3, None, "_") == "more"
        
        # Test with colon separator
        read4 = MockRead("read:UMI456")
        assert extract_umi(read4, None, ":") == "UMI456"
        
        read5 = MockRead("read:UMI456:extra")
        assert extract_umi(read5, None, ":") == "extra"
        
        # Test with no separator
        read6 = MockRead("read")
        assert extract_umi(read6, None, "_") == ""  # No separator found, no UMI extracted
        assert extract_umi(read6, None, ":") == ""  # No separator found, no UMI extracted
        
        # Test empty string
        read7 = MockRead("")
        assert extract_umi(read7, None, "_") == ""
        
        # Test separator at end
        read8 = MockRead("read_")
        assert extract_umi(read8, None, "_") == ""
        
        # Test separator at beginning
        read9 = MockRead("_UMI1")
        assert extract_umi(read9, None, "_") == "UMI1"
    
    def test_calculate_average_base_quality_comprehensive(self):
        """Test average base quality calculation comprehensively."""
        # Test with valid qualities
        assert calculate_average_base_quality([30, 35, 40, 25, 20]) == 30.0
        assert calculate_average_base_quality([10, 20, 30, 40, 50]) == 30.0
        assert calculate_average_base_quality([30]) == 30.0
        
        # Test with empty list
        assert calculate_average_base_quality([]) == 0.0
        
        # Test with None
        assert calculate_average_base_quality(None) == 0.0
        
        # Test with zero qualities
        assert calculate_average_base_quality([0, 0, 0]) == 0.0
        
        # Test with mixed qualities including zero
        assert calculate_average_base_quality([0, 30, 60]) == 30.0
        
        # Test with single quality
        assert calculate_average_base_quality([30]) == 30.0
    
    def test_cluster_umis_by_edit_distance_comprehensive(self):
        """Test UMI clustering comprehensively."""
        umi_groups = {
            "UMI1": [Mock(), Mock()],
            "UMI2": [Mock()],
            "UMI3": [Mock()]
        }
        
        # Test with high threshold (no clustering)
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.5)
        assert len(clusters) >= 1
        
        # Test with low threshold (clustering)
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.1)
        assert len(clusters) >= 1
        
        # Test with empty groups
        clusters = cluster_umis_by_edit_distance({}, 0.1)
        assert clusters == []
        
        # Test with single group
        single_group = {"UMI1": [Mock()]}
        clusters = cluster_umis_by_edit_distance(single_group, 0.1)
        assert len(clusters) == 1
        
        # Test with identical UMIs
        identical_groups = {
            "UMI1": [Mock()],
            "UMI1": [Mock()]  # Same UMI
        }
        clusters = cluster_umis_by_edit_distance(identical_groups, 0.1)
        assert len(clusters) == 1  # Should be clustered together
    
    def test_select_best_read_comprehensive(self):
        """Test best read selection comprehensively."""
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
        
        # Test with empty list - should raise ValueError
        with pytest.raises(ValueError):
            select_best_read([], "mapq")
    
    def test_select_best_fragment_comprehensive(self):
        """Test best fragment selection comprehensively."""
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
        
        # Test with empty list - should raise ValueError
        with pytest.raises(ValueError):
            select_best_fragment([], "mapq")


class TestEdgeCasesComprehensive:
    """Comprehensive edge case tests."""
    
    def test_levenshtein_distance_edge_cases(self):
        """Test Levenshtein distance with comprehensive edge cases."""
        # Empty strings
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("", "abc") == 3
        
        # Identical strings
        assert levenshtein_distance("abc", "abc") == 0
        
        # Very different strings
        assert levenshtein_distance("abc", "xyz") == 3
        
        # Single character differences
        assert levenshtein_distance("abc", "ab") == 1
        assert levenshtein_distance("abc", "abcd") == 1
        assert levenshtein_distance("abc", "axc") == 1
        
        # Long strings
        long_str1 = "A" * 100
        long_str2 = "B" * 100
        assert levenshtein_distance(long_str1, long_str2) == 100
    
    def test_calculate_average_base_quality_edge_cases(self):
        """Test average base quality calculation with comprehensive edge cases."""
        # Empty list
        assert calculate_average_base_quality([]) == 0.0
        
        # None input
        assert calculate_average_base_quality(None) == 0.0
        
        # Single quality
        assert calculate_average_base_quality([30]) == 30.0
        
        # Zero qualities
        assert calculate_average_base_quality([0, 0, 0]) == 0.0
        
        # Mixed qualities including zero
        assert calculate_average_base_quality([0, 30, 60]) == 30.0
        
        # Very large numbers
        assert calculate_average_base_quality([1000, 2000, 3000]) == 2000.0
        
        # Negative numbers (should be handled gracefully)
        assert abs(calculate_average_base_quality([-10, 10, 20]) - 6.67) < 0.01  # Approximate
    
    def test_extract_umi_from_query_name_edge_cases(self):
        """Test UMI extraction with comprehensive edge cases."""
        # Create mock read objects
        class MockRead:
            def __init__(self, query_name):
                self.query_name = query_name
                self.tags = {}
            
            def has_tag(self, tag):
                return tag in self.tags
            
            def get_tag(self, tag):
                return self.tags[tag]
        
        # No separator
        read1 = MockRead("read")
        assert extract_umi(read1, None, "_") == ""  # No separator found, no UMI extracted
        
        # Empty query name
        read2 = MockRead("")
        assert extract_umi(read2, None, "_") == ""
        
        # Multiple separators
        read3 = MockRead("read_UMI1_extra_more")
        assert extract_umi(read3, None, "_") == "more"
        
        # Separator at end
        read4 = MockRead("read_")
        assert extract_umi(read4, None, "_") == ""
        
        # Separator at beginning
        read5 = MockRead("_UMI1")
        assert extract_umi(read5, None, "_") == "UMI1"
        
        # Only separators
        read6 = MockRead("___")
        assert extract_umi(read6, None, "_") == ""
        
        # Mixed separators
        read7 = MockRead("read_UMI1:extra")
        assert extract_umi(read7, None, "_") == "UMI1:extra"
    
    def test_cluster_umis_by_edit_distance_edge_cases(self):
        """Test UMI clustering with comprehensive edge cases."""
        # Empty groups
        assert cluster_umis_by_edit_distance({}, 0.1) == []
        
        # Single group
        umi_groups = {"UMI1": [Mock()]}
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.1)
        assert len(clusters) == 1
        
        # Identical UMIs (should be handled gracefully)
        umi_groups = {
            "UMI1": [Mock()],
            "UMI1": [Mock()]  # Same UMI
        }
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.1)
        assert len(clusters) == 1  # Should be clustered together
        
        # Very similar UMIs
        umi_groups = {
            "UMI1": [Mock()],
            "UMI2": [Mock()],  # Very similar
            "UMI3": [Mock()]
        }
        clusters = cluster_umis_by_edit_distance(umi_groups, 0.9)  # High threshold
        assert len(clusters) >= 1


if __name__ == "__main__":
    pytest.main([__file__])