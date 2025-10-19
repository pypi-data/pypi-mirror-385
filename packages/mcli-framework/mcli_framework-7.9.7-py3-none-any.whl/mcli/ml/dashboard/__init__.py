"""ML Dashboard for real-time monitoring"""

from .app import main
from .cli import app as cli_app


def main():
    """Main entry point for dashboard CLI"""
    cli_app()


__all__ = ["main", "cli_app"]
