try:
    from ._version import __version__  # type: ignore[import]
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings

    warnings.warn(
        "Importing 'jupyterlab_classiq' outside a proper installation.", stacklevel=2
    )
    __version__ = "dev"


def _jupyter_labextension_paths() -> list[dict]:
    return [{"src": "labextension", "dest": "jupyterlab-classiq"}]
