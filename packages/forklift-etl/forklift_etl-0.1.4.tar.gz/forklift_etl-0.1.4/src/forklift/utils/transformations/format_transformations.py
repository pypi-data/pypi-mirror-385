"""Format transformation utilities for structured data types.

This module has been refactored into a modular package structure.
This file now serves as a backward compatibility layer.

For new code, consider importing directly from the format package:
- from forklift.utils.transformations.format import SSNFormatter
- from forklift.utils.transformations.format import ZipCodeFormatter
- etc.
"""

# Import individual formatters for direct use
from .format import (
    BaseFormatter,
    EmailFormatter,
    IPAddressFormatter,
    MACAddressFormatter,
    PhoneNumberFormatter,
    SSNFormatter,
    ZipCodeFormatter,
)

# Import the refactored FormatTransformer for backward compatibility
from .format.transformer import FormatTransformer

__all__ = [
    "FormatTransformer",  # Backward compatibility
    "BaseFormatter",
    "SSNFormatter",
    "ZipCodeFormatter",
    "PhoneNumberFormatter",
    "EmailFormatter",
    "IPAddressFormatter",
    "MACAddressFormatter",
]
