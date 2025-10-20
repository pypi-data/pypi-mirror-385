"""Contains pure functions used by higher-level constructs throughout the module."""

from collections.abc import Mapping, Sequence


def get_in(m: Mapping, key_seq: Sequence, default=None, /):
    """Returns the value for key_seq if each key is in the nested dictionary."""
    def _get_in(m, key_seq, default=None, /):
        try:
            first_key = key_seq[0]
            rest = key_seq[1:]
        except IndexError:
            # No more keys. We've arrived at the final value.
            return m
        except TypeError as ex:
            raise TypeError(f"Second argument 'key_seq' must be a sequence: {ex}")

        try:
            next_m = m.get(first_key, {})
        except AttributeError:
            # M isn't a dict
            return default

        try:
            if first_key not in m:
                # Key was not found in m. Fall back to default.
                return default
        except TypeError:
            # M is not iterable. Should not happen; fall back to default anyway.
            return default

        return _get_in(next_m, rest, default)

    # Check for valid types in top-level args before proceeding
    try:
        get = getattr(m, "get")
        if not callable(get):
            raise AttributeError("'get' attribute is not callable.")
    except AttributeError as ex:
        raise TypeError(f"First argument 'm' must be a mapping: {ex}")

    return _get_in(m, key_seq, default)
