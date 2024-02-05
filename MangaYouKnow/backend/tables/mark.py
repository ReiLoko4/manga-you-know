from sqlmodel import SQLModel, Field


class Mark(SQLModel, table=True):
    __tablename__ = 'marks'
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
