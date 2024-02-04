from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

from typing import Optional
from logging import Logger
import time
import json
import re
import os
import csv
import requests

from src.spiders.base_spider import BaseSpider
from src.utils import wait_element
from src.locators.booking_locators import*


class Booking(BaseSpider):
    INPUT_FOLDER = 'data/input'
    MAX_RETRIES = 5
    OFFSET = 1000
    OUTWARD_CODES = ['CT8', 'CT9', 'CT10', 'CT11', 'CT12']

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.logger = logger if logger else self.logger.getLogger(__name__)
        super().__init__(self.logger)

        self.sleep = wait_element

    
    def get_response(self, url) -> None:
        self.logger.info(f'Getting Response: {url}')
        response = requests.get(url)
        time.sleep(2)

        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')

            return soup
        else:
            return None

    
    def get_property_links(self, url) -> list:
        self.logger.info('Getting Property Links....')
        property_links = []
        x = 0

        while x < self.OFFSET:
            self.logger.info(f'Extracting Links on Page: {x // 25 + 1}')
            response = self.get_response(f'{url}&offset={x}')

            if response:
                property_cards = response.select('h3 a')
                
                if property_cards:
                    for link in property_cards:
                        href = link.get('href')
                        property_links.append(href)
                else:
                    break

            x += 25

        return property_links
    

    def get_property_details(self, url, location_filename):
        response = self.get_response(url)
        self.logger.info(f'Getting Property Details for: {url}')
        
        if response:
            script = response.select_one('script[type="application/ld+json"]')
            if script:
                json_string = script.string
                json_data = json.loads(json_string)

                name = json_data.get('name', None)
                description = json_data.get('description', None)

                # Location
                country = json_data.get('address', {}).get('addressCountry', None).strip()
                postal_code = json_data.get('address', {}).get('postalCode', None).strip()
                outward_code = postal_code.split(' ')[0]

                if outward_code not in self.OUTWARD_CODES:
                    self.logger.info(f'{outward_code} is not in: {self.OUTWARD_CODES}')
                    return

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

                property_type_text = response.select_one('h1 a.bui_breadcrumb__link_masked').text
                property_type = self.extract_property_type(property_type_text)

                try:
                    manager = response.select_one('h2 div:-soup-contains("Hosted"), h2 div.e1f827110f:-soup-contains("Managed by")').text
                except:
                    manager = ''

                try:
                    status_divs = response.select_one('div[data-testid="property-highlights"] div ul li div:nth-of-type(2) div')
                    for div in status_divs:
                        status_text = div.text

                        if any(keyword in status_text.strip().title() for keyword in ["Houses", "Apartments", "Entire"]):
                            status = status_text.strip().title()

                        else:
                            status = ''
                except:
                    status = ''
                    self.logger.info(f"Failed to get Status: {url}")

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

                try:
                    self.append_data_to_csv(data, f'data/output/{location_filename}.csv')
                    self.logger.info(f"Data Succesfully Append to CSV")
                except Exception as e:
                    self.logger.info(f'Failed to Append Data on CSV \n {e}')
            

    def extract_property_type(self, property_type):
        pattern = r"\(.*?\)"
        return re.findall(pattern, property_type)[0].strip(")(")
    

    def append_data_to_csv(self, data, filename):
        file_exists = os.path.exists(filename)

        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            
            if not file_exists or os.stat(filename).st_size == 0:
                writer.writeheader()

            writer.writerow(data)


    def save_property_links_to_csv(self, links, output_filename):
        with open(f'data/property links/{output_filename}.csv', 'w', newline='') as csvfile:
            fieldnames = ['urls']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()  

            for link in links:
                writer.writerow({'urls': link})

    
    def run(self) -> None:
        """
        Run the scraper to collect data.
        """
        self.logger.info("Running scraper.")

        try:
            for filename in os.listdir(self.INPUT_FOLDER):
                file_path = os.path.join(self.INPUT_FOLDER, filename)
                if os.path.isfile(file_path):
                    location_filename = filename

                    with open(file_path, 'r') as file:
                        all_property_links = []
                        for line in file:
                            url = line.strip()

                            property_links = self.get_property_links(url)
                            all_property_links.extend(property_links)
                            time.sleep(3)

                        unique_all_property_links = list(set(all_property_links))
                        self.save_property_links_to_csv(unique_all_property_links, location_filename)

                    time.sleep(10)

                    with open(f'data/property links/{location_filename}', 'r') as property_links_file:
                        reader = csv.DictReader(property_links_file)
                        for row in reader:
                            property_url = row['urls']

                            try:
                                self.get_property_details(property_url, location_filename)
                            except Exception as e:
                                self.logger.error(f"Got an error on Getting Property Details: {[property_url]}\n{e}")
                

        except Exception as err:
            self.logger.error(f"An error occured while scraping: {str(err)}")

        finally:
            self.close_browser()