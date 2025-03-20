# Advanced Proxy Checker

A high-performance proxy checking tool with colorized output, detailed reporting, and support for multiple input formats.

## Features ✨

- **Multi-Format Support**: Process proxies from CSV, JSON, and TXT files
- **Folder Scanning**: Automatically detect proxy files in directories
- **Colorized Console Output**: Instant visual feedback
- **Performance Metrics**: Latency & speed measurements
- **Geo-Location**: Country detection for each proxy
- **Comprehensive Reports**: CSV, TXT, and summary files
- **Proxy Type Detection**: Auto-detect HTTP/HTTPS/SOCKS
- **Multi-Threading**: Configurable concurrency (up to 100 threads)

## Supported File Formats 📁

### 1. CSV Files
```csv
ip,port
192.168.1.1,8080
10.0.0.1,1080
```

### 2. JSON Files
```json
{
  "proxies": [
    "192.168.1.1:8080",
    "10.0.0.1:1080"
  ]
}
```

### 3. TXT Files
```
192.168.1.1:8080
10.0.0.1:1080
```

## Installation 📦

```bash
git clone https://github.com/yourusername/proxy-checker.git
cd proxy-checker
pip install -r requirements.txt
```

## Usage 🚀

Basic usage:
```bash
python proxy_checker.py --input proxies/ --output results --threads 50
```

All options:
```bash
python proxy_checker.py \
  --input <file_or_directory> \
  --output <results_dir> \
  --threads <num_threads> \
  --timeout <seconds> \
  --sort <latency|speed>
```

## Output Structure 📂
```
results/
├── 20231024_153045/
│   ├── working_report.csv     # Complete check results
│   ├── summary.txt           # Check statistics
│   ├── working_proxies.txt   # All working proxies
│   ├── latency_sorted.txt    # Fastest proxies first
│   └── speed_sorted.txt      # Highest bandwidth first
```

## Requirements 📋
- Python 3.8+
- `requests` library
