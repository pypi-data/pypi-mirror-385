from typing import Dict, Set
from sports31.logging_config import setup_logger


logger = setup_logger(__name__)


def load_config(configdict: Dict, ovset: Set, localdict: Dict):
    if not ovset:
        localdict.update(configdict)
    else:
        for k in ovset:
            if k not in configdict:
                continue
            localdict[k] = configdict[k]
            logger.debug(f"{k}, {localdict[k]}, {type(localdict[k])}")
    logger.debug(f"{configdict}")
