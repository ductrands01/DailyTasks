import logging


class Logger:
    @staticmethod
    def get_logger():
        # Configure the logger
        logger = logging.getLogger("DataCrawlerLogger")
        logger.setLevel(logging.INFO)

        # Create handler
        handler = logging.FileHandler('DataCrawler/Log/System.log')
        handler.setLevel(logging.INFO)

        # Create formatter and add to handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to logger
        if not logger.hasHandlers():
            logger.addHandler(handler)

        return logger
