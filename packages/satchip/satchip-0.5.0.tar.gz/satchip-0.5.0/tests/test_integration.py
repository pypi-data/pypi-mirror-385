from datetime import datetime
from pathlib import Path

import pytest
from osgeo import gdal

from satchip.chip_data import create_chips
from satchip.chip_label import chip_labels


gdal.UseExceptions()


def create_dataset(outpath: Path, start: tuple[int, int]) -> Path:
    x, y = start
    pixel_size = 10
    cols, rows = 512, 512
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(str(outpath), cols, rows, 1, gdal.GDT_UInt16)
    dataset.SetGeoTransform((x, pixel_size, 0, y, 0, -pixel_size))
    dataset.SetProjection('EPSG:32611')
    array = dataset.GetRasterBand(1).ReadAsArray()
    array[:, :] = 0
    array[128:384, 128:384] = 1
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()
    dataset = None
    return outpath


def create_label_and_data(label_tif, out_dir, image_dir):
    chip_labels(label_tif, datetime.fromisoformat('20240115'), out_dir)
    for platform in ['S2L2A', 'HLS', 'S1RTC']:
        create_chips(
            list((out_dir / 'LABEL').glob('*.zarr.zip')),
            platform,
            datetime.fromisoformat('20240101'),
            datetime.fromisoformat('20240215'),
            'BEST',
            20,
            out_dir,
            image_dir,
        )


@pytest.mark.integration
def test_integration():
    data_dir = Path('integration_test')
    train_dir = data_dir / 'train'
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir = data_dir / 'val'
    val_dir.mkdir(parents=True, exist_ok=True)
    image_dir = data_dir / 'images'
    image_dir.mkdir(parents=True, exist_ok=True)

    train_tif = create_dataset(data_dir / 'train.tif', (431795, 3943142))
    create_label_and_data(train_tif, train_dir, image_dir)
    val_tif = create_dataset(data_dir / 'val.tif', (431795, 3943142 - 10 * 512))
    create_label_and_data(val_tif, val_dir, image_dir)
