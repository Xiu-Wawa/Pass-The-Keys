from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

import time


class BaseSpider:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def __init__(self, logger=None):
        """Initialize the BaseSpider class.

        Args:
            logger: Logger object for logging.
        """
        self.logger = logger

        self.logger.info(f"Initializing {self.__class__.__name__.lower()} scraper.")

        # Number of retries for driver initialization
        max_retries = 5

        for retry_count in range(max_retries):
            try:
                # Chrome browser options setup
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument(f'user-agent={self.user_agent}')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument('--disable-notifications')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--ignore-certificate-errors')
                chrome_options.add_argument('--disable-cookies')
                chrome_options.add_argument('--disable-application-cache')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option('prefs', {'profile.default_content_settings.cookies': 2})

                self.browser = webdriver.Chrome(
                    service=Service(executable_path=ChromeDriverManager().install()),
                    options=chrome_options
                )
                break

            except Exception as e:
                self.logger.info(f'Failed to initialize WebDriver (Attempt {retry_count + 1}/{max_retries}): {str(e)}')
                if retry_count < max_retries - 1:
                    # Sleep for a while before retrying
                    time.sleep(10)
                else:
                    raise


    def close_browser(self):
        """Closes the browser."""
        self.logger.info("Closing browser.")
        self.browser.quit()