
class lazy_property(object):
    """ Property, that saves it's state after first access.
        All next accesses will retrieve cached value.
    """

    def __init__(self, func):
        self.__func = func
        self.__name = func.__name__

    def __get__(self, obj, obj_type):
        # Class access
        if obj is None:
            return None
        value = self.__func(obj)
        # By setting value directly to __dict__ all next accesses will be from
        # there. That's how __getattribute__ works.
        obj.__dict__[self.__name] = value
        return value
