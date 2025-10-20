from gw_enumerations.base_enum import SmartEnum

class Status(SmartEnum):
    """
    Status is an enumeration class that represents various states or statuses 
    that an entity can have. It inherits from SmartEnum, providing additional 
    functionality for enumerations.
    """
    ACTIVE = ("active", "Active")
    INACTIVE = ("inactive", "Inactive")
    DRAFT = ("draft", "Draft")
    ARCHIVED = ("archived", "Archived")
