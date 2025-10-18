# x-spaces-dl

> A powerful command-line tool and Python library for downloading Twitter/X Spaces recordings

[![PyPI version](https://badge.fury.io/py/x-spaces-dl.svg)](https://badge.fury.io/py/x-spaces-dl)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎙️ Download Twitter/X Spaces recordings (replays)
- 📦 Batch download multiple spaces from a file
- 🎵 Multiple output formats (M4A, MP3, AAC, WAV)
- 📊 Rich metadata embedding (title, host, date, participants)
- 🔄 Resume interrupted downloads
- 🚀 Fast downloads with ffmpeg or pure Python fallback
- 🔐 Guest mode (no login) with automatic fallback to authenticated mode
- 📈 Beautiful progress bars and detailed logging
- ⚙️ Highly configurable via CLI or config file
- 🐍 Use as a library in your Python projects

## 📥 Installation

### From PyPI (recommended)

```bash
pip install x-spaces-dl
```

### From source

```bash
git clone https://github.com/w3Abhishek/x-spaces-dl.git
cd x-spaces-dl
pip install -e .
```

### Optional: Install ffmpeg for faster downloads

- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## 🚀 Quick Start

### Command Line

```bash
# Download a space (guest mode)
x-spaces-dl https://x.com/i/spaces/1234567890

# Download with authentication (if guest mode fails)
x-spaces-dl https://x.com/i/spaces/1234567890 --cookies cookies.txt

# Download multiple spaces from a file
x-spaces-dl --batch urls.txt

# Download as MP3 with metadata
x-spaces-dl https://x.com/i/spaces/1234567890 --format mp3 --embed-metadata

# Custom output filename
x-spaces-dl https://x.com/i/spaces/1234567890 -o "my_space.m4a"

# Show space info without downloading
x-spaces-dl https://x.com/i/spaces/1234567890 --info-only
```

### Python Library

```python
from xspacesdl import XSpacesDL

# Initialize downloader
downloader = XSpacesDL()

# Download a space
downloader.download_space(
    "https://x.com/i/spaces/1234567890",
    output_file="space.m4a"
)

# Get space metadata
metadata = downloader.get_space_metadata("https://x.com/i/spaces/1234567890")
print(f"Title: {metadata['title']}")
print(f"Host: {metadata['host']}")
```

## 📖 Usage

### Basic Commands

```bash
# Download with default settings
x-spaces-dl <SPACE_URL>

# Specify output file
x-spaces-dl <SPACE_URL> -o output.m4a

# Use authenticated mode with cookies
x-spaces-dl <SPACE_URL> --cookies cookies.txt

# Force guest mode (no fallback)
x-spaces-dl <SPACE_URL> --guest-only
```

### Batch Download

Create a text file with one URL per line:

```text
https://x.com/i/spaces/1234567890
https://x.com/i/spaces/0987654321
https://x.com/i/spaces/1111111111
```

Then run:

```bash
x-spaces-dl --batch urls.txt
```

### Output Formats

```bash
# Convert to MP3
x-spaces-dl <SPACE_URL> --format mp3

# Convert to WAV
x-spaces-dl <SPACE_URL> --format wav

# Keep original M4A
x-spaces-dl <SPACE_URL> --format m4a
```

### Metadata

```bash
# Embed metadata (title, host, date)
x-spaces-dl <SPACE_URL> --embed-metadata

# Save metadata to JSON
x-spaces-dl <SPACE_URL> --save-metadata

# Show info only (no download)
x-spaces-dl <SPACE_URL> --info-only
```

### Advanced Options

```bash
# Custom output directory
x-spaces-dl <SPACE_URL> --output-dir ~/Downloads/Spaces

# Filename template
x-spaces-dl <SPACE_URL> --template "{date}_{host}_{title}"

# Retry failed downloads
x-spaces-dl <SPACE_URL> --retry 3

# Quiet mode (no output)
x-spaces-dl <SPACE_URL> --quiet

# Verbose mode (detailed logging)
x-spaces-dl <SPACE_URL> --verbose

# Dry run (show what would be downloaded)
x-spaces-dl <SPACE_URL> --dry-run
```

### Configuration File

Create `~/.config/xspacesdl/config.yaml`:

```yaml
output_dir: ~/Downloads/Spaces
format: mp3
embed_metadata: true
cookies_file: ~/cookies.txt
retry_attempts: 3
template: "{date}_{host}_{title}"
```

Then simply run:

```bash
x-spaces-dl <SPACE_URL>
```

## 🔐 Authentication

For private spaces or when guest mode fails:

1. **Export cookies from your browser**:
   - Install a browser extension like "Get cookies.txt" or "EditThisCookie"
   - Visit twitter.com/x.com and login
   - Export cookies to `cookies.txt` (Netscape format)

2. **Use cookies with x-spaces-dl**:
   ```bash
   x-spaces-dl <SPACE_URL> --cookies cookies.txt
   ```

## 🛠️ All CLI Options

```
x-spaces-dl [OPTIONS] [SPACE_URL]

Options:
  -o, --output TEXT           Output filename
  -d, --output-dir PATH       Output directory
  -b, --batch FILE            Batch download from file
  -f, --format [m4a|mp3|aac|wav]  Output format (default: m4a)
  -c, --cookies FILE          Path to cookies.txt file
  --guest-only                Use guest mode only (no auth fallback)
  --embed-metadata            Embed metadata into audio file
  --save-metadata             Save metadata to JSON file
  --info-only                 Show space info without downloading
  --template TEXT             Filename template
  --retry INTEGER             Retry attempts (default: 3)
  --no-resume                 Disable resume capability
  -q, --quiet                 Quiet mode
  -v, --verbose               Verbose mode
  --dry-run                   Dry run (no actual download)
  --config FILE               Config file path
  --version                   Show version
  --help                      Show this message and exit
```

## 📚 Python API

### Basic Usage

```python
from xspacesdl import XSpacesDL

# Initialize
dl = XSpacesDL()

# Download a space
dl.download_space("https://x.com/i/spaces/1234567890")
```

### With Authentication

```python
from xspacesdl import XSpacesDL

# Initialize with cookies
dl = XSpacesDL(cookies_file="cookies.txt")

# Download
dl.download_space("https://x.com/i/spaces/1234567890")
```

### Advanced Usage

```python
from xspacesdl import XSpacesDL
from xspacesdl.config import Config

# Custom configuration
config = Config(
    output_dir="./downloads",
    format="mp3",
    embed_metadata=True,
    retry_attempts=5
)

# Initialize with config
dl = XSpacesDL(config=config)

# Get metadata
metadata = dl.get_space_metadata("https://x.com/i/spaces/1234567890")

# Download with custom options
dl.download_space(
    "https://x.com/i/spaces/1234567890",
    output_file="custom_name.mp3",
    format="mp3"
)
```

### Batch Download

```python
from xspacesdl import XSpacesDL

dl = XSpacesDL()

urls = [
    "https://x.com/i/spaces/1234567890",
    "https://x.com/i/spaces/0987654321",
]

for url in urls:
    try:
        dl.download_space(url)
        print(f"✅ Downloaded: {url}")
    except Exception as e:
        print(f"❌ Failed: {url} - {e}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Make sure you have the right to download and use the content. Respect Twitter's Terms of Service and content creators' rights.

## 🙏 Acknowledgments

- Inspired by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Thanks to all contributors

## 📧 Contact

- GitHub: [@w3Abhishek](https://github.com/w3Abhishek)
- Issues: [GitHub Issues](https://github.com/w3Abhishek/x-spaces-dl/issues)

---

Made with ❤️ by [w3Abhishek](https://github.com/w3Abhishek)