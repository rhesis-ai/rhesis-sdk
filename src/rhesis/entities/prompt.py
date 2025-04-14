from rhesis.entities import BaseEntity
from typing import Any


class Prompt(BaseEntity):
    endpoint = "prompts"

    def __init__(self, **fields: Any) -> None:
        super().__init__(**fields)

        self.content = fields.get("content", None)
        self.language_code = fields.get("language_code", None)
