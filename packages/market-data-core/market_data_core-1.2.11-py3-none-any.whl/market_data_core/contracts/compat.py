"""Semver compatibility and version negotiation helpers.

Phase 9.0 Day 2: Tools for managing schema compatibility and version negotiation.
"""

from __future__ import annotations

from typing import Literal


def compatible(version_req: str, candidate: str) -> bool:
    """Check if a candidate version satisfies a version requirement.
    
    Args:
        version_req: Version requirement (e.g., ">=1.1,<2.0" or "~=1.1")
        candidate: Version to check
        
    Returns:
        True if candidate satisfies requirement
        
    Examples:
        >>> compatible(">=1.1,<2.0", "1.2.0")
        True
        >>> compatible(">=1.1,<2.0", "2.0.0")
        False
        >>> compatible("~=1.1", "1.2.0")
        True
        >>> compatible("~=1.1", "2.0.0")
        False
    """
    try:
        from packaging.version import Version
    except ImportError:
        # Fallback to simple string comparison
        return candidate.startswith(version_req.replace("~=", "").replace(">=", ""))
    
    # Parse tilde operator
    if version_req.startswith("~="):
        base = version_req.replace("~=", "").strip()
        base_ver = Version(base)
        cand_ver = Version(candidate)
        
        # ~=1.1 means >=1.1,<2.0
        # ~=1.1.2 means >=1.1.2,<1.2.0
        parts = base.split(".")
        if len(parts) == 2:  # major.minor
            upper_major = int(parts[0]) + 1
            return base_ver <= cand_ver < Version(f"{upper_major}.0.0")
        elif len(parts) == 3:  # major.minor.patch
            upper_minor = int(parts[1]) + 1
            return base_ver <= cand_ver < Version(f"{parts[0]}.{upper_minor}.0")
    
    # Parse range (e.g., ">=1.1,<2.0")
    if "," in version_req:
        parts = version_req.split(",")
        lower_str = parts[0].strip()
        upper_str = parts[1].strip()
        
        # Parse lower bound
        if lower_str.startswith(">="):
            lower = Version(lower_str.replace(">=", "").strip())
            lower_inclusive = True
        elif lower_str.startswith(">"):
            lower = Version(lower_str.replace(">", "").strip())
            lower_inclusive = False
        else:
            return False
            
        # Parse upper bound
        if upper_str.startswith("<"):
            upper = Version(upper_str.replace("<", "").strip())
            upper_inclusive = False
        elif upper_str.startswith("<="):
            upper = Version(upper_str.replace("<=", "").strip())
            upper_inclusive = True
        else:
            return False
        
        cand_ver = Version(candidate)
        
        lower_ok = cand_ver >= lower if lower_inclusive else cand_ver > lower
        upper_ok = cand_ver < upper if not upper_inclusive else cand_ver <= upper
        
        return lower_ok and upper_ok
    
    return False


def negotiate(
    preferred: list[str], available: list[str] | None = None
) -> str:
    """Negotiate schema track version between client preferences and server capabilities.
    
    Args:
        preferred: Client's preferred tracks in priority order (e.g., ["v2", "v1"])
        available: Server's available tracks (defaults to ["v2", "v1"])
        
    Returns:
        The highest priority available track
        
    Examples:
        >>> negotiate(["v2", "v1"])
        'v2'
        >>> negotiate(["v2"], available=["v1"])
        'v1'
        >>> negotiate(["v1"], available=["v2", "v1"])
        'v1'
    """
    if available is None:
        available = ["v2", "v1"]
    
    # Return first preferred that's available
    for pref in preferred:
        if pref in available:
            return pref
    
    # Fall back to highest available version
    return available[0] if available else "v1"


def is_backward_compatible_change(
    v_from: dict, v_to: dict
) -> tuple[bool, list[str]]:
    """Check if schema change from v_from to v_to is backward compatible.
    
    Backward compatible changes (allowed in minor/patch):
    - Adding optional properties
    - Adding enum values
    - Relaxing validation (removing minimum, increasing maximum)
    
    Breaking changes (require major version):
    - Removing properties
    - Changing property types
    - Tightening validation
    - Removing enum values
    
    Args:
        v_from: Original schema (JSON Schema dict)
        v_to: New schema (JSON Schema dict)
        
    Returns:
        Tuple of (is_compatible, list_of_issues)
        
    Examples:
        >>> old = {"properties": {"name": {"type": "string"}}, "required": ["name"]}
        >>> new = {"properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name"]}
        >>> is_backward_compatible_change(old, new)
        (True, [])
        
        >>> new_breaking = {"properties": {"age": {"type": "integer"}}, "required": ["age"]}
        >>> is_backward_compatible_change(old, new_breaking)
        (False, ["Removed required property: 'name'"])
    """
    issues: list[str] = []
    
    old_props = set(v_from.get("properties", {}).keys())
    new_props = set(v_to.get("properties", {}).keys())
    old_required = set(v_from.get("required", []))
    new_required = set(v_to.get("required", []))
    
    # Check for removed properties
    removed_props = old_props - new_props
    if removed_props:
        # Check if any removed property was required
        removed_required = removed_props & old_required
        if removed_required:
            for prop in sorted(removed_required):
                issues.append(f"Removed required property: '{prop}'")
        else:
            for prop in sorted(removed_props):
                issues.append(f"Removed optional property: '{prop}' (minor breaking)")
    
    # Check for newly required properties (breaking)
    newly_required = new_required - old_required
    if newly_required:
        for prop in sorted(newly_required):
            issues.append(f"Made property required: '{prop}'")
    
    # Check type changes for common properties
    for prop in old_props & new_props:
        old_type = v_from["properties"][prop].get("type")
        new_type = v_to["properties"][prop].get("type")
        
        if old_type != new_type:
            # Type narrowing is breaking
            if isinstance(old_type, list) and isinstance(new_type, str):
                # Narrowing from union to single type - always breaking
                issues.append(
                    f"Type narrowed for '{prop}': {old_type} -> {new_type}"
                )
            elif isinstance(old_type, list) and isinstance(new_type, list):
                # Narrowing a union is breaking
                removed_types = set(old_type) - set(new_type)
                if removed_types:
                    issues.append(
                        f"Type narrowed for '{prop}': removed {sorted(removed_types)}"
                    )
            elif isinstance(old_type, str) and isinstance(new_type, list):
                if old_type not in new_type:
                    issues.append(
                        f"Type changed for '{prop}': {old_type} -> {new_type}"
                    )
            elif old_type != new_type:
                issues.append(f"Type changed for '{prop}': {old_type} -> {new_type}")
        
        # Check enum changes
        old_enum = v_from["properties"][prop].get("enum")
        new_enum = v_to["properties"][prop].get("enum")
        
        if old_enum and new_enum:
            removed_values = set(old_enum) - set(new_enum)
            if removed_values:
                issues.append(
                    f"Enum values removed for '{prop}': {sorted(removed_values)}"
                )
        
        # Check validation tightening
        old_min = v_from["properties"][prop].get("minimum")
        new_min = v_to["properties"][prop].get("minimum")
        if old_min is not None and new_min is not None and new_min > old_min:
            issues.append(
                f"Minimum constraint tightened for '{prop}': {old_min} -> {new_min}"
            )
        
        old_max = v_from["properties"][prop].get("maximum")
        new_max = v_to["properties"][prop].get("maximum")
        if old_max is not None and new_max is not None and new_max < old_max:
            issues.append(
                f"Maximum constraint tightened for '{prop}': {old_max} -> {new_max}"
            )
        
        old_max_len = v_from["properties"][prop].get("maxLength")
        new_max_len = v_to["properties"][prop].get("maxLength")
        if (
            old_max_len is not None
            and new_max_len is not None
            and new_max_len < old_max_len
        ):
            issues.append(
                f"maxLength constraint tightened for '{prop}': {old_max_len} -> {new_max_len}"
            )
    
    return (len(issues) == 0, issues)


def get_compatibility_advice(issues: list[str]) -> str:
    """Generate human-readable advice for compatibility issues.
    
    Args:
        issues: List of compatibility issues from is_backward_compatible_change
        
    Returns:
        Formatted advice string
    """
    if not issues:
        return "✅ Changes are backward compatible (safe for minor/patch release)"
    
    advice = ["⚠️  Breaking changes detected (require major version bump):", ""]
    
    for issue in issues:
        advice.append(f"  • {issue}")
    
    advice.extend(
        [
            "",
            "Recommendations:",
            "  1. Bump to next major version (e.g., 1.x.x → 2.0.0)",
            "  2. Document migration path in CHANGELOG.md",
            "  3. Add x-compat mapping hints if fields were renamed",
            "  4. Consider deprecation period before removal",
        ]
    )
    
    return "\n".join(advice)

