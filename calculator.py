def add(a, b):
    """Adds two numbers together.

    Args:
        a: An integer or float.
        b: An integer or float.

    Returns:
        The sum of a and b.
    """
    return a + b

def subtract(a, b):
    """Subtracts two numbers.

    Args:
        a: An integer or float.
        b: An integer or float.

    Returns:
        The difference between a and b.
    """
    return a - b

def multiply(a, b):
    """Multiplies two numbers.

    Args:
        a: An integer or float.
        b: An integer or float.

    Returns:
        The product of a and b.
    """
    return a * b

def divide(a, b):
    """Divides two numbers.

    Args:
        a: An integer or float.
        b: An integer or float.

    Returns:
        The result of dividing a by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
