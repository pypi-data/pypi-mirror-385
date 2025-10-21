#!/usr/bin/env python3
"""Main entry point for gisce-multitools CLI applications."""

import sys
import os

# Add the package path to sys.path if running as a standalone script
if __name__ == "__main__":
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get the parent directory (where giscemultitools package is)
    parent_dir = os.path.dirname(script_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

import click

try:
    from .githubutils.scripts.github_cli import github_cli
    from .slackutils.scripts.slack_cli import slack_cli
except ImportError:
    # Fallback to absolute imports when relative imports fail
    from giscemultitools.githubutils.scripts.github_cli import github_cli
    from giscemultitools.slackutils.scripts.slack_cli import slack_cli


@click.group()
@click.version_option()
def main():
    """GISCE Multi-tools CLI - GitHub and Slack utilities."""
    pass


# Add the CLI groups
main.add_command(github_cli, name="github")
main.add_command(slack_cli, name="slack")


if __name__ == "__main__":
    main()