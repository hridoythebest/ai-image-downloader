import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import base64
from concurrent.futures import ThreadPoolExecutor

def read_products(file_path):
    with open(file_path, 'r') as file:
        products = [line.strip() for line in file.readlines()]
    return products

def download_image(url, folder_path, file_name):
    if url.startswith('http'):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(folder_path, file_name), 'wb') as file:
                for chunk in response:
                    file.write(chunk)
    elif url.startswith('data:image'):
        header, encoded = url.split(',', 1)
        data = base64.b64decode(encoded)
        with open(os.path.join(folder_path, file_name), 'wb') as file:
            file.write(data)

def search_and_download_images(product, download_path):
    options = webdriver.ChromeOptions()
    options.headless = True  # Run browser in headless mode
    driver = webdriver.Chrome(options=options)
    
    search_url = 'https://www.google.com/imghp?hl=en&ogbl'
    driver.get(search_url)
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(f'{product} PNG HD Image' + Keys.RETURN)
    time.sleep(2)  # Wait for the images to load

    # Scroll down to load more images
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    # Find image elements
    img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')

    for idx, img_element in enumerate(img_elements[:10]):  # Limiting to the first 10 images
        img_url = img_element.get_attribute('src')
        if img_url:
            file_name = f'{product}_{idx + 1}.png'
            download_image(img_url, download_path, file_name)

    driver.quit()

if __name__ == "__main__":
    products_file = 'products.txt'
    download_folder = 'downloaded_images'

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    products = read_products(products_file)
    
    # Using ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search_and_download_images, product, download_folder) for product in products]
        for future in futures:
            future.result()  # Ensure any exceptions are raised

    print("Download completed!")
