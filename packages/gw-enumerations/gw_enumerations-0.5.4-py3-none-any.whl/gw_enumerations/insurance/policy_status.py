from gw_enumerations.base_enum import SmartEnum

class PolicyStatus(SmartEnum):
    """
    PolicyStatus is an enumeration that represents the various statuses a policy can have in an insurance system.
    """
    QUOTED = ("quoted", "Quoted")
    BOUND = ("bound", "Bound")
    ISSUED = ("issued", "Issued")
    EXPIRED = ("expired", "Expired")
    CANCELLED = ("cancelled", "Cancelled")
