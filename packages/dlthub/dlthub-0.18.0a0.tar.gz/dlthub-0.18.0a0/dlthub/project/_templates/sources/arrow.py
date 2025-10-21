"""The Arrow Source Template will show how to load arrow tables."""

from typing import Iterator

import random

import dlt

from dlt.sources import DltResource, TDataItems

names = ["tom", "jerry", "bob", "alice", "john", "jane", "jim", "jill", "jack", "jenny"]


def create_example_arrow_table(row_count: int) -> Iterator[TDataItems]:
    import pyarrow as pa  # type: ignore[import-untyped]

    # NOTE: we could directly yield the pylist here, we just demonstrate that arrow tables also work
    pylist = [
        {"id": i, "name": random.choice(names), "age": random.randint(18, 65)}
        for i in range(row_count)
    ]
    yield pa.Table.from_pylist(pylist)


@dlt.source
def source(row_count: int = dlt.config.value, some_secret: int = dlt.secrets.value) -> DltResource:
    """Example arrow source"""

    # if no row count is provided or row_count is 0, use default value
    if not row_count:
        row_count = 100

    @dlt.resource(
        primary_key="id",
    )
    def items() -> Iterator[TDataItems]:
        yield from create_example_arrow_table(row_count)

    return items
