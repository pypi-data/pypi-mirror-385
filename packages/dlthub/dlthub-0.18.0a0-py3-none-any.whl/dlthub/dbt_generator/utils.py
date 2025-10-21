from typing import Sequence, Dict, cast, List, Optional

from pydantic import BaseModel

from dlt.common.schema.typing import TSchemaTables
from dlt.common.schema.utils import (
    get_first_column_name_with_prop,
    get_columns_names_with_prop,
)

from dlt import Pipeline, Schema
from dlt.common import logger
from dlt.pipeline.pipeline import with_schemas_sync

from dlthub.dbt_generator.types import TableReference
from dlthub.dbt_generator.exceptions import (
    InvalidTableReferenceMissingReferencedTable,
    InvalidTableReferenceMissingReferencingTable,
    InvalidTableReferenceColumnsMismatch,
    InvalidTableReferenceNoReferencingColumns,
    InvalidTableReferenceMissingReferencingTableColumns,
    InvalidTableReferenceMissingReferencedTableColumns,
    InvalidTableReferenceIncompleteCompoundKeyReference,
)
from dlthub.dbt_generator.config import DbtGeneratorConfig

# GLOSSARY:
# RELATION is a TABLE. We do not use the term RELATION here
# TABLES represent ENTITIES (each row - one instance of entity)
# RELATIONSHIPS are between ENTITIES
# REFERENCES are between TABLES and represent RELATIONSHIPS
# CARDINALITY is a property of RELATIONSHIP: 1:1 1:n and n:n

# types of references
# TABLE REFERENCE between FOREIGN KEY (CHILD TABLE) and PRIMARY KEY (PARENT TABLE).
#     compound keys are allowed
# NESTED TABLE REFERENCE a special type of TABLE REFERENCE for dlt nested tables.
#     FOREIGN KEY (CHILD TABLE) and UNIQUE COLUMN (PARENT TABLE). no compound keys
#     core will be updated to use specialized hints for those (row_id which is PK)
#     and (parent_row_id which is FK)
# COLUMN REFERENCE between TABLE (COLUMN) and REFERENCED TABLE (COLUMN)

# TODO: we can move this to core. it should be called `reference` to follow proper nomenclature
# such reference is COLUMN REFERENCE and does not support compound relations
# NOTE: the FOREIGN KEY - PRIMARY KEY relation is a TABLE reference and may use compound keys
REFERENCE_HINT = "x-reference"


class RenderedTableReference(BaseModel):
    """Rendered table and nested references, note that cardinality can't be 1:1"""

    referenced_table: str
    referencing_table: str
    referenced_columns: Sequence[str]
    referencing_columns: Sequence[str]
    dlt_child_table: bool = False
    """wether this reference represents dlt internal child table reference"""

    def __str__(self) -> str:
        return (
            f"Table reference from table {self.referencing_table} on foreign "
            + f"key {self.referencing_columns} to referenced table {self.referenced_table} on "
            + f" columns {self.referenced_columns}"
        )


class RenderedTable(BaseModel):
    """Table with all attributes required to render"""

    name: str
    primary_key: List[str] = []
    all_data_columns: List[str] = []
    all_columns: List[str] = []
    table_references: List[RenderedTableReference] = []


class RenderedNode(BaseModel):
    table: RenderedTable
    alias: str
    table_reference: Optional[RenderedTableReference] = None
    referenced_node: Optional["RenderedNode"] = None
    render_columns: List[str] = []
    suggested_columns: List[str] = []
    # map of normalized and shortened column aliases
    column_aliases: Dict[str, str] = {}


def get_table_references(tables: TSchemaTables) -> Dict[str, List[RenderedTableReference]]:
    """
    Verifies all table references in a schema and returns them as RenderedTableReference
    """
    references: Dict[str, List[RenderedTableReference]] = {}
    for referencing_table in tables.values():
        for reference in referencing_table.get(REFERENCE_HINT, []):  # type: ignore
            reference = cast(TableReference, reference)

            referenced_table = tables.get(reference["referenced_table"])
            referenced_columns = reference["referenced_columns"]
            referencing_columns = reference["columns"]
            referencing_table_name = referencing_table["name"]

            if not referenced_table:
                raise InvalidTableReferenceMissingReferencedTable(
                    referencing_table_name,
                    reference,
                    f"Referenced table '{reference['referenced_table']}' does not exist "
                    + "in the Schema or was not materialized in the destination.",
                )

            # check column count
            if len(referencing_columns) != len(referenced_columns):
                raise InvalidTableReferenceColumnsMismatch(
                    referencing_table_name,
                    reference,
                    "The number of referencing and referenced columns mismatch.",
                )

            if len(referencing_columns) == 0:
                raise InvalidTableReferenceNoReferencingColumns(
                    referencing_table_name,
                    reference,
                    "At least one referencing column is required. None found.",
                )

            # check existence of columns on referencing table
            for column_name in referencing_columns:
                if column_name not in referencing_table["columns"]:
                    raise InvalidTableReferenceMissingReferencingTableColumns(
                        referencing_table_name,
                        reference,
                        f"Column '{column_name}' does not exist on table "
                        + f"'{referencing_table['columns']}'.",
                    )

            # check existence of columns on referenced table
            for column_name in referenced_columns:
                if column_name not in referenced_table["columns"]:
                    raise InvalidTableReferenceMissingReferencedTableColumns(
                        referencing_table_name,
                        reference,
                        f"Column '{column_name}' does not exist on table "
                        + f"'{referenced_table['columns']}'.",
                    )

            primary_key_columns = get_columns_names_with_prop(referenced_table, "primary_key")
            unique_columns = get_columns_names_with_prop(referenced_table, "unique")
            primary_key_union = set(primary_key_columns).intersection(set(referenced_columns))

            # if set of referencing columns exactly equals the primary key, we're good
            if set(primary_key_columns) == set(referenced_columns):
                pass

            # if there is only one referenced column and it is unique
            # on the referenced table, we're also good
            elif len(referenced_columns) == 1 and referenced_columns[0] in unique_columns:
                pass

            # throw an error if the referencing columns are a subset of
            # the primary key on the referenced table
            # then we know that this might be a n:n relationship
            elif len(primary_key_union) >= 1:
                raise InvalidTableReferenceIncompleteCompoundKeyReference(
                    referencing_table_name,
                    reference,
                    f"The columns {referencing_columns} are referencing columns "
                    + f"{referenced_columns} which belong to a compound primary key on the "
                    + "referenced table. Please reference all primary key columns as "
                    + "n:n relationships are not supported at this point.",
                )

            # if there is only one referenced column which is not marked
            # as unique on the referenced table, we add this hint (could fail in transform step)
            elif len(referenced_columns) == 1:
                logger.warning(
                    f"Table {referencing_table['name']} column {referencing_columns[0]} refers to "
                    + f"table {referencing_table['name']} column {referencing_columns[0]} "
                    + "which is not unique! n:n cardinality is not yet supported. Unique hint "
                    + "was added but may fail in the transform step."
                )
                referenced_table["columns"][referenced_columns[0]]["unique"] = True

            # if we have a compound referencing key which is not part of a primary key,
            # we do not know what is going on in this case we warn but allow this
            else:
                logger.warning(
                    f"Table {referencing_table['name']} column {referencing_columns[0]} refers to "
                    + f"table {referencing_table['name']} column {referencing_columns[0]} "
                    + "which is are not the primary key and are not guaranteed to be unique. "
                    + "This may point to a n:n relationship which currently is "
                    + "not supported in the star schema generator."
                )

            table_references = references.setdefault(referencing_table["name"], [])
            table_references.append(
                RenderedTableReference(
                    referenced_table=referenced_table["name"],
                    referenced_columns=referenced_columns,
                    referencing_table=referencing_table["name"],
                    referencing_columns=referencing_columns,
                )
            )

    return references


@with_schemas_sync
def table_reference_adapter(
    pipeline: Pipeline,
    table_name: str,
    references: List[TableReference],
    schema_name: Optional[str] = None,
) -> None:
    """
    Add table references to a table, will overwrite existing references
    """
    if not references:
        return

    schema = pipeline.default_schema if not schema_name else pipeline.schemas[schema_name]
    table_name = schema.naming.normalize_path(table_name)
    for ref in references:
        ref["referenced_table"] = schema.naming.normalize_path(ref["referenced_table"])
        ref["columns"] = [schema.naming.normalize_identifier(c) for c in ref["columns"]]
        ref["referenced_columns"] = [
            schema.naming.normalize_identifier(c) for c in ref["referenced_columns"]
        ]

    if table_name not in schema.tables.keys():
        raise InvalidTableReferenceMissingReferencingTable(
            table_name,
            references[0],
            f"Trying to add table references to table {table_name}, "
            + "but this table does not exist in the schema or was not "
            + "materialized in the destination.",
        )

    # set references
    table = schema.tables[table_name]
    table[REFERENCE_HINT] = references  # type: ignore

    # verify schema
    get_table_references(schema.tables)


def get_rendered_tables(tables: TSchemaTables, schema: Schema) -> Dict[str, RenderedTable]:
    """
    Retrieve a list of tables with attributes necessary to render
    """

    # get all references defined by the user
    table_references = get_table_references(tables)

    rendered_tables: Dict[str, RenderedTable] = {}
    for table_name, table in tables.items():
        primary_key = get_columns_names_with_prop(table, "primary_key")
        if not primary_key:
            # substitute for primary key
            unique = get_first_column_name_with_prop(table, "unique")
            if unique:
                primary_key = [unique]

        # create table entry
        t = RenderedTable(
            name=table_name,
            primary_key=primary_key,
            table_references=table_references.get(table_name, []),
        )

        t.all_data_columns = [
            c
            for c in table["columns"].keys()
            if not c.startswith(schema.naming.normalize_identifier("_dlt"))
        ]
        t.all_columns = list(table["columns"].keys())

        # we add the dlt internal parent child relationships
        if parent := table.get("parent"):
            t.table_references.append(
                RenderedTableReference(
                    referenced_table=parent,
                    referencing_table=table_name,
                    referenced_columns=[schema.data_item_normalizer.c_dlt_id],  # type: ignore
                    referencing_columns=[schema.data_item_normalizer.c_dlt_parent_id],  # type: ignore
                    dlt_child_table=True,
                )
            )

        rendered_tables[table_name] = t

    return rendered_tables


def normalize_alias(c: DbtGeneratorConfig, *parts: str) -> str:
    return c.naming.normalize_path(c.naming.make_path(*parts))


def create_mart_table_name(c: DbtGeneratorConfig, table_name: str, table_type: str) -> str:
    assert table_type in ["stg", "dim", "fact"]
    path_parts = []
    if c.mart_table_prefix:
        path_parts.append(c.mart_table_prefix)
    path_parts.append(table_name)
    # add the table type with separator to the first path part
    path_parts[0] = table_type + c.table_type_separator + path_parts[0]
    return normalize_alias(c, *path_parts)
