"""
JAX-based computation tools for HIDENNSIM MCP server.
"""

from .add_jax import execute_add_jax
from .subtract_jax import execute_subtract_jax  # ADD THIS LINE

__all__ = [
    "execute_add_jax",
    "execute_subtract_jax",  # ADD THIS LINE
]