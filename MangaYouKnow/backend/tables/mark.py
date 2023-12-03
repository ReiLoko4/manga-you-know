from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Mark(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, )
    name = Column(String, nullable=False)

    def __init__(
        self, name: int = None
    ) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Mark {self.name}>'
