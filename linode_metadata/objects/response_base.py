"""
This class is the base class for response classes.
It includes basic methods for handling JSON responses.
"""

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(init=False)
class ResponseBase:
    """
    The base class for responses from the Linode Metadata Service.
    :param json_data: The JSON data that will be used to build an instance of a response class.
    :type json_data: Dict[str, Any]
    """

    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        if json_data is not None:
            self.populate(json_data)

    def populate(self, json_data):
        """
        Populates the fields in a response dataclass using the passed JSON data.
        """
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
        """
        Resolves the type of an object.
        """
        if isinstance(t, type):
            return t

        # Handle typing
        if hasattr(t, "__args__"):
            return ResponseBase._resolve_underlying_type(t.__args__[0])

        raise ValueError(f"Unhandled type: {t}")
