import logging
import coloredlogs
import verboselogs


def setup_logger(name, level=logging.INFO):
    fmt = r"%(asctime)s %(threadName)s %(funcName)s %(levelname)s %(message)s"
    verboselogs.install()
    coloredlogs.install(level=level)
    # coloredlogs.install(level=logging.INFO, fmt=fmt)
    # coloredlogs.install(level=logging.DEBUG)
    # logging.basicConfig(format=fmt, level=logging.INFO)
    # logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)

    # log_path = r"./log.runlog"
    # filehandler = logging.FileHandler(log_path, mode="a", encoding="utf8")
    # filefmt = "%(message)s"
    # filehandler.setFormatter(logging.Formatter(filefmt))
    # logger.addHandler(filehandler)

    return logger
