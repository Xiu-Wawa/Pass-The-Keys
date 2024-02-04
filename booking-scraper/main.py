import concurrent.futures
from src.utils.logger import create_logger

from src.spiders import (
    booking
)


def run_spider(spider_class):
    """Run a single spider.

    Args:
        spider_class: The spider class to run.
    """
    logger = create_logger(spider_class.__name__)
    spider = spider_class(logger)

    try:
        spider.run()
    except Exception as e:
        return spider.spider_name, str(e)
    

def run_all_spiders():
    selenium_spiders = [
        booking.Booking
    ]

    for spider in selenium_spiders:
        result = run_spider(spider)
        if result:
            spider_name, error = result
            print(f"Spider {spider_name} encountered an error: {error}")


if __name__ == '__main__':
    run_all_spiders()