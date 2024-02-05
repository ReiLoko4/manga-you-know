import json

from backend.interfaces import AnimeDl
from backend.models import Manga, Chapter
from bs4 import BeautifulSoup
from requests import Session


class AnimesVisionDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://animes.vision'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://animes.vision/search?nome=coisas',
            'Alt-Used': 'animes.vision',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })

    def search(self, query: str):
        response = self.session.get(
            f'{self.base_url}/search',
            params={'nome': query},
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_results = soup.find('div', {'class': 'film_list-wrap'})
            animes = []
            for div in div_results.find_all('div', {'class': 'flw-item'}):
                a = div.find('a')
                animes.append(
                    Manga(
                        id=a['href'].split('/')[-1],
                        name=a['title'],
                        folder_name=a['href'].split('/')[-1],
                        cover=div.find('img')['data-src'],
                    )
                )
            return animes[:10]
                # yield Manga(
                #     title=a['title'],
                #     cover=a.find('img')['src'],
                #     url=a['href'],
                # ) Test other time
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        response = self.session.get(f'{self.base_url}/animes/{anime_id}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_stats = soup.find('div', {'class': 'film-stats'})
            num_episodes = int([i for i in div_stats.find_all('span', {'class': 'item'}) if i.text.startswith('Episódios')][0].text.split(' ')[-1])
            if num_episodes == 1:
                return [Chapter(
                    id=f'{anime_id}/{soup.find('a', {'class': 'screen-item-thumbnail'})['href'].split('/')[-2]}/{'dublado' if anime_id.endswith('dublado') else 'legendado'}',
                    number='1',
                    # title='Episódio 1'
                )]
            ul = soup.find('ul', {'class': 'pagination mb-0'})
            num_pages = ul.find_all('a', {'class': 'page-link'})
            if num_pages:
                response = self.session.get(f'{self.base_url}/animes/{anime_id}?page={num_pages[-2].text}')
                soup = BeautifulSoup(response.content, 'html.parser')
            h3_list = soup.find_all('h3', {'class': 'sii-title'})
            h3_list.reverse()
            last_episode = [i.text for i in h3_list if 
                'Episodio' in i.text or 
                'Episódio' in i.text 
            ][0]
            last_episode = last_episode.split(' ')[-1] if last_episode[-1] != ' ' else last_episode.split(' ')[-2]
            last_episode = last_episode.replace(' ', '')
            last_episode = int(last_episode)
            episodes = []
            for num in range(1, num_episodes - last_episode + 1, 1):
                episodes.append(
                    Chapter(
                        id=f'{anime_id}/episodio-{num}/{'dublado' if anime_id.endswith('dublado') else 'legendado'}',
                        number=f'Especial {num}',
                        # title=f'Especial {num}'
                    )
                )
            for num in range(1, last_episode+1, 1):
                episodes.append(
                    Chapter(
                        id=f'{anime_id}/episodio-{num}/{'dublado' if anime_id.endswith('dublado') else 'legendado'}',
                        number=str(num),
                        # title=f'Episódio {num}'
                    )
                )
            episodes.reverse()
            return episodes
        return False

    def get_episode_url(self, episode_id: str) -> str | bool:
        response = self.session.get(f'{self.base_url}/animes/{episode_id}')
        if response.status_code != 200:
            split_id = episode_id.split('/')
            split_ep = split_id[1].split('-')
            response = self.session.get(f'{self.base_url}/animes/{split_id[0]}/{split_ep[0]}-0{split_ep[1]}/{split_id[2]}')
        print(response.url)
        if response.status_code == 200:
            videos = (response.text
            .split('const playerGlobalVideo = jwplayer("playerglobalapi").setup(')[1]
            .split('playlist: ')[1].replace(' ', '').replace('\n', '').replace('\r,', '')
            .split(',width:')[0]
            .split('sources:')[-1][:-4] + ']'
            .replace('\\', ''))
            videos = json.loads(videos)
            return videos[-1]['file']
        print('n passou?')
        return False
            

