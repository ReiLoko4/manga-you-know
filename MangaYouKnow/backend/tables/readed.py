from sqlmodel import SQLModel, Field


class Readed(SQLModel, table=True):
    __tablename__ = 'readed'
    id: int = Field(primary_key=True)
    favorite_id: int = Field(foreign_key='favorites.id', nullable=False, index=True)
    favorite_source_id: str = Field(nullable=False, index=True)
    chapter_id: str = Field(nullable=False, index=True)
    source: str = Field(nullable=False, index=True)
    language: str = Field(nullable=True, index=True)
