from shutil import which 

# Drivers
SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')

# Miscellaneous
BOT_NAME = "willhaben"

SPIDER_MODULES = ["willhaben.spiders"]
NEWSPIDER_MODULE = "willhaben.spiders"

ROBOTSTXT_OBEY = False

# Selenium settings
DOWNLOADER_MIDDLEWARES = {
    'willhaben.middlewares.SeleniumMiddleware': 800
}

#USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    'willhaben.pipelines.DBWriterPipeline': 300,
}

# Database settings
POSTGRES_DB = 'scraped'
POSTGRES_USER = 'scraped'
POSTGRES_PASSWORD = 'scraped'
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432

# Output settings
FEEDS = {
    'output/results.json': {
        'format': 'json',
        'encoding': 'utf-8',
        'overwrite': True,
        'indent': 4
    },
}

LOG_LEVEL = 'INFO'