import psycopg2
import json
from scrapy.exceptions import DropItem

class DBWriterPipeline:
    def __init__(self, db_params):
        self.db_params = db_params
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        # Retrieve database parameters from Scrapy settings
        db_params = {
            'dbname': crawler.settings.get('POSTGRES_DB', 'scraped'),
            'user': crawler.settings.get('POSTGRES_USER', 'scraped'),
            'password': crawler.settings.get('POSTGRES_PASSWORD', 'scraped'),
            'host': crawler.settings.get('POSTGRES_HOST', 'localhost'),
            'port': crawler.settings.get('POSTGRES_PORT', 5432)
        }
        return cls(db_params)

    def open_spider(self, spider):
        # Establish database connection
        try:
            self.connection = psycopg2.connect(**self.db_params)
            self.cursor = self.connection.cursor()
            # Create table if it doesn't exist
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS willhaben_runs (
           		scrape_run_id serial primary key,
           		navigation_url TEXT NOT NULL,
           		description TEXT DEFAULT NULL
            );
            
            CREATE TABLE IF NOT EXISTS willhaben_items (
                willhaben_code TEXT NOT NULL,
                breadcrumbs TEXT DEFAULT NULL,
                scraped_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                url TEXT NOT NULL,
                title TEXT DEFAULT NULL,
                price NUMERIC DEFAULT NULL,
                description TEXT DEFAULT NULL,
                location TEXT DEFAULT NULL,
                contact_address TEXT DEFAULT NULL,
                data JSONB DEFAULT NULL,
                PRIMARY KEY(willhaben_code),
                scrape_run_id integer REFERENCES willhaben_runs (scrape_run_id)
            );
            """)
            
            if spider.name == "willhaben_urls":
                # Insert a new scrape run record
                self.cursor.execute("""
                    INSERT INTO willhaben_runs (navigation_url, description)
                    VALUES (%s, %s)
                    RETURNING scrape_run_id;
                """, (spider.start_urls[0], "Scrape run for URLs"))
                self.scrape_run_id = self.cursor.fetchone()[0]
                spider.logger.info(f"Scrape run ID: {self.scrape_run_id}")
                
            self.connection.commit()
        except Exception as e:
            spider.logger.error(f"Failed to connect to database: {e}")
            raise

    def close_spider(self, spider):
        # Close database connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def process_item(self, item, spider):
        try:
            # Convert Scrapy item to dictionary
            item_dict = dict(item)
            
            # Check if required fields are present
            if not all(field in item_dict for field in ['willhaben_code']):
                raise DropItem(f"Missing field in items: {item_dict}")
            
            spider.logger.info(f"Processing item with id: {item_dict['willhaben_code']}")
            
            # Insert item into database
            if spider.name == "willhaben_urls":
                self.cursor.execute("""
                    INSERT INTO willhaben_items (willhaben_code, url, scrape_run_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (willhaben_code) DO UPDATE
                    SET scrape_run_id = EXCLUDED.scrape_run_id;
                    ;
                """, (item_dict['willhaben_code'], item_dict['url'], self.scrape_run_id))
                    
            if spider.name == "willhaben_items":
                self.cursor.execute("""
                    UPDATE willhaben_items
                    SET title = %s,
                        breadcrumbs = %s,
                        price = %s,
                        contact_address = %s,
                        location = %s,
                        data = %s,
                        description = %s,
                        scraped_time = CURRENT_TIMESTAMP
                    WHERE willhaben_code = %s;
                    """,(item_dict['title'],
                        item_dict['breadcrumbs'],
                        item_dict['price'],
                        item_dict['contact_address'],
                        item_dict['location'],
                        json.dumps(item_dict['data']),
                        item_dict['description'],
                        item_dict['willhaben_code']))    
                
            self.connection.commit()
            
            return item
        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Failed to insert item: {e}")
            raise DropItem(f"Failed to process item: {item_dict}")