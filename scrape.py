import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

class Property24Scraper:
    def __init__(self, max_pages=10000):  # Added max_pages parameter with default of 100
        self.base_url = "https://www.property24.co.ke/property-for-sale-in-nairobi-c1890"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.properties = []
        self.max_pages = max_pages

    def get_page_content(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def extract_property_details(self, listing):
        property_data = {}

        # Price
        price = listing.find('span', class_='p24_price')
        property_data['price'] = price.text.strip() if price else 'N/A'

        # Title
        title = listing.find('span', class_='p24_propertyTitle')
        property_data['title'] = title.text.strip() if title else 'N/A'

        # Location
        location = listing.find('span', class_='p24_location')
        property_data['location'] = location.text.strip() if location else 'N/A'

        # Address
        address = listing.find('span', class_='p24_address')
        property_data['address'] = address.text.strip() if address else 'N/A'

        # Description
        description = listing.find('span', class_='p24_excerpt')
        property_data['description'] = description.text.strip() if description else 'N/A'

        # Features
        features = listing.find('span', class_='p24_icons')
        if features:
            bedrooms = features.find('span', title='Bedrooms')
            property_data['bedrooms'] = bedrooms.find('span').text.strip() if bedrooms and bedrooms.find('span') else 'N/A'

            bathrooms = features.find('span', title='Bathrooms')
            property_data['bathrooms'] = bathrooms.find('span').text.strip() if bathrooms and bathrooms.find('span') else 'N/A'

            parking = features.find('span', title='Parking Spaces')
            property_data['parking'] = parking.find('span').text.strip() if parking and parking.find('span') else 'N/A'

            size = features.find('span', class_='p24_size')
            property_data['size'] = size.find('span').text.strip() if size and size.find('span') else 'N/A'

        # Listing URL
        link = listing.find('a', href=True)
        property_data['url'] = urljoin(self.base_url, link['href']) if link else 'N/A'

        # Image URL
        image = listing.find('image', src=True)
        property_data['image_url'] = image['src'] if image else 'N/A'

        return property_data

    def scrape_properties(self):
        page = 1
        while page <= self.max_pages:  # Modified to stop at max_pages
            url = f"{self.base_url}?Page={page}"
            print(f"Scraping page {page}: {url}")

            soup = self.get_page_content(url)
            if not soup:
                break

            # Find all property listings
            listings = soup.find_all('div', class_='p24_regularTile')
            if not listings:
                print("No more listings found")
                break

            for listing in listings:
                property_data = self.extract_property_details(listing)
                self.properties.append(property_data)

            page += 1
            time.sleep(2)  # Be respectful to the server

    def save_to_csv(self, filename='nairobi_properties.csv'):
        if not self.properties:
            print("No properties to save")
            return

        fieldnames = ['price', 'title', 'location', 'address', 'description',
                     'bedrooms', 'bathrooms', 'parking', 'size', 'url', 'image_url']

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.properties)

        print(f"Saved {len(self.properties)} properties to {filename}")

def main():
    scraper = Property24Scraper(max_pages=10000)  # Set maximum pages to 100
    scraper.scrape_properties()
    scraper.save_to_csv()

if __name__ == "__main__":
    main()