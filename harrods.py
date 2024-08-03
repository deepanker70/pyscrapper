import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

ITEMS_PER_PAGE = 60

def fetch_product_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/' 
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        json_script = soup.find('script', type='application/ld+json')
        if json_script:
            json_data = json_script.string
            try:
                data = json.loads(json_data)
                
                number_of_items = data.get('numberOfItems', 0)
                print(f"Number of Items: {number_of_items}")
                
                if 'itemListElement' in data:
                    product_urls = [item['url'] for item in data['itemListElement']]
                    
                    product_urls = [url.replace('/shopping/shopping/', '/shopping/') for url in product_urls]
                    product_urls = [urljoin('https://www.harrods.com', url) for url in product_urls]
                    
                    return product_urls, number_of_items
                else:
                    print('No itemListElement found in JSON data.')
                    return [], 0
            except Exception as e:
                print(f'Error parsing JSON: {e}')
                return [], 0
        else:
            print('No <script> tag with type "application/ld+json" found.')
            return [], 0
    else:
        print(f'Error fetching URL: Status code {response.status_code}')
        return [], 0

def fetch_product_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/'  
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.title.string if soup.title else 'No title found'
        
        try:
            brand_element = soup.find('p', {'data-test': 'buyingControl-brand'})
            brand_text = brand_element.get_text(strip=True) if brand_element else 'Brand not found'
        except Exception as e:
            print(f'Error finding brand: {e}')
            brand_text = 'Brand not found'
        
        try:
            product_title_element = soup.find('h1', {'data-test': 'buyingControl-name'})
            product_title_text = product_title_element.get_text(strip=True) if product_title_element else 'Product title not found'
        except Exception as e:
            print(f'Error finding product title: {e}')
            product_title_text = 'Product title not found'
        
        try:
            price_element = soup.find('span', {'data-test': 'product-price'})
            price_text = price_element.get_text(strip=True) if price_element else 'Price not found'
        except Exception as e:
            print(f'Error finding price: {e}')
            price_text = 'Price not found'
        
        image_urls = []
        try:
            image_elements = soup.find_all('img', {'data-test': 'product-image'})
            image_urls = [img['src'] for img in image_elements]
        except Exception as e:
            print(f'Error finding images: {e}')
        
        return {
            'Title': title,
            'Brand': brand_text,
            'Product Title': product_title_text,
            'Price': price_text,
            'Image URLs': image_urls
        }
    else:
        return {
            'Status Code': response.status_code,
            'Title': None,
            'Brand': None,
            'Product Title': None,
            'Price': None,
            'Image URLs': None
        }

def main():
    base_url = 'https://www.harrods.com/en-gb/shopping/women-clothing-dresses'
    
    product_urls, number_of_items = fetch_product_urls(base_url)
    
    total_pages = (number_of_items // ITEMS_PER_PAGE) + (1 if number_of_items % ITEMS_PER_PAGE != 0 else 0)
    print(f"Total number of pages: {total_pages}")
    
    all_product_urls = []
    for page in range(1, total_pages + 1):
        page_url = f"{base_url}?pageindex={page}"
        print(f"Fetching page: {page_url}")
        product_urls, _ = fetch_product_urls(page_url)
        all_product_urls.extend(product_urls)
    
    print(f"Total product URLs fetched: {len(all_product_urls)}")
    
    for product_url in all_product_urls:
        product_details = fetch_product_details(product_url)
        print("\nProduct Details for URL:", product_url)
        for key, value in product_details.items():
            print(f"{key}: {value}")

if __name__ == '__main__':
    main()
