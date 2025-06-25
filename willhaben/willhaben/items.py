import scrapy
import re
from scrapy.item import Field, Item

from itemloaders.processors import TakeFirst, MapCompose, Join

def parse_price_input(value):
    """
    Process the input price string to a numeric float value.
    Handles formats like '€ 1.234,56', '1.234 VB', '€ 1234', etc.
    Takes the first valid value from a list and returns None if parsing fails.
    """
    
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if not value:
        return None
    try:
        # Remove non-numeric characters except . and ,
        cleaned_price = re.sub(r'[^\d,.]', '', value)
        # Replace thousands separator (.) and keep decimal separator (,)
        cleaned_price = cleaned_price.replace('.', '').replace(',', '.')
        return float(cleaned_price)
    except (ValueError, AttributeError):
        return None

class WillhabenItem(Item):
    willhaben_code = Field(output_processor=TakeFirst())
    breadcrumbs = Field(output_processor=TakeFirst())
    title = Field(output_processor=TakeFirst())
    price = Field(output_processor=parse_price_input)
    contact_address = Field(output_processor=TakeFirst())
    location = Field(output_processor=TakeFirst())
    description = Field(output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    data = Field(output_processor=TakeFirst())