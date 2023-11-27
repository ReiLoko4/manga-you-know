import json
import sqlite3
import sqlalchemy as db
from pathlib import Path
from backend.models import Manga, Chapter
from backend.tables import Favorite, \
    favorite_columns, Readed, Mark, MarkFavorite, \
    FavoriteBase, ReadedBase, MarkBase, MarkFavoriteBase


class DataBase:
    def __init__(self):
        self.dir = Path('./database')
        self.database = Path('./database/data.db')
        self.engine = db.create_engine(
            'sqlite:///database/data.db', 
            execution_options={'isolation_level': 'AUTOCOMMIT'}
        )
        self.columns = favorite_columns
        self.config = Path('database/config.json')

    def connect(self) -> db.Connection:
        self.create_database()
        return self.engine.connect()
        
    def create_database(self):
        if not self.database.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            self.database.touch()
        FavoriteBase.metadata.create_all(self.engine, checkfirst=True)
        ReadedBase.metadata.create_all(self.engine, checkfirst=True)
        MarkBase.metadata.create_all(self.engine, checkfirst=True)
        MarkFavoriteBase.metadata.create_all(self.engine, checkfirst=True)

    def fix_favorites(self):
        table_columns = self.execute_data('PRAGMA TABLE_INFO(favorites);')
        for column in self.columns:
            if column not in [i['name'] for i in table_columns]:
                if column == 'notify':
                    self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} BOOLEAN DEFAULT FALSE;')
                    continue
                self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} TEXT;')
                self.execute_data(f'CREATE UNIQUE INDEX ta ON favorites({column});')
    
    def get_database(self) -> list[dict]:
        self.fix_favorites()
        con = self.connect()
        data = con.execute(db.select(Favorite))
        return [i._mapping for i in data.fetchall()]

    def get_database_notify_on(self) -> list[dict]:
        self.fix_favorites()
        con = self.connect()
        data = con.execute(db.select(Favorite).where(Favorite.notify == True)).fetchall()
        return [i._mapping for i in data]
    
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
                    }}
                }, file)

    def get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)['config']
        
    def _get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)

    def execute_data(self, query: str) -> list[dict] | dict | bool:
        con = self.connect()
        try:
            data = con.execute(db.text(query)).fetchall()
            return [i._mapping for i in  data] if data else True
        except Exception as e:
            print(e)
            return False

    def add_manga(
            self, manga: Manga,
            ml_id: int=None, md_id: str=None,
            ms_id: str=None, mc_id: str=None,
            mf_id: str=None, mx_id: str=None,
            tcb_id: str=None, tsct_id: str=None,
            op_id: str=None, gkk_id: str=None,
            lmorg_id: str=None
        ) -> bool:
        self.fix_favorites()
        try:
            self.engine.connect().execute(
                db.insert(Favorite), [{
                'name': manga.name,
                'folder_name': manga.folder_name,
                'cover': manga.cover,
                'description': manga.description,
                'author': manga.author,
                'score': manga.grade,
                'notify': False,
                'ml_id': ml_id,
                'md_id': md_id,
                'ms_id': ms_id,
                'mc_id': mc_id,
                'mf_id': mf_id,
                'mx_id': mx_id,
                'tcb_id': tcb_id,
                'tsct_id': tsct_id,
                'op_id': op_id,
                'gkk_id': gkk_id,
                'lmorg_id': lmorg_id
            }])
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_manga(self, favorite_id: int) -> dict | bool:
        con = self.connect()
        data = con.execute(db.select(Favorite).where(Favorite.id == favorite_id))
        return data.fetchone()._mapping if data else False

    def set_manga(self, manga_id: str, column: str, content: any) -> bool:
        cur = self.connect()
        try:
            cur.execute(db.update(Favorite).where(Favorite.id == manga_id).values({column: content}))
        except Exception as e:
            print(e)
            return False
        return True

    def delete_manga(self, manga_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.delete(Favorite).where(Favorite.id == manga_id))
        except Exception as e:
            print(e)
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

    def is_favorite(self, key, content) -> bool:
        favorites = self.get_database()
        for manga in favorites:
            if manga[key] == content:
                return True
        return False
    
    def is_readed(self, source: str, manga_id: str, chapter_id: str) -> bool:
        con = self.connect()
        data = con.execute(db.select(Readed).where(
            Readed.chapter_id == chapter_id
            and Readed.manga_id == manga_id
            and Readed.source == source
        ))
        if data.fetchall():
            return True
        return False
    
    def is_each_readed(self, source: str, manga_id: str, chapters: list[Chapter]) -> list[bool]:
        con = self.connect()
        readed = []
        list_readed = con.execute(db.select(Readed).where(
            Readed.manga_id == manga_id
            and Readed.source == source
        )).fetchall()
        if not list_readed:
            return [False for _ in range(len(chapters))]
        for chapter in chapters:
            readed.append(
                True if chapter.id in [i._mapping['chapter_id'] for i in list_readed]
                    else False
            )
        return readed
    
    def is_one_readed(self, source: str, manga_id: str, chapters: list[Chapter]) -> bool:
        con = self.connect()
        for chapter in chapters:
            data = con.execute(db.select(Readed).where(
                Readed.chapter_id == chapter.id
                and Readed.manga_id == manga_id
                and Readed.source == source
            ))
            if data.fetchall():
                return True
        con.close()
        return False
        
    def add_readed(self, source: str, manga_id: str, chapter_id: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.insert(Readed),[{
                'manga_id': manga_id, 
                'chapter_id': chapter_id,
                'source': source 
            }])
            return True
        except Exception as e:
            print(e)
            return False

    def delete_readed(self, source: str, manga_id: str, chapter_id: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.delete(Readed).where(
                Readed.chapter_id == chapter_id
                and Readed.manga_id == manga_id
                and Readed.source == source
            ))
            return True
        except:
            return False

    