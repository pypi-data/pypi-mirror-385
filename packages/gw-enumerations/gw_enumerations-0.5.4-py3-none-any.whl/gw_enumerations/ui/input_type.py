from gw_enumerations.base_enum import SmartEnum

class InputType(SmartEnum):
    """
    InputType is an enumeration class that defines various types of input fields 
    used in a user interface. Each enumeration value is represented as a tuple 
    containing a string identifier and a human-readable name.
    """
    TEXT = ("string", "Text")
    INTEGER = ("integer", "Integer")
    DECIMAL = ("decimal", "Decimal")
    DATE = ("date", "Date")
    BOOLEAN = ("boolean", "Yes/No")
    SELECT = ("select", "Dropdown")
    TEXTAREA = ("textarea", "Text Area")
