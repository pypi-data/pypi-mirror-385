import requests
from concurrent.futures import ThreadPoolExecutor
import time
import img2pdf





def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content  # or save to file here
 




image_urls = [
    "https://i3.nhentai.net/galleries/3311475/1.webp", 
    "https://i3.nhentai.net/galleries/3311475/2.webp",
    "https://i3.nhentai.net/galleries/3311475/3.webp",
    "https://i3.nhentai.net/galleries/3311475/4.webp",
    "https://i3.nhentai.net/galleries/3311475/5.webp",
    "https://i3.nhentai.net/galleries/3311475/6.webp",
    "https://i3.nhentai.net/galleries/3311475/7.webp",
    "https://i3.nhentai.net/galleries/3311475/8.webp",
    "https://i3.nhentai.net/galleries/3311475/9.webp",
    "https://i3.nhentai.net/galleries/3311475/10.webp",   
    "https://i3.nhentai.net/galleries/3311475/11.webp", 
    "https://i3.nhentai.net/galleries/3311475/12.webp",  
    "https://i3.nhentai.net/galleries/3311475/13.webp", 
    "https://i3.nhentai.net/galleries/3285893/21.jpg",           
    ]

with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_image, image_urls))

with open("test.pdf", "wb") as file:
     file.write(img2pdf.convert(results))