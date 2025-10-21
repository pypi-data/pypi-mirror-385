from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Generator,
    Iterable,
    Mapping,
    Optional,
    TypeAlias,
)
from warnings import warn

import astropy.units as u  # type: ignore
import numpy as np
from astropy import units  # type: ignore
from astropy.cosmology import Cosmology  # type: ignore
from astropy.table import QTable  # type: ignore

from opencosmo.dataset.column import ColumnMask, DerivedColumn
from opencosmo.dataset.evaluate import visit_dataset
from opencosmo.dataset.state import DatasetState
from opencosmo.header import OpenCosmoHeader
from opencosmo.index import ChunkedIndex, DataIndex
from opencosmo.io.schemas import DatasetSchema
from opencosmo.parameters import HaccSimulationParameters
from opencosmo.spatial import check
from opencosmo.spatial.protocols import Region
from opencosmo.spatial.tree import Tree

if TYPE_CHECKING:
    from opencosmo.dataset.handler import DatasetHandler


OpenCosmoData: TypeAlias = QTable | u.Quantity | dict[str, np.ndarray] | np.ndarray


class Dataset:
    def __init__(
        self,
        handler: DatasetHandler,
        header: OpenCosmoHeader,
        state: DatasetState,
        tree: Optional[Tree] = None,
    ):
        self.__handler = handler
        self.__header = header
        self.__state = state
        self.__tree = tree
        self.__cached_data: Optional[OpenCosmoData] = None

    def __repr__(self):
        """
        A basic string representation of the dataset
        """
        length = len(self)

        if len(self) < 10:
            repr_ds = self
            table_head = ""
        else:
            repr_ds = self.take(10, at="start")
            table_head = "First 10 rows:\n"

        table_repr = repr_ds.data.__repr__()
        # remove the first line
        table_repr = table_repr[table_repr.find("\n") + 1 :]
        head = f"OpenCosmo Dataset (length={length})\n"
        cosmo_repr = f"Cosmology: {self.cosmology.__repr__()}" + "\n"
        return head + cosmo_repr + table_head + table_repr

    def __len__(self):
        return len(self.__state.index)

    def __enter__(self):
        # Need to write tests
        return self

    def __exit__(self, *exc_details):
        return self.__handler.__exit__(*exc_details)

    def close(self):
        return self.__handler.__exit__()

    @property
    def header(self) -> OpenCosmoHeader:
        """
        The header associated with this dataset.

        OpenCosmo headers generally contain information about the original data this
        dataset was produced from, as well as any analysis that was done along
        the way.

        Returns
        -------
        header: opencosmo.header.OpenCosmoHeader

        """
        return self.__header

    @property
    def columns(self) -> list[str]:
        """
        The names of the columns in this dataset.

        Returns
        -------
        columns: list[str]
        """
        return self.__state.columns

    @property
    def cosmology(self) -> Cosmology:
        """
        The cosmology of the simulation this dataset is drawn from as
        an astropy.cosmology.Cosmology object.

        Returns
        -------
        cosmology: astropy.cosmology.Cosmology
        """
        return self.__header.cosmology

    @property
    def dtype(self) -> str:
        """
        The data type of this dataset.

        Returns
        -------
        dtype: str
        """
        return str(self.__header.file.data_type)

    @property
    def redshift(self) -> float | tuple[float, float]:
        """
        The redshift slice or range this dataset was drawn from

        Returns
        -------
        redshift: float

        """
        return self.__header.file.redshift

    @property
    def region(self) -> Region:
        """
        The region this dataset is contained in. If no spatial
        queries have been performed, this will be the entire
        simulation box for snapshots or the full sky for lightcones

        Returns
        -------
        region: opencosmo.spatial.Region

        """
        return self.__state.region

    @property
    def simulation(self) -> HaccSimulationParameters:
        """
        The parameters of the simulation this dataset is drawn
        from.

        Returns
        -------
        parameters: opencosmo.parameters.hacc.HaccSimulationParameters
        """
        return self.__header.simulation

    @property
    def data(self) -> QTable | u.Quantity:
        """
        Return the data in the dataset in astropy format. The value of this
        attribute is equivalent to the return value of
        :code:`Dataset.get_data("astropy")`. However data retrieved via this
        attribute will be cached, meaning further calls to
        :py:attr:`Dataset.data <opencosmo.Dataset.data>` should be instantaneous.

        However there is one caveat. If you modify the table, those modifications will
        persist if you later request the data again with this attribute. Calls to
        :py:meth:`Dataset.get_data <opencosmo.Dataset.get_data>` will be unaffected, and
        datasets generated from this dataset will not contain the modifications. If you
        plan to modify the data in this table, you should use
        :py:meth:`Dataset.with_new_columns <opencosmo.Dataset.with_new_columns>`.


        Returns
        -------
        data : astropy.table.Table or astropy.table.Column
            The data in the dataset.

        """
        # should rename this, dataset.data can get confusing
        # Also the point is that there's MORE data than just the table
        if self.__cached_data is None:
            self.__cached_data = self.get_data("astropy")
        return self.__cached_data.copy()

    @property
    def index(self) -> DataIndex:
        return self.__state.index

    def get_data(
        self, output="astropy", unpack=True, attach_index=False
    ) -> OpenCosmoData:
        """
        Get the data in this dataset as an astropy table/column or as
        numpy array(s). Note that a dataset does not load data from disk into
        memory until this function is called. As a result, you should not call
        this function until you have performed any transformations you plan to
        on the data.

        You can get the data in two formats, "astropy" (the default) and "numpy".
        "astropy" format will return the data as an astropy table with associated
        units. "numpy" will return the data as a dictionary of numpy arrays. The
        numpy values will be in the associated unit convention, but no actual
        units will be attached.

        If the dataset only contains a single column, it will be returned as an
        astropy quantity (if it has units) or numpy array.

        This method does not cache data. Calling "get_data" always reads data
        from disk, even if you have already called "get_data" in the past.
        You can use :py:attr:`Dataset.data <opencosmo.Dataset.data>` to return
        data and keep it in memory.

        Parameters
        ----------
        output: str, default="astropy"
            The format to output the data in

        Returns
        -------
        data: Table | Quantity | dict[str, ndarray] | ndarray
            The data in this dataset.
        """
        if output not in {"astropy", "numpy"}:
            raise ValueError(f"Unknown output type {output}")

        data = self.__state.get_data(self.__handler, attach_index=attach_index)  # table
        if len(data) == 1 and unpack:  # unpack length-1 tables
            data = {name: data[0] for name, data in data.items()}
        elif len(data.colnames) == 1:
            cn = data.colnames[0]
            data = data[cn]

        if output == "numpy":
            if isinstance(data, u.Quantity):
                data = data.value
            elif isinstance(data, (QTable, dict)):
                data = dict(data)
                is_quantity = filter(
                    lambda v: isinstance(data[v], u.Quantity), data.keys()
                )
                for colname in is_quantity:
                    data[colname] = data[colname].value

        if isinstance(data, dict) and len(data) == 1:
            return next(iter(data.values()))

        return data

    def bound(self, region: Region, select_by: Optional[str] = None):
        """
        Restrict the dataset to some subregion. The subregion will always be evaluated
        in the same units as the current dataset. For example, if the dataset is
        in the default "comoving" unit convention, positions are always in units of
        comoving Mpc. However Region objects themselves do not carry units.
        See :doc:`spatial_ref` for details of how to construct regions.

        Parameters
        ----------
        region: opencosmo.spatial.Region
            The region to query.

        Returns
        -------
        dataset: opencosmo.Dataset
            The portion of the dataset inside the selected region

        Raises
        ------
        ValueError
            If the query region does not overlap with the region this dataset resides
            in
        AttributeError:
            If the dataset does not contain a spatial index
        """
        if self.__tree is None:
            raise AttributeError(
                "Your dataset does not contain a spatial index, "
                "so spatial querying is not available"
            )

        check_region = region.into_scalefree(
            self.__state.convention, self.cosmology, self.redshift
        )

        if not self.__state.region.intersects(check_region):
            new_index = ChunkedIndex.empty()
            new_state = self.__state.with_index(new_index)
            return Dataset(self.__handler, self.__header, new_state, self.__tree)

        if not self.__state.region.contains(check_region):
            warn(
                "You're querying with a region that is not fully contained by the "
                "region this dataset is in. This may result in unexpected behavior"
            )

        contained_index: DataIndex
        intersects_index: DataIndex
        contained_index, intersects_index = self.__tree.query(check_region)

        contained_index = contained_index.intersection(self.__state.index)
        intersects_index = intersects_index.intersection(self.__state.index)

        check_state = self.__state.with_index(intersects_index)
        check_dataset = Dataset(
            self.__handler,
            self.__header,
            check_state,
            self.__tree,
        )
        if not self.__header.file.is_lightcone:
            check_dataset = check_dataset.with_units("scalefree")

        mask = check.check_containment(check_dataset, check_region, self.__header.file)
        new_intersects_index = intersects_index.mask(mask)

        new_index = contained_index.concatenate(new_intersects_index)

        new_state = self.__state.with_index(new_index).with_region(check_region)

        return Dataset(self.__handler, self.__header, new_state, self.__tree)

    def evaluate(
        self,
        func: Callable,
        vectorize=False,
        insert=False,
        format="astropy",
        **evaluate_kwargs,
    ) -> Dataset | np.ndarray:
        """
        Iterate over the rows in this dataset, apply :code:`func` to each, and collect
        the result as new columns in the dataset.

        This function is the equivalent of :py:meth:`with_new_columns <opencosmo.Dataset.with_new_columns>`
        for cases where the new column is not a simple algebraic combination of existing columns. Unlike
        :code:`with_new_columns`, this method will evaluate the results immediately and the resulting
        columns will not change under unit transformations. You may also choose to simply return the result
        instead of adding it as a column.

        The function should take in arguments with the same name as the columns in this dataset that
        are needed for the computation, and should return a dictionary of output values.
        The dataset will automatically selected the needed columns to avoid reading unnecessarily reading
        data from disk. You may also include all columns in the dataset by providing a function with a single
        import argument with the same name as the data type of this dataset (see :py:attr:`Dataset.dtype <opencosmo.Dataset.dtype>`
        In this case, the data will be provided as a dictionary of astropy quantity arrays or numpy arrays

        The new columns will have the same names as the keys of the output dictionary
        See :ref:`Evaluating On Datasets` for more details.

        If vectorize is set to True, the full columns will be pased to the dataset. Otherwise,
        rows will be passed to the function one at a time.

        If the function returns None, this method will also return None as output. For example, the function
        could simply produce plots and save the to files.

        Parameters
        ----------

        func: Callable
            The function to evaluate on the rows in the dataset.

        vectorize: bool, default = False
            Whether to provide the values as full columns (True) or one row at a time (False)

        insert: bool, default = True
            If true, the data will be inserted as a column in this dataset. The new column will have the same name
            as the function. Otherwise the data will be returned directly.

        format: str, default = astropy
            Whether to provide data to your function as "astropy" quantities or "numpy" arrays/scalars. Default "astropy"

        **evaluate_kwargs: any,
            Any additional arguments that are required for your function to run. These will be passed directly
            to the function as keyword arguments. If a kwarg is an array of values with the same length as the dataset,
            it will be treated as an additional column.

        Returns
        -------
        result : Dataset | dict[str, np.ndarray | astropy.units.Quantity]
            The new dataset with the evaluated column(s) or the results as numpy arrays or astropy quantities
        """
        kwarg_columns = set(evaluate_kwargs.keys()).intersection(self.columns)
        if kwarg_columns:
            raise ValueError(
                "Keyword arguments cannot have the same name as columns in your dataset!"
            )

        output = visit_dataset(func, self, vectorize, format, evaluate_kwargs)
        if output is None or not insert:
            return output
        is_same_length = all(
            isinstance(o, np.ndarray) and len(o) == len(self) for o in output.values()
        )

        if not is_same_length:
            raise ValueError(
                "The function to evaluate must produce an array with the same length as this dataset!"
            )
        return self.with_new_columns(**output)

    def filter(self, *masks: ColumnMask) -> Dataset:
        """
        Filter the dataset based on some criteria. See :ref:`Querying Based on Column
        Values` for more information.

        Parameters
        ----------
        *masks : Mask
            The masks to apply to dataset, constructed with :func:`opencosmo.col`

        Returns
        -------
        dataset : Dataset
            The new dataset with the masks applied.

        Raises
        ------
        ValueError
            If the given  refers to columns that are
            not in the dataset, or the  would return zero rows.

        """
        required_columns = set(m.column_name for m in masks)
        data = self.select(required_columns).get_data()
        bool_mask = np.ones(len(data), dtype=bool)
        for mask in masks:
            bool_mask &= mask.apply(data)

        new_state = self.__state.with_mask(bool_mask)
        return Dataset(self.__handler, self.__header, new_state, self.__tree)

    def rows(
        self,
        output="astropy",
        attach_index=False,
    ) -> Generator[Mapping[str, float | units.Quantity | np.ndarray]]:
        """
        Iterate over the rows in the dataset. Rows are returned as a dictionary
        For performance, it is recommended to first select the columns you need to
        work with.

        Parameters
        ----------
        output: str, default = "astropy"
            Whether to return values as "astropy" quantities or "numpy" scalars


        Yields
        -------
        row : dict
            A dictionary of values for each row in the dataset with units.

        """
        max = len(self)
        if max == 0:
            warn("Tried to iterate over a dataset with no rows!")

        chunk_ranges = [(i, min(i + 1000, max)) for i in range(0, max, 1000)]
        if len(chunk_ranges) == 0:
            raise StopIteration
        for start, end in chunk_ranges:
            chunk = self.take_range(start, end)
            chunk_data = chunk.get_data(output, attach_index=attach_index)
            try:
                output_chunk_data = dict(chunk_data)
            except TypeError:
                output_chunk_data = {self.columns[0]: chunk_data}

            if len(chunk) == 1:
                yield output_chunk_data
                return

            for i in range(len(chunk)):
                yield {k: v[i] for k, v in output_chunk_data.items()}

    def select(self, columns: str | Iterable[str]) -> Dataset:
        """
        Create a new dataset from a subset of columns in this dataset

        Parameters
        ----------
        columns : str or list[str]
            The column or columns to select.

        Returns
        -------
        dataset : Dataset
            The new dataset with only the selected columns.

        Raises
        ------
        ValueError
            If any of the given columns are not in the dataset.
        """
        new_state = self.__state.select(columns)
        return Dataset(
            self.__handler,
            self.__header,
            new_state,
            self.__tree,
        )

    def drop(self, columns: str | Iterable[str]) -> Dataset:
        """
        Create a new dataset without the provided columns.

        Parameters
        ----------
        columns : str or list[str]
            The columns to drop

        Returns
        -------
        dataset : Dataset
            The new dataset without the droppedcolumns

        Raises
        ------
        ValueError
            If any of the provided columns are not in the dataset.

        """
        if isinstance(columns, str):
            columns = [columns]

        current_columns = set(self.__state.columns)
        dropped_columns = set(columns)

        if missing := dropped_columns.difference(current_columns):
            raise ValueError(f"Columns {missing} are  not in this dataset")

        return self.select(current_columns - dropped_columns)

    def sort_by(self, column: str, invert: bool = False) -> Dataset:
        """
        Sort this dataset by the values in a given column. By default sorting is in
        ascending order (least to greatest). Pass invert = True to sort in descending
        order (greatest to least).

        This can be used to, for example, select largest halos in a given
        dataset:

        .. code-block:: python

            dataset = oc.open("haloproperties.hdf5")
            dataset = dataset
                        .sort_by("fof_halo_mass")
                        .take(100, at="start")

        Parameters
        ----------
        column : str
            The column in the halo_properties or galaxy_properties dataset to
            order the collection by.

        invert : bool, default = False
            If False (the default), ordering will be from least to greatest.
            Otherwise greatest to least.

        Returns
        -------
        result : Dataset
            A new Dataset ordered by the given column.


        """
        new_state = self.__state.sort_by(column, self.__handler, invert)
        return Dataset(
            self.__handler,
            self.__header,
            new_state,
            self.__tree,
        )

    def take(
        self,
        n: int,
        at: str = "random",
    ) -> Dataset:
        """
        Create a new dataset from some number of rows from this dataset.

        Can take the first n rows, the last n rows, or n random rows
        depending on the value of 'at'.


        Parameters
        ----------
        n : int
            The number of rows to take.
        at : str
            Where to take the rows from. One of "start", "end", or "random".
            The default is "random".


        Returns
        -------
        dataset : Dataset
            The new dataset with only the selected rows.

        Raises
        ------
        ValueError
            If n is negative or greater than the number of rows in the dataset,
            or if 'at' is invalid.

        """

        new_state = self.__state.take(n, at, self.__handler)

        return Dataset(
            self.__handler,
            self.__header,
            new_state,
            self.__tree,
        )

    def take_range(self, start: int, end: int) -> Dataset:
        """
        Create a new dataset from a row range in this dataset.

        Parameters
        ----------
        start : int
            The first row to get.
        end : int
            The last row to get.

        Returns
        -------
        table : astropy.table.Table
            The table with only the rows from start to end.

        Raises
        ------
        ValueError
            If start or end are negative or greater than the length of the dataset
            or if end is greater than start.

        """
        new_state = self.__state.take_range(start, end)

        return Dataset(
            self.__handler,
            self.__header,
            new_state,
            self.__tree,
        )

    def with_index(self, index: DataIndex):
        new_state = self.__state.with_index(index)
        return Dataset(self.__handler, self.__header, new_state, self.__tree)

    def with_new_columns(
        self, **new_columns: DerivedColumn | np.ndarray | units.Quantity
    ):
        """
        Create a new dataset with additional columns. These new columns can be derived
        from columns already in the dataset, a numpy array, or an astropy quantity
        array. When a column is derived from other columns, it will behave
        appropriately under unit transformations. Columns provided directly as astropy
        quantities will not change under unit transformations. See
        :ref:`Adding Custom Columns` for examples.

        Parameters
        ----------
        ** columns : opencosmo.DerivedColumn | np.ndarray | units.Quantity

        Returns
        -------
        dataset : opencosmo.Dataset
            This dataset with the columns added

        """
        new_state = self.__state.with_new_columns(**new_columns)
        return Dataset(self.__handler, self.__header, new_state, self.__tree)

    def make_schema(self, with_header: bool = True) -> DatasetSchema:
        """
        Prep to write the dataset. This should not be called directly for the user.
        The opencosmo.write file writer automatically handles the file context.

        Parameters
        ----------
        file : h5py.File
            The file to write to.
        dataset_name : str
            The name of the dataset in the file. The default is "data".

        """

        schema = self.__state.make_schema(self.__handler)
        if not with_header:
            schema.header = None

        if self.__tree is not None:
            tree = self.__tree.apply_index(self.__state.index)
            spat_idx_schema = tree.make_schema()
            schema.add_child(spat_idx_schema, "index")
        return schema

    def with_units(self, convention: str) -> Dataset:
        """
        Create a new dataset from this one with a different unit convention.

        Parameters
        ----------
        convention : str
            The unit convention to use. One of "physical", "comoving",
            "scalefree", or "unitless".

        Returns
        -------
        dataset : Dataset
            The new dataset with the requested unit convention.

        """
        new_state = self.__state.with_units(convention, self.cosmology, self.redshift)
        new_header = self.__header.with_units(convention)

        return Dataset(
            self.__handler,
            new_header,
            new_state,
            self.__tree,
        )

    def collect(self) -> Dataset:
        """
        Given a dataset that was originally opend with opencosmo.open,
        return a dataset that is in-memory as though it was read with
        opencosmo.read.

        This is useful if you have a very large dataset on disk, and you
        want to filter it down and then close the file.

        For example:

        .. code-block:: python

            import opencosmo as oc
            with oc.open("path/to/file.hdf5") as file:
                ds = file.(ds["sod_halo_mass"] > 0)
                ds = ds.select(["sod_halo_mass", "sod_halo_radius"])
                ds = ds.collect()

        The selected data will now be in memory, and the file will be closed.

        If working in an MPI context, all ranks will recieve the same data.
        """
        new_handler = self.__handler.collect(
            self.__state.builder.columns, self.__state.index
        )
        new_index = ChunkedIndex.from_size(len(new_handler))
        new_state = self.__state.with_index(new_index)
        return Dataset(
            new_handler,
            self.__header,
            new_state,
            self.__tree,
        )
