def validate_next_params(barn, add, batch, duration, expiry, calls, display):
    # Validate types and values for integers
    for name, value in [("batch", batch), ("calls", calls)]:
        if not isinstance(value, int):
            raise TypeError(f"❌ '{name}' must be an integer, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"❌ '{name}' must be a positive integer, got {value}")

    # Validate types and values for time parameters
    for name, value in [("duration", duration), ("expiry", expiry)]:
        if not isinstance(value, (int, float)):
            raise TypeError(f"❌ '{name}' must be an int or float (time), got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"❌ '{name}' must be a positive number, got {value}")

    # Optional: validate display flag
    if not isinstance(display, bool):
        raise TypeError(f"❌ 'display' must be a boolean, got {type(display).__name__}")

    # Optional: validate barn and add
    if not isinstance(barn, str):
        raise TypeError(f"❌ 'barn' must be a string, got {type(barn).__name__}")

    if not callable(add):
        raise TypeError(f"❌ 'add' must be a callable (function), got {type(add).__name__}")


def validate_find_params(barn, keys, values, display):
    if not isinstance(barn, str):
        raise ValueError("Parameter 'barn' must be a non-empty string.")

    if keys is not None and values is not None:
        raise ValueError("Parameters 'keys' and 'values' cannot be provided at the same time.")
    
    if keys is None and values is None:
        raise ValueError("Either 'keys' or 'values' must be provided.")

    if not isinstance(display, bool):
        raise ValueError("Parameter 'display' must be a boolean.")


