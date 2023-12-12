import json
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
            execution_options={'isolation_level': 'AUTOCOMMIT'},
            pool_size=20, max_overflow=0, pool_timeout=30, pool_recycle=1800
        )
        self.columns = favorite_columns
        self.config = Path('database/config.json')
        self.ids = {
            'ml_id': Favorite.ml_id,
            'md_id': Favorite.md_id,
            'ms_id': Favorite.ms_id,
            'mc_id': Favorite.mc_id,
            'mf_id': Favorite.mf_id,
            'mx_id': Favorite.mx_id,
            'tcb_id': Favorite.tcb_id,
            'tsct_id': Favorite.tsct_id,
            'op_id': Favorite.op_id,
            'gkk_id': Favorite.gkk_id,
            'lmorg_id': Favorite.lmorg_id
        }

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
        # columns = self.execute_data('PRAGMA TABLE_INFO(readed);')
        # if not 'language' in [i['name'] for i in columns]:

    def fix_favorites(self):
        table_columns = self.execute_data('PRAGMA TABLE_INFO(favorites);')
        for column in self.columns:
            if column not in [i['name'] for i in table_columns]:
                if column == 'notify':
                    self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} BOOLEAN DEFAULT FALSE;')
                    continue
                self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} TEXT;')
                self.execute_data(f'CREATE UNIQUE INDEX ta ON favorites({column});')
    
    def get_database(self, mark_id: str = None) -> list[dict]:
        self.fix_favorites()
        con = self.connect()
        if mark_id:
            data = con.execute(
                db.select(Favorite).join(
                    MarkFavorite, Favorite.id == MarkFavorite.favorite_id
                ).where(
                    MarkFavorite.mark_id == mark_id
                )
            )
            return [i._mapping for i in data.fetchall()]
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
                'author': manga.author[0] if manga.author else 'Desconhecido',
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
        con = self.connect()
        try:
            con.execute(db.delete(Favorite).where(self.ids[key] == id))
        except Exception as e:
            print(e)
            return False
        return True

    def is_notify(self, manga_id: int) -> bool:
        con = self.connect()
        data = con.execute(db.select(Favorite).where(Favorite.id == manga_id))
        return data.fetchone()._mapping['notify']
    
    def add_notify(self, manga_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.update(Favorite).where(Favorite.id == manga_id).values({'notify': True}))
        except Exception as e:
            print(e)
            return False
        return True
    
    def delete_notify(self, manga_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.update(Favorite).where(Favorite.id == manga_id).values({'notify': False}))
        except Exception as e:
            print(e)
            return False
        return True

    def is_favorite(self, key, content) -> bool:
        con = self.connect()
        data = con.execute(db.select(Favorite).where(
            self.ids[key] == content
        )).fetchall()
        return True if data else False
    
    def is_readed(self, source: str, manga_id: str, manga_source_id: str, chapter_id: str) -> bool:
        con = self.connect()
        data = con.execute(db.select(Readed).where(
            Readed.chapter_id == chapter_id,
            Readed.manga_id == manga_id,
            Readed.manga_source_id == manga_source_id,
            Readed.source == source
        ))
        if data.fetchall():
            return True
        return False
    
    def is_each_readed(self, source: str, manga_id: str, manga_source_id: str, chapters: list[Chapter]) -> list[bool]:
        con = self.connect()
        readed = []
        list_readed = con.execute(db.select(Readed).where(
            Readed.manga_id == manga_id,
            Readed.manga_source_id == manga_source_id,
            Readed.source == source
        )).fetchall()
        if not list_readed:
            return [False for _ in range(len(chapters))]
        for chapter in chapters:
            readed.append(
                True if chapter.id in [i._mapping['chapter_id'] for i in list_readed]
                    else False
            )
        return readed
    
    def is_one_readed(self, source: str, manga_id: str, manga_source_id: str, chapters: list[Chapter]) -> bool:
        con = self.connect()
        for chapter in chapters:
            data = con.execute(db.select(Readed).where(
                Readed.chapter_id == chapter.id,
                Readed.manga_id == manga_id,
                Readed.manga_source_id == manga_source_id,
                Readed.source == source
            ))
            if data.fetchall():
                return True
        con.close()
        return False
    
    def get_last_readed(self, manga_id: str) -> dict | bool:
        con = self.connect()
        data = con.execute(db.select(Readed).where(
            Readed.manga_id == manga_id
        ).order_by(db.desc(Readed.chapter_id))).fetchone()
        if not data:
            return False
        return data._mapping

    def get_last_readed_by_source(self, source: str, manga_id: str) -> dict | bool:
        con = self.connect()
        data = con.execute(db.select(Readed).where(
            Readed.manga_id == manga_id,
            Readed.source == source
        ).order_by(db.desc(Readed.chapter_id)))
        if not data:
            return False
        return data.fetchone()._mapping
    
    def add_readed(self, source: str, manga_id: str, manga_source_id: str, chapter_id: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.insert(Readed),[{
                'manga_id': manga_id,
                'manga_source_id': manga_source_id,
                'chapter_id': chapter_id,
                'source': source 
            }])
            return True
        except Exception as e:
            print(e)
            return False

    def delete_readed(self, source: str, manga_id: str, manga_source_id: str, chapter_id: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.delete(Readed).where(
                Readed.chapter_id == chapter_id,
                Readed.manga_id == manga_id,
                Readed.manga_source_id == manga_source_id,
                Readed.source == source
            ))
            return True
        except:
            return False

    def add_mark(self, name: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.insert(Mark), [{
                'name': name
            }])
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_marks(self) -> list[dict]:
        con = self.connect()
        data = con.execute(db.select(Mark))
        return [i._mapping for i in data.fetchall()]
    
    def get_mark(self, mark_id: int) -> dict | bool:
        con = self.connect()
        data = con.execute(db.select(Mark).where(Mark.id == mark_id))
        return data.fetchone()._mapping if data else False
    
    def delete_mark(self, mark_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.delete(Mark).where(Mark.id == mark_id))
            con.execute(db.delete(MarkFavorite).where(MarkFavorite.mark_id == mark_id))
            return True
        except:
            return False
        
    def add_mark_favorite(self, favorite_id: int, mark_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.insert(MarkFavorite), [{
                'mark_id': mark_id,
                'favorite_id': favorite_id
            }])
            return True
        except Exception as e:
            print(e)
            return False

    def edit_mark(self, mark_id: int, name: str) -> bool:
        con = self.connect()
        try:
            con.execute(db.update(Mark).where(Mark.id == mark_id).values({'name': name}))
            return True
        except Exception as e:
            print(e)
            return False

    def is_marked(self, favorite_id: int, mark_id: int) -> bool:
        con = self.connect()
        data = con.execute(db.select(MarkFavorite).where(
            MarkFavorite.mark_id == mark_id, 
            MarkFavorite.favorite_id == favorite_id
        ))
        if data.fetchall():
            return True
        return False
    
    def delete_mark_favorite(self, favorite_id: int, mark_id: int) -> bool:
        con = self.connect()
        try:
            con.execute(db.delete(MarkFavorite).where(
                MarkFavorite.mark_id == mark_id,
                MarkFavorite.favorite_id == favorite_id
            ))
            return True
        except Exception as e: 
            print(e)
            return False
