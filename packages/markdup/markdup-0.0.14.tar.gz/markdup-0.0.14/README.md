# MarkDup

[![Pypi Releases](https://img.shields.io/pypi/v/markdup.svg)](https://pypi.python.org/pypi/markdup)
[![Downloads](https://img.shields.io/pepy/dt/markdup)](https://pepy.tech/project/markdup)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/y9c/markdup)

**A fast, accurate BAM deduplication tool with intelligent UMI detection and correct fragment detection.**

## Why MarkDup?

Existing BAM deduplication tools suffer from several critical issues: buggy duplicate detection due to incorrect biological positioning and strand handling, poor performance especially with UMI-based deduplication, and inadequate UMI clustering that leads to over-merging.

MarkDup solves these problems with:

- **Correct fragment detection** using proper strand-aware coordinate handling
- **Significantly faster processing** through optimized algorithms and parallel processing
- **Smart UMI clustering** that prevents over-merging with frequency-aware algorithms
- **Automatic detection** that handles both UMI and non-UMI data without requiring different tools

## Quick Start

```bash
# Installation
pip install markdup
```

```bash
# Basic usage (auto-detects everything)
markdup input.bam output.bam

# With multiple threads
markdup input.bam output.bam --threads 8

# Force coordinate-based (no UMIs)
markdup input.bam output.bam --no-umi
```

## Key Features

### 🧬 **Correct Fragment Detection**

- **Strand-aware coordinates**: Properly handles forward/reverse strand reads
- **CIGAR-aware positioning**: Correctly processes indels and complex alignments
- **Biological positioning**: Uses 5'/3' positions, not reference positions

### ⚡ **High Performance**

- **Significantly faster** UMI clustering with optimized algorithms
- **Parallel processing**: Multi-core support for large files
- **Memory efficient**: Window-based processing for large datasets

### 🔄 **Automatic Detection**

- **UMI auto-detection**: Finds UMIs in read names or BAM tags
- **Sequencing type detection**: Automatically detects single-end vs paired-end
- **Quality metrics**: Selects the best quality criteria automatically

### 🎯 **Smart UMI Clustering**

- **Frequency-aware**: Prevents over-clustering of high-frequency UMIs
- **Edit distance**: Configurable similarity thresholds
- **Exact matching**: Handles identical UMIs efficiently

## Performance

- **Significantly faster** UMI clustering with optimized algorithms
- **Multi-core processing** for parallel performance
- **Memory efficient** window-based processing for large files
- **Automatic optimization** based on input data characteristics

## How It Works

1. **Auto-detect**: UMI presence, sequencing type, and quality metrics
2. **Group fragments**: By biological position and strand
3. **Cluster UMIs**: Using edit distance and frequency-aware algorithms
4. **Select best**: The highest quality read from each cluster
5. **Output**: Deduplicated reads with cluster information

## Documentation

### Usage Examples

#### Basic Deduplication

```bash
# Auto-detect UMIs and process
markdup input.bam output.bam

# Force coordinate-based method (no UMIs)
markdup input.bam output.bam --no-umi
```

#### Advanced Options

```bash
# Custom UMI settings
markdup input.bam output.bam --umi-tag UB --min-edit-dist-frac 0.15

# Start-only positioning (useful for ChIP-seq)
markdup input.bam output.bam --start-only

# Keep duplicates and mark them
markdup input.bam output.bam --keep-duplicates
```

### Performance Tuning

```bash
# Use 8 threads
markdup input.bam output.bam --threads 8

# Use larger windows for better performance
markdup input.bam output.bam --window-size 200000
```

### Detailed Documentation

- [Installation Guide](docs/installation.md) - How to install MarkDup
- [Usage Guide](docs/usage.md) - How to use MarkDup
- [Algorithm Details](docs/algorithm.md) - How MarkDup works and fixes existing problems
- [FAQ](docs/faq.md) - Frequently asked questions
- [Contributing](docs/contributing.md) - How to contribute

### Command Line Options

| Option                  | Description                   | Default     |
| ----------------------- | ----------------------------- | ----------- |
| `INPUT_BAM`             | Input BAM file                | Required    |
| `OUTPUT_BAM`            | Output BAM file               | Required    |
| `--threads`             | Number of threads             | 1           |
| `--no-umi`              | Force coordinate-based method | Auto-detect |
| `--umi-tag`             | UMI BAM tag (e.g., UB)        | Auto-detect |
| `--start-only`          | Use start position only       | False       |
| `--end-only`            | Use end position only         | False       |
| `--keep-duplicates`     | Keep and mark duplicates      | False       |
| `--max-dist-frac`       | UMI edit distance threshold   | 0.1         |
| `--max-frequency-ratio` | UMI frequency threshold       | 0.1         |

### Output Format

MarkDup adds BAM tags to track deduplication:

| Tag  | Description                             |
| ---- | --------------------------------------- |
| `cn` | Cluster name (chr:start-end:strand:UMI) |
| `cs` | Cluster size (number of reads)          |

## License

MIT License - see [LICENSE](LICENSE) for details.

&nbsp;

<p align="center">
  <img
    src="https://raw.githubusercontent.com/y9c/y9c/master/resource/footer_line.svg?sanitize=true"
  />
</p>
<p align="center">
  Copyright &copy; 2025-present
  <a href="https://github.com/y9c" target="_blank">Chang Y</a>
</p>
<p align="center">
  <a href="https://github.com/y9c/markdup/blob/master/LICENSE">
    <img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=MIT&logoColor=d9e0ee&colorA=282a36&colorB=c678dd" />
  </a>
</p>
