import os
from typing import Dict, Any, List, Optional

from dlt.common import logger
from dlt.common.exceptions import MissingDependencyException
from dlt.common.schema.utils import is_complete_column

from dlthub.dbt_generator.config import (
    DbtGeneratorConfig,
    TESTS_FOLDER,
    MACROS_FOLDER,
    ANALYSIS_FOLDER,
    MARTS_MODELS_FOLDER,
)

from dlthub.dbt_generator.exceptions import FilesExistException

try:
    from jinja2 import Environment, PackageLoader
    from dlthub.dbt_generator.utils import (
        RenderedNode,
        RenderedTableReference,
        get_rendered_tables,
        create_mart_table_name,
        normalize_alias,
    )
except ImportError as import_ex:
    from dlthub import version

    raise MissingDependencyException(
        "dbt package generator",
        [f"{version.PKG_NAME}[dbt]"],
        "Install extras above in order to render dbt packages",
    ) from import_ex


def _protect_overwrite(path: str, config: DbtGeneratorConfig) -> None:
    if os.path.exists(os.path.join(path)) and not config.force:
        raise FilesExistException(path)


def _render_template(
    folder: str, template_name: str, output_location: str, vars: Dict[str, Any] = {}
) -> None:
    jinja_env = Environment(loader=PackageLoader("dlthub.dbt_generator"), autoescape=True)
    template = jinja_env.get_template(template_name)
    if folder:
        output_location = os.path.join(folder, output_location)
    with open(output_location, "w", encoding="utf-8") as f:
        f.write(template.render(**vars))


def _create_project_folders(config: DbtGeneratorConfig) -> None:
    # folder
    for folder in [
        MARTS_MODELS_FOLDER,
        MACROS_FOLDER,
        ANALYSIS_FOLDER,
        TESTS_FOLDER,
    ]:
        f = os.path.join(config.package_root_folder, folder)
        os.makedirs(f, exist_ok=True)

    for folder in [
        config.mart_folder,
        config.staging_models_folder,
        config.mart_models_folder,
    ]:
        os.makedirs(folder, exist_ok=True)


def render_fact_table(config: DbtGeneratorConfig) -> str:
    # folder
    _create_project_folders(config)
    render_tables = get_rendered_tables(config.tables_to_render, config.schema)

    # collect all tables in table tree
    table_tree: List[RenderedNode] = []

    def _add_rendered_columns(table_node: RenderedNode, *column_names: str) -> None:
        for column_name in column_names:
            if column_name not in table_node.render_columns:
                table_node.render_columns.append(column_name)

    def _make_tree_for_table_name(
        table_name: str,
        reference: Optional[RenderedTableReference] = None,
        referenced_node: Optional[RenderedNode] = None,
    ) -> None:
        logger.info(f"Adding {table_name} via {reference}")
        table_node = RenderedNode(
            table=render_tables[table_name], alias=table_name, referenced_node=referenced_node
        )
        _add_rendered_columns(table_node, *table_node.table.primary_key)
        # build reference tree
        # TODO: we should probably detect cycles
        if referenced_node:
            alias_chain: List[str] = []
            while referenced_node:
                # build alias chain
                if reference:
                    chain_items = [reference.referenced_table]
                    if not reference.dlt_child_table:
                        chain_items += [*reference.referencing_columns]
                    new_chain_entry = config.naming.make_path(*chain_items)
                    if alias_chain:
                        alias_chain.append(new_chain_entry)
                    else:
                        alias_chain = [new_chain_entry]
                        table_node.table_reference = reference
                reference = referenced_node.table_reference
                referenced_node = referenced_node.referenced_node
            table_node.alias = normalize_alias(config, *alias_chain)
        else:
            # we need to add all columns of the fact table to be selected and rendered
            _add_rendered_columns(table_node, *table_node.table.all_data_columns)

        table_tree.append(table_node)

        # TODO: allow users to configure max nesting IMO 2 tables away is good enough

        # follow table references
        for ref in table_node.table.table_references:
            _make_tree_for_table_name(
                ref.referenced_table,
                ref,
                table_node,
            )

    _make_tree_for_table_name(config.fact_table)

    for table_node in table_tree:
        if config.fact_table_render_all_columns:
            _add_rendered_columns(table_node, *table_node.table.all_data_columns)
        else:
            table_node.suggested_columns = [
                col
                for col in table_node.table.all_data_columns
                if col not in table_node.render_columns
            ]

    # for each node in table tree we create normalized and shorted identifiers for columns
    for table_node in table_tree:
        table_node.column_aliases = {
            c: normalize_alias(config, table_node.alias, c) for c in table_node.table.all_columns
        }

    # mapping of plain table names to sources in facts and dimension tables
    table_sources: Dict[str, str] = {}
    for table_node in table_tree:
        table_type = "stg" if table_node.table.name == config.fact_table else "dim"
        source = create_mart_table_name(config, table_node.table.name, table_type)
        table_sources[table_node.table.name] = source

    # output name
    fact_name = create_mart_table_name(config, config.fact_table, "fact") + ".sql"
    location = os.path.join(config.mart_models_folder, fact_name)

    # protect from overwriting the whole project
    _protect_overwrite(location, config)
    _render_template(
        folder=config.mart_models_folder,
        template_name="table_fact.sql.j2",
        output_location=fact_name,
        vars={
            "table_sources": table_sources,
            "fact_table_name": config.fact_table,
            "table_tree": table_tree,
        },
    )

    return location


def render_dbt_project(config: DbtGeneratorConfig) -> str:
    # folder
    _protect_overwrite(config.package_root_folder, config)
    _create_project_folders(config)

    # render main file
    if config.render_run_script:
        _render_template(
            folder=config.base_folder,
            template_name="main.py.j2",
            output_location=config.main_file_name,
            vars={
                "pipeline_name": config.project_name,
                "dbt_package_location": config.package_name,
                "dbt_venv_location": config.venv_location,
                "destination": config.destination,
            },
        )
    if config.render_readme_file:
        _render_template(
            folder=config.base_folder,
            template_name="README.md.j2",
            output_location="README.md",
            vars={
                "project_name": config.project_name,
                "mart_table_prefix": config.mart_table_prefix,
                "tables": config.tables_to_render,
            },
        )

    # render requirements file
    # TODO: use dlt[cli] extra to generate only top level deps
    # with pipdeptree and from actual Venv where dbt got installed
    # NOTE: why we need it at all? dlt creates virtual env with required dbt deps
    _render_template(
        folder=config.package_root_folder,
        template_name="requirements.txt.j2",
        output_location="requirements.txt",
    )

    # main dbt project file
    _render_template(
        folder=config.package_root_folder,
        template_name="dbt_project.yml.j2",
        output_location="dbt_project.yml",
        vars={
            "project_name": config.project_name,
        },
    )

    return config.package_root_folder


def render_mart(config: DbtGeneratorConfig) -> str:
    """Renders mart for a selected pipeline schema"""

    # prepare a list of normalized identifiers used by various templates
    identifiers = {
        "c_dlt_parent_id": config.schema.data_item_normalizer.c_dlt_parent_id,  # type: ignore
        "c_dlt_id": config.schema.data_item_normalizer.c_dlt_id,  # type: ignore
        "c_dlt_load_id": config.schema.data_item_normalizer.c_dlt_load_id,  # type: ignore
        "c_inserted_at": config.naming.normalize_identifier("inserted_at"),
        "c_load_id": config.naming.normalize_identifier("load_id"),
        "c_status": config.naming.normalize_identifier("status"),
        "t_dlt_loads": config.naming.normalize_identifier("_dlt_loads"),
    }

    active_load_id_table_name = config.naming.normalize_identifier(
        f"{config.mart_table_prefix}dlt_active_load_ids"
    )
    processed_load_id_table_name = config.naming.normalize_identifier(
        f"{config.mart_table_prefix}dlt_processed_load_ids"
    )

    _render_template(
        folder=config.mart_folder,
        template_name="sources.yml.j2",
        output_location="sources.yml",
        vars={
            "tables": config.tables_to_render,
            "processed_load_id_table_name": processed_load_id_table_name,
            **identifiers,
        },
    )

    mart_table_names: List[str] = []

    # render tables
    for table_name, table in config.tables_to_render.items():
        stage_name = create_mart_table_name(config, table_name, "stg")
        mart_name = create_mart_table_name(config, table_name, "dim")
        parent_stage_name = None
        if parent_table := table.get("parent"):
            parent_stage_name = create_mart_table_name(config, parent_table, "stg")

        mart_table_names.append(mart_name)

        # get column names for all complete columns
        columns = [c.get("name") for c in filter(is_complete_column, table["columns"].values())]

        template_vars = {
            "table_name": table_name,
            "stg_table_name": stage_name,
            "description": table.get("description", ""),
            "parent": table.get("parent"),
            "columns": columns,
            "active_table_name": active_load_id_table_name,
            "is_data_table": not table_name.startswith(config.naming.normalize_identifier("_dlt")),
            "parent_stage_name": parent_stage_name,
            "enable_load_id_incremental": config.enable_load_id_incremental,
            **identifiers,
        }

        _render_template(
            folder=config.staging_models_folder,
            template_name="table_staging.sql.j2",
            output_location=f"{stage_name}.sql",
            vars=template_vars,
        )

        _render_template(
            folder=config.mart_models_folder,
            template_name="table_mart.sql.j2",
            output_location=f"{mart_name}.sql",
            vars=template_vars,
        )

    if config.enable_load_id_incremental:
        # render active load ids table
        _render_template(
            folder=config.mart_folder,
            template_name="table_active_load_ids.sql.j2",
            output_location=f"{active_load_id_table_name}.sql",
            vars={
                "tables": config.tables_to_render,
                "processed_load_id_table_name": processed_load_id_table_name,
                **identifiers,
            },
        )

        # render processed load ids table
        _render_template(
            folder=config.mart_folder,
            template_name="table_processed_load_ids.sql.j2",
            output_location=f"{processed_load_id_table_name}.sql",
            vars={
                "mart_table_names": mart_table_names,
                "active_table_name": active_load_id_table_name,
                **identifiers,
            },
        )

    return config.mart_folder
