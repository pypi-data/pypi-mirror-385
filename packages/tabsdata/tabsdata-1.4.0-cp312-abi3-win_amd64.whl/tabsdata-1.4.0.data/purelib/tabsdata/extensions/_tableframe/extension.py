#
#  Copyright 2024 Tabs Data Inc.
#

import logging
import uuid
from enum import Enum
from typing import Any, Type

import polars as pl

# noinspection PyProtectedMember
import tabsdata._utils.tableframe._constants as td_constants

# noinspection PyProtectedMember
from tabsdata.extensions._features.api.features import Feature, FeaturesManager
from tabsdata.extensions._tableframe.api.api import Extension
from tabsdata.extensions._tableframe.provenance import (
    decode_src,
    encode_src,
)
from tabsdata.extensions._tableframe.version import version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _row_default() -> pl.Expr:
    return pl.lit(0, pl.UInt64)


class SrcGenerator:
    def __init__(
        self,
        tab: int | None = None,
    ):
        self._temp_column = f"__tmp_{uuid.uuid4().hex}"
        self._tab = tab
        self._row = 0

    @property
    def temp_column(self):
        return self._temp_column

    @property
    def tab(self):
        return self._tab

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value: int) -> None:
        self._row = value

    def python(
        self,
        batch: pl.DataFrame | pl.Series,
    ) -> pl.DataFrame | pl.Series:
        n = batch.len() if isinstance(batch, pl.Series) else batch.height

        if n == 0:
            empty = pl.Series(
                self.temp_column, [[] for _ in range(n)], dtype=pl.List(pl.Binary)
            )
            if isinstance(batch, pl.Series):
                return empty
            return batch.with_columns(empty)

        if self.tab is None:
            empty = pl.Series(
                self.temp_column, [[] for _ in range(n)], dtype=pl.List(pl.Binary)
            )
            if isinstance(batch, pl.Series):
                return empty
            return batch.with_columns(empty)

        rows = range(self.row, self.row + n)
        column = [
            [
                encode_src(
                    ver=None,
                    op=td_constants.RowOperation.ROW.value,
                    tab=self.tab,
                    par=None,
                    row=row,
                )
            ]
            for row in rows
        ]
        self.row += n
        output = pl.Series(self.temp_column, column, dtype=pl.List(pl.Binary))

        if isinstance(batch, pl.Series):
            return output
        return batch.with_columns(output)


def _src_default() -> pl.Expr:
    return pl.lit([], pl.List(pl.Binary))


class SrcAggregator:
    def __init__(
        self,
        column: str,
        state: td_constants.RowOperation | None = None,
    ):
        self.temp_column = f"__tmp_{uuid.uuid4().hex}"
        self.column = column
        if state is None:
            self.state = td_constants.RowOperation.UNDEFINED
        else:
            self.state = state

    # flake8: noqa: C901
    def python(  # noqa: C901
        self,
        batch: pl.DataFrame | pl.Series,
    ) -> pl.DataFrame | pl.Series | list[pl.Binary]:
        n = batch.len() if isinstance(batch, pl.Series) else batch.height

        if n == 0:
            if isinstance(batch, pl.Series):
                empty = []
                return empty
            empty = pl.Series(self.temp_column, [[]], dtype=pl.List(pl.Binary))
            return batch.with_columns(empty)

        if isinstance(batch, pl.Series):
            series = batch
        else:
            series = batch[self.column]

        seen = set()
        for bytes_array_list in series:
            if bytes_array_list is None:
                continue
            if isinstance(bytes_array_list, (bytes, bytearray)):
                bytes_array_iterator = [bytes_array_list]
            else:
                bytes_array_iterator = []
                for bytes_array_item in bytes_array_list:
                    if isinstance(bytes_array_item, list):
                        bytes_array_iterator.extend(bytes_array_item)
                    else:
                        bytes_array_iterator.append(bytes_array_item)
            if bytes_array_iterator is None:
                continue
            for bytes_array in bytes_array_iterator:
                _, _, op, tab, _, _ = decode_src(bytes_array)
                if op != td_constants.RowOperation.ROW.value:
                    seen.add(bytes_array)
                group_bytes_array = encode_src(
                    ver=None,
                    op=self.state.value,
                    tab=tab,
                    par=None,
                    row=None,
                )
                seen.add(group_bytes_array)
        output = sorted(seen)

        if isinstance(batch, pl.Series):
            return output
        else:
            output = pl.Series(self.temp_column, [output], dtype=pl.List(pl.Binary))
            return batch.with_columns(output)


class ExtendedSystemColumns(Enum):
    TD_ROWINDEX = "$td.row"
    TD_PROVENANCE = "$td.src"


class ExtendedSystemColumnsMetadata(Enum):
    TD_ROWINDEX = td_constants.SystemColumn(
        dtype=pl.UInt64,
        default=_row_default,
        language=td_constants.Language.RUST,
        generator=pl.LazyFrame.with_row_index.__name__,
        inception=td_constants.Inception.REGENERATE,
        aggregation=None,
    )
    TD_PROVENANCE = td_constants.SystemColumn(
        dtype=pl.List(pl.Binary),
        default=_src_default,
        language=td_constants.Language.PYTHON,
        generator=SrcGenerator,
        inception=td_constants.Inception.PROPAGATE,
        aggregation=SrcAggregator,
    )


class SystemColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_ROWINDEX = ExtendedSystemColumns.TD_ROWINDEX.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


class RequiredColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_ROWINDEX = ExtendedSystemColumns.TD_ROWINDEX.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


_s_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_s_row_metadata = ExtendedSystemColumnsMetadata.TD_ROWINDEX.value
_s_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

SYSTEM_COLUMNS_METADATA = {
    SystemColumns.TD_IDENTIFIER.value: _s_id_metadata,
    SystemColumns.TD_ROWINDEX.value: _s_row_metadata,
    SystemColumns.TD_PROVENANCE.value: _s_src_metadata,
}

_r_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_r_row_metadata = ExtendedSystemColumnsMetadata.TD_ROWINDEX.value
_r_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

REQUIRED_COLUMNS_METADATA = {
    RequiredColumns.TD_IDENTIFIER.value: _r_id_metadata,
    RequiredColumns.TD_ROWINDEX.value: _r_row_metadata,
    RequiredColumns.TD_PROVENANCE.value: _r_src_metadata,
}


def system_columns() -> list[str]:
    return [member.value for member in SystemColumns]


class TableFrameExtension(Extension):
    name = "TableFrame Extension (Enterprise)"
    version = version()

    def __init__(self) -> None:
        FeaturesManager.instance().enable(Feature.ENTERPRISE)
        logger.debug(
            f"Single instance of {Extension.__name__}: {TableFrameExtension.name} -"
            f" {TableFrameExtension.version}"
        )

    @classmethod
    def instance(cls) -> "TableFrameExtension":
        return instance

    @property
    def summary(self) -> str:
        return "Enterprise"

    @property
    def standard_system_columns(self) -> Type[Enum]:
        return td_constants.StandardSystemColumns

    @property
    def extended_system_columns(self) -> Type[Enum]:
        return ExtendedSystemColumns

    @property
    def system_columns(self) -> Type[Enum]:
        return SystemColumns

    @property
    def system_columns_metadata(self) -> dict[str, td_constants.SystemColumn]:
        return SYSTEM_COLUMNS_METADATA

    @property
    def required_columns(self) -> Type[Enum]:
        return RequiredColumns

    @property
    def required_columns_metadata(self) -> dict[str, td_constants.SystemColumn]:
        return REQUIRED_COLUMNS_METADATA

    def apply_system_column(
        self,
        lf: pl.LazyFrame,
        column: str,
        function: Any,
    ) -> pl.LazyFrame:
        if function == pl.LazyFrame.with_row_index.__name__:
            if column in lf.collect_schema().names():
                lf = lf.drop(column)
            lf = lf.with_row_index(name=column, offset=0).with_columns(
                pl.col(column).cast(pl.UInt64)
            )
            return lf
        else:
            raise ValueError(
                f"Invalid function to generate a new system column: {function}"
            )

    # It does the same as the standard implementation. Additionally, it merges all
    # provenance into a single one with a list of provenance values from all merged
    # columns.
    def assemble_system_columns(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        src_cols = [
            c
            for c in lf.collect_schema().names()
            if c.startswith(ExtendedSystemColumns.TD_PROVENANCE.value)
        ]
        lf = lf.with_columns(
            pl.concat_list([pl.col(c) for c in src_cols])
            .list.unique()
            .list.sort()
            .alias(ExtendedSystemColumns.TD_PROVENANCE.value)
        )
        target_cols = [
            c
            for c in lf.collect_schema().names()
            if c in system_columns() or not c.startswith(td_constants.TD_COLUMN_PREFIX)
        ]
        lf = lf.select(target_cols)
        return lf


instance = TableFrameExtension()
