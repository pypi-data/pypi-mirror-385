"""large-image utilities."""

import os
import pathlib
import tempfile
from typing import List, Optional, Tuple, Union

import large_image
from large_image.constants import TileOutputMimeTypes
from large_image.tilesource import FileTileSource
from rest_framework.exceptions import ValidationError

from django_large_image import utilities

SHORTENED_FORMATS = {
    'JPG': 'JPEG',
    'JP2': 'JPEG2000',
    'TIF': 'TIFF',
}


def get_tilesource_from_path(
    path: str,
    projection: Optional[str] = None,
    style: Optional[str] = None,
    encoding: Optional[str] = None,
    source: Optional[str] = None,
) -> FileTileSource:
    if not encoding:
        encoding = 'PNG'
    if source:
        large_image.tilesource.loadTileSources()
        sources = large_image.tilesource.AvailableTileSources
        try:
            reader = sources[source]
        except KeyError:
            raise ValidationError(
                f'{source!r} is not a valid source. Try one of: {list(sources.keys())}'
            )
    else:
        reader = large_image.open
    return reader(str(path), projection=projection, style=style, encoding=encoding)


def is_geospatial(source: FileTileSource) -> bool:
    return source.getMetadata().get('geospatial', False)


def get_bounds(
    source: FileTileSource,
    projection: str = 'EPSG:4326',
) -> Optional[List[float]]:
    bounds = source.getBounds(srs=projection)
    if not bounds:
        return None
    threshold = 89.9999
    for key in ('ymin', 'ymax'):
        bounds[key] = max(min(bounds[key], threshold), -threshold)
    return bounds


def _metadata_helper(source: FileTileSource, metadata: dict):
    metadata.setdefault('geospatial', is_geospatial(source))
    if metadata.get('projection'):
        metadata['projection'] = str(metadata['projection'])
    if metadata['geospatial']:
        metadata['bounds'] = get_bounds(source)
        # metadata['proj4'] = (source.getProj4String(),)  # not supported by rasterio
    if 'frames' not in metadata:
        metadata['frames'] = False


def get_metadata(source: FileTileSource) -> dict:
    metadata = source.getMetadata()
    _metadata_helper(source, metadata)
    return metadata


def get_metadata_internal(source: FileTileSource) -> dict:
    metadata = source.getInternalMetadata()
    _metadata_helper(source, metadata)
    return metadata


def _get_region(source: FileTileSource, region: dict, encoding: str) -> Tuple[pathlib.Path, str]:
    result, mime_type = source.getRegion(region=region, encoding=encoding)
    if encoding == 'TILED':
        path = result
    else:
        # Write content to temporary file
        fd, path = tempfile.mkstemp(
            suffix=f'.{encoding}', prefix='pixelRegion_', dir=str(utilities.get_cache_dir())
        )
        os.close(fd)
        path = pathlib.Path(path)
        with open(path, 'wb') as f:
            f.write(result)
    return path, mime_type


def get_region(
    source: FileTileSource,
    left: Union[float, int],
    right: Union[float, int],
    bottom: Union[float, int],
    top: Union[float, int],
    units: str = None,
    encoding: str = None,
) -> Tuple[pathlib.Path, str]:
    if isinstance(units, str):
        units = units.lower()
    if not encoding and is_geospatial(source):
        # Use tiled encoding by default for geospatial rasters
        #   output will be a tiled TIF
        encoding = 'TILED'
    elif not encoding:
        # Use JPEG encoding by default for nongeospatial rasters
        encoding = 'JPEG'
    if is_geospatial(source) and units not in [
        'pixels',
        'pixel',
    ]:
        if not units:
            units = 'EPSG:4326'
        region = dict(left=left, right=right, bottom=bottom, top=top, units=units)
        return _get_region(source, region, encoding)
    units = 'pixels'
    left, right = min(left, right), max(left, right)
    top, bottom = min(top, bottom), max(top, bottom)
    region = dict(left=left, right=right, bottom=bottom, top=top, units=units)
    return _get_region(source, region, encoding)


def get_formats(return_dict: bool = False):
    def keys(d):
        return [s.lower() for s in d.keys()]

    shortened = {
        k: TileOutputMimeTypes[v] for k, v in SHORTENED_FORMATS.items() if v in TileOutputMimeTypes
    }
    if return_dict:
        to_return = shortened.copy()
        to_return.update(TileOutputMimeTypes)
        return to_return
    return keys(TileOutputMimeTypes) + keys(shortened)


def format_to_encoding(format: Optional[str], pil_safe: Optional[bool] = False) -> str:
    """Translate format extension (e.g., `tiff`) to encoding (e.g., `TILED`)."""
    if not format:
        return 'PNG'
    if format.lower() in ['tif', 'tiff']:
        format = 'TILED'
    if format.lower() not in get_formats():
        raise ValidationError(f'Format {format!r} is not valid. Try on of: {get_formats()}')
    if format.upper() in SHORTENED_FORMATS:
        format = SHORTENED_FORMATS[format.upper()]
    if pil_safe and format.upper() == 'TILED':
        return 'TIFF'
    return format.upper()


def get_mime_type(format: str):
    if format.upper() in SHORTENED_FORMATS:
        format = SHORTENED_FORMATS[format.upper()]
    if format.lower() not in get_formats():
        raise ValidationError(f'Format {format!r} is not valid. Try on of: {get_formats()}')
    return TileOutputMimeTypes[format.upper()]


def get_frames(source: FileTileSource):
    """Return lists of channels/bands per frame index.

    Example Data
    ------------

    { frames: [
        { frame: 'Frame 1', bands: [
            {'index': 1, 'frame': 0, 'name': 'red'},
            {'index': 2, 'frame': 0, 'name': 'green'},
            {'index': 3, 'frame': 0, 'name': 'blue'},
        ]}
    ]}

    { frames: [
        { frame: 'Frame 1', bands: [{'index': 1, 'frame': 0, 'name': 'NUCLEI'}, ...]},
        { frame: 'Frame 2', bands: [{'index': 1, 'frame': 1, 'name': 'CD4'}, ...] },
        ...
    ]}


    """
    frame_data = source.getMetadata().get('frames', [])
    if not frame_data:
        # Single frame image
        bands = source.getBandInformation()
        frame = {
            'frame': 'Frame null',
            'bands': [
                {'index': k, 'frame': None, 'name': v.get('interpretation', '')}
                for k, v in bands.items()
            ],
        }
        frames = [frame]
    else:
        frames = {}
        for channel in frame_data:
            fid = channel['Frame']
            frames.setdefault(fid, [])
            frames[fid].append(
                {
                    'index': channel['Index'],
                    'frame': fid,
                    'name': channel.get('Name', ''),
                }
            )
        frames = [{'frame': f'Frame {i}', 'bands': v} for i, v in frames.items()]
    return {'frames': frames}
