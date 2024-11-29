import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def fetch_page_content(url):
    """Fetch the content of a webpage."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_images(content, size=150):
    """Parse image URLs and titles from the webpage content."""
    soup = BeautifulSoup(content, 'html.parser')
    cards = soup.select('.gallerybox')
    items = []

    for card in cards:
        img_tag = card.find('img')
        if img_tag:
            img_url = img_tag['src']
            title = img_tag.get('alt', 'unknown')
            base_url = '/'.join(img_url.split('/')[:-1])
            high_res_url = f"{base_url}/{size}px-{img_url.split('/')[-1]}"

            items.append({
                'title': title,
                'url': f"https:{high_res_url}"
            })

    return items

def save_image(image_url, save_path):
    """Download and save an image with a custom User-Agent header."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(image_url, headers=headers)
    response.raise_for_status()
    
    image = Image.open(BytesIO(response.content))
    image.save(save_path, format='PNG')

def scrape_and_save_images(base_url, folder_name, size=150):
    """Scrape images from a Wikipedia page and save them to a folder."""
    os.makedirs(folder_name, exist_ok=True)

    content = fetch_page_content(base_url)
    items = parse_images(content, size=size)

    for item in items:
        title = item['title'].replace('/', '_').replace(' ', '_')
        save_path = os.path.join(folder_name, f"{title}.png")

        try:
            print(f"Downloading {title}...")
            save_image(item['url'], save_path)
        except Exception as e:
            print(f"Failed to download {title}: {e}")

if __name__ == "__main__":
    # URLs for the Wikipedia pages
    province_url = "https://id.wikipedia.org/wiki/Daftar_lambang_provinsi_di_Indonesia"
    regency_url = "https://id.wikipedia.org/wiki/Daftar_lambang_kabupaten_dan_kota_di_Indonesia"

    # Scrape and save province images
    scrape_and_save_images(province_url, "provinces", size=500)

    # Scrape and save regency images
    scrape_and_save_images(regency_url, "regencies", size=500)