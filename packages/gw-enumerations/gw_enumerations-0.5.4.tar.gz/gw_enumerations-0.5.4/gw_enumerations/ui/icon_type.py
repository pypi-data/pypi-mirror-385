from gw_enumerations.base_enum import SmartEnum


class IconType(SmartEnum):
    """
    IconType is an enumeration class that extends SmartEnum to represent various types of icons 
    used in the application. Each enumeration member is defined with a unique code, a label, 
    and a path to the corresponding icon image.
    """
    MONEY = ("money", "Money", "/app/static/MoneyAttribute.png")
    TEXT = ("text", "Text", "/app/static/TextAttribute.png")
    PARTY = ("party", "Party", "/app/static/PartyAttribute.png")
    DATE_TIME = ("date_time", "DateTime", "/app/static/DateTimeAttribute.png")
    DECIMAL = ("decimal", "Decimal", "/app/static/DecimalAttribute.png")
    DROP_DOWN = ("drop_down", "DropDown", "/app/static/DropdownAttribute.png")
    INTEGER = ("integer", "Integer", "/app/static/IntegerAttribute.png")
    LOCATION = ("location", "Location", "/app/static/LocationAttribute.png")
    PRODUCT = ("product", "Product", "/app/static/Product.png")
    RISK_OBJECT = ("risk_object", "RiskObject", "/app/static/RiskObject.png")
    COVERAGE = ("coverage", "Coverage", "/app/static/Coverage.png")
    SECTION = ("section", "Section", "/app/static/ClauseCategory.png")
    LINE = ("line", "Line", "/app/static/Line.png")
    CONDITION = ("condition", "Condition", "/app/static/Condition.png")
    EXCLUSION = ("exclusion", "Exclusion", "/app/static/Exclusion.png")
    RISK_ATTRIBUTE_CATEGORY = ("risk_attribute_category", "Risk Attribute Category", "/app/static/RiskAttributeCategory.png")

    def __init__(self, code, label, icon_path):
        super().__init__(code, label)
        self.icon_path = None
        object.__setattr__(self, "icon_path", icon_path)