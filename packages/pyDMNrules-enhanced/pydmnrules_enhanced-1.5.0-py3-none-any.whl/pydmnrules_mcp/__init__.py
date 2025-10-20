"""
pyDMNrules MCP Server

A Model Context Protocol (MCP) server for pyDMNrules DMN decision engine.
Enables LLMs to load, manage, and execute DMN rules.
"""

__version__ = "1.0.0"
__author__ = "uengine (rickjang)"
__license__ = "MIT"

from .server import (
    DMNModel,
    PyDMNrulesEngine,
    DecisionResult,
    mcp,
    main
)

__all__ = [
    "DMNModel",
    "PyDMNrulesEngine", 
    "DecisionResult",
    "mcp",
    "main",
    "__version__"
]

