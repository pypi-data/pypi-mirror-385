from itertools import repeat
from numbers import Number
from typing import Any, Callable, Iterable, List, MutableSequence, Sequence, Sized, Union

import tinytim.data as data_functions
import tinytim.sequences as sequences_functions
import tinytim.utils as utils_functions
from tinytim.custom_types import DataDict, DataMapping, data_dict
from tinytim.interfaces import (
    DeleteItem,
    GetMutableSequence,
    KeyNamesGetItem,
    KeyNamesGetMutableSequence,
    KeyNamesGetMutableSequenceSequenceValues,
    SequenceItems,
    SequenceItemsGetMutableSequence,
)


def edit_row_items_inplace(
    data: GetMutableSequence,
    index: int,
    items: KeyNamesGetItem
) -> None:
    """
    Changes row index to mapping items values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    index : int
        index of row to edit
    items : Mapping[str, Any]
        {column names: value} of new values to edit in data

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_row_items_inplace(data, 0, {'x': 11, 'y': 66})
    >>> data
    {'x': [11, 2, 3], 'y': [66, 7, 8]}
    """
    for col in items:
        data[col][index] = items[col]


def edit_row_values_inplace(
    data: KeyNamesGetMutableSequence,
    index: int,
    values: Sequence[Any]
) -> None:
    """
    Changed row index to values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    index : int
        index of row to edit
    values : Sequence[Any]

        new values to replace in data row

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_row_values_inplace(data, 1, (22, 77))
    >>> data
    {'x': [1, 22, 3], 'y': [6, 77, 8]}
    """
    if len(values) != data_functions.column_count(data):
        raise AttributeError('values length must match columns length.')
    for col, value in zip(data_functions.column_names(data), values):
        data[col][index] = value


def edit_column_inplace(
    data: KeyNamesGetMutableSequenceSequenceValues,
    column_name: str,
    values: Union[Sequence[Any], str]
) -> None:
    """
    Edit values in named column.
    Overrides existing values if column exists,
    Created new column with values if column does not exist.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        new values to replace in data column

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_column_inplace(data, 'x', [11, 22, 33])
    >>> data
    {'x': [11, 22, 33], 'y': [6, 7, 8]}
    """
    iterable_and_sized = isinstance(values, Iterable) and isinstance(values, Sized)
    if isinstance(values, str) or not iterable_and_sized:
        if column_name in data:
            utils_functions.set_values_to_one(data[column_name], values)
        else:
            for i in range(data_functions.row_count(data)):
                data[column_name][i] = values
        return
    if len(values) != data_functions.row_count(data):
        raise ValueError('values length must match data rows count.')
    if column_name in data:
        utils_functions.set_values_to_many(data[column_name], values)
    else:
        for i, value in enumerate(values):
            data[column_name][i] = value


def operator_column_inplace(
    data: GetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], str, Number],
    func: Callable[[Any, Any], Any]
) -> None:
    """
    Uses func operator on values from existing named column.
    If values is a Sequence[Any], operate each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], operate value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to subtract from data column
    func : Callable[[Any, Any], Any]
        operator function to use to use values on existing column values

    Returns
    -------
    None
    """
    new_values = sequences_functions.operate_on_sequence(data[column_name], values, func)
    utils_functions.set_values_to_many(data[column_name], new_values)


def add_to_column_inplace(
    data: GetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], str, Number]
) -> None:
    """
    Add values to existing named column.
    If values is a Sequence[Any], add each value to each existing value.
    Must be same len as column.
    If not a Sequence[Any], adds value to all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to add to data column

    Returns
    -------
    None

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> add_to_column_inplace(data, 'x', [11, 22, 33])
    >>> data
    {'x': [12, 24, 36], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> add_to_column_inplace(data, 'x', 1)
    >>> data
    {'x': [2, 3, 4], 'y': [6, 7, 8]}
    """
    operator_column_inplace(data, column_name, values, lambda x, y : x + y)


def subtract_from_column_inplace(
    data: GetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> None:
    """
    Subtract values from existing named column.
    If values is a Sequence[Any], subtract each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], subtracts value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to subtract from data column

    Returns
    -------
    None

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> subtract_from_column_inplace(data, 'x', [11, 22, 33])
    >>> data
    {'x': [-10, -20, -30], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> subtract_from_column_inplace(data, 'x', 1)
    >>> data
    {'x': [0, 1, 2], 'y': [6, 7, 8]}
    """
    operator_column_inplace(data, column_name, values, lambda x, y : x - y)


def divide_column_inplace(
    data: GetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> None:
    """
    Divide values from existing named column.
    If values is a Sequence[Any], Divide each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], divide value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to divide from data column

    Returns
    -------
    None

    Raises
    ------
    ZeroDivisionError
        if values is 0 or contains 0

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> divide_column_inplace(data, 'x', [2, 3, 4])
    >>> data
    {'x': [0.5, 0.6666666666666666, 0.75], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> divide_column_inplace(data, 'x', 2)
    >>> data
    {'x': [0.5, 1.0, 1.5], 'y': [6, 7, 8]}
    """
    operator_column_inplace(data, column_name, values, lambda x, y : x / y)


def drop_row_inplace(
    data: KeyNamesGetMutableSequence,
    index: int
) -> None:
    """
    Remove index row from data.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    index : int
        index of row to remove from data

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> drop_row_inplace(data, 1)
    >>> data
    {'x': [1, 3], 'y': [6, 8]}
    """
    for col in data_functions.column_names(data):
        data[col].pop(index)


def drop_label_inplace(
    labels: Union[None, MutableSequence[Any]],
    index: int
) -> None:
    """
    If labels exists, drop item at index.

    Parameters
    ----------
    labels : List[Any], optional
        list of values used as labels
    index : int
        index of value to remove from labels list

    Returns
    -------
    None

    Examples
    --------
    >>> labels = [1, 2, 3, 4, 5]
    >>> drop_label_inplace(labels, 1)
    >>> labels
    [1, 3, 4, 5]

    >>> labels = None
    >>> drop_label_inplace(labels, 1)
    >>> labels
    None
    """
    if labels is not None:
        labels.pop(index)


def drop_column_inplace(
    data: DeleteItem,
    column_name: str
) -> None:
    """
    Remove named column from data.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        name of column to remove from data

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> drop_column_inplace(data, 'y')
    >>> data
    {'x': [1, 2, 3]}
    """
    del data[column_name]


def edit_value_inplace(
    data: GetMutableSequence,
    column_name: str,
    index: int,
    value: Any
) -> None:
    """
    Edit the value in named column as row index.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        name of column to remove from data
    index : int
        row index of column to edit
    value : Any
        new value to change to

    Returns
    -------
    None

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_value_inplace(data, 'x', 0, 11)
    >>> data
    {'x': [11, 2, 3], 'y': [6, 7, 8]}
    """
    data[column_name][index] = value


def edit_row_items(
    data: SequenceItemsGetMutableSequence,
    index: int,
    items: KeyNamesGetItem
) -> DataDict:
    """
    Return data with row values at index changed to mapping items values.

    Parameters
    ----------
    data : Mapping[str, Sequence[Any]]
        data mapping of {column name: column values}
    index : int
        index of row to edit
    items : Mapping[str, Any]
        {column names: value} of new values to edit in data

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_row_items(data, 0, {'x': 11, 'y': 66})
    {'x': [11, 2, 3], 'y': [66, 7, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    data = data_dict(data)
    edit_row_items_inplace(data, index, items)
    return data


def edit_row_values(
    data: SequenceItemsGetMutableSequence,
    index: int,
    values: Sequence[Any]
) -> DataDict:
    """
    Return data with row values at index changed to sequence of values.

    Parameters
    ----------
    data : Mapping[str, Sequence[Any]]
        data mapping of {column name: column values}
    index : int
        index of row to edit
    values : Sequence[Any]

        new values to replace in data row

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_row_values(data, 1, (22, 77))
    {'x': [1, 22, 3], 'y': [6, 77, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    data = data_dict(data)
    if len(values) != data_functions.column_count(data):
        raise AttributeError('values length must match columns length.')
    for col, value in zip(data_functions.column_names(data), values):
        data[col][index] = value
    return data


def edit_column(
    data: SequenceItemsGetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], str]
) -> DataDict:
    """
    Return data with values changed in named column.
    Overrides existing values if column exists,
    Created new column with values if column does not exist.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        new values to replace in data column

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_column(data, 'x', [11, 22, 33])
    {'x': [11, 22, 33], 'y': [6, 7, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}

    >>> edit_column(data, 'z', [66, 77, 88])
    {'x': [1, 2, 3], 'y': [6, 7, 8], 'z': [66, 77, 88]}
    """
    data = data_dict(data)
    iterable_and_sized = isinstance(values, Iterable) and isinstance(values, Sized)
    if isinstance(values, str) or not iterable_and_sized:
        if column_name in data:
            utils_functions.set_values_to_one(data[column_name], values)
        else:
            data[column_name] = list(repeat(values, data_functions.row_count(data)))
        return data
    if len(values) != data_functions.row_count(data):
        raise ValueError('values length must match data rows count.')
    if column_name in data:
        utils_functions.set_values_to_many(data[column_name], values)
    else:
        data[column_name] = list(values)
    return data


def operator_column(
    data: SequenceItems,
    column_name: str,
    values: Union[Sequence[Any], str, Number],
    func: Callable[[Any, Any], Any]
) -> DataDict:
    """
    Return data with func operator used on values from named column.
    If values is a Sequence[Any], operate each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], operate value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to subtract from data column
    func : Callable[[Any, Any], Any]
        operator function to use to use values on existing column values

    Returns
    -------
    Dict[str, list]

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> operator_column(data, 'x', 1, lambda x, y : x + y)
    {'x': [2, 3, 4], 'y': [6, 7, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}

    >>> operator_column(data, 'x', [3, 4, 5], lambda x, y : x + y)
    {'x': [4, 6, 8], 'y': [6, 7, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    data = data_dict(data)
    new_values = sequences_functions.operate_on_sequence(data[column_name], values, func)
    utils_functions.set_values_to_many(data[column_name], new_values)
    return data


def add_to_column(
    data: SequenceItems,
    column_name: str,
    values: Union[Sequence[Any], str, Number]
) -> DataDict:
    """
    Return data with values added to named column values.
    If values is a Sequence[Any], add each value to each existing value.
    Must be same len as column.
    If not a Sequence[Any], adds value to all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to add to data column

    Returns
    -------
    Dict[str, list]

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> add_to_column(data, 'x', [11, 22, 33])
    {'x': [12, 24, 36], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> add_to_column(data, 'x', 1)
    {'x': [2, 3, 4], 'y': [6, 7, 8]}
    """
    return operator_column(data, column_name, values, lambda x, y : x + y)


def subtract_from_column(
    data: SequenceItems,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> DataDict:
    """
    Return data with values subtracted from named column values.
    If values is a Sequence[Any], subtract each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], subtracts value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to subtract from data column

    Returns
    -------
    Dict[str, list]

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> subtract_from_column_inplace(data, 'x', [11, 22, 33])
    >>> data
    {'x': [-10, -20, -30], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> subtract_from_column_inplace(data, 'x', 1)
    >>> data
    {'x': [0, 1, 2], 'y': [6, 7, 8]}
    """
    return operator_column(data, column_name, values, lambda x, y : x - y)


def multiply_column_inplace(
    data: GetMutableSequence,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> None:
    """
    Multiply values with existing named column.
    If values is a Sequence[Any], multiply each value with each existing value.
    Must be same len as column.
    If not a Sequence[Any], multiply value with all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to multiply with data column

    Returns
    -------
    Dict[str, list]

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> multiply_column_inplace(data, 'x', [11, 22, 33])
    >>> data
    {'x': [11, 44, 99], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> multiply_column_inplace(data, 'x', 2)
    >>> data
    {'x': [2, 4, 6], 'y': [6, 7, 8]}
    """
    operator_column_inplace(data, column_name, values, lambda x, y : x * y)


def multiply_column(
    data: SequenceItems,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> DataDict:
    """
    Return data with values multiplied with named column values.
    If values is a Sequence[Any], multiply each value with each existing value.
    Must be same len as column.
    If not a Sequence[Any], multiply value with all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to multiply with data column

    Returns
    -------
    Dict[str, list]

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> multiply_column(data, 'x', [11, 22, 33])
    {'x': [11, 44, 99], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> multiply_column(data, 'x', 2)
    {'x': [2, 4, 6], 'y': [6, 7, 8]}
    """
    data = data_dict(data)
    return operator_column(data, column_name, values, lambda x, y : x * y)


def divide_column(
    data: SequenceItems,
    column_name: str,
    values: Union[Sequence[Any], Number]
) -> DataDict:
    """
    Return data with named column divided by values.
    If values is a Sequence[Any], Divide each value from each existing value.
    Must be same len as column.
    If not a Sequence[Any], divide value from all existing values.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        column name to edit in data
    values : Sequence[Any]

        values to divide from data column

    Returns
    -------
    Dict[str, list]

    Raises
    ------
    ZeroDivisionError
        if values is 0 or contains 0

    Examples
    --------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> divide_column(data, 'x', [2, 3, 4])
    {'x': [0.5, 0.6666666666666666, 0.75], 'y': [6, 7, 8]}

    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> divide_column(data, 'x', 2)
    {'x': [0.5, 1.0, 1.5], 'y': [6, 7, 8]}
    """
    return operator_column(data, column_name, values, lambda x, y : x / y)


def drop_row(
    data: DataMapping,
    index: int
) -> DataDict:
    """
    Return data with row at index removed from data.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    index : int
        index of row to remove from data

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> drop_row(data, 1)
    {'x': [1, 3], 'y': [6, 8]}
    """
    data = data_dict(data)
    for col in data_functions.column_names(data):
        data[col].pop(index)
    return data


def drop_label(
    labels: Union[None, Sequence[Any]],
    index: int
) -> Union[None, List[Any]]:
    """
    If labels exists, drop item at index.

    Parameters
    ----------
    labels : List[Any], optional
        list of values used as labels
    index : int
        index of value to remove from labels list

    Returns
    -------
    None | list

    Examples
    --------
    >>> labels = [1, 2, 3, 4, 5]
    >>> drop_label_inplace(labels, 1)
    >>> labels
    [1, 3, 4, 5]

    >>> labels = None
    >>> drop_label_inplace(labels, 1)
    >>> labels
    None
    """
    if labels is not None:
        labels = list(labels)
        labels.pop(index)
    return labels


def drop_column(
    data: DataMapping,
    column_name: str
) -> DataDict:
    """
    Return data with named column dropped.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        name of column to remove from data

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> drop_column(data, 'y')
    {'x': [1, 2, 3]}
    """
    data = data_dict(data)
    del data[column_name]
    return data


def edit_value(
    data: DataMapping,
    column_name: str,
    index: int,
    value: Any
) -> DataDict:
    """
    Return data with value in named column and row index edited with value.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    column_name : str
        name of column to remove from data
    index : int
        row index of column to edit
    value : Any
        new value to change to

    Returns
    -------
    Dict[str, list]

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> edit_value(data, 'x', 0, 11)
    {'x': [11, 2, 3], 'y': [6, 7, 8]}
    """
    data = data_dict(data)
    data[column_name][index] = value
    return data


def replace_column_names(
    data: DataMapping,
    new_names: Sequence[str]
) -> DataDict:
    """
    Return data with same column data but with new column names.

    Parameters
    ----------
    data : MutableMapping[str, MutableSequence]
        data mapping of {column name: column values}
    new_names : Sequence[str]
        new names of columns

    Returns
    -------
    Dict[str, list]
        copy of data with new column names

    Example
    -------
    >>> data = {'x': [1, 2, 3], 'y': [6, 7, 8]}
    >>> replace_column_names(data, ('xx', 'yy'))
    >>> {'xx': [1, 2, 3], 'yy': [6, 7, 8]}
    >>> data
    {'x': [1, 2, 3], 'y': [6, 7, 8]}
    """
    old_names = data_functions.column_names(data)
    if len(new_names) != len(old_names):
        raise ValueError('new_names must be same size as data column_count.')
    return {new_name: list(data[old_name]) for new_name, old_name in zip(new_names, old_names)}
