from gw_enumerations.base_enum import SmartEnum

class Environment(SmartEnum):
    """
    Environment is a SmartEnum class that represents various deployment environments.
    """
    DEV = ("dev", "Development")
    TEST = ("test", "Test")
    STAGING = ("staging", "Staging")
    PROD = ("prod", "Production")
