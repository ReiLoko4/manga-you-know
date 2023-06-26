import json
from pathlib import Path


class DataBase:
    def __init__(self):
        self.dir = Path('database')
        self.database = Path('database/data.json')
        self.config = Path('database/config.json')

    def create_database(self):
        if not self.database.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.database.touch()
            with open(self.database, mode='w') as file:
                json.dump({
                    'data': []
                }, file)

    def get_database(self) -> dict:
        self.create_database()
        with open(self.database, 'r', encoding='UTF-8') as file:
            return json.load(file)

    def create_config(self):
        if not self.config.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.config.touch()
            with open(self.config, mode='w') as file:
                json.dump({
                    'config': {
                    'theme-mode':'dark',
                    'theme-color':'blue',
                    'reader-type':'h-n'
                    }
                }, file)

    def get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)['config']

    def add_manga(self, manga:dict) -> bool:
        database = self.get_database()
        if manga['id'] in [i['id'] for i in database['data']]: return False
        database['data'].append(manga)
        with open(self.database, 'w', encoding='UTF-8') as file:
            json.dump(database, file)
        return True
    
    def get_manga(self, manga_id:str) -> dict | bool:
        database = self.get_database()
        for manga in database['data']:
            if manga['id'] == manga_id: return manga
        return False

    def set_manga(self, manga_id:str, key:str, content:str):
        database = self.get_database()
        for manga in database['data']:
            if manga['id'] == manga_id:
                manga[key] = content
                break
        with open(self.database, 'w', encoding='UTF-8') as file:
            json.dump(database, file)

    def delete_manga(self, manga_id:str) -> bool:
        database = self.get_database()
        len_data = len(database['data'])
        for i, manga in enumerate(database['data']):
            if manga['id'] == manga_id: database['data'].pop(i)
        if len_data == len(database['data']):
            return False
        with open(self.database, 'w', encoding='UTF-8') as file:
            json.dump(database, file)
        return True

    def add_data_chapters(self, manga_name:str, chapters:dict):
        manga_data_path = Path(f'mangas/{manga_name}/data/')
        manga_data_path.mkdir(parents=True, exist_ok=True)
        data_file = Path(f'{manga_data_path}/chapters.json')
        data_file.touch(exist_ok=True)
        with open(data_file, 'w', encoding='UTF-8') as file:
            json.dump(chapters,file)

    def get_data_chapters(self, manga_name:str) -> list | bool:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_chapters = Path(f'mangas/{manga_name}/data/chapters.json')
        if not manga_chapters.exists(): return False
        with open(manga_chapters, mode='r', encoding='utf-8') as file:
            return json.load(file)
    
    def get_manga_info(self, manga_id) -> dict | bool:
        data = self.get_database()
        for manga in data['data']:
            if manga['id'] == manga_id:
                return manga
        return False
    
    # def get_chapter_id(self, manga_name:str, chapter:str) -> str or bool:
    #     chapters = self.get_data_chapters(manga_name)
    #     for line in chapters: 
    #         if line[0] == chapter: return line[1]
    #     return False
    
    def get_chapter_info(self, manga_id, id_release) -> dict | bool:
        chapters = self.get_data_chapters(self.get_manga(manga_id)['folder_name'])
        for chapter in chapters:
            if chapter['releases'][list(chapter['releases'].keys())[0]]['id_release'] == id_release:
                return chapter
        return False
    