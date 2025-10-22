import logging
from sports31.logging_config import setup_logger
from sports31.crawl import crawler
from sports31.processing_files.gpx import merge_gpx

logger = setup_logger(__name__)


if __name__ == "__main__":
    scripts_to_run = [crawler, merge_gpx]
    for script in scripts_to_run:
        logger.info(f"{script.__name__}")
        try:
            script.defaultmain()
        except Exception as e:
            logger.error(f"异常结束 {e}")
            break
