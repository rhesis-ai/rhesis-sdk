from rhesis.entities import BaseEntity
from typing import Any


class Category(BaseEntity):
    endpoint = "categories"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
