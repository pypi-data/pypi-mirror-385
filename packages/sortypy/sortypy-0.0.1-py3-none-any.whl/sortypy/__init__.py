# SPDX-License-Identifier: Apache-2.0
"""
SortyPy - Placeholder Package

This is a minimal placeholder to reserve the 'sortypy' name on PyPI.
The actual implementation is under development.

For more information, visit: https://github.com/mdasifbinkhaled/SortyPy
"""

__version__ = "0.0.1"
__all__ = ["__version__"]


def _placeholder_message():
    """Display a message indicating this is a placeholder package."""
    return (
        "⚠️  This is a placeholder package to reserve the PyPI name.\n"
        "The actual SortyPy library is under active development.\n"
        "Visit https://github.com/mdasifbinkhaled/SortyPy for updates."
    )


# Display message when imported
print(_placeholder_message())
