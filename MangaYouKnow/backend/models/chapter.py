from dataclasses import dataclass


@dataclass
class Chapter:
    id: str | int
    number: str | int
    title: str = None
