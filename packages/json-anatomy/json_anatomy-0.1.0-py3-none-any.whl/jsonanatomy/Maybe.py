
"""
Safe access wrapper for JSON data structures.

This module provides the Maybe class, which implements a monadic-style
pattern for safely accessing nested JSON data without raising exceptions
when keys or indices don't exist.
"""

class Maybe:
    """
    A wrapper for safe optional traversal over JSON data structures.

    The Maybe class provides safe access to fields and indices without raising
    exceptions when accessing non-existent keys or out-of-bounds indices.
    This follows a monadic pattern where operations can be chained safely.

    Parameters
    ----------
    json_object : any
        The JSON object to wrap. Can be a dict, list, or any other type.

    Attributes
    ----------
    data : any
        The wrapped JSON object that may or may not exist.

    Examples
    --------
    >>> data = {'name': 'Alice', 'age': 30}
    >>> maybe = Maybe(data)
    >>> name = maybe.field('name').value()  # 'Alice'
    >>> missing = maybe.field('missing').value()  # None

    >>> data = [10, 20, 30]
    >>> maybe = Maybe(data)
    >>> first = maybe.index(0).value()  # 10
    >>> out_of_bounds = maybe.index(5).value()  # None
    """
    def __init__(self, json_object):
        self.data = json_object

    def __repr__(self):
        """
        Return a string representation of the Maybe object.

        Returns
        -------
        str
            A formatted string showing the type of the wrapped object.
        """
        return f"Maybe({type(self.data)})"
    
    def __getitem__(self, key):
        """
        Safely access a field or index using bracket notation.

        Parameters
        ----------
        key : str or int
            The key (for dict) or index (for list) to access.

        Returns
        -------
        Maybe
            A new Maybe instance wrapping the accessed value or None if not found.

        Examples
        --------
        >>> maybe = Maybe({'name': 'Alice', 'age': 30})
        >>> name = maybe['name'].value()  # 'Alice'
        >>> age = maybe['age'].value()    # 30
        >>> missing = maybe['missing'].value()  # None

        >>> maybe_list = Maybe([10, 20, 30])
        >>> first = maybe_list[0].value()  # 10
        >>> out_of_bounds = maybe_list[5].value()  # None
        """
        if self.data is not None:
            if type(self.data) is dict and key in self.data:
                return Maybe(self.data[key])
            if type(self.data) is list and isinstance(key, int) and 0 <= key < len(self.data):
                return Maybe(self.data[key])
        return Maybe(None)
        
    def field(self, field):
        """
        Safely access a field in a JSON object (dict).

        Parameters
        ----------
        field : str
            The field name to access in the dictionary.

        Returns
        -------
        Maybe
            A new Maybe instance wrapping the field value or None if not present.

        Examples
        --------
        >>> maybe = Maybe({'name': 'Alice'})
        >>> name = maybe.field('name').value()  # 'Alice'
        >>> age = maybe.field('age').value()    # None
        """
        if self.data is not None and type(self.data) is dict and field in self.data:
            return Maybe(self.data[field])
        return Maybe(None)
    
    def index(self, index):
        """
        Safely access an index in a JSON array (list).

        Parameters
        ----------
        index : int
            The zero-based index to access in the list.

        Returns
        -------
        Maybe
            A new Maybe instance wrapping the item value or None if not present.

        Examples
        --------
        >>> maybe = Maybe([1, 2, 3])
        >>> first = maybe.index(0).value()  # 1
        >>> fourth = maybe.index(3).value()  # None
        """
        if self.data is not None and type(self.data) is list and index < len(self.data):
            return Maybe(self.data[index])
        return Maybe(None)

    def array(self, func=lambda k,o: o, filter=lambda k,o: True, as_type=list):
        """
        Safely convert a JSON array or object to a list of transformed items.

        Applies a transformation function to each item in an array or each 
        key-value pair in an object. Items can be filtered before transformation.

        Parameters
        ----------
        func : callable, optional
            Function to transform each item. For arrays: func(index, value).
            For objects: func(key, value). Default returns the value unchanged.
        filter : callable, optional
            Function to filter items before transformation. Same signature as func.
            Default accepts all items.
        as_type : type, optional
            The type constructor for the result container, by default list.

        Returns
        -------
        list or as_type
            A container of transformed items, or empty container if not applicable.

        Examples
        --------
        >>> maybe_list = Maybe([1, 2, 3])
        >>> doubled = maybe_list.array(lambda k,v: v*2)  # [2, 4, 6]
        >>> filtered = maybe_list.array(lambda k,v: v*2, lambda k,v: v > 2)  # [6]

        >>> maybe_dict = Maybe({'a': 1, 'b': 2, 'c': 3})
        >>> items = maybe_dict.array(lambda k,v: (k, v*2))  # [('a', 2), ('b', 4), ('c', 6)]
        >>> filtered = maybe_dict.array(lambda k,v: (k, v*2), lambda k,v: v > 2)  # [('c', 6)]

        >>> not_array = Maybe(42).array()  # []
        """
        if self.data is not None:
            if type(self.data) is dict:
                return as_type([func(key, obj) for key,obj in self.data.items() if filter(key, obj)])
            elif type(self.data) is list:
                return as_type([func(idx, obj) for idx,obj in enumerate(self.data) if filter(idx, obj)])
        return []
    
    def filter(self, func=lambda k,o: True):
        """
        Safely filter items in a JSON array or object.

        Parameters
        ----------
        func : callable, optional
            Function to determine which items to keep. For arrays: func(index, value).
            For objects: func(key, value). Default keeps all items.

        Returns
        -------
        Maybe
            A new Maybe wrapping filtered data of the same type, or None if not applicable.

        Examples
        --------
        >>> maybe_dict = Maybe({'a': 1, 'b': 2, 'c': 3})
        >>> filtered = maybe_dict.filter(lambda k,v: v > 2).value()  # {'c': 3}

        >>> maybe_list = Maybe([1, 2, 3, 4])
        >>> filtered = maybe_list.filter(lambda i,v: v % 2 == 0).value()  # [2, 4]
        """
        if self.data is not None:
            if type(self.data) is dict:
                return Maybe({k: v for k,v in self.data.items() if func(k,v)})
            elif type(self.data) is list:
                return Maybe([obj for idx,obj in enumerate(self.data) if func(idx, obj)])
        return Maybe(None)

    def value(self):
        """
        Get the wrapped value.

        Returns
        -------
        any
            The wrapped data object, which may be None if no value exists.

        Examples
        --------
        >>> maybe = Maybe({'name': 'Alice'})
        >>> data = maybe.value()  # {'name': 'Alice'}
        >>> assert data == maybe.data  # Both access methods return same object

        >>> empty = Maybe(None)
        >>> data = empty.value()  # None
        """
        return self.data
    
    