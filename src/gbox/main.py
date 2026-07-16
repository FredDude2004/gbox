import argparse
import logging

from .database import init_db
from .logger import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Run the project application.")
    parser.add_argument(
        "--debug", action="store_true", help="Turn on verbose debug logging."
    )

    args = parser.parse_args()

    setup_logging(debug_mode=args.debug)

    logger = logging.getLogger(__name__)
    logger.info("Starting GBox...")

    init_db()


if __name__ == "__main__":
    main()
