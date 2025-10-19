"""
bbcli - DEPRECATED

This Python version of bbcli is deprecated and no longer maintained.

Please uninstall this package and install the new Rust version:
    pip uninstall bbcli

Then install the new version using one of these methods:
    eget hako/bbcli
    cargo binstall bbc-news-cli
    cargo install bbc-news-cli

Repository: https://github.com/hako/bbcli
"""

import warnings

warnings.warn(
    "The Python version of bbcli is DEPRECATED. "
    "Please uninstall this package (pip uninstall bbcli) and install the new Rust version. "
    "See: https://github.com/hako/bbcli",
    DeprecationWarning,
    stacklevel=2
)
