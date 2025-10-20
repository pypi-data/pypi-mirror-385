from gw_enumerations.base_enum import SmartEnum

class NodeType(SmartEnum):
    """
    NodeType is an enumeration class that extends SmartEnum to represent various types of nodes 
    used in the application. Each node type is defined with a unique code, a label, and an optional 
    icon path.
    """
    PRODUCT = ("product", "Product", "/app/static/Product.png")
    RISK_OBJECT = ("risk_object", "RiskObject", "/app/static/RiskObject.png")
    LINE = ("line", "Line", "/app/static/Line.png")
    COVERAGE = ("coverage", "Coverage", "/app/static/Coverage.png")
    SECTION = ("section", "Section", "/app/static/ClauseCategory.png")
    CONDITION = ("condition", "Condition", "/app/static/Condition.png")
    EXCLUSION = ("exclusion", "Exclusion", "/app/static/Exclusion.png")
    ATTRIBUTE = ("attribute", "Attribute", None)

    def __init__(self, code, label, icon_path):
        super().__init__(code, label)
        self.icon_path = None
        object.__setattr__(self, "icon_path", icon_path)
