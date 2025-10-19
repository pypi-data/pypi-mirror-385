try:
    # Python 3.9 and later
    from importlib.resources import as_file, files  # type: ignore

    def resource_path(name: str) -> str:
        return str(files("maestral_cocoa.resources") / name)

except ImportError:
    # Python 3.8
    from importlib.resources import path  # type: ignore

    def resource_path(name: str) -> str:
        """Returns the resource path as a string. Extracts the resource if necessary."""
        return str(path("maestral_cocoa.resources", name).__enter__())


APP_ICON_PATH = resource_path("maestral.icns")
FACEHOLDER_PATH = resource_path("faceholder.pdf")
RELEASE_NOTES_CSS_PATH = resource_path("release_notes.css")
