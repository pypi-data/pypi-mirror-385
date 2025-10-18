"""
Command-line interface for x-spaces-dl
"""

import sys

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import Config
from .core import XSpacesDL

console = Console()


def print_banner():
    """Print application banner"""
    banner = f"""
╔═══════════════════════════════════════════════════════════╗
║                      x-spaces-dl                          ║
║          X/Twitter Spaces Downloader v{__version__}              ║
║                 github.com/w3Abhishek                     ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


@click.command()
@click.argument("space_url", required=False)
@click.option("-o", "--output", type=str, help="Output filename")
@click.option("-d", "--output-dir", type=click.Path(), help="Output directory")
@click.option(
    "-b",
    "--batch",
    type=click.Path(exists=True),
    help="Batch download from file (one URL per line)",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["m4a", "mp3", "aac", "wav"], case_sensitive=False),
    help="Output format (default: m4a)",
)
@click.option("-c", "--cookies", type=click.Path(exists=True), help="Path to cookies.txt file")
@click.option("--guest-only", is_flag=True, help="Use guest mode only (no auth fallback)")
@click.option("--embed-metadata", is_flag=True, help="Embed metadata into audio file")
@click.option("--save-metadata", is_flag=True, help="Save metadata to JSON file")
@click.option("--info-only", is_flag=True, help="Show space info without downloading")
@click.option("--template", type=str, help='Filename template (e.g., "{date}_{host}_{title}")')
@click.option(
    "--retry", type=int, default=3, help="Retry attempts for failed downloads (default: 3)"
)
@click.option("--no-resume", is_flag=True, help="Disable resume capability")
@click.option("-q", "--quiet", is_flag=True, help="Quiet mode (minimal output)")
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode (detailed output)")
@click.option("--dry-run", is_flag=True, help="Dry run (show what would be downloaded)")
@click.option("--config", type=click.Path(), help="Path to config file")
@click.option(
    "--create-config", type=click.Path(), help="Create default config file at specified path"
)
@click.version_option(version=__version__, prog_name="x-spaces-dl")
def main(
    space_url,
    output,
    output_dir,
    batch,
    format,
    cookies,
    guest_only,
    embed_metadata,
    save_metadata,
    info_only,
    template,
    retry,
    no_resume,
    quiet,
    verbose,
    dry_run,
    config,
    create_config,
):
    """
    x-spaces-dl - Download Twitter/X Spaces recordings

    Examples:

      # Download a space
      x-spaces-dl https://x.com/i/spaces/1234567890

      # Download with authentication
      x-spaces-dl https://x.com/i/spaces/1234567890 --cookies cookies.txt

      # Batch download
      x-spaces-dl --batch urls.txt

      # Download as MP3 with metadata
      x-spaces-dl https://x.com/i/spaces/1234567890 --format mp3 --embed-metadata

      # Show space info only
      x-spaces-dl https://x.com/i/spaces/1234567890 --info-only
    """

    # Print banner unless quiet
    if not quiet:
        print_banner()

    # Handle config creation
    if create_config:
        try:
            Config.create_default_config(create_config)
            console.print(f"✅ Config file created: {create_config}", style="green")
            return
        except Exception as e:
            console.print(f"❌ Failed to create config: {str(e)}", style="red")
            sys.exit(1)

    # Validate input
    if not space_url and not batch:
        console.print("❌ Error: Either SPACE_URL or --batch is required", style="red")
        console.print("\nRun 'x-spaces-dl --help' for usage information", style="yellow")
        sys.exit(1)

    try:
        # Initialize config
        cfg = Config(
            config_file=config,
            output_dir=output_dir,
            format=format,
            embed_metadata=embed_metadata,
            save_metadata=save_metadata,
            template=template,
            retry_attempts=retry,
            no_resume=no_resume,
            verbose=verbose,
            quiet=quiet,
            cookies_file=cookies,
        )

        # Initialize downloader
        downloader = XSpacesDL(
            config=cfg,
            cookies_file=cookies,
            guest_mode=not guest_only,
        )

        # Handle batch download
        if batch:
            if dry_run:
                console.print(f"[DRY RUN] Would download spaces from: {batch}", style="yellow")
                with open(batch, "r") as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                console.print(f"Found {len(urls)} URLs to download:", style="cyan")
                for url in urls:
                    console.print(f"  • {url}")
                return

            results = downloader.download_batch(batch)

            # Print summary
            successful = sum(1 for v in results.values() if v)
            failed = len(results) - successful

            if not quiet:
                console.print("\n" + "=" * 60, style="cyan")
                console.print("📊 Batch Download Complete", style="bold cyan")
                console.print(f"   ✅ Successful: {successful}", style="green")
                console.print(f"   ❌ Failed: {failed}", style="red")
                console.print("=" * 60, style="cyan")

            sys.exit(0 if failed == 0 else 1)

        # Handle single space
        if space_url:
            # Info only mode
            if info_only:
                try:
                    metadata = downloader.get_space_metadata(space_url)
                    display_space_info(metadata)
                    return
                except Exception as e:
                    console.print(f"❌ Error: {str(e)}", style="red")
                    sys.exit(1)

            # Dry run
            if dry_run:
                try:
                    metadata = downloader.get_space_metadata(space_url)
                    console.print("[DRY RUN] Would download:", style="yellow")
                    display_space_info(metadata)
                    return
                except Exception as e:
                    console.print(f"❌ Error: {str(e)}", style="red")
                    sys.exit(1)

            # Actual download
            try:
                success = downloader.download_space(
                    space_url,
                    output_file=output,
                    format=format,
                    embed_metadata=embed_metadata,
                    save_metadata=save_metadata,
                )

                if success:
                    if not quiet:
                        console.print("\n🎉 Download completed successfully!", style="bold green")
                    sys.exit(0)
                else:
                    if not quiet:
                        console.print("\n❌ Download failed", style="bold red")
                    sys.exit(1)

            except KeyboardInterrupt:
                console.print("\n\n⚠️  Download interrupted by user", style="yellow")
                sys.exit(130)
            except Exception as e:
                console.print(f"\n❌ Error: {str(e)}", style="red")
                if verbose:
                    import traceback

                    console.print("\n" + traceback.format_exc(), style="dim")
                sys.exit(1)

    except Exception as e:
        console.print(f"❌ Fatal error: {str(e)}", style="red")
        if verbose:
            import traceback

            console.print("\n" + traceback.format_exc(), style="dim")
        sys.exit(1)


def display_space_info(metadata: dict):
    """Display space information in a formatted table"""
    table = Table(title="🎙️  Space Information", show_header=False, box=None)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")

    # Add rows
    table.add_row("Space ID", metadata.get("space_id", "N/A"))
    table.add_row("Title", metadata.get("title", "N/A"))
    table.add_row(
        "Host", f"{metadata.get('host_display_name', 'N/A')} (@{metadata.get('host', 'N/A')})"
    )
    table.add_row("State", metadata.get("state", "N/A"))

    if metadata.get("started_date"):
        table.add_row("Started", metadata["started_date"])

    if metadata.get("ended_date"):
        table.add_row("Ended", metadata["ended_date"])

    table.add_row("Participants", str(metadata.get("total_participants", 0)))
    table.add_row("URL", metadata.get("url", "N/A"))

    console.print(table)


if __name__ == "__main__":
    main()
