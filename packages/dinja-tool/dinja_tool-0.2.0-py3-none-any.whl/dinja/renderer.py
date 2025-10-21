"""
Boundary implementation of the `Jinja2` based renderer.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import override

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.utils import select_autoescape

from dinja.api import SchemaMetadata, Table
from dinja.core import RenderedTemplate, RendererBoundary


class Jinja2Renderer(RendererBoundary):
    """
    The [renderer] component which renders Jinja2 templates using the provided business data (see
    [api] module).
    """

    def __init__(self, template_path: Path):
        """
        Create a new instance rendering all templates found in the provided [template_path] and
        writing them into the [output_path] directory.
        """
        self._template_path = template_path

    @override
    def render(
        self,
        meta_data: SchemaMetadata,
        table_data: list[Table],
    ) -> Iterator[RenderedTemplate]:
        template_files = self._find_template_files()
        for template_file in template_files:
            rendered_data = RenderedTemplate(
                destination_name=self._get_destination_name(template_file),
                content=self._render_template(template_file, meta_data, table_data),
            )
            yield rendered_data

    def _find_template_files(self) -> list[Path]:
        return [f for f in self._template_path.iterdir() if f.suffix in [".in", ".jinja"]]

    def _render_template(
        self,
        template_file: Path,
        meta_data: SchemaMetadata,
        table_data: list[Table],
    ) -> str:
        env = Environment(
            loader=FileSystemLoader(self._template_path),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_file.name)

        return template.render(metadata=meta_data, tables=table_data)

    def _get_destination_name(self, template_file: Path) -> str:
        return template_file.stem
