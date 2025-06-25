# bigdata-scrapy

## Setup conda

### Installation

https://github.com/mozilla/geckodriver/releases

### Environment

```bash
python -m venv .

# MacOs/Linux
. bin/activate 

# Windows
.\Sripts\activate

pip install -r requirements.txt
```

### Testbench
```python
response = requests.get("https://www.willhaben.at/iad/gebrauchtwagen/d/auto/mazda-mazda3-gt-edition-2010-1841368769")
response = requests.get("https://www.willhaben.at/iad/kaufen-und-verkaufen/d/barbour-beaufort-sl-made-for-japan-1540084647")
response = requests.get("https://www.willhaben.at/iad/immobilien/d/mietwohnungen/oberoesterreich/linz/modern-sanierte-altbauwohnung-mit-balkon-und-garten-1500605247")

soup = BeautifulSoup(response.text, "html.parser")

# Title
soup.select('[data-testid="ad-detail-header-sticky"]')[0].text

# Price
soup.select('[data-testid*="contact-box-price-box-price-value"]')[0].text

# Contact Address
soup.select('[data-testid="top-contact-box-address-box"]')[0].text

# Location
if soup.select('[data-testid*="location"]'):
	soup.select('[data-testid*="location"]')[0].text

# Data
data = {}

for group in soup.select('[data-testid="attribute-group"]'):
	data[group.find_previous().text] = dict(zip([div.get_text().strip() for div in group.select('[data-testid="attribute-title"]')],
		[div.get_text().strip() for div in group.select('[data-testid="attribute-value"]')]))

if soup.select('[data-testid="price-information-box"]'):
	data[soup.select('[data-testid="price-information-box"]')[0].find('h2').text] = dict(zip([div.get_text().strip() for div in soup.select('[data-testid="price-information-box"]')[0].select('[data-testid*="label"]')],
				[div.get_text().strip() for div in soup.select('[data-testid="price-information-box"]')[0].select('[data-testid*="value"]')]))

if soup.select('[data-testid="equipment-item"]'):
	data[soup.select('[data-testid="equipment-item"]')[0].find_previous('h2').text]= [li.select('[data-testid="equipment-value"]')[0].text for li in soup.select('[data-testid="equipment-item"]')]

# Description
soup.select('[data-testid^="ad-description"]')[0].text
```