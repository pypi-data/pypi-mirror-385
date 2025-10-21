from __future__ import annotations

from itertools import count
from typing import Sequence
from uuid import uuid1

import h5py
import numpy as np

try:
    from mpi4py import MPI
except ImportError:
    MPI = None  # type: ignore

from opencosmo.index import ChunkedIndex, DataIndex, SimpleIndex
from opencosmo.io.schemas import SpatialIndexLevelSchema, SpatialIndexSchema
from opencosmo.spatial.healpix import HealPixIndex
from opencosmo.spatial.octree import OctTreeIndex
from opencosmo.spatial.protocols import Region, SpatialIndex, TreePartition
from opencosmo.spatial.utils import combine_upwards


def open_tree(file: h5py.File | h5py.Group, box_size: int, is_lightcone: bool = False):
    """
    Read a tree from an HDF5 file and the associated
    header. The tree is just a mapping between a spatial
    index and a slice into the data.

    Note: The max level in the header may not actually match
    the max level in the file. When a large dataset is filtered down,
    we may reduce the tree level to save space in the output file.

    The max level in the header is the maximum level in the full
    dataset, so this is the HIGHEST it can be.
    """
    try:
        group = file["index"]
    except KeyError:
        raise ValueError("This file does not have a spatial index!")

    if is_lightcone:
        spatial_index = HealPixIndex()
    else:
        spatial_index = OctTreeIndex.from_box_size(box_size)
    return Tree(spatial_index, group)


def read_tree(file: h5py.File | h5py.Group, box_size: int):
    try:
        group = file["index"]
    except KeyError:
        raise ValueError("This file does not have a spatial index!")

    f = h5py.File(f"{uuid1()}.hdf5", "w", driver="core", backing_store=False)
    for ds in group.keys():
        group.copy(ds, f)
    spatial_index = OctTreeIndex.from_box_size(box_size)
    return Tree(spatial_index, f)


def apply_range_mask(
    mask: np.ndarray,
    range_: tuple[int, int],
    starts: dict[int, np.ndarray],
    sizes: dict[int, np.ndarray],
) -> dict[int, tuple[int, np.ndarray]]:
    """
    Given an index range, apply a mask of the same size to produces new sizes.
    """
    output_sizes = {}

    for level, st in starts.items():
        ends = st + sizes[level]
        # Not in range if the end is less than start, or the start is greater than end
        overlaps_mask = ~((st > range_[1]) | (ends < range_[0]))
        # The first start may be less thank the range start so
        first_start_index = int(np.argmax(overlaps_mask))
        st = st[overlaps_mask]
        st[0] = range_[0]
        st = st - range_[0]
        # Determine how many true values are in the mask in the ranges
        new_sizes = np.add.reduceat(mask, st)
        output_sizes[level] = (first_start_index, new_sizes)
    return output_sizes


def pack_masked_ranges(
    old_starts: dict[int, np.ndarray],
    new_sizes: list[dict[int, tuple[int, np.ndarray]]],
    min_level_size: int = 500,
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    """
    Given a list of masked ranges, pack them into a new set of sizes.
    This is used when working with MPI, and allows us to avoid sending
    very large masks between ranks.

    For queries that return a small fraction of the data, we can end up
    writing a lot of zeros in the lower levels of the tree. So we can
    dynamically choose to stop writing levels when the average size of
    the level is below a certain threshold
    """
    output_starts = {}
    output_sizes = {}
    for level in new_sizes[0]:
        new_level_sizes = np.zeros_like(old_starts[level])
        new_start_info = [rm[level] for rm in new_sizes]
        for first_idx, sizes in new_start_info:
            new_level_sizes[first_idx : first_idx + len(sizes)] += sizes

        avg_size = np.mean(new_level_sizes[new_level_sizes > 0])
        if avg_size < min_level_size:
            break
        output_sizes[level] = new_level_sizes
        output_starts[level] = np.cumsum(np.insert(new_level_sizes, 0, 0))[:-1]

    return output_starts, output_sizes


def partition_index(n_partitions: int, counts: h5py.Group):
    levels = [int(key.split("_")[1]) for key in counts.keys()]
    lowest_level = min(levels)
    highest_level = max(levels)
    split_level = -1
    for level in range(lowest_level, highest_level + 1):
        level_counts = counts[f"level_{level}"]["size"][:]
        full_region_indices = np.where(level_counts > 0)[0]
        n_full = len(full_region_indices)
        if n_full < n_partitions:
            continue
        elif n_full % n_partitions == 0:
            split_level = level
            break

    if split_level == -1:
        split_level = highest_level

    split_level_indices = full_region_indices

    partition_indices = np.array_split(split_level_indices, n_partitions)
    return [SimpleIndex(idx) for idx in partition_indices], split_level


class Tree:
    """
    The Tree handles the spatial indexing of the data. As of right now, it's only
    functionality is to read and write the spatial index. Later we will add actual
    spatial queries
    """

    def __init__(self, index: SpatialIndex, data: h5py.File | h5py.Group):
        self.__index = index
        self.__data = data
        for i in count():
            try:
                _ = self.__data[f"level_{i}"]["start"]
                _ = self.__data[f"level_{i}"]["size"]
            except KeyError:
                self.__max_level = i - 1
                break

        if self.__max_level == -1:
            raise ValueError("Tried to read a tree but no levels were found!")

    def partition(
        self, n_partitions: int, counts: h5py.Group
    ) -> Sequence[TreePartition]:
        """
        Partition into n trees, where each tree contains an equally sized
        region of space.

        This function is used primarily in an MPI context.
        """
        partition_indices, split_level = partition_index(n_partitions, counts)
        partitions = []
        start = self.__data[f"level_{split_level}"]["start"]
        size = self.__data[f"level_{split_level}"]["size"]
        for index_ in partition_indices:
            if len(index_) == 0:
                continue
            index_starts = index_.get_data(start)
            index_sizes = index_.get_data(size)
            partition_start = index_starts[0]
            partition_size = np.sum(index_sizes)
            idx = ChunkedIndex.single_chunk(partition_start, partition_size)
            region = self.__index.get_partition_region(index_, split_level)
            partitions.append(TreePartition(idx, region, split_level))

        return partitions

    def query(self, region: Region) -> tuple[ChunkedIndex, ChunkedIndex]:
        indices = self.__index.query(region, self.__max_level)

        contains = [ChunkedIndex.empty()]
        intersects = [ChunkedIndex.empty()]
        for level, (cidx, iidx) in indices.items():
            level_key = f"level_{level}"
            level_starts = self.__data[level_key]["start"]
            level_sizes = self.__data[level_key]["size"]
            c_starts = cidx.get_data(level_starts)
            c_sizes = cidx.get_data(level_sizes)
            i_starts = iidx.get_data(level_starts)
            i_sizes = iidx.get_data(level_sizes)
            c_idx = ChunkedIndex(c_starts, c_sizes)
            i_idx = ChunkedIndex(i_starts, i_sizes)
            contains.append(c_idx)
            intersects.append(i_idx)

        c_ = contains[0].concatenate(*contains[1:])
        i_ = intersects[0].concatenate(*intersects[1:])
        return c_, i_

    def apply_index(self, index: DataIndex, min_counts: int = 100) -> Tree:
        max_level_starts = self.__data[f"level_{self.__max_level}"]["start"][:]
        max_level_sizes = self.__data[f"level_{self.__max_level}"]["size"][:]
        n_in_range = index.n_in_range(max_level_starts, max_level_sizes)
        target = h5py.File(f"{uuid1()}.hdf5", "w", driver="core", backing_store=False)
        result = combine_upwards(
            n_in_range, self.__index.subdivision_factor, self.__max_level, target
        )
        return Tree(self.__index, result)

    def make_schema(self):
        schema = SpatialIndexSchema()
        for level in range(self.__max_level + 1):
            level_schema = SpatialIndexLevelSchema.from_source(
                self.__data[f"level_{level}"]
            )
            schema.add_child(level_schema, level)
        return schema
