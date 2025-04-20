from pydantic import BaseModel
from typing import List, Optional
from .breakpoint import Breakpoint
from .expression import Expression

class DebuggerArguments(BaseModel):
    """Arguments for the debugger."""
    breakpoints: Optional[List[Breakpoint]] = None
    """List of breakpoints to set."""
    expressions: Optional[List[Expression]] = None
    """List of expressions to evaluate."""
    pdb_args: Optional[List[str]] = None
    """List of arguments to pass to the PDB debugger."""