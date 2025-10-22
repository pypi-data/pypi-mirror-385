import functools
import typing
import warnings

__all__ = ["deprecated"]


def deprecated(
    *, new_method: str | typing.Callable[[typing.Any], typing.Any] | None = None
) -> typing.Callable[[typing.Any], typing.Any]:
    def inner_fn_wrap(func: typing.Callable[[typing.Any], typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used."""

        @functools.wraps(func)
        def new_func(*args: typing.Any, **kwargs: typing.Any) -> typing.Callable[[typing.Any], typing.Any]:
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter
            warning_message = f"Call to deprecated function {func.__name__}."
            if new_method is not None:
                new_method_name = new_method
                if callable(new_method):
                    new_method_name = new_method.__name__
                warning_message = f"{warning_message} Use {new_method_name} instead!"
            warnings.warn(warning_message, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)  # reset filter
            return func(*args, **kwargs)

        return new_func

    return inner_fn_wrap
