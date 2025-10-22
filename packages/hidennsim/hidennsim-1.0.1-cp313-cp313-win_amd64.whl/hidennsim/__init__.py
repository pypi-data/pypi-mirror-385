"""
HIDENNSIM - Secure MCP Server with JAX Integration.

A licensed Model Context Protocol (MCP) server providing JAX-based
numerical computation tools with hardware-bound license validation.
"""

__version__ = "1.0.1"
__author__ = "HIDENNSIM Team"
__license__ = "Proprietary"

from .server import HIDENNSIMServer

__all__ = ["HIDENNSIMServer"]
