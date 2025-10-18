"""CLI forwarder for xspacesdl.

Keeps backward compatibility by delegating to the original implementation in
the xspacedl package.
"""

from xspacedl.cli import main  # re-export

__all__ = ["main"]
