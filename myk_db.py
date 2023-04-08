import csv
import json
from os import remove, path
from pathlib import Path

class MangaYouKnowDB:
    def __init__(self):
        self.database = Path('database/data.csv')
        self.config = Path('database/config.json')

    def create_database(self):
        if not self.database.exists():
            self.database.touch()
            with open(self.database, mode='w') as file:
                csv.writer(file, lineterminator='\n').writerow([
                    'id_manga',
                    'name_manga',
                    'last_read',
                    'type',
                    'manga_path'
                ])

    def get_database(self) -> list:
        self.create_database()
        with open(self.database, mode='r', encoding='utf-8') as file:
            database = list(csv.reader(file))
        del[database[0]]
        return database

    def create_config(self):
        if not self.config.exists():
            self.config.touch()
            with open(self.config, mode='w') as file:
                json.dump({
                    'config': {
                    'reader-type':'pass-n',
                    'theme-color':'blue'
                    }
                }, file)

    def get_config(self) -> dict:
        self.create_config()
        with open(self.config, mode='r', encoding='utf-8') as file:
            config = json.load(file)
        return config

    def add_manga(self, manga:list) -> bool:
        self.create_database()
        list_favs = self.get_database()
        if manga[0] in [i[0] for i in list_favs]: return False
        with open(self.database, mode='a') as file:
            csv.writer(file, lineterminator='\n').writerow(manga)
        return True
    
    def get_manga(self, manga_id:str) -> list or bool:
        list_mangas = self.get_database()
        for manga in list_mangas:
            if manga[0] == manga_id:
                return manga
        return False

    def edit_manga(self, manga_id:str, last_read:str) -> bool:
        self.create_database()
        with open(self.database, mode='r', encoding='utf-8') as file:
            database = list(csv.reader(file))
        for line in database:
            if line[0] == manga_id:
                line[2] = last_read
                break
        with open(self.database, 'w', newline='') as file:
            csv.writer(file).writerows(database)
        return True

    def delete_manga(self, manga_id:str):
        manga_id = str(manga_id)
        with open(self.database, 'r') as file:
            lista_csv = list(csv.reader(file))
        for line in lista_csv:
            if manga_id in line:
                lista_csv.remove(line)
        with open(self.database, 'w', newline='') as file:
            escritor_csv = csv.writer(file)
            escritor_csv.writerows(lista_csv)

    def add_data_chapters(self, manga_name:str, chapters_list:list):
        manga_data_path = Path(f'Mangas/{manga_name}/data/')
        manga_data_path.mkdir(parents=True, exist_ok=True)
        data_file = Path(f'{manga_data_path}/chapters.csv')
        if path.isfile(data_file): remove(data_file)
        data_file.touch(exist_ok=True)
        for chapter in chapters_list:
            with open(data_file, mode='a+', encoding='utf-8') as file:
                writer_csv = csv.writer(file, lineterminator='\n')
                writer_csv.writerow(chapter)

    def get_data_chapters(self, manga_name:str) -> list or bool :
        manga_name = manga_name.replace(' ', '-').lower()
        manga_chapters = Path(f'Mangas/{manga_name}/data/chapters.csv')
        if not manga_chapters.exists(): return False
        with open(manga_chapters, mode='r', encoding='utf-8') as file:
            return list(csv.reader(file))
    
    def get_chapter_id(self, manga_name:str, chapter:str) -> str or bool:
        chapters = self.get_data_chapters(manga_name)
        for line in chapters:
            if chapter == line[0]: return line[1]


    
