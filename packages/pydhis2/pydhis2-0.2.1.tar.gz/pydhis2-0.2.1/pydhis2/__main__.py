"""
Main entry point for pydhis2 CLI
Allows running: python -m pydhis2 [command]
"""

from pydhis2.cli.main import app


def main():
    """Main entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
