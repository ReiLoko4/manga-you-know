from backend.interfaces import AnimeDl
from backend.models import Chapter, Episode, Manga
from bs4 import BeautifulSoup
from requests import Session


class EraiRawsDl(AnimeDl):
    def __init__(self):
        self.base_url = 'https://www.erai-raws.info/'
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        })
        self.session.cookies.update({
            '__ddg1_': 'Z8mWxMS2GPqmh1Cj6S1O',
            'wordpress_logged_in_25c65adc7d24c2f6075a3cbdddcf4db0': 'ReiLoko%7C1719190782%7CJtnw9BojJM48YUY8JLDADaO07sqNCKZeX3kMc0fJivv%7C52f29e45c74b4995d451dfc3943f68412a81bc6cfdae2efe15b22bd025078933',
            'PHPSESSID': '5qmt44puosja5kbo4u4kio9c69',
            'wfwaf-authcookie-f95bdc8896162871dd9440f078446f26': '115269%7Cother%7Cread%7C84287b359506d1d8c0b76d0b9b5ce1629b277b9c81ce919a21cc131ad408762f',
            'wpdiscuz_nonce_25c65adc7d24c2f6075a3cbdddcf4db0': '8d15adcdb9',
        })

    def search(self, query: str) -> list[Manga] | bool:
        response = self.session.get(
            self.base_url,
            params={
                's': query
            }
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            main = soup.find('main')
            animes = []
            for a in main.find_all(a):
                split_url = a['href'].split('/')
                animes.append(
                    Manga(
                        id=split_url[-2:],
                        name=a.text,
                        folder_name=split_url[-2],
                        cover='https://mapacultural.funcap.se.gov.br/_next/static/images/no-capa-814c308aa1d2c7aa3ca6da4f90a4a581.jpg'
                    )
                )
            return animes[:10]
        return False

    def get_episodes(self, anime_id: str) -> list[Chapter] | bool:
        pass

    def get_episode_url(self, episode_id: str) -> list[Episode] | bool: 
        pass

