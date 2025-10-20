"""
Lightweight structural explorer for JSON objects.

This module provides the Explore class for basic inspection and navigation
of nested JSON data structures (dictionaries and lists).
"""

class Explore:
    """
    A lightweight explorer for inspecting JSON object structures.

    This class provides methods to examine the structure of JSON data,
    navigate through nested objects, and analyze the distribution of
    child properties across collections.

    Parameters
    ----------
    json_object : dict, list, or any
        The JSON object to explore. Can be a dictionary, list, or any other type.

    Attributes
    ----------
    data : dict, list, or any
        The original JSON object being explored.
    child_keys : list
        A list of keys (for dicts) or indices (for lists) of direct children.

    Examples
    --------
    >>> data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
    >>> explorer = Explore(data)
    >>> print(explorer.get_child_keys())
    ['users']

    >>> users_explorer = explorer.explore_child('users')
    >>> print(users_explorer.get_child_keys())
    [0, 1]
    """
    def __init__(self, json_object):
        self.data = json_object
        self.child_keys = []
        if type(self.data) is dict:
            self.child_keys = list(self.data.keys())
        if type(self.data) is list:
            self.child_keys = [idx for idx in range(len(self.data))]

    def __repr__(self):
        """
        Return a string representation of the Explore object.

        Returns
        -------
        str
            A formatted string showing the type and size of the explored object.
        """
        return f"Explore({type(self.data)}[size={len(self.child_keys)}])"
    
    def value(self):
        """
        Get the underlying data object.

        Returns
        -------
        any
            The wrapped data object being explored.

        Examples
        --------
        >>> data = {'name': 'Alice', 'age': 30}
        >>> explorer = Explore(data)
        >>> original = explorer.value()  # Returns: {'name': 'Alice', 'age': 30}
        >>> assert original is data  # Same object reference
        """
        return self.data

    def keys(self):
        """
        Get the keys or indices of direct children.

        Returns
        -------
        list
            For dictionaries: list of string keys.
            For lists: list of integer indices.
            For other types: empty list.

        Examples
        --------
        >>> data = {'a': 1, 'b': 2}
        >>> explorer = Explore(data)
        >>> print(explorer.keys())
        ['a', 'b']

        >>> data = [10, 20, 30]
        >>> explorer = Explore(data)
        >>> print(explorer.keys())
        [0, 1, 2]
        """
        return self.child_keys
    
    def child(self, child_key):
        """
        Create a new Explore instance for a specific child.

        Parameters
        ----------
        child_key : str or int
            The key (for dict) or index (for list) of the child to explore.

        Returns
        -------
        Explore
            A new Explore instance wrapping the child object, or None if not found.

        Examples
        --------
        >>> data = {'users': [{'name': 'Alice'}]}
        >>> explorer = Explore(data)
        >>> child = explorer.child('users')
        >>> print(type(child.data))
        <class 'list'>
        """
        if child_key in self.child_keys:
            return Explore(self.data[child_key])
        return Explore(None)
    
    def field_counts(self, verbose=False):
        """
        Analyze the distribution of field names across all children in a collection.

        This method examines each child of the current object and counts
        how frequently each field name appears across all children.
        Useful for understanding the schema of collections with varying structures.

        Parameters
        ----------
        verbose : bool, optional
            If True, print detailed exploration progress, by default False.

        Returns
        -------
        dict
            A dictionary mapping field names to their occurrence counts.

        Examples
        --------
        >>> data = {
        ...     'users': [
        ...         {'name': 'Alice', 'age': 30},
        ...         {'name': 'Bob', 'email': 'bob@example.com'},
        ...         {'name': 'Charlie', 'age': 25}
        ...     ]
        ... }
        >>> explorer = Explore(data['users'])
        >>> counts = explorer.field_counts()
        >>> print(counts)
        {'name': 3, 'age': 2, 'email': 1}

        Notes
        -----
        This method is particularly useful for analyzing collections where
        objects may have varying schemas or optional properties.
        """
        if verbose:
            print(f"Exploring grandchildren of type: {type(self.child_keys)} (size={len(self.data)}) with keys: {self.keys()}")
        counts = {}
        for child_key in self.child_keys:
            if verbose:
                print(f"Exploring child key: {child_key}")
            expChild = self.child(child_key)
            if verbose:
                print(f"  Child type: {type(expChild.data)} with keys: {expChild.keys()}")
            for grandChildKey in expChild.keys():
                if verbose:
                    print(f"    Found grandchild key: {grandChildKey}")
                if grandChildKey in counts:
                    counts[grandChildKey] += 1
                else:
                    counts[grandChildKey] = 1
            
        return counts