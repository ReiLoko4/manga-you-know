import json
import sqlite3
from pathlib import Path


class DataBase:
    def __init__(self):
        self.dir = Path('database')
        self.database = Path('database/data.db')
        self.dump = '''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                ml_id INTEGER UNIQUE,
                md_id STRING UNIQUE,
                mf_id STRING UNIQUE,
                tcb_id STRING UNIQUE,
                tsct_id STRING UNIQUE,
                op_id STRING UNIQUE,
                gkk_id STRING UNIQUE,
                name TEXT NOT NULL,
                folder_name STRING NOT NULL,
                cover STRING NOT NULL,
                description TEXT,
                author STRING,
                last_chapter_readed_id STRING,
                last_chapter_readed_source STRING,
                last_chapter_readed_number STRING,
                score FLOAT
            );
        '''
        #  CREATE TABLE IF NOT EXISTS last (
        self.config = Path('database/config.json')

    def connect(self) -> sqlite3.Cursor:
        self.create_database()
        con = sqlite3.connect(self.database)
        con.row_factory = sqlite3.Row
        return con.cursor()
        
    def create_database(self):
        if not self.database.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.database.touch()
            cur = sqlite3.connect(self.database).cursor()
            cur.execute(self.dump)
            cur.close()
                
    def get_database(self) -> list[dict]:
        cur = self.connect()
        cur.execute('SELECT * FROM favorites;')
        return [dict(i) for i in  cur.fetchall()]
    
    def create_config(self):
        if not self.config.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.config.touch()
            with open(self.config, mode='w') as file:
                json.dump({
                    'config': {
                    'theme-mode':'dark',
                    'theme-color':'blue',
                    'reader-type':'h-n',
                    'keybinds': {
                        'full-screen': 'F11',
                        'return-home': 'F4',
                        'next-page': 'Arrow Right',
                        'previous-page': 'Arrow Left',
                    }
                    }
                }, file)

    def get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)['config']
        
    def _get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)

    def add_manga(
            self, 
            name: str,
            folder_name: str,
            cover: str,
            ml_id: int=None,
            md_id: str=None,
            mf_id: str=None,
            tcb_id: str=None,
            tsct_id: str=None,
            op_id: str=None,
            gkk_id: str=None,
            description: str=None,
            author: str=None,
            score: float=None
        ) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'INSERT INTO favorites (ml_id, md_id, mf_id, tcb_id, tsct_id, op_id, gkk_id, name, folder_name, cover, description, author, score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (ml_id, md_id, mf_id, tcb_id, tsct_id, op_id, gkk_id, name, folder_name, cover, description, author, score)
            )
            cur.connection.commit()
            cur.close()
        except:
            return False
        return True
    
    def get_manga(self, favorite_id:int) -> dict | bool:
        cur = self.connect()
        cur.execute(
            'SELECT * FROM favorites WHERE id = ?;',
            (favorite_id,)
        )
        cur.connection.commit()
        cur.close()
        return dict(cur.fetchone())

    def set_manga(self, manga_id:str, key:str, content:str) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'UPDATE favorites SET ? = ? WHERE id = ?;',
                (key, content, manga_id)
            )
            cur.connection.commit()
            cur.close()
        except:
            return False
        return True

    def set_last_read(self, manga_id:str, source: str, chapter:str, id_chapter:str) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'UPDATE favorites SET last_chapter_readed = JSON_INSERT(last_chapter_readed, "$[0]", JSON_OBJECT("source", ?, "chapter", ?, "release", ?)) WHERE id = ?;',
                (source, chapter, id_chapter, manga_id)
            )
            cur.connection.commit()
            cur.close()
        except:
            return False
        return True
        

    def delete_manga(self, manga_id: int) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'DELETE FROM favorites WHERE id = ?;',
                (manga_id,)
            )
            cur.connection.commit()
            cur.close()
        except:
            return False
        return True
    
    def delete_manga_by_id_key(self, key: str, id: int | str) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'DELETE FROM favorites WHERE ? = ?;',
                (key, id)
            )
            cur.connection.commit()
            cur.close()
        except:
            return False
        return True
        
    
    def is_favorite(self, key, content) -> bool:
        cur = self.connect()
        cur.execute(
            'SELECT * FROM favorites WHERE ? = ?;',
            (key, content)
        )
        if len(cur.fetchall()) > 0:
            return True
        return False

    def add_data_chapters(self, manga_name:str, chapters:list[dict]):
        manga_data_path = Path(f'mangas/{manga_name}/data/')
        manga_data_path.mkdir(parents=True, exist_ok=True)
        data_file = Path(f'{manga_data_path}/chapters.json')
        data_file.touch(exist_ok=True)
        with open(data_file, 'w', encoding='UTF-8') as file:
            json.dump(chapters,file)
        return True

    def get_data_chapters(self, manga_name:str) -> list[dict] | bool:
        manga_name = manga_name.replace(' ', '-').lower()
        manga_chapters = Path(f'mangas/{manga_name}/data/chapters.json')
        if not manga_chapters.exists(): return False
        with open(manga_chapters, mode='r', encoding='utf-8') as file:
            return json.load(file)
    
    def get_manga_info_by_key(self, key, content) -> dict | bool:
        data = self.get_database()
        for manga in data:
            if str(manga[key]) == str(content):
                return manga
        return False
    
    # def get_chapter_id(self, manga_name:str, chapter:str) -> str or bool:
    #     chapters = self.get_data_chapters(manga_name)
    #     for line in chapters: 
    #         if line[0] == chapter: return line[1]
    #     return False
    
    def get_chapter_info(self, manga_id, id_release) -> dict | bool:
        chapters = self.get_data_chapters(self.get_manga_info_by_key(manga_id)['folder_name'])
        for chapter in chapters:
            if str(chapter['releases'][list(chapter['releases'].keys())[0]]['id_release']) == str(id_release):
                return chapter
        return False
    
# print(DataBase().add_manga('teste', 'teste', 'teste'))
