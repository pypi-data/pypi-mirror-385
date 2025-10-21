"""
The `main` component which connects all software parts together and starts the application.
"""

from dinja.core import DinjaApplication
from dinja.parser import DbmlParser
from dinja.renderer import Jinja2Renderer
from dinja.settings import CliSettings
from dinja.storage import FileSystemStorage


def main() -> None:
    """
    The application's main entry point. Responsible for defining the concrete boundary
    implementations to use.
    """
    app = DinjaApplication(
        settings_factory=CliSettings,
        parser_factory=DbmlParser,
        renderer_factory=Jinja2Renderer,
        storage_factory=FileSystemStorage,
    )
    app.run_application()


if __name__ == "__main__":
    main()
