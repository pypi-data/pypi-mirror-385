#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 GFZ Helmholtz Centre for Geosciences
# SPDX-FileCopyrightText: 2025 Felix Dombrowski
# SPDX-License-Identifier: EUPL-1.2

"""Console script for enmap_downloader."""

import argparse
import sys


def get_argparser():
    """
    Get a console argument parser for EnMAP Downloader and return them as `argparse.ArgumentParser`.

    Returns
    -------
    argparse.ArgumentParser
        The argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("_", nargs="*")

    return parser


def main():
    """
    Console script for EnMAP Downloader.

    Returns
    -------
    int
        The exit code.
    """
    argparser = get_argparser()
    parsed_args = argparser.parse_args()

    print("Arguments: " + str(parsed_args._))
    print("Replace this message by putting your code into enmap_downloader.enmap_downloader_cli")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
