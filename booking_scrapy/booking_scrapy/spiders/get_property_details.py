import scrapy
import logging
import json
import re
import csv
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

class Booking(scrapy.Spider):
    name = 'get_property_details'
    LOCATION_NAME = 'Shropshire'
    logger = logging.getLogger(__name__)
    OFFSET_MAX = 1000
    OUTWARD_CODES = ['SY1', 'SY2', 'SY3', 'SY4', 'SY5', 'SY6']


    def start_requests(self):
        with open(f'data/property_links/{self.LOCATION_NAME}.csv', 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                url = row['url']
                self.logger.info(f"Processing URL: {url}")
                yield scrapy.Request(url=url, callback=self.parse_property_details, dont_filter=True)


    def parse_property_details(self, response):
        self.logger.info(f'Getting Property Details: {response.url}')
        script = response.xpath('//script[@type="application/ld+json"]/text()').get()
        json_data = json.loads(script)

        if json_data:
            name = json_data.get('name', None)
            description = json_data.get('description', None)

            # Location
            country = json_data.get('address', {}).get('addressCountry', None).strip()
            postal_code = json_data.get('address', {}).get('postalCode', None).strip()
            outward_code = postal_code.split(' ')[0]

            if outward_code in self.OUTWARD_CODES:
                county = json_data.get('address', {}).get('addressRegion', None).strip()
                city = json_data.get('address', {}).get('streetAddress', None).split(',')[-3].strip()

                address_locality = json_data.get('address', {}).get('addressLocality', None)
                if address_locality:
                    locality_parts = [part.strip() for part in address_locality.split(',')]
                    address1 = locality_parts[0] if locality_parts else None
                    address2, address3 = locality_parts[1:3] + [None] * (3 - len(locality_parts))
                else:
                    address1 = city
                    address2 = address3 = ''

                property_type_text = response.xpath('//h1/a[@class="bui_breadcrumb__link_masked"]/text()').get()
                property_type = self.extract_property_type(property_type_text)

                try:
                    manager = response.xpath("//h2/div[contains(text(), 'Hosted')]/text() | //h2/div[@class='e1f827110f' or contains(text(), 'Managed by')]/text()").get()
                except:
                    manager = ''

                try:
                    status = response.xpath('//div[@data-testid="property-highlights"]//div[contains(text(), "Entire") or contains(text(), "Apartments") or contains(text(), "Houses")]/text()').get()
                except:
                    status = ''

                data = {
                    "name": name,
                    "description": description,
                    "address1": address1,
                    "address2": address2,
                    "address3": address3,
                    "city": city,
                    "county": county,
                    "postcode": postal_code,
                    "country": country,
                    "animal": '',
                    "pet_name": '',
                    'renewal_date': '',
                    'date': '',
                    "outward_code": outward_code,
                    "Type of Property": property_type,
                    "Current Manager": manager,
                    "Status": status
                }
                
                self.logger.info(f'Successfuly Append Data')
                yield data

            else:
                self.logger.info(f'{outward_code} is not in: {self.OUTWARD_CODES}')

    def extract_property_type(self, property_type):
        pattern = r"\(.*?\)"
        return re.findall(pattern, property_type)[0].strip(")(")