from dataclasses import dataclass


@dataclass
class Episode:
    url: str 
    label: str | None = None
    headers: dict | None = None
    cookies: str | None = None
