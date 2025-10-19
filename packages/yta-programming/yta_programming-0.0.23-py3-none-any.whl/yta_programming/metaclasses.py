"""
Module to include classes that must be
inherited as metaclasses like this example
below:

`class Colors(metaclass = _GetAttrReturnsNoneMetaClass):`
"""
from abc import ABCMeta


class _GetAttrReturnsNoneMetaClass(type):
    """
    Meta class to be used when we don't want
    to receive an exception if accessing to a
    non-existing attribute but getting None
    instead.

    Useful for some classes we will use as
    static classes, like Colors, that is just
    a holder of color values built dynamically
    so if one of the values doesn't exist, we
    just get None as it is not defined.
    """

    def __getattr__(
        self,
        name: str
    ):
        """
        Accessing to any property that doesn't exist
        will return None instead of raising an 
        Exception.
        """
        return None
    
# TODO: I think this should be the option to use and
# deprecate the SingletonWrapper if confirmed that
# this metaclass is better.
class SingletonMeta(type):
    """
    Singleton meta class to be used by the classes you
    want to be singleton. Here you have an example with
    inheritance:

    ```
    class A(metaclass = SingletonMeta):
        pass

    class B(A):
        pass
    ```

    Instantiating any of these 2 instances, A() or B(),
    will return you the same instance of that class,
    which means that B will be also singleton.
    """
    _instances = {}
    """
    The list of instances of the different classes.
    """

    def __call__(
        cls,
        *args,
        **kwargs
    ):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            
        return cls._instances[cls]
    
class SingletonReinitiableMeta(type):
    """
    Singleton meta class to be used by the classes you
    want to be singleton, but every time the class is
    instantiated the `__reinit__` method is called.
    Please, make sure the `__reinit__` method is set
    or this class will behave like `SingletonMeta`.
    
    Here you have an example with
    inheritance:

    ```
    class A(metaclass = SingletonMeta):
        pass

    class B(A):
        pass
    ```

    Instantiating any of these 2 instances, A() or B(),
    will return you the same instance of that class,
    which means that B will be also singleton.
    """
    _instances = {}
    """
    The list of instances of the different classes.
    """

    REINIT_METHOD_NAME = '__reinit__'
    """
    The name of the method that reinitializes the 
    instance.
    """

    def __call__(
        cls,
        *args,
        **kwargs
    ):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            instance = cls._instances[cls]
            # Reset the instance calling the `__reinit__`
            reinit_method = getattr(instance, cls.REINIT_METHOD_NAME, None)
            if callable(reinit_method):
                reinit_method(*args, **kwargs)
            
        return cls._instances[cls]

    
class SingletonABCMeta(SingletonMeta, ABCMeta):
    """
    Hybrid metaclass that includes:
    - Singleton pattern (by implementing the
    SingletonMeta metaclass)
    - The ability to define abstract methods as ABC
    (by implementing the ABCMeta metaclass).

    Use this metaclass to be able to create an 
    abstract class that you will force the children
    classes to be singleton.
    """
    pass

class SingletonReinitiableABCMeta(SingletonReinitiableMeta, ABCMeta):
    """
    Hybrid metaclass that includes:
    - Singleton pattern (by implementing the
    SingletonReinitiableMeta metaclass)
    - The ability to reset values of the instance
    or do whatever we need in a specific method
    called `__reinit__` each time the singleton
    instance is tried to be reinstantiated.
    - The ability to define abstract methods as ABC
    (by implementing the ABCMeta metaclass).

    Use this metaclass to be able to create an 
    abstract class that you will force the children
    classes to be singleton.
    """
    pass

# TODO: Maybe we can make this `__reinit__` behaviour
# default and use it in the normal SingletonMeta class
