from pathlib import Path
import flet as ft
import requests
import json


class Updater:
    def __init__(self):
        self.endpoint = 'https://api.github.com/repos/ReiLoko4/manga-you-know'
        self.app_meta = Path('app/metadata.json')

    def get_local_release(self) -> str:
        if self.app_meta.exists():
            return json.loads(open(self.app_meta, 'r').read())['version']
        self.app_meta.parent.mkdir(parents=True, exist_ok=True)
        self.app_meta.touch()
        self.app_meta.write_text(json.dumps({'version': 'none'}))
        return 'none'

    def get_releases(self) -> list[dict]:
        return requests.get(f'{self.endpoint}/releases').json()

    def get_latest_release(self) -> dict:
        return requests.get(f'{self.endpoint}/releases/latest').json()
    
    def is_downloaded(self, version: str) -> bool:
        return Path(f'app/{version}.exe').exists()
    
    def set_version(self, version: str):
        if self.app_meta.exists():
            self.app_meta.write_text(json.dumps({'version': version}))
    
    def download_release(self, download_url, tag_name, bar: ft.ProgressBar = None):
        if bar:
            bar.value = 0
        with requests.get(download_url, stream=True) as response, \
	        open(f'app/{tag_name}.exe', 'wb') as file:
            total = int(response.headers.get('content-length'))
            for chunk in response.iter_content(1024):
                if chunk:
                    file.write(chunk)
                if bar:
                    bar.value += round(len(chunk) / total, 5)
                    bar.update()
        self.app_meta.write_text(json.dumps({'version': tag_name}))


