from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Readed(Base):
    __tablename__ = 'readed'
    id = Column(Integer, primary_key=True, autoincrement=True)
    manga_id = Column(Integer, nullable=False)
    chapter_id = Column(Integer, nullable=False)
    source = Column(String, nullable=False)

    def __init__(
        self, manga_id: int = None, 
        chapter_id: int = None, 
        source: str = None
    ) -> None:
        self.manga_id = manga_id
        self.chapter_id = chapter_id
        self.source = source

    def __repr__(self) -> str:
        return f'<Readed {self.manga_id} {self.chapter_id} {self.source}>'