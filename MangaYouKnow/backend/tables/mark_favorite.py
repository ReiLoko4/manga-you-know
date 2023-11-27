from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class MarkFavorite(Base):
    __tablename__ = 'mark_favorite'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mark_id = Column(Integer, nullable=False)
    favorite_id = Column(Integer, nullable=False)

    def __init__(
        self, mark_id: int = None, 
        favorite_id: int = None
    ) -> None:
        self.mark_id = mark_id
        self.favorite_id = favorite_id

    def __repr__(self) -> str:
        return f'<MarkFavorite {self.mark_id} {self.favorite_id}>'
    