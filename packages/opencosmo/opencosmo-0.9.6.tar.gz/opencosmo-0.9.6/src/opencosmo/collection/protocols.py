from typing import Iterable, Protocol, Self, Union

from opencosmo.dataset import Dataset
from opencosmo.dataset.column import ColumnMask
from opencosmo.header import OpenCosmoHeader
from opencosmo.io.io import OpenTarget
from opencosmo.io.protocols import DataSchema


class Collection(Protocol):
    """
    Collections represent a group of datasets that are related in some way. They
    support higher-level operations that are applied across all datasets in the
    collection, sometimes in a non-obvious way.

    This protocol defines methods a collection must implement. Most notably they
    must include  __getitem__, keys, values and __items__, which allows
    a collection to behave like a read-only dictionary.


    Note that the "open" and "read" methods are used in the case an entire collection
    is located within a single file. Multi-file collections are handled
    in the collection.io module. Most complexity is hidden from the user
    who simply calls "oc.read" and "oc.open" to get a collection. The io
    module also does sanity checking to ensure files are structurally valid,
    so we do not have to do it here.
    """

    @classmethod
    def open(
        cls, targets: list[OpenTarget], **kwargs
    ) -> Union["Collection", Dataset]: ...

    def make_schema(self) -> DataSchema: ...
    @property
    def dtype(self) -> str | dict[str, str]: ...

    @property
    def header(self) -> OpenCosmoHeader | dict[str, OpenCosmoHeader]: ...

    def __getitem__(self, key: str) -> Union[Dataset, "Collection"]: ...
    def keys(self) -> Iterable[str]: ...
    def values(self) -> Iterable[Union[Dataset, "Collection"]]: ...
    def items(self) -> Iterable[tuple[str, Union[Dataset, "Collection"]]]: ...
    def __enter__(self): ...
    def __exit__(self, *exc_details): ...
    def filter(self, *masks: ColumnMask) -> Self: ...
    def select(self, *args, **kwargs) -> Self: ...
    def with_units(self, convention: str) -> Self: ...
    def take(self, *args, **kwargs) -> Self: ...
