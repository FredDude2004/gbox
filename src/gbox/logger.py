import logging


def setup_logging(debug_mode: bool = False):
    """Configures global logging. Level is DEBUG if debug_mode is True, else INFO."""

    log_level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        filename="project.log",
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level,
    )

    if debug_mode:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
