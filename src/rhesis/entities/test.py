from rhesis.entities import BaseEntity
from typing import Any


class Test(BaseEntity):
    endpoint = "tests"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
