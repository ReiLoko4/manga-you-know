from dataclasses import dataclass


@dataclass
class Episode:
    url: str 
    label: str | None = None
