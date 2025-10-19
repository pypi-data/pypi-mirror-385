"""Main module for uncertainAPI."""

import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the application."""
    logger.info("uncertainAPI started")
    # Your main application logic here


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
