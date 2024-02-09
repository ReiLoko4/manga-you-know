from sqlmodel import SQLModel, Field


class MarkFavorite(SQLModel, table=True):
    __tablename__ = 'mark_favorite'
    id: int = Field(primary_key=True)
    mark_id: int = Field(foreign_key='marks.id', nullable=False, index=True)
    favorite_id: int = Field(foreign_key='favorites.id', nullable=False, index=True)
