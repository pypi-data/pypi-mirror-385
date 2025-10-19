import copy
from typing import Any, Sequence, TypeVar

from tinytim.custom_types import DataMapping

TypeVarDataMapping = TypeVar('TypeVarDataMapping', bound='DataMapping')
TypeVarSequence = TypeVar('TypeVarSequence', bound='Sequence[Any]')


def copy_table(data: TypeVarDataMapping) -> TypeVarDataMapping:
    """
    Copy data and return the copy.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}

    Returns
    -------
    MutableMapping[str, MutableSequence]
        copy of data

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> copy_table(data)
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    return copy.deepcopy(data)


def deepcopy_table(data: TypeVarDataMapping) -> TypeVarDataMapping:
    """
    Deep copy data and return the copy.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}

    Returns
    -------
    MutableMapping[str, MutableSequence]
        copy of data

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> deepcopy_table(data)
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    constructor = type(data)
    return constructor({col: copy.deepcopy(values) for col, values in data.items()}) # type: ignore


def copy_sequence(values: TypeVarSequence) -> TypeVarSequence:
    """
    Copy list and return the copy.

    Parameters
    ----------
    values : list
        list of values

    Returns
    -------
    list
        copy of list

    Example
    -------
    >>> values = [1, 2, 3, 6, 7, 8]
    >>> values_copy = copy_list(values)
    >>> values_copy
    [1, 2, 3, 6, 7, 8]
    >>> values_copy[0] = 11
    >>> values_copy
    [11, 2, 3, 6, 7, 8]
    >>> values
    [1, 2, 3, 6, 7, 8]
    """
    return copy.copy(values)


def deepcopy_sequence(values: TypeVarSequence) -> TypeVarSequence:
    """
    Deep copy list and return the copy.

    Parameters
    ----------
    values : list
        list of values

    Returns
    -------
    list
        deep copy of list

    Example
    -------
    >>> values = [1, 2, 3, 6, 7, 8]
    >>> values_copy = deepcopy_list(values)
    >>> values_copy
    [1, 2, 3, 6, 7, 8]
    >>> values_copy[0] = 11
    >>> values_copy
    [11, 2, 3, 6, 7, 8]
    >>> values
    [1, 2, 3, 6, 7, 8]
    """
    return copy.deepcopy(values)
