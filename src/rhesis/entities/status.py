from rhesis.entities import BaseEntity
from typing import Any


class Status(BaseEntity):
    endpoint = "statuses"  # Yes, this is not pretty, but the plural of status is statuses, check on Merriam-Webster ;)

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
