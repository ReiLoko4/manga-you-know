from dataclasses import dataclass


@dataclass
class Manga:
    id: str | int
    name: str
    folder_name: str
    cover: str
    description: str = None
    extra_name: str | list[str] = None
    author: str | list[str] = None
    grade: float = None
