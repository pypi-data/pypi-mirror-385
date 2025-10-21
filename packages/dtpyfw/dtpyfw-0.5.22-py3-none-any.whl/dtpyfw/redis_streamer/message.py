import json
from dataclasses import dataclass
from typing import Dict


@dataclass
class Message:
    name: str
    body: Dict

    def get_json_encoded(self) -> Dict[str, str]:
        """Return a JSON-encoded representation of the message.
        
        Returns:
            Dict[str, str]: Dictionary with 'name' and JSON-encoded 'body'.
        """
        return {"name": self.name, "body": json.dumps(self.body, default=str)}
