from sqlmodel import SQLModel, Field


class Readed(SQLModel, table=True):
    __tablename__ = 'readed'
    id: int = Field(primary_key=True)
    favorite_id: int = Field(foreign_key='favorites.id', nullable=False)
    favorite_source_id: str = Field(nullable=False)
    chapter_id: str = Field(nullable=False)
    source: str = Field(nullable=False)
    language: str = Field(nullable=True)
