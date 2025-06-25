import scrapy
from willhaben.http import SeleniumRequest
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from willhaben.items import WillhabenItem

class WillhabenURLsSpider(scrapy.Spider):
    
    name = 'willhaben_urls'
    allowed_domains = ['willhaben.at']
    
    # The maximum number of pages to scrape
    max_page = 9999
    
    # The current page number
    current_page = 1
    
    # Accept cookies and scroll to the bottom of the page
    SCROLL_SCRIPT = """
    var button = document.getElementById('didomi-notice-agree-button');
    if (button) {
        button.click();
    }
    window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: "smooth" });
    """
    
    def __init__(self, navigation_url=None, scrape_run_id=None, *args, **kwargs):
        super().__init__()
        
        if navigation_url is None:
            raise ValueError("A navigation URL must be provided. Use -a navigation_url=<URL>")
        
        self.navigation_url = navigation_url
        
        if '?' in navigation_url:
            self.start_urls = [navigation_url + f"&page={self.current_page}"]
        else:
            self.start_urls = [navigation_url + f"?page={self.current_page}"]
        
        self.url_selector = '[data-testid^="search-result-entry"][href^="/' + '/'.join(navigation_url.split('/')[3:5]) + '/d/"]::attr(href)'
        
    def start_requests(self):
        yield SeleniumRequest(
                url=self.start_urls[0],
                callback=self.parse,
                wait_time=5,
                script=self.SCROLL_SCRIPT
            )

    def parse(self, response):
        
        links = response.css(self.url_selector).getall()
        
        # Check if links are found, otherwise stop the spider
        if not links:
            self.logger.info(f"No links found on page {self.current_page}")
            return
        
        for link in links:
            # Convert relative URLs to absolute
            absolute_url = urljoin(response.url, link)
            loader = ItemLoader(item=WillhabenItem(), response=response)
            
            loader.add_value('url', absolute_url)
            loader.add_value('willhaben_code', link.split('/')[-2].split('-')[-1])
            
            yield loader.load_item()
        
        self.current_page += 1
        if self.current_page > self.max_page:
            return
        
        if '?' in self.navigation_url:
            next_page_url = self.navigation_url + f"&page={self.current_page}"
        else: 
            next_page_url = self.navigation_url + f"?page={self.current_page}"
            
        # Follow the next page
        yield SeleniumRequest(
            url=next_page_url,
            callback=self.parse,
            wait_time=5,
            script=self.SCROLL_SCRIPT,
        )
        
        
        