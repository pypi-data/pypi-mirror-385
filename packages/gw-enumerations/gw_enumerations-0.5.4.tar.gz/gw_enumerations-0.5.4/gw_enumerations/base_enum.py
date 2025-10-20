from enum import Enum

class SmartEnum(Enum):
    """
    SmartEnum is an extension of the Enum class that provides additional functionality for managing
    enumerations with associated codes and labels. It is designed to simplify the process of working
    with enumerations that require human-readable labels and unique codes.

    Usage:
        This class can be used to define enumerations with additional metadata (code and label) and
        provides utility methods for querying and resolving enumeration values based on various
        attributes.
    """
    def __init__(self, code: str, label: str):
        super().__init__()
        object.__setattr__(self, "_code", code)
        object.__setattr__(self, "_label", label)

    @property
    def code(self):
        return self._code

    @property
    def label(self):
        return self._label

    def __str__(self):
        return self.label

    @classmethod
    def from_code(cls, code: str):
        """
        Retrieve an enumeration member by its code.

        Args:
            code (str): The code to match against the enumeration members.

        Returns:
            Enum: The enumeration member whose `code` attribute matches the given code,
                  ignoring case. Returns `None` if no match is found.
        """
        return next((item for item in cls if item.code.lower() == code.lower()), None)

    @classmethod
    def from_label(cls, label: str):
        """
        Retrieve an enumeration member by its label.

        Args:
            label (str): The label to search for in the enumeration members.

        Returns:
            Enum: The enumeration member whose label matches the provided label,
                  or None if no match is found. The comparison is case-insensitive.
        """
        return next((item for item in cls if item.label.lower() == label.lower()), None)

    @classmethod
    def from_name(cls, name: str):
        """
        Retrieve an enumeration member by its name.

        Args:
            name (str): The name of the enumeration member to retrieve.

        Returns:
            Enum: The enumeration member with the matching name, or None if no match is found.
        """
        return next((item for item in cls if item.name == name.upper()), None)

    @classmethod
    def resolve(cls, value: str):
        """
        Resolves an enumeration instance based on the provided value.

        This method attempts to find an enumeration instance by checking the value
        against different attributes in the following order:
        1. `from_code(value)` - Matches the value to a code representation.
        2. `from_label(value)` - Matches the value to a label representation.
        3. `from_name(value)` - Matches the value to a name representation.

        Args:
            value (str): The string value to resolve into an enumeration instance.

        Returns:
            Enum: The resolved enumeration instance if a match is found, or None if no match is found.
        """
        return cls.from_code(value) or cls.from_label(value) or cls.from_name(value)

    @classmethod
    def as_choices(cls, subset=None):
        """
        Converts the enumeration values into a list of choices suitable for use in 
        dropdowns or selection fields. Each choice is represented as a dictionary 
        containing a 'code' and a 'label'.

        Args:
            subset (Optional[Iterable[str]]): A subset of codes or names to filter 
                the enumeration values. If provided, only values matching the codes 
                or names in the subset will be included.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary 
            contains 'code' and 'label' keys representing the enumeration values.
        """
        values = list(cls)
        if subset:
            values = [v for v in values if v.code in subset or v.name in subset]
        return [{"code": v.code, "label": v.label} for v in values]