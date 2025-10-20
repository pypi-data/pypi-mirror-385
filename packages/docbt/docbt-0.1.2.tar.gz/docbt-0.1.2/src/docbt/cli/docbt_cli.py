import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

import click
from loguru import logger

NAME = "docbt"
ASCII_LOGO = r"""
     .___           ___.    __
  __| _/____   ____\_ |___/  |_
 / __ |/  _ \_/ ___\| __ \   __\
/ /_/ (  <_> )  \___| \_\ \  |
\____ |\____/ \___  >___  /__|
      \/           \/    \/
"""


# Try to get version from package metadata first, then fallback to __init__.py
try:
    __version__ = version(NAME)
except PackageNotFoundError:
    try:
        from docbt import __version__
    except ImportError:
        __version__ = "unknown"


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name=NAME)
@click.pass_context
def cli(ctx):
    click.echo(click.style(f"{ASCII_LOGO}\n", fg="cyan"))
    if __version__ != "unknown":
        click.echo(click.style(f"docbt version: {__version__}\n", fg="green"))
    else:
        click.echo(click.style(f"docbt version: {__version__}\n", fg="red"))
    """The docbt command line interface"""
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))


@cli.command("help")
def help_command():
    """Show this message and exit."""
    click.echo(cli.get_help(click.Context(cli)))


@cli.command("run")
@click.option(
    "--port",
    "-p",
    type=int,
    default=8501,
    help="Port to run the server on (default: 8501)",
)
@click.option(
    "--host",
    "-h",
    type=str,
    default="localhost",
    help="Host to bind the server to (default: localhost)",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(
        ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
        case_sensitive=False,
    ),
    default="INFO",
    help="Set the logging level (default: INFO)",
)
def run_streamlit_server(port: int, host: str, log_level: str):
    """Spawn a Streamlit server as a subprocess with given host and port."""
    # Configure logging level
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=log_level.upper())

    logger.info(f"Logging level set to: {log_level.upper()}")
    click.echo(f"Spawning Streamlit server at {host}:{port}")

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        os.path.join(os.path.dirname(__file__), "..", "server", "server.py"),
        f"--server.port={port}",
        f"--server.address={host}",
    ]

    logger.debug(f"Starting Streamlit server with command: {' '.join(streamlit_cmd)}")

    try:
        result = subprocess.run(streamlit_cmd, check=True)
        logger.info(f"Streamlit server started successfully with return code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit server: {e}")
        click.echo(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"Unexpected error: {e}")


if __name__ == "__main__":
    cli()
