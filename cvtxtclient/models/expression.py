from pydantic import BaseModel
from typing import Optional

class Expression(BaseModel):
    """Represents an expression to be evaluated by the debugger."""
    command: Optional[str] = None
    """Debugger command associated with the expression."""
    expression_key: str
    """Key of the expression."""
    type: Optional[str] = None
    """Data type of the expression's value."""
    value: Optional[str] = None
    """Current value of the expression."""