"""
Batch download example for x-spaces-dl
"""

from xspacesdl import XSpacesDL
from xspacesdl.config import Config

# Create custom config
config = Config(
    output_dir="./downloads", format="mp3", embed_metadata=True, template="{date}_{host}_{title}"
)

# Initialize downloader
dl = XSpacesDL(config=config)

# Method 1: Download from file
print("Method 1: Batch download from file")
results = dl.download_batch("urls.txt")

# Print summary
successful = sum(1 for v in results.values() if v)
print(f"\nDownload complete: {successful}/{len(results)} successful")

# Method 2: Download from list
print("\nMethod 2: Download from list")
urls = [
    "https://x.com/i/spaces/1234567890",
    "https://x.com/i/spaces/0987654321",
    "https://x.com/i/spaces/1111111111",
]

for i, url in enumerate(urls, 1):
    print(f"\nDownloading {i}/{len(urls)}: {url}")
    try:
        success = dl.download_space(url)
        if success:
            print(f"✅ Success")
        else:
            print(f"❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")
