# JSHunter - High-Performance JavaScript Security Scanner

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](https://github.com/iamunixtz/JsHunter)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![TruffleHog](https://img.shields.io/badge/powered%20by-TruffleHog-orange.svg)](https://github.com/trufflesecurity/trufflehog)

A blazing-fast JavaScript security scanner that can process **1 million URLs in ~5 hours** using advanced parallel processing and async operations. JSHunter is designed for security researchers, penetration testers, and developers who need to identify sensitive information in JavaScript files at scale.

## 🚀 Performance Features

- **Async Downloads**: 200+ concurrent HTTP downloads with connection pooling
- **Batch Scanning**: TruffleHog processes multiple files simultaneously
- **Parallel Processing**: 50+ worker threads for maximum throughput
- **Memory Efficient**: Chunked processing to handle massive datasets
- **Progress Tracking**: Real-time progress with ETA and rate monitoring
- **Resume Capability**: Built-in error handling and recovery

## 🔧 Installation

### Option 1: PyPI Installation (Recommended)

```bash
# Install JSHunter from PyPI
pip install jshunter

# Setup TruffleHog binary
jshunter --setup

# Verify installation
jshunter --version
```

### Option 2: Source Installation

```bash
# Clone the repository
git clone https://github.com/iamunixtz/JsHunter.git
cd JsHunter

# Install dependencies
pip install -r requirements.txt

# Setup TruffleHog binary
python3 jshunter --setup
```

## 📊 Performance Benchmarks

| URLs | Legacy Mode | High-Performance Mode | Speedup |
|------|-------------|----------------------|---------|
| 100  | 5-15 min    | 30-60 sec           | 10x     |
| 1K   | 1-3 hours   | 3-8 min             | 20x     |
| 10K  | 14-42 hours | 15-45 min           | 30x     |
| 100K | 6-17 days   | 2.5-7.5 hours       | 40x     |
| 1M   | 2-6 months  | 4-12 hours          | 50x     |

## 🎯 Usage

### CLI Usage

#### High-Performance Mode (Recommended for 100+ URLs)

```bash
# Basic high-performance scan
jshunter --high-performance -f urls.txt

# Custom performance tuning
jshunter --high-performance \
  --max-workers 100 \
  --concurrent-downloads 500 \
  --batch-size 200 \
  -f urls.txt

# With Discord notifications
jshunter --high-performance \
  --discord-webhook "https://discord.com/api/webhooks/..." \
  -f urls.txt
```

#### Legacy Mode (Small batches)

```bash
# Single URL
jshunter -u "https://example.com/script.js"

# Multiple URLs from file
jshunter -f urls.txt

# With SSL bypass
jshunter --ignore-ssl -f urls.txt
```

### Web Interface

```bash
# Start the web interface
jshunter-web

# Access at http://localhost:8000
```

## 🔗 Discord Integration

JSHunter supports Discord webhook integration for real-time notifications:

- **Verified findings**: Sent immediately as they are found
- **Unverified findings**: Sent as detailed TXT file after scan completion
- **Full secret values**: Complete API keys and secrets (not truncated)
- **Formatted reports**: Easy-to-read findings with source URLs and line numbers

```bash
jshunter -f urls.txt --discord-webhook "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

## ⚙️ Configuration

### Performance Tuning

**Small (100-1K URLs):**
```bash
--max-workers 20 --concurrent-downloads 50 --batch-size 25
```

**Medium (1K-10K URLs):**
```bash
--max-workers 50 --concurrent-downloads 200 --batch-size 100
```

**Large (10K-100K URLs):**
```bash
--max-workers 100 --concurrent-downloads 500 --batch-size 200
```

**Massive (100K+ URLs):**
```bash
--max-workers 200 --concurrent-downloads 1000 --batch-size 500
```

### Command Line Options

```
--high-performance     Enable parallel processing mode
--max-workers N        Number of worker threads (default: 50)
--concurrent-downloads N  Max concurrent downloads (default: 200)
--batch-size N         TruffleHog batch size (default: 100)
--connection-limit N   HTTP connection limit (default: 100)
--ignore-ssl          Bypass SSL certificate errors
--discord-webhook URL Send findings to Discord
--output FILE         Save results to specific file
```

## 📁 Output Formats

### Separate Verified/Unverified Files
The tool automatically separates results into different files:

- **`verified_results_TIMESTAMP.json`** - Only verified findings (sent immediately to Discord)
- **`unverified_results_TIMESTAMP.json`** - Only unverified findings (saved after scan completes)
- **`combined_results.json`** - All findings together (if using `--output`)

### JSON Results
```json
{
  "DetectorName": "GitHub",
  "Verified": true,
  "Raw": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "source_url": "https://example.com/script.js",
  "SourceMetadata": {
    "Data": {
      "Filesystem": {
        "file": "/path/to/file.js",
        "line": 42
      }
    }
  }
}
```

## 🛠️ System Requirements

- **CPU**: 4+ cores recommended (8+ for massive scans)
- **RAM**: 4GB minimum (8GB+ for large batches)
- **Network**: Stable internet connection
- **Disk**: 1GB+ free space for downloads

## 🔍 Error Handling

- **Network failures**: Automatic retry with exponential backoff
- **SSL errors**: Bypass with `--ignore-ssl` flag
- **Memory management**: Chunked processing prevents OOM
- **Interrupt handling**: Graceful shutdown on Ctrl+C
- **Resume capability**: Can restart from last checkpoint
- **File cleanup**: Downloaded files automatically deleted after processing

## 🤝 Integration

### With Other Tools

```bash
# From rezon (silent mode)
rezon | jshunter --high-performance

# From subfinder
subfinder -d example.com | jshunter --high-performance
```

### API Integration

```python
import asyncio
from jshunter import process_urls_high_performance

async def scan_urls(urls):
    results = await process_urls_high_performance(
        urls=urls,
        tr_bin="/path/to/trufflehog",
        max_concurrent_downloads=200,
        batch_size=100
    )
    return results
```

## 📋 Best Practices

1. **Start Small**: Test with 100 URLs before scaling up
2. **Monitor Resources**: Watch CPU/memory usage during large scans
3. **Rate Limiting**: Respect target server resources
4. **Backup Results**: Save important findings immediately
5. **Network Stability**: Use stable internet for large batches

## 🐛 Troubleshooting

### Common Issues

**"Too many open files"**
```bash
ulimit -n 65536  # Increase file descriptor limit
```

**"Connection refused"**
```bash
--concurrent-downloads 50  # Reduce concurrent connections
```

**"Out of memory"**
```bash
--batch-size 25  # Reduce batch size
```

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/iamunixtz/JsHunter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iamunixtz/JsHunter/discussions)

---

**Ready to scan 1M URLs in 5 hours? Let's go!** 🚀
