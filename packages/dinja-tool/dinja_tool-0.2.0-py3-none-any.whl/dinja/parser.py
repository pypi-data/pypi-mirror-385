"""
Boundary implementation of the `PyDBML` based DBML parser.
"""

import json
from pathlib import Path
from typing import Final, cast, override

from pydbml.parser.parser import PyDBML

from dinja.api import Column, ColumnName, Index, Reference, SchemaMetadata, Table, TableName
from dinja.core import ParserBoundary


class DbmlParser(ParserBoundary):
    """
    The [parser] component which reads the given input (DBML) file into the business entities that
    can later be handed to the Jinja2 templates.
    """

    _NOTE_NAME_UNIQUE_CONSTRAINT: Final = "composite_unique_constraints"
    """ Name of a special DBML project special defining composite UNIQUE constraints. """

    def __init__(self) -> None:
        """
        Create a new instance reading from the given [dbml_file].
        """
        self._parsed_tables: list[Table] = []
        self._parsed_metadata: SchemaMetadata = SchemaMetadata("?", "?")

    @override
    def parse_dbml(self, input_file: Path) -> None:
        parsed_dbml = PyDBML(input_file)
        self._parsed_metadata = self._get_schema_metadata(parsed_dbml)
        unique_constraints = self._get_all_unique_constraints(parsed_dbml)
        references = self._get_all_references(parsed_dbml)

        self._parsed_tables = [
            Table(
                name=t.name,
                note=t.note.text,
                columns=[
                    Column(
                        name=c.name,
                        type=c.type,
                        nullable=not c.not_null,
                        unique=c.unique,
                        primary_key=c.pk,
                        autoincrement=c.autoinc,
                        note=c.note.text,
                    )
                    for c in t.columns
                ],
                primary_key=self._get_compound_primary_key_columns(t),
                indices=[
                    Index(
                        name=i.name,
                        column_names=i.subject_names,
                        sql=i.sql,
                    )
                    for i in t.indexes if not i.pk
                ],
                unique_constraints=unique_constraints.get(t.name, []),
                references=references.get(t.name, []),
            )
            for t in parsed_dbml.tables
        ]

    def _get_schema_metadata(self, parser: PyDBML) -> SchemaMetadata:
        """
        Read the schema metadata from the "Project" item, if any. If there is no project version
        or it doesn't define a schema version, the default SchemaMetadata instance is returned.
        """
        if not parser.project:
            return SchemaMetadata()

        schema_version = parser.project.items.get("schema_version", None)
        if not schema_version:
            return SchemaMetadata()

        return SchemaMetadata(
            schema_version_major=schema_version.split(".")[0],
            schema_version_minor=schema_version.split(".")[1],
        )

    def _get_compound_primary_key_columns(self, table: Table) -> list[ColumnName]:
        pk_columns = [c for c in table.columns if c.pk]
        compound_pk_indices = [index for index in table.indexes if index.pk]

        if pk_columns and compound_pk_indices:
            raise ValueError(
                f"Table {table.name} must either define a single PK column or a compound, but not "
                f"both."
            )

        if len(pk_columns) > 1:
            raise ValueError(
                f"Table {table.name} must not have multiple 'pk' columns. Use a primary key index "
                f"to define a compound primary key."
            )

        if len(compound_pk_indices) > 1:
            raise ValueError(f"Table {table.name} must not have multiple 'pk' indices.")

        if compound_pk_indices:
            return compound_pk_indices[0].subject_names

        return []

    def _get_all_unique_constraints(self, parser: PyDBML) -> dict[str, list[list[ColumnName]]]:
        if not parser.project:
            return {}

        unique_constraint_json = parser.project.items.get(self._NOTE_NAME_UNIQUE_CONSTRAINT, "{}")
        return cast(dict[str, list[list[ColumnName]]], json.loads(unique_constraint_json))

    def _get_all_references(self, parser: PyDBML) -> dict[TableName, list[Reference]]:
        table_references: dict[TableName, list[Reference]] = {}
        for ref in parser.refs:
            table_references.setdefault(ref.table2.name, []).append(
                Reference(
                    table_name=ref.table1.name,
                    remote_columns=[c.name for c in ref.col1],
                    local_columns=[c.name for c in ref.col2],
                    delete_action=ref.on_delete.upper(),
                )
            )
        return table_references

    @override
    def get_parsed_metadata(self) -> SchemaMetadata:
        return self._parsed_metadata

    @override
    def get_parsed_tables(self) -> list[Table]:
        return self._parsed_tables
