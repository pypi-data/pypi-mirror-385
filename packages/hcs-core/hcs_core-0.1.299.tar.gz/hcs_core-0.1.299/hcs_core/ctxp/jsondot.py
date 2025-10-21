"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
jsondot is utility to make json/dict object accessible in the "." way.

##########
#Example 1: load, update, and save JSON file
##########

data = jsondot.load('path/to/my.json')
print(data.hello.message)
data.hello.message = 'Hello, mortal.'
jsondot.save(data, 'path/to/my.json')


##########
#Example 2: decorate an existing python dict
##########

my_dict = jsondot.dotify(my_dict)
print(my_dict.key1.key2)
"""


import copy
import json
import os.path
import random
import time
from typing import Any, Dict, Optional, Union


class dotdict(dict):
    """dot.notation access to dictionary attributes with enhanced safety.

    A dictionary subclass that provides attribute-style access to its elements
    while maintaining compatibility with regular dict operations.

    Examples:
        >>> d = dotdict({'a': 1, 'b': {'c': 2}})
        >>> d.a
        1
        >>> d.b.c
        2
        >>> d.b.c = 3
        >>> d.b.c
        3
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __lt__(self, other: Union[dict, "dotdict"]) -> bool:
        """Support proper sorting by comparing underlying dictionaries."""
        if isinstance(other, dict):
            return dict(self) < dict(other)
        return NotImplemented

    def __eq__(self, other: Union[dict, "dotdict"]) -> bool:
        """Support equality comparison with other dictionaries."""
        if isinstance(other, dict):
            return dict(self) == dict(other)
        return NotImplemented

    def __deepcopy__(self, memo: Optional[Dict] = None) -> "dotdict":
        """Support deep copying of the dictionary.

        Args:
            memo: Memoization dictionary for handling circular references

        Returns:
            A deep copy of the dotdict instance
        """
        new = {}
        for key in self.keys():
            new[key] = copy.deepcopy(self[key], memo=memo)
        return dotdict(new)

    def __repr__(self) -> str:
        """Return a string representation of the dictionary.

        Returns:
            A string showing this is a dotdict instance with its contents
        """
        return dict.__repr__(self)

    # def __getstate__(self):
    #     """Return state for serialization - just return the underlying dict"""
    #     return dict(self)

    # def __setstate__(self, state):
    #     """Restore state from serialization"""
    #     self.update(state)

    # def __reduce_ex__(self, protocol):
    #     return dict, (dict(self),)

    # def __getattribute__(self, name):
    #     """Make this look like a plain dict to introspection"""
    #     if name in ('__getstate__', '__setstate__', '__reduce__', '__reduce_ex__', '__class__'):
    #         return getattr(dict, name)
    #     return super().__getattribute__(name)


def _yaml_interoperability() -> None:
    """Set up YAML serialization support for dotdict objects.

    Registers a custom representer with PyYAML to properly serialize
    dotdict objects as regular dictionaries. This ensures dotdict
    objects can be seamlessly used with YAML operations.

    Note:
        This function is automatically called during module initialization.
    """
    try:
        import yaml

        def _represent_dict(dumper: yaml.SafeDumper, data: dotdict) -> yaml.nodes.MappingNode:
            return dumper.represent_dict(data.items())

        yaml.SafeDumper.add_representer(dotdict, _represent_dict)
    except ImportError:
        pass  # PyYAML not available, silently skip registration


def dotify(target: Any) -> Any:
    """Deeply convert an object from dict to dotdict.

    Recursively converts all nested dictionaries to dotdict instances
    while preserving other data types. Handles circular references safely.

    Args:
        target: The object to convert

    Returns:
        The converted object with all dicts replaced by dotdict instances

    Raises:
        RecursionError: If maximum recursion depth is exceeded
    """
    # Handle circular references with recursion depth check
    if getattr(dotify, "_depth", 0) > getattr(dotify, "_max_depth", 1000):
        raise RecursionError("Maximum recursion depth exceeded")

    dotify._depth = getattr(dotify, "_depth", 0) + 1
    try:
        if isinstance(target, dotdict):
            return target
        if isinstance(target, list):
            return [dotify(item) for item in target]
        if isinstance(target, dict):
            return dotdict({k: dotify(v) for k, v in target.items()})
        return target
    finally:
        dotify._depth -= 1


def undot(target: Any) -> Any:
    """Deeply convert an object from dotdict to plain dict.

    Recursively converts all nested dotdict instances to regular dictionaries
    while preserving other data types. Handles circular references safely.

    Args:
        target: The object to convert

    Returns:
        The converted object with all dotdict instances replaced by plain dicts

    Raises:
        RecursionError: If maximum recursion depth is exceeded
    """
    # Handle circular references with recursion depth check
    if getattr(undot, "_depth", 0) > getattr(undot, "_max_depth", 1000):
        raise RecursionError("Maximum recursion depth exceeded")

    undot._depth = getattr(undot, "_depth", 0) + 1
    try:
        if isinstance(target, list):
            return [undot(item) for item in target]
        if isinstance(target, dict):
            return {k: undot(v) for k, v in target.items()}
        return target
    finally:
        undot._depth -= 1


def _is_primitive(obj: Any) -> bool:
    """Check if the object is a primitive type.

    Determines if an object is a basic Python type that doesn't need
    conversion when serializing/deserializing.

    Args:
        obj: Any Python object

    Returns:
        bool: True if the object is a primitive type (str, bool, int, float, None)
    """
    return obj is None or isinstance(obj, (str, bool, int, float))


def plain(target: Any) -> Any:
    """Convert a complex object structure to plain Python types.

    Recursively converts all objects to their basic Python equivalents,
    making the structure suitable for serialization. Handles nested
    dictionaries, lists, and primitive types.

    Args:
        target: The object to convert

    Returns:
        The converted object with all complex types replaced by basic Python types

    Examples:
        >>> d = dotdict({'a': 1, 'b': {'c': 2}})
        >>> plain(d)
        {'a': 1, 'b': {'c': 2}}
    """
    if _is_primitive(target):
        return target
    if isinstance(target, list):
        return [plain(item) for item in target]
    if isinstance(target, dict):
        return {k: plain(v) for k, v in target.items()}
    return target


def parse(text: str) -> dotdict:
    """Parse a JSON string into a dotdict object.

    Args:
        text: JSON string to parse

    Returns:
        dotdict: The parsed and converted data

    Raises:
        JSONDecodeError: If the string contains invalid JSON
        TypeError: If input is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    try:
        dict_data = json.loads(text)
        return dotify(dict_data)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON: {str(e)}") from e


def _lock_with_retry(file: str, for_read: bool, max_retry: int = 6, initial_backoff: float = 0.05) -> None:
    """Attempt to lock a file with retries using exponential backoff.

    Args:
        file: File handle to lock
        for_read: If True, acquire shared lock; if False, acquire exclusive lock
        max_retry: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds

    Raises:
        Exception: If unable to acquire lock after max retries
        portalocker.LockException: If locking fails
    """
    import portalocker

    flags = portalocker.LockFlags.SHARED if for_read else portalocker.LockFlags.EXCLUSIVE

    retry = 0
    backoff_seconds = initial_backoff
    while True:
        try:
            portalocker.lock(file, flags)
            return
        except portalocker.LockException as e:
            retry += 1
            if retry > max_retry:
                raise Exception(f"Failed to acquire lock for file {file} after {max_retry} attempts") from e
            random_delay = backoff_seconds + random.uniform(0, 0.1)
            time.sleep(random_delay)
            backoff_seconds *= 2


def load(file: str, default: Any = None, lock: bool = False) -> dotdict:
    """Load and parse a JSON file into a dotdict object.

    Args:
        file: Path to the JSON file
        default: Value to return if file doesn't exist
        lock: Whether to use file locking

    Returns:
        dotdict: The loaded and converted data

    Raises:
        FileNotFoundError: If file doesn't exist and no default provided
        JSONDecodeError: If file contains invalid JSON
        IOError: If file access fails
    """
    try:
        if not os.path.exists(file):
            if default is None:
                raise FileNotFoundError(f"File not found: {file}")
            return dotify(default)

        with open(file) as json_file:
            if lock:
                _lock_with_retry(json_file, True)
            dict = json.load(json_file)
        return dotify(dict)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in file {file}: {str(e)}") from e
    except IOError as e:
        raise Exception(f"Error accessing file {file}: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Unexpected error loading file {file}: {str(e)}") from e


def save(data: dict, file: str, pretty: bool = True, lock: bool = False) -> None:
    """Save data as JSON to a file with optional pretty printing and locking.

    Args:
        data: Dictionary data to save
        file: Path to the output JSON file
        pretty: If True, format JSON with indentation
        lock: Whether to use file locking

    Raises:
        IOError: If file access fails
        TypeError: If data contains non-serializable objects
    """
    try:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as outfile:
            if lock:
                _lock_with_retry(outfile, False)
            json.dump(data, outfile, indent="\t" if pretty else None, default=vars)
    except IOError as e:
        raise Exception(f"Error writing to file {file}: {str(e)}") from e
    except TypeError as e:
        raise Exception(f"Error serializing data to JSON: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Unexpected error saving file {file}: {str(e)}") from e
