from dataclasses import dataclass, field
from typing import Any
from wowool.error import Error as WowoolError


@dataclass
class UID:
    """A UID object representing a component identifier with options.

    Attributes:
        name (str): The name of the component.
        options (dict[str,Any]): Configuration options for the component.
    """

    name: str
    options: dict[str, Any] = field(default_factory=dict)

    def to_json(self):
        """Convert the UID to a JSON-serializable dictionary.

        Returns:
            dict[str,Any]: A dictionary containing the name and options.
        """
        return {"name": self.name, "options": self.options}


def createUID(uid: str | UID | dict) -> UID:
    """Create a UID object from various input types.

    Args:
        uid (str|UID|dict): The input to create a UID from. Can be a string name,
            an existing UID object, or a dictionary with 'name' and optional 'options' keys.

    Returns:
        UID: A UID object created from the input.

    Raises:
        WowoolError: If the input type is not supported.

    Examples:
        >>> createUID("component_name")
        UID(name='component_name', options={})

        >>> createUID({"name": "component", "options": {"key": "value"}})
        UID(name='component', options={'key': 'value'})
    """
    if isinstance(uid, str):
        return UID(name=uid)
    elif isinstance(uid, UID):
        return uid
    elif isinstance(uid, dict):
        if "options" not in uid:
            uid["options"] = {}
        return UID(name=uid["name"], options=uid["options"])
    else:
        raise WowoolError(f"Invalid uid type:{type(uid)}, only support str, UID or dict")


@dataclass
class ComponentInfo:
    """Component information for pipeline components.

    Contains metadata and configuration information for a component in the pipeline.

    Attributes:
        options (dict[str,Any]): Configuration options on how the component has been initialized.
        type (str): The type of component (e.g., 'language', 'domain', 'app').
        name (str): The name of the component. (e.g., 'english.language', 'english-entity.dom').
        uid (str): Unique identifier for the component.
        filename (str|None): Optional filename associated with the component (if applicable).
        app (dict[str,str]|None): Optional application-specific information.
        original (str|None): Optional original source information.
    """

    options: dict[str, Any]
    type: str
    name: str
    uid: str
    filename: str | None = None
    app: dict[str, str] | None = None
    original: str | None = None

    def to_json(self):
        """Convert the ComponentInfo to a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: A dictionary containing the component information with
                type, uid, and optionally options, filename, and app information.
        """
        retval: dict[str, Any] = {"type": self.type, "uid": self.uid}
        if self.options:
            retval["options"] = self.options
        if self.filename:
            retval["filename"] = self.filename
        if self.app:
            retval["app"] = self.app
        return retval
