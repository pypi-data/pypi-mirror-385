from gw_enumerations.base_enum import SmartEnum

class LineOfBusiness(SmartEnum):
    """
    LineOfBusiness is an enumeration class that categorizes various types of insurance lines of business.
    Each enumeration value is represented as a tuple containing a unique identifier and a descriptive name.
    """
    # Personal Lines
    HOME = ("home", "Homeowners")
    MOTOR = ("motor", "Motor")
    TRAVEL = ("travel", "Travel")
    PET = ("pet", "Pet")
    PERSONAL_ACCIDENT = ("personal_accident", "Personal Accident")
    MOBILE_DEVICE = ("mobile_device", "Mobile Device")
    LIFE = ("life", "Life")
    HEALTH = ("health", "Health")

    # Commercial Lines
    PROPERTY = ("property", "Commercial Property")
    LIABILITY = ("liability", "General Liability")
    EMPLOYERS_LIABILITY = ("employers_liability", "Employers' Liability")
    PUBLIC_LIABILITY = ("public_liability", "Public Liability")
    PRODUCT_LIABILITY = ("product_liability", "Product Liability")
    PROFESSIONAL_INDEMNITY = ("professional_indemnity", "Professional Indemnity")
    CYBER = ("cyber", "Cyber")
    DIRECTORS_OFFICERS = ("d_and_o", "Directors & Officers (D&O)")
    COMMERCIAL_AUTO = ("commercial_auto", "Commercial Auto")
    BUSINESS_INTERRUPTION = ("business_interruption", "Business Interruption")
    WORKERS_COMP = ("workers_comp", "Workers' Compensation")
    CONSTRUCTION = ("construction", "Construction / CAR / EAR")
    ENGINEERING = ("engineering", "Engineering")
    MARINE_CARGO = ("marine_cargo", "Marine Cargo")
    MARINE_HULL = ("marine_hull", "Marine Hull")
    ENERGY = ("energy", "Energy")
    AVIATION = ("aviation", "Aviation")
    SPACE = ("space", "Space")
    TRANSIT = ("transit", "Goods in Transit")
    BOND = ("bond", "Surety / Bonds")

    # Specialty & Niche
    FINE_ART = ("fine_art", "Fine Art and Specie")
    TERRORISM = ("terrorism", "Terrorism")
    POLITICAL_RISK = ("political_risk", "Political Risk")
    CREDIT = ("credit", "Credit Insurance")
    LEGAL_EXPENSES = ("legal_expenses", "Legal Expenses")
    EVENT_CANCELLATION = ("event_cancellation", "Event Cancellation")
    SPORTS = ("sports", "Sports & Leisure")
    AGRICULTURE = ("agriculture", "Agriculture / Crop / Livestock")
    WEATHER = ("weather", "Weather Parametric")

    # Reinsurance
    TREATY_PROP = ("treaty_prop", "Treaty Proportional")
    TREATY_XOL = ("treaty_xol", "Treaty Excess of Loss")
    FACULTATIVE = ("facultative", "Facultative Reinsurance")
    BINDER = ("binder", "Delegated Authority / Binder")
