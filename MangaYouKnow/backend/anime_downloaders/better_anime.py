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
        self.episode_headers = self.session.headers.copy()
        self.episode_headers['Sec-Fetch-Dest'] = 'iframe'
        self.episode_headers['Cookie'] = '__ddg1_=mxDbK7MpYf7husQpsgEV; newBetterCountry=eyJpdiI6IjNyNHJVb016Qk1ocmdZVDQydU1hTmc9PSIsInZhbHVlIjoia0lyK2JKNXVQKzhoSUlmcFlXeWdaR1dmVFgybkVURGk2cEo5WkZiOGwzV1crb1lsejZOZ1JYai82S2o0S3ZrVVJDSndiNUFLR0tsMHp2elJJV25iSXplMGFwZCt3SlhLcDNEbmIxQnRYVGc9IiwibWFjIjoiMThmNGMxMmQ4YTNjMmFhNDljZDg1ZDc3NGRhOTFjNDY3ZWYyYmM1ZTY0ZjNhNDNiMmNmZGNmMDFiOGMwNGJkOCIsInRhZyI6IiJ9; XSRF-TOKEN=eyJpdiI6IkpORlVhVWdIbklqQmZOTXFnc1BpWWc9PSIsInZhbHVlIjoiZjVLVVo5NkI1MUo2THZ1bzlsSXpEK1ZzcWlLSGNyRDQyRy9sOUI0UUZvRjEwSVRYMW9oNEc3dnNDdWxwTkI0YnFUbzM5dzJVSENVelpGMWZQNzJ6UDk1T1BscnpPWkJNSGt3WHZFZzdsMHVEdXBWdCtYenNrQmhpcjFGQlEzWlgiLCJtYWMiOiJjNjAzZWE1NGMxZmQ2YWQzYjE4YWVmZDI4NzJlNTUzYjA5NWIyY2M1MzA3N2JjZWY1MzdlN2EyYTc5N2U2OTM4IiwidGFnIjoiIn0%3D; betteranime_session=eyJpdiI6ImVxOVNrZlBnMmFWaG55cGFreHBsc0E9PSIsInZhbHVlIjoiSndsZHBEakNQZE9pZVZiaWIyZlVHM3FiSmVPMEZaMVhKeDJWbVlUZTNqUnFEYzYxWDV6bXVydkxIK2x2bkJuTG1jZk9ZL1ozVXFNTEJvaFdzOGtXVnJOS3g2TkQ5V2lwOC8zWlJ6Z1BHWk5MNm55WVpyVHo2by95bzVlZm5JRUEiLCJtYWMiOiJjNjMxYmEyYzk5NmFmOGEwNDUyY2FhODkzNzhiODY5NGVkMWYwZGMzMjVmYTlmNmE5YTI3ODYwMjU0N2U2Y2NmIiwidGFnIjoiIn0%3D; BetterQuality=eyJpdiI6ImRCakJKaGVBZU9waHEvWFlwZFl6ZGc9PSIsInZhbHVlIjoiNG1VcUNOME5ZV25ZaktES00xVmZCc2h3RG91R2dTTUc5YjA4OFAwMS81b3hTRnE1dHRBU1ZQN1N3R2xXQzZseiIsIm1hYyI6IjhmYTc3M2ZiZjMzODA4MmQ3MGEzOGQ0MTdhMmE2OWU0YTkxZWNiMDIzNTBhNWM5YTc4NmRiNGNiNTI1MGFmNTAiLCJ0YWciOiIifQ%3D%3D; BetterAppModal_v2=eyJpdiI6IkR6K25QOHNjZUd2Q0dlZkNEWUwrUVE9PSIsInZhbHVlIjoiUGVJSkVTRTdzeTdmM1l3WCs1OGhidUZReE45MGNvVHZHUHJmM3AwbHVtSEQ1V1l3WTBRTEU4clFKb0piT3ZLcy96bHdMSmppaE1kOThTd1RtbGszT3c9PSIsIm1hYyI6IjQyNmUwZGZiNDkyYjkwOWMyNzM4ZTc5ZTJmMDM3MThhNmJmMzVkN2RiODYzM2ZmMWE3YTc0ZWUxYTczOTI3OGQiLCJ0YWciOiIifQ%3D%3D; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IkltYS8zOUM5cE1kaHYwS3B2dngwTVE9PSIsInZhbHVlIjoiN2FCbE5LVUQyNHFkRFZSa016N2swc2c4bS9mYnVsSm1DU1RPcFVYYjRuUjBlMXd2b255cmt1SjFiWk54bDl3ZTdzT0ZVa3pxSWxDWlpocGpwNFNxV3hqZlYxa2NnV3oxbWN1WnFsRDBRbXU5cm5BKzNHWER2c0g0VXE4c2p1aXFuclVvNU0rRHRBaWJmbkt1ZnZQYi9vZ3pHMXRGTDBlR1ZPVjNZbU0reUxnbG9VRnlRcVdkWEVIMVdPUXVtSEJSNlNqbUVHcUJTbC9ZTm9LSHlldGJGOFd4K2ZRZFdodGYwSnQ4VkJIampRST0iLCJtYWMiOiIwN2Y0YzNlMzUzYzJiNjdmNWI3NjhkMTEyZGNjMmIxYTlmNDExM2YwM2RjYzA4Nzg3MmE5NjJlM2E3OGJmNmQ3IiwidGFnIjoiIn0%3D'

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
    
    def get_episode_url(self, episode_id: str) -> Episode | bool:
        response = self.session.get(f'{self.base_url}/anime/{episode_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            url = soup.find('iframe')['src']
            buttons_opt = soup.find('div', {'id': 'qualitiesColumn'}).find_all('button')
            if len(buttons_opt) == 1:
                return Episode(
                    url=url,
                    label=buttons_opt[0].text,
                )
            return [Episode(
                url=url,
                label=button.text,
                headers=self.episode_headers,
            ) for button in buttons_opt][::-1]
        return False
    