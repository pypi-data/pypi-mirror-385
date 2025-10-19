class ConfigDict(dict):
    """
    A dictionary-like object that allows attribute-style access (obj.key)
    and recursively converts nested dictionaries into ConfigDicts.
    """
    def __init__(self, *args, **kwargs):
        """
        Custom __init__ to intercept args and kwargs,
        ensuring __setitem__ is called for all items.
        """
        # Initialize as an empty dict
        super().__init__()
        
        # Handle positional argument (e.g., ConfigDict(my_dict))
        if args:
            if len(args) > 1:
                raise TypeError(f"expected at most 1 arguments, got {len(args)}")
            if isinstance(args[0], dict):
                # This loop will call our __setitem__ for each item
                for key, value in args[0].items():
                    self[key] = value 

        # Handle keyword arguments (e.g., ConfigDict(a=1, b=2))
        # This loop will also call our __setitem__
        for key, value in kwargs.items():
            self[key] = value

    def _recursive_convert(self, value):
        """
        Recursively converts values to ConfigDicts.
        Handles dicts, lists, and tuples.
        """
        if isinstance(value, dict):
            # Convert dictionaries (and prevent re-converting ConfigDicts)
            return ConfigDict(value)
        elif isinstance(value, (list, tuple)):
            # Convert items within lists or tuples
            return type(value)(self._recursive_convert(item) for item in value)
        else:
            # Return all other types as-is
            return value

    def __getattr__(self, name):
        """
        Called when obj.key is accessed.
        Retrieves the item from the dictionary.
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Called when obj.key = value is set.
        This will call __setitem__ internally.
        """
        # Prevent setting reserved names
        if name in self.__dict__:
             super().__setattr__(name, value)
        else:
            self[name] = value

    def __setitem__(self, key, value):
        """
        Called when obj['key'] = value is set.
        Recursively converts the value before setting.
        """
        converted_value = self._recursive_convert(value)
        super().__setitem__(key, converted_value)

    def __delattr__(self, name):
        """
        Called when del obj.key is used.
        """
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")