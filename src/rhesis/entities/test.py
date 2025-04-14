from rhesis.entities import BaseEntity
from typing import Any


class Test(BaseEntity):
    endpoint = "tests"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)
        self.category = fields.get("category", None)
        self.topic = fields.get("topic", None)
        self.behavior = fields.get("behavior", None)
        self.prompt = fields.get("prompt", None)
