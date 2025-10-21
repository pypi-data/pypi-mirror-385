"""Decorators for warning messages."""

import inspect
import warnings
from collections.abc import Callable
from typing import Any

import wrapt

_routine_stacklevel = 2

__all__ = ["deprecated", "deprecated_argument", "experimental"]


def _get_msg(  # noqa: PLR0913
    decorator_name: str,
    wrapped: Callable[..., Any],
    reason: str | None = None,
    since: str | None = None,
    removed: str | None = None,
    additional_msg: str | None = None,
) -> str:
    """Add messages to the decorators."""
    kind = "Class" if inspect.isclass(wrapped) else "Function"
    name = wrapped.__name__
    since = f"since version {since}" if since else ""
    reason = f": {reason}. " if reason else ". "
    removed = f"Will be removed from version {removed}. " if removed else ""
    additional_msg = f"{additional_msg}." or ""

    return f"{kind} '{name}' deprecated {since}{reason}{removed}{additional_msg}"


def _warning_decorator(decorator_name: str) -> Any:
    """Create decorators to emit warnings.

    This is a decorator factory used to create actual decorators such as 'experimental' and
    'deprecated'.
    The 'decorator_name' parameter specifies the name of the decorator being created.
    """
    # REFERENCE: adapted from 'deprecated' of deprecated library
    # REFERENCE: see also how they handle the deprecated decorator in sklearn

    def actual_decorator(*args: Any, **kwargs: Any) -> Any:
        category: type[Warning] = kwargs.get("category", Warning)
        if len(args) == 1 and callable(args[0]):

            @wrapt.decorator
            def wrapper_without_args(
                wrapped: Callable[..., Any],
                instance: Any | None,
                args_: tuple[Any, ...],
                kwargs_: dict[str, Any],
            ) -> Any:
                msg = _get_msg(decorator_name, wrapped, None, None)
                warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped(*args_, **kwargs_)

            return wrapper_without_args(args[0])

        @wrapt.decorator
        def wrapper_with_args(
            wrapped: Callable[..., Any],
            instance: Any | None,
            args_: tuple[Any, ...],
            kwargs_: dict[str, Any],
        ) -> Any:
            msg = _get_msg(
                decorator_name,
                wrapped,
                kwargs.get("reason"),
                kwargs.get("since"),
                kwargs.get("removed"),
                kwargs.get("additional_msg"),
            )
            if action := kwargs.get("action"):
                with warnings.catch_warnings():
                    warnings.simplefilter(action)
                    warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
            else:
                warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
            return wrapped(*args_, **kwargs_)

        return wrapper_with_args

    return actual_decorator


def experimental(*args: Any, **kwargs: Any) -> Any:
    """Mark functions or classes as experimental.

    Parameters
    ----------
    reason : str, optional
        The reason why the function or class is marked as experimental.
    since : str, optional
        The version since when the function or class is marked as experimental.
    additional_msg : str, optional
        Additional message to be included in the warning, e.g., "Use with caution".
    category : Type[Warning], optional
        The category of the warning to be issued. By default, `FutureWarning`.
    action : {None, "error", "ignore", "always", "default", "module", "once"}
        The action to be taken when the warning is issued. If `None`, uses the global
        warning filter.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    ```python
    @experimental
    def function(a, b):
        return [a, b]


    @experimental(
        reason="use another function", since="1.2.0", category=FutureWarning, action="error"
    )
    def function(a, b):
        return [a, b]
    ```
    """
    kwargs["category"] = kwargs.get("category", FutureWarning)
    return _warning_decorator("experimental")(*args, **kwargs)


def deprecated(*args: Any, **kwargs: Any) -> Any:
    """Mark functions or classes as deprecated.

    Parameters
    ----------
    reason : str, optional
        The reason why the function or class is marked as deprecated.
    since : str, optional
        The version since when the function or class is marked as deprecated.
    removed : str, optional
        The version in which will be removed.
    additional_msg : str, optional
        Additional message to be included in the warning, e.g., "Use 'other_arg' instead".
    category : Type[Warning], optional
        The category of the warning to be issued. By default, `DeprecationWarning`.
    action : {None, "error", "ignore", "always", "default", "module", "once"}
        The action to be taken when the warning is issued. If `None`, uses the global
        warning filter.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    ```python
    @deprecated
    def function(a, b):
        return [a, b]

    @deprecated(reason="changed name",
        since="1.2.0",
        what_do="Use 'new' instead"
        category=DeprecationWarning,
        action="error")
    def function(a, b):
        return [a, b]
    ```
    """
    kwargs["category"] = kwargs.get("category", DeprecationWarning)
    return _warning_decorator("deprecated")(*args, **kwargs)


def deprecated_argument(
    arguments: str | list[str],
    since: str = "",
    additional_msg: str = "",
    category: type[Warning] = DeprecationWarning,
) -> Any:
    """Warn of deprecated arguments.

    Used by decorating the function or method in which the argument(s) are being deprecated.

    Parameters
    ----------
    arguments : str or list[str]
        The name(s) of the deprecated argument(s). Can be a single string or a list of strings.
    since : str, optional
        The version in which the argument(s) will be removed.
    additional_msg : str, optional
        Additional message to be included in the warning, e.g., "Use 'other_arg' instead".
    category : Warning, optional
        The category of the warning. Default is DeprecationWarning.

    Returns
    -------
    Callable[..., Any]
        The decorated function or class.

    Examples
    --------
    Single deprecated argument:
    ```python
    @deprecated_argument(arguments="my_arg1", since="2.0", additional_msg="Use 'other_arg' instead")
    def my_func(my_arg1=None, my_arg2=None, other_arg=None):
        pass
    ```

    Multiple deprecated arguments:
    ```python
    @deprecated_argument(
        arguments=["my_arg1", "my_arg2"], since="2.0", additional_msg="Use 'other_arg' instead"
    )
    def my_func(my_arg1=None, my_arg2=None, other_arg=None):
        pass
    ```

    You can also specify different messages for different sets of arguments:
    ```python
    @deprecated_argument(
        arguments=["old_arg1", "old_arg2"], since="2.0", additional_msg="Use 'new_arg' instead"
    )
    @deprecated_argument(
        arguments="legacy_arg", since="3.0", additional_msg="This feature will be removed"
    )
    def my_func(old_arg1=None, old_arg2=None, legacy_arg=None, new_arg=None):
        pass
    ```
    """
    arg_list = [arguments] if isinstance(arguments, str) else arguments

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: Any | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        # Check for any deprecated arguments in kwargs
        found_deprecated = [arg for arg in arg_list if arg in kwargs]

        if found_deprecated:
            # Build the method name for the warning
            module = inspect.getmodule(wrapped)
            if module is not None:
                module_name = module.__name__
                if module_name == "__main__":
                    module_name = ""
                else:
                    module_name += "."
            else:
                module_name = ""

            method = module_name + wrapped.__name__
            if instance is not None:
                method = instance.__class__.__name__ + "." + method

            # Build warning message
            version_str = f" in version {since}" if since else ""
            add_msg_str = f" {additional_msg}." if additional_msg else ""

            if len(found_deprecated) == 1:
                arg_str = f"Argument '{found_deprecated[0]}'"
                number = "is"
            else:
                arg_str = f"Arguments {found_deprecated}"
                number = "are"

            msg = f"{arg_str} from '{method}' {number} being deprecated{version_str}.{add_msg_str}"

            warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)

        return wrapped(*args, **kwargs)

    return wrapper
