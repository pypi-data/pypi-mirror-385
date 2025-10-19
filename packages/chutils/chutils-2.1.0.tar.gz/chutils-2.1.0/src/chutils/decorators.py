import functools


def print_return_value(func):
    """
    Декоратор, который печатает возвращаемое значение
    и сохраняет метаданные оригинальной функции.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Функция '{func.__name__}' вернула: {result}")
        return result

    return wrapper