from gw_enumerations.base_enum import SmartEnum

class RiskObject(SmartEnum):
    """
    RiskObject is an enumeration class that represents various types of risk objects 
    commonly used in insurance contexts. Each member of the enumeration is defined 
    with a unique identifier and a human-readable name.
    """
    BUILDING = ("building", "Building")
    CONTENTS = ("contents", "Contents")
    STOCK = ("stock", "Stock")
    VEHICLE = ("vehicle", "Vehicle")
    TRAVELER = ("traveler", "Traveler")
    COMPUTER_EQUIPMENT = ("computer_equipment", "Computer Equipment")
    MACHINERY = ("machinery", "Machinery")
    BUSINESS_INTERRUPTION = ("business_interruption", "Business Interruption")
    MONEY = ("money", "Money")
    EMPLOYEE = ("employee", "Employee")
    LIABILITY = ("liability", "Liability")
    CARGO = ("cargo", "Cargo")
    PORTABLE_EQUIPMENT = ("portable_equipment", "Portable Equipment")
    FARM_PROPERTY = ("farm_property", "Farm Property")
    LIVESTOCK = ("livestock", "Livestock")
    MEDICAL_EQUIPMENT = ("medical_equipment", "Medical Equipment")
    ARTWORK = ("artwork", "Artwork")
    VESSEL = ("vessel", "Vessel")
    AIRCRAFT = ("aircraft", "Aircraft")
    PET = ("pet", "Pet")
