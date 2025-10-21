# MarkDup

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/y9c/markdup)
[![Version](https://img.shields.io/badge/version-0.0.2-blue.svg)](https://github.com/y9c/markdup)

A comprehensive Python tool for deduplicating BAM files that **automatically handles multiple sequencing conditions and edge cases** with intelligent UMI clustering and biological positioning.

> **⚠️ Early Development Stage**: This tool is currently in alpha development. While functional, it may have bugs and the API may change. Please report any issues you encounter.

> **🆕 Version 0.0.2**: Enhanced error handling, better input validation, improved memory management, and more detailed progress reporting.

## 🎯 Key Differentiators

Unlike other deduplication tools, MarkDup **automatically handles multiple sequencing conditions and edge cases**:

- **🔬 Multi-condition Support**: Works with or without UMIs, single-end or paired-end reads
- **🧬 Biological Positioning**: Automatically handles strand-aware positioning (start-only, end-only, or full fragment)
- **🎯 Intelligent Clustering**: Frequency-aware UMI clustering prevents unrealistic merging
- **⚡ Edge Case Handling**: Automatically detects and handles various sequencing artifacts
- **🔧 Adaptive Processing**: Automatically adjusts algorithms based on input data characteristics

## 🚀 Features

### Core Capabilities

- **🔬 UMI-based deduplication** with quality-based read selection
- **📍 Coordinate-based deduplication** for files without UMIs
- **🧬 Biological positioning** for strand-aware clustering
- **⚡ Process-based parallelism** for multi-core performance
- **🎯 Advanced clustering** with edit distance and frequency-aware algorithms
- **📊 Comprehensive statistics** and progress tracking

### Automatic Edge Case Handling

- **🔄 UMI Detection**: Automatically detects UMI presence and format
- **🧬 Strand Awareness**: Automatically handles forward/reverse strand reads
- **📏 CIGAR Handling**: Properly processes reads with indels and complex CIGAR strings
- **🎯 Position Grouping**: Intelligent grouping based on biological vs. reference coordinates
- **⚖️ Frequency Balancing**: Prevents over-clustering of high-frequency UMIs
- **🔧 Quality Selection**: Multiple quality metrics with automatic fallback

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install markdup
```

### From Source

```bash
git clone https://github.com/y9c/markdup.git
cd markdup
pip install .
```

### Using uv (Development)

```bash
git clone https://github.com/y9c/markdup.git
cd markdup
uv sync
```

## 🚀 Quick Start

### Automatic UMI Detection and Processing

```bash
# Tool automatically detects UMIs and chooses appropriate method
markdup input.bam output.bam

# With multiple threads
markdup input.bam output.bam --threads 8

# Keep duplicates and mark them
markdup input.bam output.bam --keep-duplicates
```

### Explicit Method Selection

```bash
# Force UMI-based deduplication
markdup input.bam output.bam --method umi

# Force coordinate-based deduplication (no UMIs)
markdup input.bam output.bam --method coordinate
```

### Advanced Positioning Options

```bash
# Start-only positioning (e.g., for ChIP-seq)
markdup input.bam output.bam --start-only

# End-only positioning (e.g., for reverse-complemented reads)
markdup input.bam output.bam --end-only

# Full fragment positioning (default, handles both start and end)
markdup input.bam output.bam
```

### UMI Clustering Tuning

```bash
# Custom edit distance threshold
markdup input.bam output.bam --min-edit-dist-frac 0.17

# Frequency-aware clustering to prevent over-merging
markdup input.bam output.bam --min-frequency-ratio 0.1

# Custom UMI separator
markdup input.bam output.bam --umi-separator ":"
```

## 📋 Command Line Interface

### Global Options

| Option      | Description              | Default |
| ----------- | ------------------------ | ------- |
| `--help`    | Show help message        | -       |
| `--version` | Show version information | -       |

### Input/Output Options

| Option       | Description                        | Default  |
| ------------ | ---------------------------------- | -------- |
| `INPUT_BAM`  | Input BAM file path                | Required |
| `OUTPUT_BAM` | Output BAM file path               | Required |
| `--force`    | Overwrite output file if it exists | False    |

### Deduplication Method

| Option     | Description                                 | Default |
| ---------- | ------------------------------------------- | ------- |
| `--method` | Deduplication method: `umi` or `coordinate` | `umi`   |

### UMI Options

| Option                  | Description                                         | Default |
| ----------------------- | --------------------------------------------------- | ------- |
| `--umi-separator`       | Separator for extracting UMIs from read names       | `_`     |
| `--min-edit-dist-frac`  | Minimum UMI edit distance as fraction of UMI length | `0.1`   |
| `--min-frequency-ratio` | Minimum frequency ratio for UMI clustering          | `0.1`   |

### Positioning Options

| Option         | Description                        | Default |
| -------------- | ---------------------------------- | ------- |
| `--start-only` | Group reads by start position only | False   |
| `--end-only`   | Group reads by end position only   | False   |

### Quality Selection

| Option           | Description                               | Default      |
| ---------------- | ----------------------------------------- | ------------ |
| `--best-read-by` | Select best read by: `mapq`, `avg_base_q` | `avg_base_q` |

### Processing Options

| Option              | Description                               | Default  |
| ------------------- | ----------------------------------------- | -------- |
| `--threads`         | Number of threads for parallel processing | `1`      |
| `--window-size`     | Size of genomic windows for processing    | `100000` |
| `--keep-duplicates` | Keep duplicate reads and mark them        | False    |

## 🧬 Algorithm Details

### Automatic Condition Detection

The tool automatically detects and handles:

1. **UMI Presence**: Scans read names for UMI patterns
2. **Read Type**: Single-end vs. paired-end detection
3. **Strand Orientation**: Forward vs. reverse strand handling
4. **CIGAR Complexity**: Indel and complex alignment handling
5. **Quality Metrics**: Available quality scores and selection criteria

### UMI-based Deduplication

1. **Fragment Creation**: Reads are grouped into fragments (single-end or paired-end)
2. **Biological Positioning**: Fragments are positioned using strand-aware coordinates
3. **Position Grouping**: Fragments are grouped by biological position and strand
4. **UMI Clustering**: Within each position group, UMIs are clustered using:
   - Exact matching for identical UMIs
   - Edit distance clustering for similar UMIs
   - Frequency-aware clustering to prevent unrealistic merging
5. **Quality Selection**: The highest quality read from each cluster is selected
6. **Output Generation**: Selected reads are written with comprehensive cluster information

### Coordinate-based Deduplication

1. **Fragment Creation**: Reads are grouped into fragments
2. **Position Grouping**: Fragments are grouped by genomic coordinates
3. **Quality Selection**: The highest quality read from each group is selected
4. **Output Generation**: Selected reads are written

### Biological Positioning

- **Forward strand**: Biological start = reference start, Biological end = reference end
- **Reverse strand**: Biological start = reference end, Biological end = reference start
- **Strand-aware clustering**: Ensures proper grouping regardless of strand orientation
- **CIGAR-aware positioning**: Properly handles indels and complex alignments

## 📊 Output Format

### BAM Tags

| Tag  | Description                                                                        |
| ---- | ---------------------------------------------------------------------------------- |
| `cn` | Cluster name with genomic coordinates and UMI (format: `chr:start-end:strand:UMI`) |
| `cs` | Cluster size (number of reads in cluster)                                          |

### Example Output

```
read1_UMI123    0    chr1    1001    60    50M    *    0    0    ATGC...    IIII...    cn:Z:chr1:1001-1050:+:UMI123    cs:i:3
read2_UMI123    1024  chr1    1001    50    50M    *    0    0    ATGC...    IIII...    cn:Z:chr1:1001-1050:+:UMI123    cs:i:3
read3_UMI123    1024  chr1    1001    45    50M    *    0    0    ATGC...    IIII...    cn:Z:chr1:1001-1050:+:UMI123    cs:i:3
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Algorithm Details](docs/algorithm.md)
- [FAQ](docs/faq.md)
- [Contributing](docs/contributing.md)
