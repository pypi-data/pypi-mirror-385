from gw_enumerations.base_enum import SmartEnum


class RiskClass(SmartEnum):
    """
    RiskClass is an enumeration that categorizes various types of insurance risk classes.
    Each enumeration member is represented as a tuple containing a unique identifier and
    a human-readable name.
    """

    CYBER = ("cyber", "Cyber")
    GENERAL_LIABILITY = ("general_liability", "General Liability")
    PUBLIC_LIABILITY = ("public_liability", "Public Liability")
    PRODUCT_LIABILITY = ("product_liability", "Product Liability")
    PROFESSIONAL_INDEMNITY = ("professional_indemnity", "Professional Indemnity")
    DIRECTORS_OFFICERS = ("directors_officers", "Directors & Officers")
    EMPLOYERS_LIABILITY = ("employers_liability", "Employers’ Liability")
    ENVIRONMENTAL_LIABILITY = ("environmental_liability", "Environmental Liability")

    PROPERTY_RESIDENTIAL = ("property_residential", "Residential Property")
    PROPERTY_COMMERCIAL = ("property_commercial", "Commercial Property")
    PROPERTY_INDUSTRIAL = ("property_industrial", "Industrial Property")
    BUILDERS_RISK = ("builders_risk", "Builders Risk")

    PRIVATE_MOTOR = ("private_motor", "Private Motor")
    COMMERCIAL_MOTOR = ("commercial_motor", "Commercial Motor")
    MOTOR_FLEET = ("motor_fleet", "Motor Fleet")
    MOTORCYCLE = ("motorcycle", "Motorcycle")
    AGRICULTURAL_VEHICLE = ("agricultural_vehicle", "Agricultural Vehicle")

    MARINE_CARGO = ("marine_cargo", "Marine Cargo")
    MARINE_HULL = ("marine_hull", "Marine Hull")
    MARINE_LIABILITY = ("marine_liability", "Marine Liability")
    YACHT = ("yacht", "Yacht")

    AVIATION_HULL = ("aviation_hull", "Aviation Hull")
    AVIATION_LIABILITY = ("aviation_liability", "Aviation Liability")

    CRIME = ("crime", "Crime / Fidelity")
    KIDNAP_RANSOM = ("kidnap_ransom", "Kidnap & Ransom")
    TRADE_CREDIT = ("trade_credit", "Trade Credit")
    SURETY = ("surety", "Surety / Bond")
    POLITICAL_RISK = ("political_risk", "Political Risk")

    HOMEOWNERS = ("homeowners", "Homeowners")
    RENTERS = ("renters", "Tenants / Renters")
    TRAVEL = ("travel", "Travel")
    PET = ("pet", "Pet")
    GADGET = ("gadget", "Gadget / Mobile Device")

    INDIVIDUAL_HEALTH = ("individual_health", "Individual Health")
    GROUP_HEALTH = ("group_health", "Group Health")
    CRITICAL_ILLNESS = ("critical_illness", "Critical Illness")
    LIFE = ("life", "Life Insurance")
    INCOME_PROTECTION = ("income_protection", "Income Protection")
    DISABILITY = ("disability", "Disability")

    TREATY_PROPORTIONAL = ("treaty_proportional", "Treaty Proportional Reinsurance")
    TREATY_NON_PROPORTIONAL = (
        "treaty_non_proportional",
        "Treaty Non-Proportional Reinsurance",
    )
    FACULTATIVE = ("facultative", "Facultative Reinsurance")
