import img2pdf
import cloudscraper
from typing import NoReturn
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
import sys
import time
import threading
from pathlib import Path
from math import trunc
import io
from PIL import Image

nhpdf_dir = Path.home()/"Documents"/"nhpdf"
nhpdf_dir.mkdir(parents=True, exist_ok=True) 

scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
    }
)

def loading_animation() -> NoReturn:
    global la, pages, page
    spinner = ['|', '/', '-', '\\']
    while not la:
        for frame in spinner:
            sys.stdout.write(f'\rDownloading the pages ({trunc(((page-1)/pages)*100)}%/{100}%)...{frame}')
            sys.stdout.flush()
            time.sleep(0.1)
            if la:  
                sys.stdout.write(f'\rDownloading the pages (100%/100%)...{frame}')
                sys.stdout.flush()
                break

def download_image(raw_url: str) -> bytes:
    global pages, page
    page += 1
    img_code, f_type = re.search(r'/(\d+)', raw_url['data-src']).group(), re.search(r'\b(.(jpg|jpeg|png|webp|gif|tiff|svg))\b', raw_url['data-src']).group()
    url = f'https://i3.nhentai.net/galleries{img_code}/{page}{f_type}'
    response = scraper.get(url)
    if response.status_code == 200:
        content = check_alpha(response.content)
        return content
    return None

def compile_images(raw: list, name: str) -> NoReturn:
    with ThreadPoolExecutor(max_workers=10) as executor:
        raw_images = list(executor.map(download_image, raw))
    for img in raw_images:
        check_alpha(img)
    nhpdf = nhpdf_dir/f"{name}.pdf"
    with open(nhpdf, "wb") as file:
        file.write(img2pdf.convert(raw_images))

def check_alpha(image: bytes) -> bytes:
    try:
        img2pdf.convert(image)
    except img2pdf.AlphaChannelError:
        buffered = io.BytesIO(image)
        img = Image.open(buffered)
        converted: Image = img.convert('RGB')
        buf = io.BytesIO()
        converted.save(buf, format='PNG')
        image = buf.getvalue() 
    return image


def start_nhpdf():
    global la, page, pages
    if len(sys.argv) < 2:
        print("Usage: nhpdf <doujin-code>\nExamples:\n1. nhpdf 566212\n2. nhpdf 566212 563102")
        return
    codes = sys.argv[1:] 
    items = len(codes)
    item = 0
    for code in codes:
        la = False
        page = 0
        item += 1
        try: 
            code = int(code)
        except Exception:
            print("\nThe code needs to be numbers (Ex: 177013) :) \n\ngoing to the next code...")
            continue
        url = f'https://nhentai.net/g/{code}/'
        response = scraper.get(url)
        try: 
            soup = BeautifulSoup(response.text, "html.parser")
            pages = len(soup.find_all(class_='gallerythumb'))
            name = soup.find(class_='pretty').text
            author = soup.find(class_='before').text
            raw_data = soup.find_all(class_='lazyload')
            if not author:
                author = '[NAME-MISSING]: They forgot to put the author name in the website.'
        except Exception:
            print("\n[ERROR]: The code cannot be found in the website.\n\ngoing to the next code...")
            continue
        print(f"\nH-Doujin Details:\nname: {name}\nauthor: {author}\npages: {pages}\n")
        raw_data.remove(raw_data[0])
        function_thread = threading.Thread(target=loading_animation)
        function_thread.start()
        compile_images(raw_data[:pages], name)
        la = True
        function_thread.join()
        if item != items:
            print(f"\n\n{name}.pdf was successfully downloaded\n\ngoing to the next code...")

    print(f"\n\nOperation was success, the pdf's was saved into the nhpdf folder in your documents folder.\n")
        
