import csv
import json
from os import remove, path
from pathlib import Path


class MangaYouKnowDB:
    def __init__(self):
        self.dir = Path('database')
        self.database = Path('database/data.csv')
        self.config = Path('database/config.json')

    def create_database(self):
        if not self.database.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.database.touch()
            with open(self.database, mode='w') as file:
                csv.writer(file, lineterminator='\n').writerow([
                    'id_manga',
                    'name_manga',
                    'last_read',
                    'cover_path',
                    'name_with_hyphen'
                ])

    def get_database(self) -> list:
        self.create_database()
        with open(self.database, 'r', encoding='UTF-8') as file:
            database = list(csv.reader(file))
        del[database[0]]
        return database

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
            config = json.load(file)
        return config

    def add_manga(self, manga:list) -> bool:
        list_favs = self.get_database()
        if manga[0] in [i[0] for i in list_favs]: return False
        with open(self.database, 'a', encoding='UTF-8') as file:
            csv.writer(file, lineterminator='\n').writerow(manga)
        return True
    
    def get_manga(self, manga_id:str) -> list or bool:
        list_mangas = self.get_database()
        for manga in list_mangas:
            if manga[0] == manga_id: return manga
        return False

    def set_manga(self, manga_id:str, column:int, last_read:str) -> bool:
        """
        def set_manga
        -------------
        set a atributte of an manga on data.csv file

        column=0: edit id (id is stattic, but its localizated in 0 column)
        column=1: edit manga name
        column=2: edit last chapter read
        column=3: edit cover path
        """


        with open(self.database, 'r', encoding='UTF-8') as file:
            database = list(csv.reader(file))
        for line in database:
            if line[0] == manga_id:
                line[column] = last_read
                break
        with open(self.database, 'w', encoding='UTF-8', newline='') as file:
            csv.writer(file).writerows(database)
        return True

    def delete_manga(self, manga_id:str):
        manga_id = str(manga_id)
        with open(self.database, 'r', encoding='UTF-8') as file:
            lista_csv = list(csv.reader(file))
        for line in lista_csv:
            if manga_id in line: lista_csv.remove(line)
        with open(self.database, 'w', encoding='UTF-8', newline='') as file:
            csv.writer(file).writerows(lista_csv)
        return True

    def add_data_chapters(self, manga_name:str, chapters_list:list):
        manga_data_path = Path(f'mangas/{manga_name}/data/')
        manga_data_path.mkdir(parents=True, exist_ok=True)
        data_file = Path(f'{manga_data_path}/chapters.csv')
        if path.isfile(data_file): remove(data_file)
        data_file.touch(exist_ok=True)
        for chapter in chapters_list:
            with open(data_file, 'a+', encoding='UTF-8') as file:
                csv.writer(file, lineterminator='\n').writerow(chapter)

    def get_data_chapters(self, manga_name:str) -> list or bool :
        manga_name = manga_name.replace(' ', '-').lower()
        manga_chapters = Path(f'mangas/{manga_name}/data/chapters.csv')
        if not manga_chapters.exists(): return False
        with open(manga_chapters, mode='r', encoding='utf-8') as file:
            return list(csv.reader(file))
    
    def get_chapter_id(self, manga_name:str, chapter:str) -> str or bool:
        chapters = self.get_data_chapters(manga_name)
        for line in chapters: 
            if line[0] == chapter: return line[1]
        return False
