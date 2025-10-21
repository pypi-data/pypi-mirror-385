"""
The Dinja application core. Contains the business logic and the definition of all boundary
interfaces.
"""

from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from dinja.api import SchemaMetadata, Table


class SettingsBoundary(metaclass=ABCMeta):
    """
    Boundary that gives access to the current application configuration.
    """

    @abstractmethod
    def get_output_dir(self) -> Path:
        """
        Returns the output directory to use.
        """

    @abstractmethod
    def get_template_dir(self) -> Path:
        """
        Returns the template search directory to use.
        """

    @abstractmethod
    def get_input_file(self) -> Path:
        """
        Returns the input (DBML) file path to convert.
        """


class ParserBoundary(metaclass=ABCMeta):
    """
    Boundary interface of a parser capable reading the given input file. Call `parse_dbml()` once to
    parse an input file, and user the `get_*` methods to retrieve the parsed data afterwards.
    """

    @abstractmethod
    def parse_dbml(self, input_file: Path) -> None:
        """
        Read and parse the given [input_file].
        """

    @abstractmethod
    def get_parsed_metadata(self) -> SchemaMetadata:
        """
        Return the parsed database schema metadata, or a default `SchemaMetadata` instance if no
        file has been parsed yet.
        """

    @abstractmethod
    def get_parsed_tables(self) -> list[Table]:
        """
        Return the database table definition parsed from the input file. Empty list if no file has
        been parsed yet.
        """


@dataclass
class RenderedTemplate:
    """
    Represents a rendered template, as returned by the RendererBoundary.
    """

    destination_name: str
    """
    The final name of the rendered template. Can be used e.g. as file name.
    """

    content: str
    """
    The final content data.
    """


class RendererBoundary(metaclass=ABCMeta):
    """
    Boundary interface of the renderer component which collects and renders all template files.
    """

    @abstractmethod
    def render(
        self,
        meta_data: SchemaMetadata,
        table_data: list[Table],
    ) -> Iterator[RenderedTemplate]:
        """
        Render all found template files with the given data and write the results into the output
        directory.
        """


class StorageBoundary(metaclass=ABCMeta):
    """
    Boundary interface of the storage component which writes the rendered data into the final
    storage space.
    """

    @abstractmethod
    def store_data(self, rendered_data: RenderedTemplate) -> None:
        """
        Store the provided [rendered_data] into its final location.
        """


class DinjaApplication:
    """
    Represents the Dinja application executing the main use case
    """

    def __init__(
        self,
        settings_factory: Callable[[], SettingsBoundary],
        parser_factory: Callable[[], ParserBoundary],
        renderer_factory: Callable[[Path], RendererBoundary],
        storage_factory: Callable[[Path], StorageBoundary],
    ):
        """
        Create a new application instance that uses the boundary objects provided by the given
        factories.
        :param settings_factory: Factory providing the SettingsBoundary to use.
        :param parser_factory: Factory providing the ParserBoundary to use.
        :param renderer_factory: Factory providing the RendererBoundary to use. Parameter is the
            directory to search for template files.
        :param storage_factory: Factory providing the StorageBoundary to use. Parameter is the
            directory to write rendered files into.
        """
        self._settings_factory = settings_factory
        self._parser_factory = parser_factory
        self._renderer_factory = renderer_factory
        self._storage_factory = storage_factory

    def run_application(self) -> None:
        """
        Execute the application's main use case of parsing the given DBML file and rendering it
        using the available templates.
        """
        self._display_status_message("Initializing application...")
        settings = self._settings_factory()
        parser = self._parser_factory()
        renderer = self._renderer_factory(settings.get_template_dir())
        storage = self._storage_factory(settings.get_output_dir())

        self._display_status_message(f"Parsing file {settings.get_input_file()}...")
        parser.parse_dbml(settings.get_input_file())
        metadata = parser.get_parsed_metadata()
        tables = parser.get_parsed_tables()
        self._display_status_message("Rendering all templates...")
        for rendered_data in renderer.render(meta_data=metadata, table_data=tables):
            self._display_status_message(
                f"Writing rendered template {rendered_data.destination_name}"
            )
            storage.store_data(rendered_data)
        self._display_status_message("Done")

    def _display_status_message(self, msg: str) -> None:
        """
        Prints the provided [msg] to stdout. This is a simple wrapper to the print() function. It's
        main purpose is to have only a single usage of print() within the project (because it
        triggers a linter warning which must be disabled here).
        If we need any more fancy user interaction/output in the future, the correct way is to
        create a `ui` component module (and a `UiBoundary`) which encapsulates this stuff.
        """
        print(msg)  # noqa: T201
