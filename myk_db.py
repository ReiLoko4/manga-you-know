import csv
import json
from pathlib import Path

class MangaYouKnowDB:
    def __init__(self):
        self.database = Path('database/data.csv')
        self.config = Path('database/config.json')

    def create_database(self):
        self.database.mkdir(parents=True, exist_ok=True)
        with open(self.database, mode='w') as data_csv:
            writer_csv = csv.writer(data_csv)
            # bla bla bla tem q terminar

    def get_database(self):
        self.create_database()
        with open(self.database, mode='r') as data_csv:
            leitor_csv = csv.reader(data_csv)
            database = []
            for linha in leitor_csv:
                database.append(linha)
        del[database[0]]
        return database
    
    def create_config(self):
        self.config.mkdir(parents=True, exist_ok=True)