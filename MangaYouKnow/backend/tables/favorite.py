from sqlmodel import SQLModel, Field


class Favorite(SQLModel, table=True):
    __tablename__ = 'favorites'
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False, index=True)
    folder_name: str = Field(nullable=False)
    cover: str = Field(nullable=False)
    source: str = Field(nullable=False, index=True)
    source_id: str = Field(nullable=False, index=True)
    type: str = Field(nullable=False, index=True)
    description: str = Field(nullable=True)
    author: str = Field(nullable=True, index=True)
    score: float = Field(nullable=True)
    notify: bool = Field(default=False, index=True)

