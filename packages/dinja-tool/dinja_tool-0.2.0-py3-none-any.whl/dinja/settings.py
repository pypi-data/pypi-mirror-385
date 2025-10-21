"""
Settings boundary implementation that takes the application configuration from the command line.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import override

from dinja.core import SettingsBoundary


class CliSettings(SettingsBoundary):
    """
    Represents the configuration given by all command line arguments.
    """

    def __init__(self) -> None:
        """
        Creates a new instance from the applications command line.

        In case of parsing errors, the application may immediately exit() from this constructor.
        """
        args = self.__parse_command_line()
        self.__dbml_file: Path = args.dbml_file
        self.__template_dir: Path = args.template_dir
        self.__output_dir: Path = args.output_dir

    def __parse_command_line(self) -> Namespace:
        """
        Returns the parsed command line.
        """
        parser = self.__create_parser()
        return parser.parse_args()

    def __create_parser(self) -> ArgumentParser:
        """
        Creates the `argparse` parser and configures the allowed CLI arguments and options as well
        as their help texts. Returns the configured parser object.
        """
        parser = ArgumentParser()
        parser.add_argument(
            "dbml_file",
            help="a DBML file to be converted",
            type=Path,
        )
        parser.add_argument(
            "template_dir",
            help="path to search for Jinja template files",
            type=Path,
        )
        parser.add_argument(
            "output_dir",
            help="path to a directory to write the converted files into",
            type=Path,
        )
        return parser

    @override
    def get_output_dir(self) -> Path:
        return self.__output_dir

    @override
    def get_template_dir(self) -> Path:
        return self.__template_dir

    @override
    def get_input_file(self) -> Path:
        return self.__dbml_file
