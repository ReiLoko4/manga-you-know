import csv
import json
from pathlib import Path

class MangaYouKnowDB:
    def __init__(self):
        self.database = Path('database/data.csv')
        self.config = Path('database/config.json')

    def create_database(self):
        if not self.database.exists():
            self.database.touch()
            with open(self.database, mode='w') as file:
                writer_csv = csv.writer(file, lineterminator='\n')
                writer_csv.writerow([
                    'id_manga',
                    'name_manga',
                    'last_read',
                    'type',
                    'manga_path'
                ])

    def get_database(self) -> list:
        self.create_database()
        with open(self.database, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            database = []
            for line in leitor_csv:
                database.append(line)
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

    def add_manga(self, manga:list):
        self.create_database()
        with open(self.database, mode='a') as file:
            writer_csv = csv.writer(file, lineterminator='\n')
            writer_csv.writerow(manga)
    
    def add_data_chapters(self, manga_name:str, chapters_list:list):
        manga_data_path = Path(f'Mangas/{manga_name}/data/')
        manga_data_path.mkdir(parents=True, exist_ok=True)
        data_file = Path(f'{manga_data_path}/chapters.csv')
        data_file.touch(exist_ok=True)
        for chapter in chapters_list:
            with open(data_file, mode='a+') as file:
                writer_csv = csv.writer(file, lineterminator='\n')
                writer_csv.writerow(chapter)

    def get_data_chapters(self, manga_name:str) -> list or bool :
        manga_chapters = Path(f'Mangas/{manga_name}/data/chapters.csv')
        if not manga_chapters.exists(): return False
        with open(manga_chapters, mode='r', encoding='utf-8') as file:
            leitor_csv = csv.reader(file)
            list_chapters = []
            for line in leitor_csv:
                list_chapters.append(line)
        return list_chapters
    
    def get_chapter_id(self, manga_name:str, chapter:str) -> str or bool:
        chapters = self.get_data_chapters(manga_name)
        for line in chapters:
            if chapter == line[0]: return line[1]


    def delete_manga(self, manga_id:str):
        manga_id = str(manga_id)
        with open(self.database, "r") as file:
            leitor_csv = csv.reader(file)
            lista_csv = list(leitor_csv)
        for line in lista_csv:
            if manga_id in line:
                lista_csv.remove(line)
        with open(self.database, "w", newline="") as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerows(lista_csv)


