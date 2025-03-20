# ⚡ ProxyPulse 🚀

ProxyPulse is a high-performance proxy verification tool 🚀. It supports CSV, JSON, and TXT input formats 📂, provides colorized console output 🎨, measures latency & speed ⏳⚡, detects proxy types 🔗, and includes geo-location analysis 🌍. With multi-threading 🧵 and detailed reporting 📊, it ensures fast and accurate proxy validation ✅.

## ✨ Key Features

- 🗂 **Multi-Format Support**: Process proxy lists from 📄 CSV, 📝 JSON, and 📃 TXT files.
- 📁 **Automated Directory Scanning**: Detect and process all proxy files within a folder 📂.
- 🎨 **Colorized Console Output**: Provides real-time ⏳, visually distinct feedback 👀.
- 🚀 **Performance Metrics**: Measures ⏱ latency and ⚡ connection speed.
- 🌎 **Geo-Location Analysis**: Identifies the 🏳️ country of each proxy.
- 📊 **Comprehensive Reporting**: Generates structured reports in 📄 CSV, 📃 TXT, and 📜 summary formats.
- 🔍 **Proxy Type Identification**: Auto-detects 🔗 HTTP, 🔐 HTTPS, and 🧦 SOCKS proxies.
- 🧵 **High-Concurrency Processing**: Supports multi-threading with 🔄 configurable concurrency (up to 100 threads ⚡).

## 📁 Supported Input Formats

### 📄 CSV Files
```csv
ip,port
192.168.1.1,8080
10.0.0.1,1080
```

### 📝 JSON Files
```json
{
  "proxies": [
    "192.168.1.1:8080",
    "10.0.0.1:1080"
  ]
}
```

### 📃 TXT Files
```
192.168.1.1:8080
10.0.0.1:1080
```

## 📦 Installation

```bash
git clone https://github.com/yourusername/proxy-checker.git
cd proxy-checker
pip install -r requirements.txt
```

## 🏃‍♂️ Usage

### 🚀 Basic Usage
```bash
python proxy_checker.py --input proxies/ --output results --threads 50
```

### ⚙️ Full Command Options
```bash
python proxy_checker.py \
  --input <file_or_directory> \
  --output <results_dir> \
  --threads <num_threads> \
  --timeout <seconds> \
  --sort <latency|speed>
```

### 📜 Option Descriptions
| 🏷 **Option**   | 📖 **Description** |
|---------------|-------------|
| `--input`     | 📂 Specifies the input file or directory containing proxies. |
| `--output`    | 🗂 Defines the directory where the results will be stored. |
| `--threads`   | ⚙️ Sets the number of concurrent threads for faster processing (default: 50). |
| `--timeout`   | ⏳ Configures the timeout period (in seconds) for each proxy request. |
| `--sort`      | 🔄 Sorts proxies by `latency` (fastest first ⏱) or `speed` (highest bandwidth first 🚀). |

## 📂 Output Structure
```
results/
├── 20231024_153045/
│   ├── working_report.csv     # 📄 Complete proxy check results
│   ├── summary.txt            # 📜 Overall check statistics
│   ├── working_proxies.txt    # ✅ List of functional proxies
│   ├── latency_sorted.txt     # ⏳ Proxies sorted by response time
│   └── speed_sorted.txt       # 🚀 Proxies sorted by bandwidth capacity
```

## 📋 System Requirements
- 🐍 **Python 3.8+**
- 📦 **`requests` library**

Boost your productivity with this ⚡ powerful, high-performance 🏎 proxy checking tool! 🎯

