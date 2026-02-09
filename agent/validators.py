"""Input validation utilities for security.

Provides validation functions to prevent path traversal, injection attacks,
and other security vulnerabilities from user-supplied inputs.
"""

import re
from typing import Optional


def validate_project_id(project_id: str) -> bool:
    """Validate project ID to prevent path traversal attacks.

    Project IDs must be lowercase alphanumeric with hyphens only.
    This prevents patterns like "../../../etc/passwd" from being used.

    Args:
        project_id: The project ID to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_project_id("my-project-123")
        True
        >>> validate_project_id("../etc/passwd")
        False
        >>> validate_project_id("project/with/slashes")
        False
    """
    if not project_id or not isinstance(project_id, str):
        return False

    # Must be 1-100 characters, lowercase alphanumeric with hyphens
    # No dots, slashes, or other special characters
    pattern = r'^[a-z0-9]([a-z0-9-]{0,98}[a-z0-9])?$'
    return bool(re.match(pattern, project_id))


def validate_user_role(user_role: str) -> bool:
    """Validate user role against allowed values.

    Args:
        user_role: The user role to validate

    Returns:
        True if valid, False otherwise
    """
    if not user_role or not isinstance(user_role, str):
        return False

    allowed_roles = {
        "process_owner",
        "business_analyst",
        "sme",
        "developer",
    }

    return user_role.lower() in allowed_roles


def validate_file_path(file_path: str, allowed_extensions: Optional[set] = None) -> bool:
    """Validate file path for safe file operations.

    Args:
        file_path: The file path to validate
        allowed_extensions: Optional set of allowed file extensions (e.g., {'.pdf', '.docx'})

    Returns:
        True if valid, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False

    # Prevent path traversal
    if ".." in file_path or file_path.startswith("/") or "\\" in file_path:
        return False

    # Check allowed extensions if provided
    if allowed_extensions:
        extension = file_path[file_path.rfind("."):].lower() if "." in file_path else ""
        if extension not in allowed_extensions:
            return False

    return True


def sanitize_project_id(project_id: str) -> str:
    """Sanitize a project name to create a valid project ID.

    Converts to lowercase, replaces spaces/underscores with hyphens,
    removes special characters.

    Args:
        project_id: The raw project name

    Returns:
        Sanitized project ID safe for file system use

    Examples:
        >>> sanitize_project_id("My Project 2024")
        'my-project-2024'
        >>> sanitize_project_id("SD_Light Invoicing!")
        'sd-light-invoicing'
    """
    # Convert to lowercase
    result = project_id.lower()

    # Replace spaces and underscores with hyphens
    result = result.replace(" ", "-").replace("_", "-")

    # Remove all non-alphanumeric except hyphens
    result = re.sub(r'[^a-z0-9-]', '', result)

    # Replace multiple consecutive hyphens with single hyphen
    result = re.sub(r'-+', '-', result)

    # Remove leading/trailing hyphens
    result = result.strip("-")

    return result


if __name__ == "__main__":
    # Quick tests
    test_cases = [
        ("my-project", True),
        ("test-project-123", True),
        ("../etc/passwd", False),
        ("project/with/slash", False),
        ("UPPERCASE", False),
        ("a" * 100, True),
        ("a" * 101, False),
    ]

    print("Testing validate_project_id:")
    for test_id, expected in test_cases:
        result = validate_project_id(test_id)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{test_id[:30]}...' -> {result} (expected {expected})")
