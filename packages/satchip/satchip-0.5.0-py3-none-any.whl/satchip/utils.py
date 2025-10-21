import datetime
import warnings
from pathlib import Path
from typing import TypedDict

import xarray as xr
import zarr
from pyproj import CRS, Transformer


class RtcImageSet(TypedDict):
    VV: Path
    VH: Path


class ChipDataRequiredOpts(TypedDict):
    strategy: str
    date_start: datetime.datetime
    date_end: datetime.datetime


class ChipDataOpts(ChipDataRequiredOpts, total=False):
    max_cloud_pct: int
    local_hyp3_paths: dict[str, list[RtcImageSet]]


def get_overall_bounds(bounds: list) -> list:
    minx = min([b[0] for b in bounds])
    miny = min([b[1] for b in bounds])
    maxx = max([b[2] for b in bounds])
    maxy = max([b[3] for b in bounds])
    return [minx, miny, maxx, maxy]


def get_epsg4326_point(x: float, y: float, in_epsg: int) -> tuple[float, float]:
    if in_epsg == 4326:
        return x, y
    in_crs = CRS.from_epsg(in_epsg)
    out_crs = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(in_crs, out_crs, always_xy=True)
    newx, newy = transformer.transform(x, y)
    return round(newx, 5), round(newy, 5)


def get_epsg4326_bbox(
    bounds: tuple[float, float, float, float], in_epsg: int, buffer: float = 0.1
) -> tuple[float, float, float, float]:
    minx, miny = get_epsg4326_point(bounds[0], bounds[1], in_epsg)
    maxx, maxy = get_epsg4326_point(bounds[2], bounds[3], in_epsg)
    bbox = minx - buffer, miny - buffer, maxx + buffer, maxy + buffer
    return bbox


def save_chip(dataset: xr.Dataset, save_path: str | Path) -> None:
    """Save a zipped zarr archive"""
    store = zarr.storage.ZipStore(save_path, mode='w')  # type: ignore
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Duplicate name:', module='zipfile')
        dataset.to_zarr(store)
    store.close()


def load_chip(label_path: str | Path) -> xr.Dataset:
    """Load a zipped zarr archive"""
    store = zarr.storage.ZipStore(label_path, read_only=True)  # type: ignore
    dataset = xr.open_zarr(store)
    return dataset
