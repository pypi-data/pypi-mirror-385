"""
Dinja Template Data Interface.

This module contains all data types that can be provided to Jinja2 templates, and thus is the
relevant interface for template authors.
"""

from dataclasses import dataclass, field
from typing import Final, Literal, NewType

TableName = NewType("TableName", str)
""" Name of a table within the database. """

ColumnName = NewType("ColumnName", str)
""" Name of a column within the database. """

IndexName = NewType("IndexName", str)
""" Name of an index within the database. """

DataType = NewType("DataType", str)
"""
Data type for the values stored in a table columns.

A certain type name value is forward as-is to the renderer, so the allowed names depend on the
destination format. It is recommended to use BOOLEAN, INTEGER, REAL, TEST and BLOB, but this is in
no way enforced by Dinja.
"""


@dataclass
class Column:
    """Definition of a single table column."""

    name: ColumnName
    """ The column name. """

    type: DataType
    """ Column content data type. """

    nullable: bool = field(default=True, kw_only=True)
    """ Does the column accept NULL values (True) or not (False)? """

    unique: bool = field(default=False, kw_only=True)
    """ Is this column unique within its table (True)? """

    primary_key: bool = field(default=False, kw_only=True)
    """ Is this a primary key column (True)? """

    autoincrement: bool = field(default=False, kw_only=True)
    """
    Enable (True) or disable (False) the SQL "autoincrement" feature for this column. Only supported
    for primary key ID columns.
    """

    note: str = field(kw_only=True)
    """ Textual column documentation. """

    def __post_init__(self) -> None:
        """
        Post-initialization checks for the data fields.
        """
        if self.autoincrement and not self.primary_key:
            raise ValueError("Autoincrement is only supported for primary key columns.")


@dataclass
class Index:
    """Definition of a single index on a certain table."""

    name: str
    """ The name of the index. """

    column_names: list[ColumnName]
    """ Names of the columns the index is built on (in that order). """

    sql: str
    """ The rendered SQL (DDL) for this index. """


@dataclass
class Reference:
    """Definition of a foreign key relation."""

    table_name: TableName
    """ The name of the referenced ("parent") table. """

    local_columns: list[ColumnName]
    """
    The name(s) of the referencing ("child") column(s) (of the table this Reference is assigned to).
    """

    remote_columns: list[ColumnName]

    """ The name(s) of the referenced ("parent") column(s) within [table_name]. """

    delete_action: Literal["CASCADE", "REJECT", "SET NULL", "SET DEFAULT", "NO ACTION"] | None = (
        field(default="NO ACTION", kw_only=True)
    )
    """ The desired behaviour in case the remote value is deleted. """


@dataclass
class Table:
    """Definition of a single database table."""

    name: TableName
    """ The name of the table. """

    columns: list[Column]
    """ Definition of this table's columns. """

    primary_key: list[ColumnName]
    """
    Name of all columns defining the primary key, in that order. Empty if there is no explicit
    primary key.
    """

    indices: list[Index]
    """
    List of indices on this table. All columns within the index specification must of course be
    defined within [columns].
    """

    unique_constraints: list[list[ColumnName]]
    """
    List of unique constraints for this table. Each item is a list of columns whose combined values
    shall be unique. All columns must be defined within [column_specification()], of course.
    """

    references: list[Reference]
    """ Definition of all foreign key references from this table to others. """

    note: str
    """ Textual table documentation. """

    def __post_init__(self) -> None:
        """
        Post-initialization checks for the data fields.
        """
        column_names: Final = [c.name for c in self.columns]
        for idx in self.indices:
            if any(c not in column_names for c in idx.column_names):
                raise ValueError("Some index refers to an undefined column.")
        for uc in self.unique_constraints:
            if any(c not in column_names for c in uc):
                raise ValueError("Some unique constraint refers to an undefined column.")
        for ref in self.references:
            if any(c not in column_names for c in ref.local_columns):
                raise ValueError("A foreign key is defined on an undefined column.")


@dataclass
class SchemaMetadata:
    """
    Metadata about the database schema as described by the parsed DBML files.
    """

    schema_version_major: str = "?"
    """
    Major database schema version (increased for incompatible changes).
    """

    schema_version_minor: str = "?"
    """
    Minor database schema version (increased for backward-compatible changes).
    """
