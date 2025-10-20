
"""
Unified convenience facade for JSON exploration.

This module provides the Xplore class, which combines the functionality
of Explore, Maybe, and SimpleXML into a single convenient interface
for exploring and navigating JSON data structures.
"""

from .Maybe import Maybe
from .Explore import Explore
from .SimpleXML import SimpleXML


class Xplore:
    """
    Unified convenience facade combining exploration tools.

    This class provides a single entry point that wires together the
    functionality of Explore (structural exploration), Maybe (safe access),
    and SimpleXML (XML parsing) into one convenient interface.

    Parameters
    ----------
    data : any
        The input data to be explored. Can be JSON data, XML string, or other data types.

    Attributes
    ----------
    data : any
        The original input data.
    explore : Explore
        An Explore instance for general data exploration.
    maybe : Maybe
        A Maybe instance for safe data access operations.
    xml : SimpleXML or None
        A SimpleXML instance if data is an XML string, None otherwise.

    Examples
    --------
    >>> data = {'users': [{'name': 'Alice', 'age': 30}]}
    >>> xplore = Xplore(data)
    >>> name = xplore['users'][0]['name'].value()
    >>> print(name)  # 'Alice'

    >>> xml_data = '<user><name>Bob</name></user>'
    >>> xplore = Xplore(xml_data)
    >>> xml_dict = xplore.xml.to_dict()
    >>> print(xml_dict)  # {'name': 'Bob'}

    Notes
    -----
    - Creates an Explore instance for general data exploration
    - Creates a Maybe instance for safe data access operations  
    - Creates a SimpleXML instance only if data is a string starting with "<"
    - The xml attribute will be None if data is not XML-formatted
    """
    def __init__(self, data):
        self.data = data
        self.explore = Explore(data)
        self.maybe = Maybe(data)
        self.xml = SimpleXML(data) if isinstance(data, str) and data.strip().startswith("<") else None

    def __repr__(self):
        """
        Return a string representation of the Xplore object.

        Returns
        -------
        str
            A formatted string showing the type and size of the explored data.
        """
        return f"Explore({type(self.data)}[size={len(self.data)}])" if hasattr(self.data, "__len__") else f"Xplore({type(self.data)})[size=N/A]"
    
    def __getitem__(self, key):
        """
        Allow direct access to Maybe functionality via indexing.

        This enables chaining of safe access operations using bracket notation.

        Parameters
        ----------
        key : str or int
            The key (for dict) or index (for list) to access.

        Returns
        -------
        Xplore
            A new Xplore instance wrapping the accessed value.

        Examples
        --------
        >>> data = {'name': 'Alice', 'details': {'age': 30}}
        >>> xplore = Xplore(data)
        >>> name = xplore['name'].value()  # 'Alice'
        >>> age = xplore['details']['age'].value()  # 30
        >>> missing = xplore['missing'].value()  # None
        """
        return Xplore(self.maybe[key].value())
    
    def keys(self):
        """
        Get the keys of the current data if it's a dictionary or list.

        Returns
        -------
        list
            For dictionaries: list of string keys.
            For lists: list of integer indices.
            For other types: empty list.

        Examples
        --------
        >>> data = {'name': 'Alice', 'age': 30}
        >>> xplore = Xplore(data)
        >>> print(xplore.keys())
        ['name', 'age']

        >>> data = [10, 20, 30]
        >>> xplore = Xplore(data)
        >>> print(xplore.keys())
        [0, 1, 2]
        """
        return self.explore.keys()
    
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
        >>> xplore = Xplore(data)
        >>> original = xplore.value()  # Returns: {'name': 'Alice', 'age': 30}
        >>> assert original is data  # Same object reference
        """
        return self.data