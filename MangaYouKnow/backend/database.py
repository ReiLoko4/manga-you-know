import json
import sqlite3
# import sqlalchemy as db
from pathlib import Path
from backend.models import Manga, Chapter
from backend.tables import Favorites, favorite_columns


class DataBase:
    def __init__(self):
        self.dir = Path('./database')
        self.database = Path('./database/data.db')
        self.favorites_dump = '''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT NOT NULL,
                folder_name TEXT NOT NULL,
                cover TEXT NOT NULL,
                description TEXT,
                author TEXT,
                score FLOAT,
                md_id TEXT UNIQUE,
                ml_id INTEGER UNIQUE,
                ms_id TEXT UNIQUE,
                mc_id TEXT UNIQUE,
                mf_id TEXT UNIQUE,
                mx_id TEXT UNIQUE,
                tcb_id TEXT UNIQUE,
                tsct_id TEXT UNIQUE,
                op_id TEXT UNIQUE,
                gkk_id TEXT UNIQUE,
                lmorg_id TEXT UNIQUE
            );
        '''
        self.readed_dump = '''
            CREATE TABLE IF NOT EXISTS readed (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                manga_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                source TEXT NOT NULL
            );
        '''
        self.columns = favorite_columns
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
            cur.execute(self.favorites_dump)
            cur.close()

    def fix_favorites(self):
        table_columns = self.execute_data('PRAGMA table_info(favorites);')
        for column in self.columns:
            if column not in [i['name'] for i in table_columns]:
                self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} TEXT;')
                self.execute_data(f'CREATE UNIQUE INDEX ta ON favorites({column});')
    
    def get_database(self) -> list[dict]:
        self.fix_favorites()
        cur = self.connect()
        cur.execute('SELECT * FROM favorites;')
        return [dict(i) for i in cur.fetchall()]
    
    def get_database_readed(self) -> list[dict]:
        cur = self.connect()
        cur.execute('SELECT * FROM favorites WHERE last_chapter_readed_id IS NOT NULL;')
        return [dict(i) for i in cur.fetchall()]
    
    def create_config(self):
        if not self.config.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.config.touch()
            with open(self.config, mode='w') as file:
                json.dump({
                    'config': {
                    'theme-mode': 'dark',
                    'theme-color':'blue',
                    'reader-type': 'h-n',
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

    def execute_data(self, sql: str) -> list[dict] | bool:
        cur = self.connect()
        try:
            cur.execute(sql)
            cur.connection.commit()
            data = cur.fetchall()
            return [dict(i) for i in  data] if data else True
        except Exception as e:
            print(e)
            return False
        finally:
            cur.close()

    def add_manga(
            self, 
            manga: Manga,
            ml_id: int=None,
            md_id: str=None,
            ms_id: str=None,
            mc_id: str=None,
            mf_id: str=None,
            mx_id: str=None,
            tcb_id: str=None,
            tsct_id: str=None,
            op_id: str=None,
            gkk_id: str=None,
            lmorg_id: str=None
        ) -> bool:
        self.fix_favorites()
        cur = self.connect()
        try:
            cur.execute(
                'INSERT INTO favorites (name, folder_name, cover, description, author, score, ml_id, md_id, ms_id, mc_id, mf_id, mx_id, tcb_id, tsct_id, op_id, gkk_id, lmorg_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                (manga.name, manga.folder_name, manga.cover, manga.description, manga.author, manga.grade, ml_id, md_id, ms_id, mc_id, mf_id, mx_id, tcb_id, tsct_id, op_id, gkk_id, lmorg_id)
            )
            cur.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            cur.close()
    
    def get_manga(self, favorite_id:int) -> dict | bool:
        cur = self.connect()
        cur.execute(
            'SELECT * FROM favorites WHERE id = ?;',
            (favorite_id,)
        )
        cur.connection.commit()
        cur.close()
        return dict(cur.fetchone())

    def set_manga(self, manga_id:str, column:str, content: any) -> bool:
        cur = self.connect()
        try:
            cur.execute(
                'UPDATE favorites SET {} = ? WHERE id = ?;'.format(column),
                (content, manga_id)
            )
            cur.connection.commit()
            cur.close()
        except Exception as e:
            print(e)
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
        
    def delete_manga_by_key(self, key: str, id: int | str) -> bool:
        database = self.get_database()
        id_row = None
        for manga in database:
            if manga[key] == id:
                id_row = manga['id']
                break
        if not id_row: return False
        cur = self.connect()
        try:
            cur.execute(
                'DELETE FROM favorites WHERE id = ?;',
                (id_row,)
            )
            cur.connection.commit()
            return True   
        except:
            return False
        finally:
            cur.close()

    def is_favorite(self, key, content) -> bool:
        favorites = self.get_database()
        for manga in favorites:
            if manga[key] == content:
                return True
        return False
    
    def is_readed(self, source: str, manga_id: str, chapter_id: str) -> bool:
        self.execute_data(self.readed_dump)
        cur = self.connect()
        cur.execute(
            'SELECT * FROM readed WHERE source = ? AND manga_id = ? AND chapter_id = ?;',
            (source, manga_id, chapter_id)
        )
        data = cur.fetchall()
        cur.close()
        if data:
            return True
        return False
    
    def is_each_readed(self, source: str, manga_id: str, chapters: list[Chapter]) -> list[bool]:
        self.execute_data(self.readed_dump)
        cur = self.connect()
        readed = []
        list_readed = cur.execute(
            'SELECT * FROM readed WHERE source = ? AND manga_id = ?;',
            (source, manga_id)
        ).fetchall()
        for chapter in chapters:
            readed.append(
                True if chapter.id in [i['chapter_id'] for i in list_readed]
                    else False
            )
        cur.close()
        return readed
    
    def is_one_readed(self, source: str, manga_id: str, chapters: list[Chapter]) -> bool:
        self.execute_data(self.readed_dump)
        cur = self.connect()
        for chapter in chapters:
            cur.execute(
                'SELECT * FROM readed WHERE source = ? AND manga_id = ? AND chapter_id = ?;',
                (source, manga_id, chapter.id)
            )
            data = cur.fetchall()
            if data:
                return True
        cur.close()
        return False
        
    def add_readed(self, source: str, manga_id:str, chapter_id:str) -> bool:
        self.execute_data(self.readed_dump)
        cur = self.connect()
        try:
            cur.execute(
                'INSERT INTO readed (manga_id, chapter_id, source) VALUES (?, ?, ?);',
                (manga_id, chapter_id, source)
            )
            cur.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            cur.close()

    def delete_readed(self, source: str, manga_id: str, chapter_id: str) -> bool:
        self.execute_data(self.readed_dump)
        cur = self.connect()
        try:
            cur.execute(
                'DELETE FROM readed WHERE source = ? AND manga_id = ? AND chapter_id = ?;',
                (source, manga_id, chapter_id)
            )
            cur.connection.commit()
            return True
        except:
            return False
        finally:
            cur.close()

    