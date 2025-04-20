from pydantic import BaseModel
from typing import List
from .breakpoint import Breakpoint
from .program_location import ProgramLocation
from .expression import Expression

class DebuggerResponse(BaseModel):
    """Response from the debugger."""
    breakpoints: List[Breakpoint]
    """List of active breakpoints."""
    callstack: List[ProgramLocation]
    """Current call stack."""
    expressions: List[Expression]
    """List of evaluated expressions."""
    program_location: ProgramLocation
    """Current location in the program."""