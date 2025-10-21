"""Migration validation and out-of-order detection for SQLSpec.

This module provides functionality to detect and handle out-of-order migrations,
which can occur when branches with migrations merge in different orders across
staging and production environments.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console

from sqlspec.exceptions import OutOfOrderMigrationError
from sqlspec.utils.version import parse_version

if TYPE_CHECKING:
    from sqlspec.utils.version import MigrationVersion

__all__ = ("MigrationGap", "detect_out_of_order_migrations", "format_out_of_order_warning")

console = Console()


@dataclass(frozen=True)
class MigrationGap:
    """Represents a migration that is out of order.

    An out-of-order migration occurs when a pending migration has a timestamp
    earlier than already-applied migrations, indicating it was created in a branch
    that merged after other migrations were already applied.

    Attributes:
        missing_version: The out-of-order migration version.
        applied_after: List of already-applied migrations with later timestamps.
    """

    missing_version: "MigrationVersion"
    applied_after: "list[MigrationVersion]"


def detect_out_of_order_migrations(
    pending_versions: "list[str]", applied_versions: "list[str]"
) -> "list[MigrationGap]":
    """Detect migrations created before already-applied migrations.

    Identifies pending migrations with timestamps earlier than the latest applied
    migration, which indicates they were created in branches that merged late or
    were cherry-picked across environments.

    Extension migrations are excluded from out-of-order detection as they maintain
    independent sequences within their own namespaces.

    Args:
        pending_versions: List of migration versions not yet applied.
        applied_versions: List of migration versions already applied.

    Returns:
        List of migration gaps representing out-of-order migrations.
        Empty list if no out-of-order migrations detected.

    Example:
        Applied: [20251011120000, 20251012140000]
        Pending: [20251011130000, 20251013090000]
        Result: Gap for 20251011130000 (created between applied migrations)

        Applied: [ext_litestar_0001, 0001, 0002]
        Pending: [ext_adk_0001]
        Result: [] (extensions excluded from out-of-order detection)
    """
    if not applied_versions or not pending_versions:
        return []

    gaps: list[MigrationGap] = []

    parsed_applied = [parse_version(v) for v in applied_versions]
    parsed_pending = [parse_version(v) for v in pending_versions]

    core_applied = [v for v in parsed_applied if v.extension is None]
    core_pending = [v for v in parsed_pending if v.extension is None]

    if not core_applied or not core_pending:
        return []

    latest_applied = max(core_applied)

    for pending in core_pending:
        if pending < latest_applied:
            applied_after = [a for a in core_applied if a > pending]
            if applied_after:
                gaps.append(MigrationGap(missing_version=pending, applied_after=applied_after))

    return gaps


def format_out_of_order_warning(gaps: "list[MigrationGap]") -> str:
    """Create user-friendly warning message for out-of-order migrations.

    Formats migration gaps into a clear warning message explaining which migrations
    are out of order and what migrations were already applied after them.

    Args:
        gaps: List of migration gaps to format.

    Returns:
        Formatted warning message string.

    Example:
        >>> gaps = [MigrationGap(version1, [version2, version3])]
        >>> print(format_out_of_order_warning(gaps))
        Out-of-order migrations detected:

        - 20251011130000 created before:
          - 20251012140000
          - 20251013090000
    """
    if not gaps:
        return ""

    lines = ["Out-of-order migrations detected:", ""]

    for gap in gaps:
        lines.append(f"- {gap.missing_version.raw} created before:")
        lines.extend(f"  - {applied.raw}" for applied in gap.applied_after)
        lines.append("")

    lines.extend(
        (
            "These migrations will be applied but may cause issues if they",
            "depend on schema changes from later migrations.",
            "",
            "To prevent this in the future, ensure migrations are merged in",
            "chronological order or use strict_ordering mode in migration_config.",
        )
    )

    return "\n".join(lines)


def validate_migration_order(
    pending_versions: "list[str]", applied_versions: "list[str]", strict_ordering: bool = False
) -> None:
    """Validate migration order and raise error if out-of-order in strict mode.

    Checks for out-of-order migrations and either warns or raises an error
    depending on the strict_ordering configuration.

    Args:
        pending_versions: List of migration versions not yet applied.
        applied_versions: List of migration versions already applied.
        strict_ordering: If True, raise error for out-of-order migrations.
            If False (default), log warning but allow.

    Raises:
        OutOfOrderMigrationError: If out-of-order migrations detected and
            strict_ordering is True.

    Example:
        >>> validate_migration_order(
        ...     ["20251011130000"],
        ...     ["20251012140000"],
        ...     strict_ordering=True,
        ... )
        OutOfOrderMigrationError: Out-of-order migrations detected...
    """
    gaps = detect_out_of_order_migrations(pending_versions, applied_versions)

    if not gaps:
        return

    warning_message = format_out_of_order_warning(gaps)

    if strict_ordering:
        msg = f"{warning_message}\n\nStrict ordering is enabled. Use --allow-missing to override."
        raise OutOfOrderMigrationError(msg)

    console.print("[yellow]Out-of-order migrations detected[/]")
    console.print(f"[yellow]{warning_message}[/]")
