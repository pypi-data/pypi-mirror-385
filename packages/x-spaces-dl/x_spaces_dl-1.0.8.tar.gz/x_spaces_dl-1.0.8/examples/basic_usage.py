"""
Basic usage examples for x-spaces-dl
"""

from xspacesdl import XSpacesDL

# Example 1: Simple download
print("Example 1: Simple download")
dl = XSpacesDL()
dl.download_space("https://x.com/i/spaces/1234567890")

# Example 2: Download with custom filename
print("\nExample 2: Custom filename")
dl.download_space("https://x.com/i/spaces/1234567890", output_file="my_space.m4a")

# Example 3: Download as MP3 with metadata
print("\nExample 3: MP3 with metadata")
dl.download_space("https://x.com/i/spaces/1234567890", format="mp3", embed_metadata=True)

# Example 4: Get space information
print("\nExample 4: Get space info")
metadata = dl.get_space_metadata("https://x.com/i/spaces/1234567890")
print(f"Title: {metadata['title']}")
print(f"Host: {metadata['host']}")
print(f"Participants: {metadata['total_participants']}")

# Example 5: Using authentication
print("\nExample 5: With authentication")
dl_auth = XSpacesDL(cookies_file="cookies.txt")
dl_auth.download_space("https://x.com/i/spaces/1234567890")
