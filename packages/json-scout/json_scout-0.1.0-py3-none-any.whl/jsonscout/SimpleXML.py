"""
Simple XML to dictionary converter.

This module provides a utility class for parsing XML strings and converting
them to nested dictionary structures for easier JSON-like manipulation.
"""

import xml.etree.ElementTree as ET

class SimpleXML:
    """
    A utility class for converting XML strings to nested dictionary structures.

    This class provides simple XML parsing capabilities, converting XML
    elements to nested dictionaries and analyzing tag usage patterns.

    Parameters
    ----------
    xml_string : str
        The XML string to parse and convert.

    Attributes
    ----------
    xml_string : str
        The original XML string.
    root : xml.etree.ElementTree.Element
        The parsed XML root element.

    Raises
    ------
    xml.etree.ElementTree.ParseError
        If the XML string is malformed or cannot be parsed.

    Examples
    --------
    >>> xml_data = '<users><user><name>Alice</name><age>30</age></user></users>'
    >>> parser = SimpleXML(xml_data)
    >>> result = parser.to_dict()
    >>> print(result)
    {'user': {'name': 'Alice', 'age': '30'}}
    """
    def __init__(self, xml_string):
        self.xml_string = xml_string
        self.root = ET.fromstring(self.xml_string)

    def to_dict(self):
        """
        Convert the XML structure to a nested dictionary.

        Returns
        -------
        dict
            A nested dictionary representation of the XML structure.
            Text content becomes string values, and nested elements become
            nested dictionaries.

        Examples
        --------
        >>> xml_data = '<person><name>John</name><age>25</age></person>'
        >>> parser = SimpleXML(xml_data)
        >>> result = parser.to_dict()
        >>> print(result)
        {'name': 'John', 'age': '25'}
        """
        return self._element_to_dict(self.root)

    def _element_to_dict(self, element):
        """
        Recursively convert an XML element to a dictionary.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element or None
            The XML element to convert.

        Returns
        -------
        dict or str or None
            A dictionary for elements with children, a string for text content,
            or None for empty elements.
        """
        if element is None:
            return None

        result = {}
        for child in element:
            result[child.tag] = self._element_to_dict(child)

        if not result:
            return element.text

        return result
    
    def analyze_tag_usagee(self):
        """
        Analyze the frequency of XML tags in the document.

        Returns
        -------
        dict
            A dictionary mapping tag names to their occurrence counts.

        Examples
        --------
        >>> xml_data = '<root><item>1</item><item>2</item><name>test</name></root>'
        >>> parser = SimpleXML(xml_data)
        >>> counts = parser.analyze_tag_usagee()
        >>> print(counts)
        {'root': 1, 'item': 2, 'name': 1}

        Notes
        -----
        The method name contains a typo ('usagee' instead of 'usage') but is
        preserved for backward compatibility.
        """
        tag_counts = {}
        self._count_tags(self.root, tag_counts)
        return tag_counts
    
    def _count_tags(self, element, tag_counts):
        """
        Recursively count occurrences of each XML tag.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            The XML element to process.
        tag_counts : dict
            Dictionary to store tag counts (modified in place).
        """
        if element.tag in tag_counts:
            tag_counts[element.tag] += 1
        else:
            tag_counts[element.tag] = 1
        
        for child in element:
            self._count_tags(child, tag_counts)
