# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2024 OWS Contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections.abc import Iterable
from threading import Lock
from typing import Any
from uuid import UUID

import click
from antimeridian import fix_shape
from datacube import Datacube
from datacube.model import Dataset, Product, Range
from odc.geo import CRS, Geometry
from sqlalchemy import text
from typing_extensions import override

from datacube_ows.index.api import (
    LayerExtent,
    LayerSignature,
    OWSAbstractIndex,
    OWSAbstractIndexDriver,
    TimeSearchTerm,
)
from datacube_ows.index.sql import run_sql
from datacube_ows.ows_configuration import OWSNamedLayer

from ...utils import default_to_utc
from .product_ranges import create_range_entry as create_range_entry_impl
from .product_ranges import get_ranges as get_ranges_impl


class OWSPostgisIndex(OWSAbstractIndex):
    name: str = "postgis"

    # method to check database access (for ping op)
    @override
    def check_db_access(self, dc: Datacube) -> bool:
        db_ok = False
        try:
            with dc.index._db._give_me_a_connection() as conn:  # type: ignore[attr-defined]
                results = conn.execute(
                    text("""
                    SELECT *
                    FROM ows.layer_ranges
                    LIMIT 1""")
                )
                for _ in results:
                    db_ok = True
        except Exception:
            pass
        return db_ok

    # method to delete obsolete schemas etc.
    @override
    def cleanup_schema(self, dc: Datacube) -> None:
        # No obsolete schema for postgis databases to clean up.
        pass

    # Schema creation method
    @override
    def create_schema(self, dc: Datacube) -> None:
        click.echo("Creating/updating schema and tables...")
        self._run_sql(dc, "ows_schema/create")

    # Permission management method
    @override
    def grant_perms(self, dc: Datacube, role: str, read_only: bool = False) -> None:
        if read_only:
            self._run_sql(dc, "ows_schema/grants/read_only", role=role)
        else:
            self._run_sql(dc, "ows_schema/grants/read_write", role=role)

    # Spatiotemporal index update method (e.g. refresh materialised views)
    @override
    def update_geotemporal_index(self, dc: Datacube) -> None:
        # Native ODC geotemporal index used in postgis driver.
        pass

    @override
    def create_range_entry(
        self, layer: OWSNamedLayer, cache: dict[LayerSignature, list[str]]
    ) -> None:
        create_range_entry_impl(layer, cache)

    @override
    def get_ranges(self, layer: OWSNamedLayer) -> LayerExtent | None:
        return get_ranges_impl(layer)

    def _query(
        self,
        layer: OWSNamedLayer,
        times: Iterable[TimeSearchTerm] | None = None,
        geom: Geometry | None = None,
        products: Iterable[Product] | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if geom:
            if geom.crs and geom.crs in layer.dc.index.spatial_indexes():
                query["geopolygon"] = geom
            else:
                # Default to 4326 and take a long hard look at yourself.
                prepared_geom = self._prep_geom(layer, geom)
                assert prepared_geom is not None
                geopoly = prepared_geom.to_crs("epsg:4326")
                geopoly = Geometry(fix_shape(geopoly.geom), crs="epsg:4326")
                query["geopolygon"] = geopoly
        if products is not None:
            query["product"] = [p.name for p in products]
        if times is not None:

            def normalise_to_dtr(
                unnorm: datetime.datetime | datetime.date,
            ) -> tuple[datetime.datetime, datetime.datetime]:
                if isinstance(unnorm, datetime.datetime):
                    st: datetime.datetime = default_to_utc(unnorm)
                    tmax = st + datetime.timedelta(seconds=1)
                elif isinstance(t, datetime.date):
                    st = datetime.datetime(
                        unnorm.year,
                        unnorm.month,
                        unnorm.day,
                        tzinfo=datetime.timezone.utc,
                    )
                    tmax = st + datetime.timedelta(days=1)
                else:
                    raise ValueError("Not a datetime object")
                return st, tmax

            time_args = []
            for t in times:
                if isinstance(t, datetime.date | datetime.datetime):
                    start, tmax = normalise_to_dtr(t)
                    time_args.append(Range(start, tmax))
                else:
                    st, et = t
                    st, _ = normalise_to_dtr(st)
                    et, _ = normalise_to_dtr(et)
                    time_args.append(Range(st, et))
            if len(time_args) > 1:
                raise ValueError("Huh?")
            query["time"] = time_args[0]
        return query

    @override
    def ds_search(
        self,
        layer: OWSNamedLayer,
        times: Iterable[TimeSearchTerm] | None = None,
        geom: Geometry | None = None,
        products: Iterable[Product] | None = None,
    ) -> Iterable[Dataset]:
        return layer.dc.index.datasets.search(
            **self._query(layer, times, geom, products)
        )

    @override
    def dsid_search(
        self,
        layer: OWSNamedLayer,
        times: Iterable[TimeSearchTerm] | None = None,
        geom: Geometry | None = None,
        products: Iterable[Product] | None = None,
    ) -> Iterable[UUID]:
        for ds in layer.dc.index.datasets.search_returning(
            field_names=["id"], **self._query(layer, times, geom, products)
        ):
            yield ds.id  # type: ignore[attr-defined]

    @override
    def count(
        self,
        layer: OWSNamedLayer,
        times: Iterable[TimeSearchTerm] | None = None,
        geom: Geometry | None = None,
        products: Iterable[Product] | None = None,
    ) -> int:
        return layer.dc.index.datasets.count(
            **self._query(layer, times, geom, products)
        )

    @override
    def extent(
        self,
        layer: OWSNamedLayer,
        times: Iterable[TimeSearchTerm] | None = None,
        geom: Geometry | None = None,
        products: Iterable[Product] | None = None,
        crs: CRS | None = None,
    ) -> Geometry | None:
        if crs is None:
            crs = CRS("epsg:4326")
        return layer.dc.index.datasets.spatial_extent(
            self.dsid_search(layer, times=times, geom=geom, products=products), crs=crs
        )

    def _run_sql(self, dc: Datacube, path: str, **params: str) -> bool:
        return run_sql(dc, self.name, path, **params)


pgisdriverlock = Lock()


class OWSPostgisIndexDriver(OWSAbstractIndexDriver):
    _driver = None

    @classmethod
    @override
    def ows_index_class(cls) -> type[OWSAbstractIndex]:
        return OWSPostgisIndex

    @classmethod
    @override
    def ows_index(cls) -> OWSAbstractIndex:
        with pgisdriverlock:
            if cls._driver is None:
                cls._driver = OWSPostgisIndex()
        return cls._driver


def ows_index_driver_init() -> OWSPostgisIndexDriver:
    return OWSPostgisIndexDriver()
