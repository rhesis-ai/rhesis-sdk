from rhesis.entities import BaseEntity
from typing import Any


class Behavior(BaseEntity):
    endpoint = "behaviors"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
