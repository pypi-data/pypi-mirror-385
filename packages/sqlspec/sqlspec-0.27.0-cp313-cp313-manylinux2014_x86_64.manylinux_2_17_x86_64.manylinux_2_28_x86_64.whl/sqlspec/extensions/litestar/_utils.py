from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from litestar.types import Scope

__all__ = ("delete_sqlspec_scope_state", "get_sqlspec_scope_state", "set_sqlspec_scope_state")

_SCOPE_NAMESPACE = "_sqlspec"


def get_sqlspec_scope_state(scope: "Scope", key: str, default: Any = None, pop: bool = False) -> Any:
    """Get an internal value from connection scope state.

    Note:
        If called with a default value, this method behaves like `dict.setdefault()`, both setting the key in the
        namespace to the default value, and returning it.

        If called without a default value, the method behaves like `dict.get()`, returning ``None`` if the key does not
        exist.

    Args:
        scope: The connection scope.
        key: Key to get from internal namespace in scope state.
        default: Default value to return.
        pop: Boolean flag dictating whether the value should be deleted from the state.

    Returns:
        Value mapped to ``key`` in internal connection scope namespace.
    """
    namespace = scope.setdefault(_SCOPE_NAMESPACE, {})  # type: ignore[misc]
    return namespace.pop(key, default) if pop else namespace.get(key, default)  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]


def set_sqlspec_scope_state(scope: "Scope", key: str, value: Any) -> None:
    """Set an internal value in connection scope state.

    Args:
        scope: The connection scope.
        key: Key to set under internal namespace in scope state.
        value: Value for key.
    """
    scope.setdefault(_SCOPE_NAMESPACE, {})[key] = value  # type: ignore[misc]


def delete_sqlspec_scope_state(scope: "Scope", key: str) -> None:
    """Remove an internal value from connection scope state.

    Args:
        scope: The connection scope.
        key: Key to set under internal namespace in scope state.
    """
    del scope.setdefault(_SCOPE_NAMESPACE, {})[key]  # type: ignore[misc]
