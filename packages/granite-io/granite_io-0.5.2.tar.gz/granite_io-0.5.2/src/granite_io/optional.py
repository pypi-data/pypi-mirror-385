# SPDX-License-Identifier: Apache-2.0

"""
Utilities for optional dependencies
"""

# Standard
from contextlib import contextmanager
import logging

_NLTK_INSTALL_INSTRUCTIONS = """
Please install nltk with:
    pip install nltk
In some environments you may also need to manually download model weights with:
    python -m nltk.downloader punkt_tab
See https://www.nltk.org/install.html#installing-nltk-data for more detailed 
instructions."""


@contextmanager
def import_optional(extra_name: str):
    """Context manager to handle optional imports"""
    try:
        yield
    except ImportError as err:
        logging.warning(
            "%s.\nHINT: You may need to pip install %s[%s]",
            err,
            __package__,
            extra_name,
        )
        raise


@contextmanager
def nltk_check(feature_name: str):
    """Variation on import_optional for nltk.

    :param feature_name: Name of feature that requires NLTK"""
    try:
        yield
    except ImportError as err:
        raise ImportError(
            f"'nltk' package not installed. This package is required for "
            f"{feature_name} in the 'granite_io' library."
            f"{_NLTK_INSTALL_INSTRUCTIONS}"
        ) from err
