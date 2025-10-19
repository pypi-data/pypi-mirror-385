"""Singleton pattern implementation using metaclasses.

This module provides a robust implementation of the Singleton design pattern using
Python metaclasses. It ensures that classes inheriting from the Singleton base class
can have only one instance throughout the application lifecycle, which is useful
for shared resources like loggers, configuration managers, and database connections.

The implementation uses a metaclass approach to control instance creation at the
class level, providing thread-safe singleton behavior without requiring explicit
synchronization in the client code.

Example:
    Creating singleton classes:

    >>> class DatabaseManager(Singleton):
    ...     def __init__(self):
    ...         self.connection = "db_connection"
    >>>
    >>> db1 = DatabaseManager()
    >>> db2 = DatabaseManager()
    >>> db1 is db2
    True

Attributes:
    None: This module contains only class definitions.
"""


class SingletonMeta(type):
    """Metaclass that implements the Singleton pattern.

    This metaclass ensures that only one instance of a class can exist.
    When a class uses this metaclass, subsequent instantiation attempts
    will return the same instance.

    Attributes:
        _instances (dict): Dictionary storing singleton instances by class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Control instance creation to ensure singleton behavior.

        Args:
            *args: Variable length argument list for class instantiation.
            **kwargs: Arbitrary keyword arguments for class instantiation.

        Returns:
            object: The singleton instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Base class for implementing singleton pattern.

    Classes that inherit from this base class will automatically
    follow the singleton pattern, ensuring only one instance exists.

    Example:
        >>> class MyClass(Singleton):
        ...     pass
        >>> obj1 = MyClass()
        >>> obj2 = MyClass()
        >>> obj1 is obj2
        True
    """

    pass
