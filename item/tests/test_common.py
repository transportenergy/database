import logging

from item.common import init_log, log


def test_log(item_tmp_dir):
    init_log(file=True)

    # Log using the standard Python method
    logger = logging.getLogger("item")
    logger.info("Hello")

    # Log using a convenience function
    log("Hello, world!")

    # Configured log file contains the log records
    with open(item_tmp_dir / "item.log") as f:
        assert f.read() == "item.test_log: Hello\nitem.log: Hello, world!\n"
