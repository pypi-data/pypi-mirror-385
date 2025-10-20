from gw_enumerations.base_enum import SmartEnum

class Role(SmartEnum):
    """
    Role is an enumeration class that defines various roles within the system.
    """
    ADMIN = ("admin", "Admin")
    UNDERWRITER = ("underwriter", "Underwriter")
    BROKER = ("broker", "Broker")
    CLIENT = ("client", "Client")
