"""
Type definitions for ADRI analysis components.

Provides clear TypedDict and Protocol definitions for standard structures,
field requirements, and data profiles to improve API clarity and type safety.
"""

from typing import Any, Dict, Optional, Protocol


class StandardMetadata(Dict[str, Any]):
    """Standard metadata structure.

    Required keys:
        id: Unique identifier for the standard
        name: Human-readable name
        version: Version string (e.g., "1.0.0")
        authority: Organization or entity that owns the standard
        description: Brief description of what the standard covers
    """

    pass


class FieldRequirement(Dict[str, Any]):
    """Field requirement structure with optional constraints.

    Common keys:
        type: Data type (string, integer, float, date, datetime, boolean)
        nullable: Whether null values are allowed
        min_length: Minimum string length (for string types)
        max_length: Maximum string length (for string types)
        pattern: Regex pattern to match (for string types)
        min_value: Minimum numeric value (for numeric types)
        max_value: Maximum numeric value (for numeric types)
        allowed_values: List of permitted values (enum constraint)
        after_date: Minimum date value (for date types)
        before_date: Maximum date value (for date types)
    """

    pass


class StandardStructure(Dict[str, Any]):
    """Complete standard structure (normalized format).

    Required top-level keys:
        standards: Metadata about the standard itself
        requirements: Field requirements and dimension requirements

    Optional top-level keys:
        record_identification: Primary key configuration
        metadata: Additional metadata (explanations, freshness, etc.)
    """

    pass


class ProfileData(Protocol):
    """Protocol for data profile objects.

    Defines the interface that ProfileResult and similar classes should implement
    to provide consistent access to profile data.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary format.

        Returns:
            Dictionary representation of the profile data
        """
        ...

    def get_field_profile(self, field_name: str) -> Dict[str, Any]:
        """Get profile information for a specific field.

        Args:
            field_name: Name of the field to get profile for

        Returns:
            Dictionary containing field profile data

        Raises:
            KeyError: If field_name is not in the profile
        """
        ...


def is_valid_standard(standard: Dict[str, Any]) -> bool:
    """Check if a standard has the correct normalized structure.

    The ONLY valid structure is:
    {
        'standards': {...},      # Metadata
        'requirements': {...}    # Field requirements & dimension requirements
    }

    Args:
        standard: Standard dictionary to validate

    Returns:
        True if standard has correct structure, False otherwise
    """
    if not isinstance(standard, dict):
        return False

    # Must have both required sections
    has_standards_section = "standards" in standard
    has_requirements_section = "requirements" in standard

    return has_standards_section and has_requirements_section


def get_standard_name(standard: Dict[str, Any]) -> Optional[str]:
    """Extract standard name from normalized format.

    Args:
        standard: Standard dictionary (must be normalized)

    Returns:
        Standard name if found, None otherwise

    Raises:
        ValueError: If standard is not in normalized format
    """
    if not is_valid_standard(standard):
        raise ValueError(
            "Standard is not in normalized format. "
            "Expected: {'standards': {...}, 'requirements': {...}}"
        )

    return standard.get("standards", {}).get("name")


def get_field_requirements(standard: Dict[str, Any]) -> Dict[str, Any]:
    """Extract field requirements from normalized format.

    Args:
        standard: Standard dictionary (must be normalized)

    Returns:
        Dictionary of field requirements (field_name -> requirements)

    Raises:
        ValueError: If standard is not in normalized format
    """
    if not is_valid_standard(standard):
        raise ValueError(
            "Standard is not in normalized format. "
            "Expected: {'standards': {...}, 'requirements': {...}}"
        )

    return standard.get("requirements", {}).get("field_requirements", {})
