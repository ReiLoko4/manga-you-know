from dataclasses import dataclass
from datetime import datetime as dt
from backend.models import Chapter
from backend.constants import DataType


@dataclass
class Data:
    model: DataType
    id: str | int
    source: str
    date: dt = dt.now()
    data: list[str] | list[Chapter] = None
    language: str = None

    def is_ten_minutes_old(self) -> bool:
        return (dt.now() - self.date).seconds >= 600
    
