import dataclasses
import typing
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(init=False)
class ResponseBase:
    def __init__(self, json_data: Dict[str, Any] = None):
        if json_data is not None:
            self.populate(json_data)

    def populate(self, json_data):
        fields = dataclasses.fields(self)
        for field in fields:
            # Resolve the corresponding JSON key allowing for overrides
            json_metadata = field.metadata.get("json")
            json_key = field.name if json_metadata is None else json_metadata

            # Skip this field if not found in JSON
            if json_key not in json_data:
                setattr(self, field.name, None)
                continue

            value = json_data[json_key]

            field_type = self._resolve_underlying_type(field.type)
            if issubclass(field_type, ResponseBase):
                if isinstance(value, list):
                    value = [field_type(json_data=v) for v in value]
                else:
                    value = field_type(json_data=value)

            # Set the object field
            setattr(self, field.name, value)

    @staticmethod
    def _resolve_underlying_type(t):
        if isinstance(t, type):
            return t

        # Handle typing
        if hasattr(t, "__args__"):
            return ResponseBase._resolve_underlying_type(t.__args__[0])

        raise ValueError(f"Unhandled type: {t}")