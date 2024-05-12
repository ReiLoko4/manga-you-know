from pathlib import Path

import requests
from bs4 import BeautifulSoup


class AoAshiDl:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'authority': 'ao-ashimanga.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Opera GX";v="99", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0',
        })

    def get_chapters(self) -> list:
        response = self.session.get('https://ao-ashimanga.com/')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_chapters = []
        for divs in soup.find_all('div'):
            if len(divs) == 0:
                continue
            if 'comic-thumb-title' in divs.get('class'):
                chapter = divs.find('a')['href'].split('/')[-2]
                chapter = chapter.replace('ao-ashi-chapter-', '')
                chapter = chapter.replace('-', '.')
                list_chapters.append(chapter)

        def sorter(e):
            return float(e)

        list_chapters.sort(key=sorter, reverse=True)
        return list_chapters

    def get_chapters_urls(self) -> list | bool:
        response = self.session.get('https://ao-ashimanga.com/')
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_chapters_urls = []
        for divs in soup.find_all('div'):
            if len(divs) == 0:
                continue
            if 'comic-thumb-title' in divs.get('class'):
                list_chapters_urls.append(divs.find('a')['href'])

        def sorter(e):
            num = str(e).split('/')[-2]
            num = num.replace('ao-ashi-chapter-', '')
            num = num.replace('-', '.')
            return float(num)

        list_chapters_urls.sort(key=sorter, reverse=True)
        return list_chapters_urls

    def get_chapter_images_url(self, chapter_or_url) -> list | bool:
        if '/' in chapter_or_url:
            url = chapter_or_url
        else:
            url = f'https://ao-ashimanga.com/manga/ao-ashi-chapter-{chapter_or_url}'
        response = self.session.get(url)
        if not response:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        list_images = []
        for item in soup.find_all('img'):
            list_images.append(item['src'])
        return list_images

    def download_manga_chapter(self, chapter_or_url) -> bool:
        list_images = self.get_chapter_images_url(chapter_or_url)
        if not list_images:
            return False
        for i, image in enumerate(list_images):
            page = self.session.get(image)
            if not page:
                continue
            chapter_local = Path(f'ao-ashi/{chapter_or_url}')
            chapter_local.mkdir(parents=True, exist_ok=True)
            with open(f'{chapter_local}/{i:04d}.jpg', 'wb') as file:
                for data in page.iter_content(1024):
                    file.write(data)
        return True
