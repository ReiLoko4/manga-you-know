import re

from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class BetterAnimeDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://betteranime.net'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Referer': 'https://betteranime.net/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })
        self.session.cookies.update({
            'betteranime_session': 'eyJpdiI6IlVuRk5LRldvc3pJaWdHbThoVCtYSlE9PSIsInZhbHVlIjoiTkJvbitCOW1uMWpYSkxCNXNsdHJTYnJUaWFabCtMdlhhdElnVFYrTlgwUUFENUhPYlIrMW5WSE9BWEd5ZG5Ba1Nqbjlma1BqWTJqQ001eWsvdnZxL1Awa21OMU96SGRlV2FMZmNyalI0MTdHYjk0UlZCeXdHakdIV1FUcWVTRkIiLCJtYWMiOiI1MjM3OGY0OGIyOWM3MWQyNmE2NDQyZGExNDJjNDliNGZjMGFmOTk0NjY4NmI5ZTQ0NzU5ZjczODUyZWMzMDYzIiwidGFnIjoiIn0%3D'
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            f'{self.base_url}/pesquisa',
            params={
                'titulo': query
            }
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_results = soup.find_all('article', {'class': 'col-xl-2 col-lg-3 col-md-3 col-sm-4 col-6'})
            animes = []
            for article in article_results:
                a = article.find('a')
                split_url = a['href'].split('/')
                animes.append(
                    Manga(
                        id='/'.join(split_url[-2:]),
                        name=a['title'],
                        folder_name=split_url[-1],
                        cover=f'https:{article.find('img')['src']}'
                    )
                )
            return animes[:10]
        return False
    
    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/anime/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            li_results = soup.find_all('li', {'class': 'list-group-item list-group-item-action'})
            episodes = []
            for li in li_results:
                h3_text = li.find('h3').text
                episodes.append(
                    Chapter(
                        id='/'.join(li.find('a')['href'].split('/')[-3:]),
                        number=h3_text.split(' ')[-1] if not 'Especial' in h3_text else h3_text.replace('Episódio', '').strip(),
                    )
                )
            return episodes[::-1]
        return False
    
    def get_url_by_quality(self, quality_info: str) -> str | bool:
        response = self.session.post(
            f'{self.base_url}/changePlayer', 
            params={
                '_token': '6ShF7Z7eEiKuICaNk0AImZuNlpnEZ36mzzisYQjT',
                'info': quality_info
            }
        )
        if not response:
            return False
        response = self.session.get(response.json()['frameLink'])
        if not response:
            return False
        quality_match = re.search(r'"file":\s*"([^"]*)"', response.text)
        if quality_match:
            return quality_match.group(1).replace('\\', '')

    def get_episode_url(self, episode_id: str) -> list[Episode] | Episode | bool:
        response = self.session.get(f'{self.base_url}/anime/{episode_id}')
        if not response:
            return False
        url_and_label = []
        matches = re.findall(r'qualityString\["([^"]*)"\]\s*=\s*"([^"]*)"', response.text)
        for match in matches:
            quality = match[0]
            value = match[1]
            url = self.get_url_by_quality(value)
            if url:
                url_and_label.append([url, quality])
        if len(url_and_label) == 0:
            return False
        if len(url_and_label) == 1:
            return Episode(
                url=url_and_label[0],
                label='Padrão'
            )
        return [
            Episode(
                url=url,
                label=label,
            ) for url, label in url_and_label
        ][::-1]
    