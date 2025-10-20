# SPDX-License-Identifier: Apache-2.0
"""
SearchyPy - Placeholder Package

This is a minimal placeholder to reserve the 'searchypy' name on PyPI.
The actual implementation may be developed in the future.

Related project: SortyPy - https://github.com/mdasifbinkhaled/SortyPy
"""

__version__ = "0.0.1"
__all__ = ["__version__"]


def _placeholder_message():
    """Display a message indicating this is a placeholder package."""
    return (
        "⚠️  This is a placeholder package to reserve the PyPI name.\n"
        "SearchyPy is a planned companion to SortyPy.\n"
        "Visit https://github.com/mdasifbinkhaled/SortyPy for more information."
    )


# Display message when imported
print(_placeholder_message())
