import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

class BuyRentKenyaScraper:
    def __init__(self, max_pages=157):
        self.base_url = "https://www.buyrentkenya.com/flats-apartments-for-sale/nairobi"
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

        # Title
        title_elem = listing.find('h3', class_='hide-title') or listing.find('h2', class_='font-semibold')
        property_data['title'] = title_elem.text.strip() if title_elem else 'N/A'

        # Price
        price_elem = listing.find('p', class_=lambda x: x and 'text-xl' in x)
        property_data['price'] = price_elem.text.strip() if price_elem else 'N/A'

        # Location
        location_elem = listing.find('p', class_=lambda x: x and 'text-sm' in x and 'truncate' in x)
        property_data['location'] = location_elem.text.strip() if location_elem else 'N/A'

        # Bedrooms
        bedrooms_elem = listing.find('span', {'data-cy': 'card-bedroom_count'})
        property_data['bedrooms'] = bedrooms_elem.text.strip() if bedrooms_elem else 'N/A'

        # Bathrooms
        bathrooms_elem = listing.find('span', {'data-cy': 'card-bathroom_count'})
        property_data['bathrooms'] = bathrooms_elem.text.strip() if bathrooms_elem else 'N/A'

        # Description
        desc_elem = listing.find('h5', class_=lambda x: x and 'mb-3' in x)
        property_data['description'] = desc_elem.text.strip() if desc_elem else 'N/A'

        # URL
        link_elem = listing.find('a', href=True)
        property_data['url'] = urljoin(self.base_url, link_elem['href']) if link_elem else 'N/A'

        # Main Image
        main_img = listing.find('img', class_='h-42')
        property_data['main_image'] = main_img['src'] if main_img else 'N/A'

        # Additional Images
        additional_imgs = listing.find_all('img', class_='h-16')
        property_data['additional_images'] = ';'.join([img['src'] for img in additional_imgs]) if additional_imgs else 'N/A'

        # Agency
        agency_elem = listing.find('a', {'data-cy': 'agency-logo'})
        property_data['agency'] = agency_elem.get('href', 'N/A') if agency_elem else 'N/A'

        return property_data

    def scrape_properties(self):
        # Scrape page 1 (no parameters)
        print(f"Scraping page 1: {self.base_url}")
        soup = self.get_page_content(self.base_url)
        if soup:
            listings = soup.find_all('div', class_='listing-card')
            if listings:
                for listing in listings:
                    property_data = self.extract_property_details(listing)
                    self.properties.append(property_data)
            else:
                print("No listings found on page 1")
        else:
            print("Failed to fetch page 1")

        time.sleep(2)  # Delay after page 1

        # Scrape pages 2 to max_pages
        for page in range(2, self.max_pages + 1):
            url = f"{self.base_url}?page={page}"
            print(f"Scraping page {page}: {url}")

            soup = self.get_page_content(url)
            if not soup:
                break

            listings = soup.find_all('div', class_='listing-card')
            if not listings:
                print("No more listings found")
                break

            for listing in listings:
                property_data = self.extract_property_details(listing)
                self.properties.append(property_data)

            time.sleep(2)  # Be respectful to the server

    def save_to_csv(self, filename='buyrentkenya_apartments.csv'):
        if not self.properties:
            print("No properties to save")
            return

        fieldnames = ['title', 'price', 'location', 'bedrooms', 'bathrooms',
                     'description', 'url', 'main_image', 'additional_images', 'agency']

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.properties)

        print(f"Saved {len(self.properties)} properties to {filename}")

def main():
    scraper = BuyRentKenyaScraper(max_pages=157)
    scraper.scrape_properties()
    scraper.save_to_csv()

if __name__ == "__main__":
    main()