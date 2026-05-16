def doc(docstring: str):
    """Декоратор для установки docstring."""
    def document(func):
        func.__doc__ = docstring
        return func
    return document