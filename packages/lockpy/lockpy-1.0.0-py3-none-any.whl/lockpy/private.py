import inspect
import functools

def private(method):
    """
    A decorator to make methods private.
    Works for instance methods, classmethods, and staticmethods.
    Raises RuntimeError if called from outside the class.
    """
    is_static = isinstance(method, staticmethod)
    is_class = isinstance(method, classmethod)
    func = method.__func__ if (is_static or is_class) else method

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_static:
            cls_name = wrapper.__qualname__.split('.')[0]
        elif is_class:
            cls_name = args[0].__name__
        else:
            cls_name = args[0].__class__.__name__

        stack = inspect.stack()
        caller_frame = stack[1]
        caller_locals = caller_frame.frame.f_locals
        caller_self = caller_locals.get('self', None)
        caller_cls = caller_locals.get('cls', None)

        same_class_call = (
            (caller_self and caller_self.__class__.__name__ == cls_name) or
            (caller_cls and caller_cls.__name__ == cls_name)
        )

        if not same_class_call:
            raise RuntimeError(
                f"❌ Illegal access to private method '{func.__name__}' of class '{cls_name}'."
            )

        return func(*args, **kwargs)

    if is_static:
        return staticmethod(wrapper)
    if is_class:
        return classmethod(wrapper)
    return wrapper
