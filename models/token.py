from dataclasses import dataclass, field
from .token_location import TokenLocation

@dataclass
class Token:
    text: str
    repo: str
    locations: list[TokenLocation]
    misspelled: bool = None
    ignore: str = 'N'

