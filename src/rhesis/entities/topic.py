from rhesis.entities import BaseEntity
from typing import Any


class Topic(BaseEntity):
    endpoint = "topics"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
