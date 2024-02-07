from sqlmodel import SQLModel, Field


class Favorite(SQLModel, table=True):
    __tablename__ = 'favorites'
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    folder_name: str = Field(nullable=False)
    cover: str = Field(nullable=False)
    source: str = Field(nullable=False)
    source_id: str = Field(nullable=False)
    type: str = Field(nullable=False)
    description: str = Field(nullable=True)
    author: str = Field(nullable=True)
    score: float = Field(nullable=True)
    notify: bool = False

