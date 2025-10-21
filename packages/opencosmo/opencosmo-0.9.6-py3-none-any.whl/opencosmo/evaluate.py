from typing import Any, Sequence

import astropy.units as u
import numpy as np

"""
General helper routines for evaluating expressions on datasets and collections
"""


def insert(
    storage: dict[str, np.ndarray], index: int, values_to_insert: dict[str, Any]
):
    if isinstance(values_to_insert, dict):
        for name, value in values_to_insert.items():
            storage[name][index] = value
        return storage

    name = next(iter(storage.keys()))
    storage[name][index] = values_to_insert


def make_output_from_first_values(first_values: dict, n_rows: int):
    storage = {}
    for name, value in first_values.items():
        shape: tuple[int, ...] = (n_rows,)
        dtype = type(value)
        if isinstance(value, np.ndarray):
            shape = shape + value.shape
            dtype = value.dtype
        storage[name] = np.zeros(shape, dtype=dtype)
    for name, value in first_values.items():
        if isinstance(value, u.Quantity):
            storage[name] = storage[name] * value.unit
        storage[name][0] = value
    return storage


def prepare_kwargs(
    n_rows: int, evaluator_kwargs: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Sequence]]:
    kwargs = {}
    array_kwargs = {}
    for name, kwarg in evaluator_kwargs.items():
        try:
            length = len(kwarg)
            if length == n_rows:
                array_kwargs[name] = kwarg
                continue
            kwargs[name] = kwarg

        except TypeError:
            kwargs[name] = kwarg

    return kwargs, array_kwargs
