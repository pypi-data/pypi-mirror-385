"""
Boundary implementation of the file system output storage.
"""
from pathlib import Path
from typing import override

from dinja.core import RenderedTemplate, StorageBoundary


class FileSystemStorage(StorageBoundary):
    """
    Storage component writing the rendered data into regular files. Existing files are silently
    replaced.
    """

    def __init__(self, output_directory: Path):
        """
        Create a new instance storing all files into the given [output_directory].
        """
        self._output_directory = output_directory

    @override
    def store_data(self, rendered_data: RenderedTemplate) -> None:
        destination_filepath = self._output_directory.joinpath(rendered_data.destination_name)
        with destination_filepath.open("wt") as fp:
            fp.write(rendered_data.content)
