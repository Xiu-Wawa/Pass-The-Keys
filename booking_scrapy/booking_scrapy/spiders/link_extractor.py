import scrapy
import logging

class Booking(scrapy.Spider):
    name = 'link_extractor'
    LOCATION_NAME = 'Mayfair'
    logger = logging.getLogger(__name__)
    OFFSET_MAX = 1000

    def start_requests(self):
        with open(f'data/input/{self.LOCATION_NAME}', 'r') as file:
            urls = [line.strip() for line in file]

            for url in urls:
                self.logger.info(f"Processing URL: {url}")
                yield scrapy.Request(url=url, callback=self.parse_pagination, cb_kwargs={'url': url})

    def parse_pagination(self, response, url):
        self.logger.info(f'Getting Property Links: {url}')

        try:
            pagination = response.xpath('//div[@data-testid="pagination"]//ol/li[last()]/button/text()').get().strip()
        except:
            pagination = 0
            self.logger.info(f'Only Page')

        pagination_param = (int(pagination) * 25)

        for page in range(0, pagination_param, 25):
            self.logger.info(f'Extracting Property Links - Page: {page // 25 + 1}')
            property_url = f'{url}&offset={page}'

            yield scrapy.Request(url=property_url, callback=self.parse_property_links, dont_filter=True)

    def parse_property_links(self, response):
        property_tags = response.xpath('//div[@data-testid="property-card"]//h3/a/@href').getall()

        for href in property_tags:
            url = href

            property_links = {
                "url": url
            }

            self.logger.info(f'Successfully Append Link')
            yield property_links
