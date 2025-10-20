"""
File reader utilities for JSON file operations.

This module provides utility functions for finding and reading JSON files
from the filesystem with proper error handling.
"""

import glob
import json
import os

def get_json_file_paths(base_path, pattern="*.json"):
    """
    Find JSON files in a directory using glob patterns.

    Parameters
    ----------
    base_path : str
        The base directory path to search for JSON files.
    pattern : str, optional
        The glob pattern to match files, by default "*.json".

    Returns
    -------
    list of str
        A list of absolute file paths to JSON files found in the directory.

    Examples
    --------
    >>> json_files = get_json_file_paths('/path/to/data')
    >>> print(json_files)
    ['/path/to/data/file1.json', '/path/to/data/file2.json']

    >>> custom_files = get_json_file_paths('/path/to/data', 'config*.json')
    >>> print(custom_files)
    ['/path/to/data/config_dev.json', '/path/to/data/config_prod.json']
    """
    json_files = glob.glob(os.path.join(base_path, pattern))
    return json_files

def read_json_file(file_path, encoding="utf-8"):
    """
    Read and parse a JSON file with error handling.

    Parameters
    ----------
    file_path : str
        The absolute path to the JSON file to read.
    encoding : str, optional
        The file encoding to use when reading, by default "utf-8".

    Returns
    -------
    dict or list
        The parsed JSON data structure.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    json.JSONDecodeError
        If the file contents are not valid JSON.

    Examples
    --------
    >>> data = read_json_file('/path/to/data.json')
    >>> print(type(data))
    <class 'dict'>

    >>> data = read_json_file('/path/to/array.json')
    >>> print(type(data))
    <class 'list'>
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    with open(file_path, "r", encoding=encoding) as file:
        data = json.load(file)
    return data
