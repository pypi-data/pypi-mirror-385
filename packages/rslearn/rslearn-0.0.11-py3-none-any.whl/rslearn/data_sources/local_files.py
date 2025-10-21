"""Data source for raster or vector data in local files."""

import functools
import json
from collections.abc import Callable
from typing import Any, Generic, TypeVar

import fiona
import shapely
import shapely.geometry
from rasterio.crs import CRS
from upath import UPath

import rslearn.data_sources.utils
from rslearn.config import LayerConfig, LayerType, RasterLayerConfig, VectorLayerConfig
from rslearn.const import SHAPEFILE_AUX_EXTENSIONS
from rslearn.log_utils import get_logger
from rslearn.tile_stores import TileStoreWithLayer
from rslearn.utils.feature import Feature
from rslearn.utils.fsspec import get_upath_local, join_upath, open_rasterio_upath_reader
from rslearn.utils.geometry import Projection, STGeometry, get_global_geometry

from .data_source import DataSource, Item, QueryConfig

logger = get_logger("__name__")
_ImporterT = TypeVar("_ImporterT", bound="Importer")


class _ImporterRegistry(dict[str, type["Importer"]]):
    """Registry for Importer classes."""

    def register(self, name: str) -> Callable[[type[_ImporterT]], type[_ImporterT]]:
        """Decorator to register an importer class."""

        def decorator(cls: type[_ImporterT]) -> type[_ImporterT]:
            self[name] = cls
            return cls

        return decorator


Importers = _ImporterRegistry()


ItemType = TypeVar("ItemType", bound=Item)
LayerConfigType = TypeVar("LayerConfigType", bound=LayerConfig)
ImporterType = TypeVar("ImporterType", bound="Importer")

SOURCE_NAME = "rslearn.data_sources.local_files.LocalFiles"


class Importer(Generic[ItemType, LayerConfigType]):
    """An abstract base class for importing data from local files."""

    def list_items(self, config: LayerConfigType, src_dir: UPath) -> list[ItemType]:
        """Extract a list of Items from the source directory.

        Args:
            config: the configuration of the layer.
            src_dir: the source directory.
        """
        raise NotImplementedError

    def ingest_item(
        self,
        config: LayerConfigType,
        tile_store: TileStoreWithLayer,
        item: ItemType,
        cur_geometries: list[STGeometry],
    ) -> None:
        """Ingest the specified local file item.

        Args:
            config: the configuration of the layer.
            tile_store: the tile store to ingest the data into.
            item: the Item to ingest
            cur_geometries: the geometries where the item is needed.
        """
        raise NotImplementedError


class RasterItemSpec:
    """Representation of configuration that directly specifies the available items."""

    def __init__(
        self,
        fnames: list[UPath],
        bands: list[list[str]] | None = None,
        name: str | None = None,
    ):
        """Create a new RasterItemSpec.

        Args:
            fnames: the list of image files in this item.
            bands: the bands provided by each of the image files.
            name: what the item should be named
        """
        self.fnames = fnames
        self.bands = bands
        self.name = name

    @staticmethod
    def from_config(src_dir: UPath, d: dict[str, Any]) -> "RasterItemSpec":
        """Decode a dict into a RasterItemSpec.

        Args:
            src_dir: the source directory.
            d: the configuration dict.

        Returns:
            the RasterItemSpec.
        """
        kwargs = dict(
            fnames=[join_upath(src_dir, suffix) for suffix in d["fnames"]],
            bands=d["bands"],
        )
        if "name" in d:
            kwargs["name"] = d["name"]
        return RasterItemSpec(**kwargs)

    def serialize(self) -> dict[str, Any]:
        """Serializes the RasterItemSpec to a JSON-encodable dictionary."""
        return {
            "fnames": [str(path) for path in self.fnames],
            "bands": self.bands,
            "name": self.name,
        }

    @staticmethod
    def deserialize(d: dict[str, Any]) -> "RasterItemSpec":
        """Deserializes a RasterItemSpec from a JSON-decoded dictionary."""
        return RasterItemSpec(
            fnames=[UPath(s) for s in d["fnames"]],
            bands=d["bands"],
            name=d["name"],
        )


class RasterItem(Item):
    """An item corresponding to a local file."""

    def __init__(self, name: str, geometry: STGeometry, spec: RasterItemSpec):
        """Creates a new LocalFileItem.

        Args:
            name: unique name of the item
            geometry: the spatial and temporal extent of the item
            spec: the RasterItemSpec that specifies the filename(s) and bands.
        """
        super().__init__(name, geometry)
        self.spec = spec

    def serialize(self) -> dict:
        """Serializes the item to a JSON-encodable dictionary."""
        d = super().serialize()
        d["spec"] = self.spec.serialize()
        return d

    @staticmethod
    def deserialize(d: dict) -> "RasterItem":
        """Deserializes an item from a JSON-decoded dictionary."""
        item = super(RasterItem, RasterItem).deserialize(d)
        spec = RasterItemSpec.deserialize(d["spec"])
        return RasterItem(name=item.name, geometry=item.geometry, spec=spec)


class VectorItem(Item):
    """An item corresponding to a local file."""

    def __init__(self, name: str, geometry: STGeometry, path_uri: str):
        """Creates a new LocalFileItem.

        Args:
            name: unique name of the item
            geometry: the spatial and temporal extent of the item
            path_uri: URI representation of the path of this file
        """
        super().__init__(name, geometry)
        self.path_uri = path_uri

    def serialize(self) -> dict:
        """Serializes the item to a JSON-encodable dictionary."""
        d = super().serialize()
        d["path_uri"] = self.path_uri
        return d

    @staticmethod
    def deserialize(d: dict) -> "VectorItem":
        """Deserializes an item from a JSON-decoded dictionary."""
        item = super(VectorItem, VectorItem).deserialize(d)
        return VectorItem(
            name=item.name, geometry=item.geometry, path_uri=d["path_uri"]
        )


@Importers.register("raster")
class RasterImporter(Importer):
    """An Importer for raster data."""

    def list_items(self, config: LayerConfig, src_dir: UPath) -> list[RasterItem]:
        """Extract a list of Items from the source directory.

        Args:
            config: the configuration of the layer.
            src_dir: the source directory.
        """
        item_specs: list[RasterItemSpec] = []
        # See if user has provided the item specs directly.
        if (
            config.data_source is not None
            and "item_specs" in config.data_source.config_dict
        ):
            for spec_dict in config.data_source.config_dict["item_specs"]:
                spec = RasterItemSpec.from_config(src_dir, spec_dict)
                item_specs.append(spec)
        else:
            # Otherwise we need to list files and assume each one is separate.
            # And we'll need to autodetect the bands later.
            file_paths = src_dir.glob("**/*.*")
            for path in file_paths:
                # Ignore JSON files.
                if path.name.endswith(".json"):
                    continue

                # Ignore temporary files that may be created by open_atomic.
                # The suffix should be like "X.tif.tmp.1234".
                parts = path.name.split(".")
                if len(parts) >= 4 and parts[-2] == "tmp" and parts[-1].isdigit():
                    continue

                spec = RasterItemSpec(fnames=[path], bands=None)
                item_specs.append(spec)

        items = []
        for spec in item_specs:
            # Get geometry from the first raster file.
            # We assume files are readable with rasterio.
            with open_rasterio_upath_reader(spec.fnames[0]) as src:
                crs = src.crs
                left = src.transform.c
                top = src.transform.f
                # Resolutions in projection units per pixel.
                x_resolution = src.transform.a
                y_resolution = src.transform.e
                start = (int(left / x_resolution), int(top / y_resolution))
                shp = shapely.box(
                    start[0], start[1], start[0] + src.width, start[1] + src.height
                )
                projection = Projection(crs, x_resolution, y_resolution)
                geometry = STGeometry(projection, shp, None)

            if geometry.is_too_large():
                geometry = get_global_geometry(time_range=None)
                logger.warning(
                    "Global geometry detected: this geometry will be matched against all "
                    "windows in the rslearn dataset. When using settings like "
                    "max_matches=1 and space_mode=MOSAIC, this may cause windows outside "
                    "the geometry’s valid bounds to be materialized from the global raster "
                    "instead of a more appropriate source. Consider using COMPOSITE mode, "
                    "or increasing max_matches if this behavior is unintended."
                )

            if spec.name:
                item_name = spec.name
            else:
                item_name = spec.fnames[0].name.split(".")[0]

            logger.debug(
                "RasterImporter.list_items: got bounds of %s: %s", item_name, geometry
            )
            items.append(RasterItem(item_name, geometry, spec))

        logger.debug("RasterImporter.list_items: discovered %d items", len(items))
        return items

    def ingest_item(
        self,
        config: RasterLayerConfig,
        tile_store: TileStoreWithLayer,
        item: RasterItem,
        cur_geometries: list[STGeometry],
    ) -> None:
        """Ingest the specified local file item.

        Args:
            config: the configuration of the layer.
            tile_store: the tile store to ingest the data into.
            item: the RasterItem to ingest
            cur_geometries: the geometries where the item is needed.
        """
        for file_idx, fname in enumerate(item.spec.fnames):
            with open_rasterio_upath_reader(fname) as src:
                if item.spec.bands:
                    bands = item.spec.bands[file_idx]
                else:
                    bands = [f"B{band_idx + 1}" for band_idx in range(src.count)]

            if tile_store.is_raster_ready(item.name, bands):
                continue
            tile_store.write_raster_file(item.name, bands, fname)


@Importers.register("vector")
class VectorImporter(Importer):
    """An Importer for vector data."""

    # We need some buffer around GeoJSON bounds in case it just contains one point.
    item_buffer_epsilon = 1e-4

    def list_items(self, config: LayerConfig, src_dir: UPath) -> list[VectorItem]:
        """Extract a list of Items from the source directory.

        Args:
            config: the configuration of the layer.
            src_dir: the source directory.
        """
        file_paths = src_dir.glob("**/*.*")
        items: list[VectorItem] = []

        for path in file_paths:
            # Ignore JSON files.
            if path.name.endswith(".json"):
                continue

            # Get the bounds of the features in the vector file, which we assume fiona can
            # read.
            # For shapefile, to open it we need to copy all the aux files.
            aux_files: list[UPath] = []
            if path.name.endswith(".shp"):
                prefix = ".".join(path.name.split(".")[:-1])
                for ext in SHAPEFILE_AUX_EXTENSIONS:
                    aux_files.append(path.parent / (prefix + ext))

            with get_upath_local(path, extra_paths=aux_files) as local_fname:
                with fiona.open(local_fname) as src:
                    crs = CRS.from_wkt(src.crs.to_wkt())
                    bounds = None
                    for feat in src:
                        shp = shapely.geometry.shape(feat.geometry)
                        cur_bounds = shp.bounds
                        if bounds is None:
                            bounds = list(cur_bounds)
                        else:
                            bounds[0] = min(bounds[0], cur_bounds[0])
                            bounds[1] = min(bounds[1], cur_bounds[1])
                            bounds[2] = max(bounds[2], cur_bounds[2])
                            bounds[3] = max(bounds[3], cur_bounds[3])

                    # Normal GeoJSON should have coordinates in CRS coordinates, i.e. it
                    # should be 1 projection unit/pixel.
                    projection = Projection(crs, 1, 1)
                    geometry = STGeometry(
                        projection,
                        shapely.box(*bounds).buffer(self.item_buffer_epsilon),
                        None,
                    )

                    # There can be problems with GeoJSON files that have large spatial
                    # coverage, since the bounds may not re-project correctly to match
                    # windows that are using projections with limited validity.
                    # We check if there is a large spatial coverage here, and mark the
                    # item's geometry as having global coverage if so.
                    if geometry.is_too_large():
                        geometry = get_global_geometry(time_range=None)

            logger.debug(
                "VectorImporter.list_items: got bounds of %s: %s", path, geometry
            )
            items.append(
                VectorItem(path.name.split(".")[0], geometry, path.absolute().as_uri())
            )

        logger.debug("VectorImporter.list_items: discovered %d items", len(items))
        return items

    def ingest_item(
        self,
        config: VectorLayerConfig,
        tile_store: TileStoreWithLayer,
        item: VectorItem,
        cur_geometries: list[STGeometry],
    ) -> None:
        """Ingest the specified local file item.

        Args:
            config: the configuration of the layer.
            tile_store: the TileStore to ingest the data into.
            item: the Item to ingest
            cur_geometries: the geometries where the item is needed.
        """
        if not isinstance(config, VectorLayerConfig):
            raise ValueError("VectorImporter requires a VectorLayerConfig")

        if tile_store.is_vector_ready(item.name):
            return

        path = UPath(item.path_uri)

        aux_files: list[UPath] = []
        if path.name.split(".")[-1] == "shp":
            prefix = ".".join(path.name.split(".")[:-1])
            for ext in SHAPEFILE_AUX_EXTENSIONS:
                aux_files.append(path.parent / (prefix + ext))

        # TODO: move converting fiona file to list[Feature] to utility function.
        with get_upath_local(path, extra_paths=aux_files) as local_fname:
            with fiona.open(local_fname) as src:
                crs = CRS.from_wkt(src.crs.to_wkt())
                # Normal GeoJSON should have coordinates in CRS coordinates, i.e. it
                # should be 1 projection unit/pixel.
                projection = Projection(crs, 1, 1)

                features = []
                for feat in src:
                    features.append(
                        Feature.from_geojson(
                            projection,
                            {
                                "type": "Feature",
                                "geometry": dict(feat.geometry),
                                "properties": dict(feat.properties),
                            },
                        )
                    )

                tile_store.write_vector(item.name, features)


class LocalFiles(DataSource):
    """A data source for ingesting data from local files."""

    def __init__(
        self,
        config: LayerConfig,
        src_dir: UPath,
    ) -> None:
        """Initialize a new LocalFiles instance.

        Args:
            config: configuration for this layer.
            src_dir: source directory to ingest
        """
        self.config = config

        self.importer = Importers[config.layer_type.value]()
        self.src_dir = src_dir

    @staticmethod
    def from_config(config: LayerConfig, ds_path: UPath) -> "LocalFiles":
        """Creates a new LocalFiles instance from a configuration dictionary."""
        if config.data_source is None:
            raise ValueError("LocalFiles data source requires a data source config")
        d = config.data_source.config_dict
        return LocalFiles(config=config, src_dir=join_upath(ds_path, d["src_dir"]))

    @functools.cache
    def list_items(self) -> list[Item]:
        """Lists items from the source directory while maintaining a cache file."""
        cache_fname = self.src_dir / "summary.json"
        if not cache_fname.exists():
            logger.debug("cache at %s does not exist, listing items", cache_fname)
            items = self.importer.list_items(self.config, self.src_dir)
            serialized_items = [item.serialize() for item in items]
            with cache_fname.open("w") as f:
                json.dump(serialized_items, f)
            return items

        logger.debug("loading item list from cache at %s", cache_fname)
        with cache_fname.open() as f:
            serialized_items = json.load(f)
        return [
            self.deserialize_item(serialized_item)
            for serialized_item in serialized_items
        ]

    def get_items(
        self, geometries: list[STGeometry], query_config: QueryConfig
    ) -> list[list[list[Item]]]:
        """Get a list of items in the data source intersecting the given geometries.

        Args:
            geometries: the spatiotemporal geometries
            query_config: the query configuration

        Returns:
            List of groups of items that should be retrieved for each geometry.
        """
        groups = []
        for geometry in geometries:
            cur_items = []
            for item in self.list_items():
                if not item.geometry.intersects(geometry):
                    continue
                cur_items.append(item)

            cur_groups = rslearn.data_sources.utils.match_candidate_items_to_window(
                geometry, cur_items, query_config
            )
            groups.append(cur_groups)
        return groups

    def deserialize_item(self, serialized_item: Any) -> RasterItem | VectorItem:
        """Deserializes an item from JSON-decoded data."""
        if self.config.layer_type == LayerType.RASTER:
            return RasterItem.deserialize(serialized_item)
        elif self.config.layer_type == LayerType.VECTOR:
            return VectorItem.deserialize(serialized_item)
        else:
            raise ValueError(f"Unknown layer type: {self.config.layer_type}")

    def ingest(
        self,
        tile_store: TileStoreWithLayer,
        items: list[Item],
        geometries: list[list[STGeometry]],
    ) -> None:
        """Ingest items into the given tile store.

        Args:
            tile_store: the tile store to ingest into
            items: the items to ingest
            geometries: a list of geometries needed for each item
        """
        for item, cur_geometries in zip(items, geometries):
            self.importer.ingest_item(self.config, tile_store, item, cur_geometries)
