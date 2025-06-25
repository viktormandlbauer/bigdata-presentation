import scrapy
from bs4 import BeautifulSoup

from willhaben.items import WillhabenItem
from scrapy.loader import ItemLoader

from willhaben.http import SeleniumRequest

from scrapy.utils.project import get_project_settings

from time import sleep

class WillhabenItemSpider(scrapy.Spider):
    name = 'willhaben_items'
    allowed_domains = ['willhaben.at']
    settings=get_project_settings()
    
    def __init__(self, item_url=None, scrape_run_id=None, selenium=True, *args, **kwargs):
        super().__init__()
        self.selenium = selenium
        
        if item_url is None and scrape_run_id is None:
            raise ValueError("Either item_url or scrape_run_id must be provided. Use -a item_url=<URL> or -a scrape_run_id=<ID>")
        
        if item_url:
            self.start_urls = [item_url]
            
        if self.selenium:
            self.custom_settings = {
                'DOWNLOADER_MIDDLEWARES': {
                    'willhaben.middlewares.SeleniumMiddleware': 543,
                }
            }
        else:
            self.custom_settings = {
                'DOWNLOADER_MIDDLEWARES': {
                    'willhaben.middlewares.SeleniumMiddleware': None,
                }
            }
        
        if scrape_run_id:
            import psycopg2
            
            self.logger.info(f"Scrape run ID: {scrape_run_id}")
            
            db_params = {
                'dbname': self.settings.get('POSTGRES_DB', 'scraped'),
                'user': self.settings.get('POSTGRES_USER', 'scraped'),
                'password': self.settings.get('POSTGRES_PASSWORD', 'scraped'),
                'host': self.settings.get('POSTGRES_HOST', 'localhost'),
                'port': self.settings.get('POSTGRES_PORT', 5432)
            }
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()
            cursor.execute("SELECT url FROM willhaben_items WHERE scrape_run_id = %s AND data IS NULL;", (scrape_run_id,))
            self.start_urls = [url[0] for url in cursor.fetchall()] 
            self.logger.info(f"Scraping {len(self.start_urls)} items") 

    def start_requests(self):
        for url in self.start_urls:
            if self.selenium:
                yield SeleniumRequest(
                    url=url,
                    callback=self.parse,
                    wait_time=5
                )
            else:
                yield scrapy.Request(url, callback=self.parse)
            sleep(self.settings.get('DOWNLOAD_DELAY', 5))

    def parse(self, response):
        # Parse response with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract breadcrumbs
        breadcrumbs = ",".join([item.text for item in soup.select('[data-testid*="breadcrumbs-item"]')][:int(len(soup.select('[data-testid*="breadcrumbs-item"]'))/2)])
        
        # Willhaben Code 
        willhaben_code = soup.select('[data-testid="ad-detail-ad-wh-code-top"]')[0].text.split(" ")[-1] if soup.select('[data-testid="ad-detail-ad-wh-code-top"]') else ''

        # Title
        title = soup.select('[data-testid="ad-detail-header-sticky"]')[0].text.strip() if soup.select('[data-testid="ad-detail-header-sticky"]') else ''

        # Price
        price = soup.select('[data-testid*="contact-box-price-box-price-value"]')[0].text.strip() if soup.select('[data-testid*="contact-box-price-box-price-value"]') else ''

        # Contact Address
        contact_address = '\n'.join([span.text for span in soup.select('[data-testid="top-contact-box-address-box"]')[0].find_all('span')]) if soup.select('[data-testid="top-contact-box-address-box"]') else ''

        # Location
        location = soup.select('[data-testid*="location"]')[0].text.strip() if soup.select('[data-testid*="location"]') else ''
        
        # Initialize data dictionary
        data = {}

        # Attribute Groups
        for group in soup.select('[data-testid="attribute-group"]'):
            
            if group.find('h3'):
                group_title = group.find('h3').text.strip()
            else:
                group_title = group.find_previous('h2').text.strip() if group.find_previous('h2') else 'Attributes'
        
            titles = [div.get_text().strip() for div in group.select('[data-testid="attribute-title"]')]
            values = [div.get_text().strip() for div in group.select('[data-testid="attribute-value"]')]
            data[group_title] = dict(zip(titles, values))

        # Price Information Box
        if soup.select('[data-testid="price-information-box"]'):
            price_info_box = soup.select('[data-testid="price-information-box"]')[0]
            price_info_title = price_info_box.find('h2').text.strip()
            labels = [div.get_text().strip() for div in price_info_box.select('[data-testid*="label"]')]
            values = [div.get_text().strip() for div in price_info_box.select('[data-testid*="value"]')]
            data[price_info_title] = dict(zip(labels, values))

        # Equipment Items
        if soup.select('[data-testid="equipment-item"]'):
            equipment_title = soup.select('[data-testid="equipment-item"]')[0].find_previous('h2').text.strip()
            equipment_values = [li.select('[data-testid="equipment-value"]')[0].text.strip() for li in soup.select('[data-testid="equipment-item"]')]
            data[equipment_title] = equipment_values

        # Description
        description = soup.select('[data-testid^="ad-description"]')[0].text.strip() if soup.select('[data-testid^="ad-description"]') else ''

        # Yield the extracted data
        loader = ItemLoader(item=WillhabenItem(), response=response)
        loader.add_value('willhaben_code', willhaben_code)
        loader.add_value('breadcrumbs', breadcrumbs)
        loader.add_value('title', title)
        loader.add_value('price', price)
        loader.add_value('contact_address', contact_address)
        loader.add_value('location', location)
        loader.add_value('data', data)
        loader.add_value('description', description)
        loader.add_value('url', response.url)
        item = loader.load_item()
        
        for field in WillhabenItem.fields:
            item.setdefault(field, None)
        
        yield item