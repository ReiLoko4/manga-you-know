import json
from pathlib import Path

from backend.models import Chapter, Manga
from backend.tables import (
    Favorite, 
    Readed,
    Mark, 
    MarkFavorite, 
)
from sqlmodel import (
    Session, 
    SQLModel, 
    create_engine, 
    select,
    delete,
    update,
    text,
    asc,
    desc,
)


class DataBase:
    def __init__(self):
        self.dir = Path('database')
        self.config = Path('database/config.json')
        connect_args = {
            'check_same_thread': False,
            'timeout': 30,
        }
        self.engine = create_engine(
            'sqlite:///database/data.db', 
            connect_args=connect_args,
            pool_size=2000, max_overflow=0, 
            pool_timeout=30000, pool_recycle=1800,
            isolation_level='AUTOCOMMIT'
        )
        self.database_path = 'database/data.db'
        self.columns = ['source', 'source_id', 'notify', 'type']
        self.order_dict = {
            'asc': asc(Favorite.id),
            'desc': desc(Favorite.id),
            'asc-mark': asc(MarkFavorite.id),
            'desc-mark': desc(MarkFavorite.id),
            'more-score': desc(Favorite.score),
            'less-score': asc(Favorite.score),
            'asc-alf': asc(Favorite.name),
            'desc-alf': desc(Favorite.name)
        }
        self.old_columns = [
            'md_id', 
            'ml_id', 
            'ms_id', 
            'mc_id', 
            'mf_id', 
            'mx_id', 
            'tcb_id', 
            'tsct_id', 
            'op_id', 
            'gkk_id', 
            'lmorg_id'
        ]

    def get_session(self) -> Session:
        self.create_database()
        return Session(self.engine)

    def create_database(self):
        if not Path(self.database_path).exists():
            self.dir.mkdir(parents=True, exist_ok=True)
        SQLModel.metadata.create_all(self.engine, checkfirst=True)

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

    def init_database(self):
        self.create_database()
        self.fix_favorites()
        self.fix_readed()
    
    def fix_favorites(self):
        table_columns = self.execute_data('PRAGMA TABLE_INFO(favorites);')
        for column in self.columns:
            if column not in [i['name'] for i in table_columns]:
                if column == 'notify':
                    self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} BOOLEAN DEFAULT FALSE;')
                    continue
                self.execute_data(f'ALTER TABLE favorites ADD COLUMN {column} TEXT;')
        if 'source' not in [i['name'] for i in table_columns]:
            favorites = self.execute_data('SELECT * FROM favorites;')
            sess = self.get_session()
            for favorite in favorites:
                source_id_key = [i for i in list(favorite.keys()) if i.endswith('_id') and favorite[i] != None][0]
                print(source_id_key, favorite[source_id_key])
                sess.exec(
                    update(Favorite)
                    .where(Favorite.id == favorite['id'])
                    .values({
                        'source': str(source_id_key).replace('_id', ''), 
                        'source_id': favorite[source_id_key],
                        'type': 'manga'
                    })
                )
            # for column in self.old_columns:
            #     self.execute_data(f'ALTER TABLE favorites DROP COLUMN {column};')
                

    def fix_readed(self):
        table_columns = self.execute_data('PRAGMA TABLE_INFO(readed);')
        for column in [i['name'] for i in table_columns]:
            if column == 'manga_id':
                self.execute_data(
                    'ALTER TABLE readed RENAME COLUMN manga_id TO favorite_id;'
                )
            if column == 'manga_source_id':
                self.execute_data(
                    'ALTER TABLE readed RENAME COLUMN manga_source_id TO favorite_source_id;'
                )
        table_columns = self.execute_data('PRAGMA TABLE_INFO(readed);')
        for column in ['favorite_source_id', 'language']:
            if column not in [i['name'] for i in table_columns]:
                self.execute_data(f'ALTER TABLE readed ADD COLUMN {column} TEXT;')
                if column == 'favorite_source_id':
                    self.execute_data(f'CREATE UNIQUE INDEX favorite_source_id ON readed({column});')
        readeds = self.execute_data('SELECT * FROM readed;')
        if readeds:
            if readeds[0]['favorite_source_id'] == None:
                sess = self.get_session()
                for readed in readeds:
                    sess.exec(
                        update(Readed)
                        .where(Readed.id == readed['id'])
                        .values({'favorite_source_id': readed['manga_source_id']})
                    )
    
    def get_favorites(self, mark_id: str = None, order: str = 'asc', fav_type: str = None) -> list[Favorite]:
        sess = self.get_session()
        if mark_id:
            return sess.exec(
                select(Favorite)
                .join(MarkFavorite, Favorite.id == MarkFavorite.favorite_id)
                .where(MarkFavorite.mark_id == mark_id)
                .order_by(self.order_dict[f'{order}-mark' if order in ['asc', 'desc'] else order])
            ).all() if fav_type is None else sess.exec(
                select(Favorite)
                .join(MarkFavorite, Favorite.id == MarkFavorite.favorite_id)
                .where(MarkFavorite.mark_id == mark_id, Favorite.type == fav_type)
                .order_by(self.order_dict[f'{order}-mark' if order in ['asc', 'desc'] else order])
            ).all()
        return sess.exec(
            select(Favorite)
            .order_by(self.order_dict[order])
        ).all() if fav_type is None else sess.exec(
            select(Favorite)
            .where(Favorite.type == fav_type)
            .order_by(self.order_dict[order])
        ).all()
    
    def get_favorites_by_source(self, source: str) -> list[Favorite]:
        sess = self.get_session()
        return sess.exec(
            select(Favorite)
            .where(Favorite.source == source)
        ).all()

    def get_favorites_notify(self) -> list[Favorite]:
        sess = self.get_session()
        return sess.exec(
            select(Favorite)
            .where(Favorite.notify == True)
        ).all()
    
    def get_favorites_sources(self) -> list[str]:
        sess = self.get_session()
        return sess.exec(
            select(Favorite.source)
        ).unique().all()

    def get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)['config']
    
    def set_config(self, key: str, value: any) -> bool:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            data = json.load(file)
        data['config'][key] = value
        with open(self.config, 'w', encoding='UTF-8') as file:
            json.dump(data, file)
        return True
        
    def _get_config(self) -> dict:
        self.create_config()
        with open(self.config, 'r', encoding='UTF-8') as file:
            return json.load(file)

    def execute_data(self, query: str) -> list[dict] | dict | bool:
        sess = self.get_session()
        try:
            data = sess.exec(text(query)).all()
            return [i._mapping for i in data]
        except Exception as e:
            print(e)
            return False

    def add_favorite(self, manga: Manga, source: str, source_id: str, fav_type: str) -> bool:
        try:
            sess = self.get_session()
            sess.add(
                Favorite(
                    name=manga.name,
                    folder_name=manga.folder_name,
                    cover=manga.cover,
                    source=source,
                    source_id=source_id,
                    type=fav_type,
                    description=manga.description,
                    author=manga.author[0] if manga.author else 'Desconhecido',
                    # score=manga.grade,
                    notify=False
                )
            )
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_favorite(self, favorite_id: int) -> dict | bool:
        sess = self.get_session()
        data = sess.exec(
            select(Favorite)
            .where(Favorite.id == favorite_id)
        )
        return data.one() if data else False

    def set_favorite(self, manga_id: str, column: str, content: any) -> bool:
        sess = self.get_session()
        try:
            sess.exec(update(Favorite).where(Favorite.id == manga_id).values({column: content}))
        except Exception as e:
            print(e)
            return False
        return True

    def delete_favorite(self, manga_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                delete(Favorite)
                .where(Favorite.id == manga_id)
            )
            sess.exec(
                delete(MarkFavorite)
                .where(MarkFavorite.favorite_id == manga_id)
            )
            sess.exec(
                delete(Readed)
                .where(Readed.favorite_id == manga_id)
            )
        except Exception as e:
            print(e)
            return False
        return True
        
    def delete_favorite_by_key(self, key: str, id: int | str) -> bool:
        sess = self.get_session()
        try:
            favorite = sess.exec(
                select(Favorite)
                .where(
                    Favorite.source == key,
                    Favorite.source_id == id
                )
            ).one()
            sess.exec(
                delete(Favorite)
                .where(
                    Favorite.source == key,
                    Favorite.source_id == id
                )
            )
            sess.exec(
                delete(MarkFavorite)
                .where(MarkFavorite.favorite_id == favorite.id)
            )
        except Exception as e:
            print(e)
            return False
        return True

    def is_notify(self, manga_id: int) -> bool:
        sess = self.get_session()
        data = sess.exec(
            select(Favorite)
            .where(Favorite.id == manga_id)
        )
        return data.one().notify
    
    def add_notify(self, manga_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                update(Favorite)
                .where(Favorite.id == manga_id)
                .values({'notify': True})
            )
        except Exception as e:
            print(e)
            return False
        return True
    
    def delete_notify(self, manga_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                update(Favorite)
                .where(Favorite.id == manga_id)
                .values({'notify': False})
            )
        except Exception as e:
            print(e)
            return False
        return True

    def is_favorite(self, key, content) -> bool:
        sess = self.get_session()
        data = sess.exec(
            select(Favorite)
            .where(
                Favorite.source == key,
                Favorite.source_id == content
            )
        ).all()
        return True if data else False
    
    def is_readed(self, source: str, manga_id: str, manga_source_id: str, chapter_id: str, language: str = None) -> bool:
        sess = self.get_session()
        data = sess.exec(
            select(Readed)
            .where(
                Readed.favorite_id == manga_id,
                Readed.chapter_id == chapter_id,
                Readed.favorite_source_id == manga_source_id,
                Readed.source == source,
                Readed.language == language
            )
        ).all()
        return data != []
    
    def is_each_readed(self, source: str, favorite_id: str, favorite_source_id: str, chapters: list[Chapter]) -> list[bool]:
        sess = self.get_session()
        list_readed = sess.exec(
            select(Readed)
            .where(
                Readed.favorite_id == favorite_id,
                Readed.favorite_source_id == favorite_source_id,
                Readed.source == source
            )
        ).all()
        if not list_readed:
            return [False for _ in range(len(chapters))]
        return [
            chapter.id in [i.chapter_id for i in list_readed]
            for chapter in chapters
        ]
    
    def is_one_readed(self, source: str, manga_id: str, manga_source_id: str, chapters: list[Chapter]) -> bool:
        is_each_readed = self.is_each_readed(source, manga_id, manga_source_id, chapters)
        for is_readed in is_each_readed:
            if is_readed:
                return True
        return False
    
    def get_last_readed(self, manga_id: str) -> Readed:
        sess = self.get_session()
        data = sess.exec(
            select(Readed)
            .limit(1)
            .where(
                Readed.favorite_id == manga_id
            ).order_by(desc(Readed.chapter_id))
        ).all()
        return data[0] if data else None

    def get_last_readed_by_source(self, source: str, manga_id: str) -> Readed:
        sess = self.get_session()
        data = sess.exec(
            select(Readed)
            .limit(1)
            .where(
                Readed.favorite_id == manga_id,
                Readed.source == source
            ).order_by(desc(Readed.chapter_id))
        ).all()
        return data[0] if data else None
    
    def add_readed(self, source: str, manga_id: str, manga_source_id, chapter_id: str, language: str = None) -> bool:
        sess = self.get_session()
        try:
            sess.add(
                Readed(
                    favorite_id=manga_id,
                    favorite_source_id=manga_source_id,
                    chapter_id=chapter_id,
                    source=source,
                    language=language
                )
            )
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def add_all_readed_below(self, favorite: Favorite, source: str, currently_chapter: Chapter, chapters: list[Chapter], language: str = None) -> bool:
        sess = self.get_session()
        try:
            each_readed = self.is_each_readed(source, favorite.id, favorite.source_id, chapters)
            readeds: list[Readed] = []
            for chapter, is_readed in zip(reversed(chapters), reversed(each_readed)):
                if not is_readed:
                    readeds.append(
                        Readed(
                            favorite_id=favorite.id,
                            favorite_source_id=favorite.source_id,
                            chapter_id=chapter.id,
                            source=source,
                            language=language
                        )
                    )
                if chapter.id == currently_chapter.id:
                    break
            sess.add_all(readeds)
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete_readed(self, source: str, manga_id: str, manga_source_id: str, chapter_id: str, language: str = None) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                delete(Readed)
                .where(
                    Readed.chapter_id == chapter_id,
                    Readed.favorite_id == manga_id,
                    Readed.favorite_source_id == manga_source_id,
                    Readed.source == source,
                    Readed.language == language
                )
            )
            return True
        except Exception as e:
            print(e)
            return False
        
    def delete_all_readed_above(self, favorite: Favorite, source: str, currently_chapter: Chapter, chapters: list[Chapter], language: str = None) -> bool:
        sess = self.get_session()
        try:
            for chapter in chapters:
                sess.exec(
                    delete(Readed)
                    .where(
                        Readed.chapter_id == chapter.id,
                        Readed.favorite_id == favorite.id,
                        Readed.favorite_source_id == favorite.source_id,
                        Readed.source == source,
                        Readed.language == language
                    )
                )
                if chapter.id == currently_chapter.id:
                    break
            return True
        except Exception as e:
            print(e)
            return False

    def add_mark(self, name: str) -> bool:
        sess = self.get_session()
        try:
            sess.add(
                Mark(name=name)
            )
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_marks(self) -> list[Mark]:
        sess = self.get_session()
        return sess.exec(select(Mark)).all()
    
    def get_mark(self, mark_id: int) -> Mark:
        sess = self.get_session()
        return sess.get(Mark, mark_id)

    def delete_mark(self, mark_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                delete(Mark)
                .where(
                    Mark.id == mark_id
                )
            )
            sess.exec(
                delete(MarkFavorite)
                .where(
                    MarkFavorite.mark_id == mark_id
                )
            )
            return True
        except Exception as e:
            print(e)
            return False
        
    def add_mark_favorite(self, favorite_id: int, mark_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.add(
                MarkFavorite(
                    mark_id=mark_id,
                    favorite_id=favorite_id
                )
            )
            sess.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def edit_mark(self, mark_id: int, name: str) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                update(Mark)
                .where(Mark.id == mark_id)
                .values({'name': name})
            )
            return True
        except Exception as e:
            print(e)
            return False

    def is_marked(self, favorite_id: int, mark_id: int) -> bool:
        sess = self.get_session()
        data = sess.exec(
            select(MarkFavorite)
            .where(
                MarkFavorite.mark_id == mark_id, 
                MarkFavorite.favorite_id == favorite_id
            ) 
        )
        if data.all():
            return True
        return False
    
    def delete_mark_favorite(self, favorite_id: int, mark_id: int) -> bool:
        sess = self.get_session()
        try:
            sess.exec(
                delete(MarkFavorite)
                .where(
                    MarkFavorite.mark_id == mark_id,
                    MarkFavorite.favorite_id == favorite_id
                )
            )
            return True
        except Exception as e: 
            print(e)
            return False
