#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is the CLI for caluma_interval.
"""

import argparse
import logging
import sys

from envparse import env

from caluma_interval import interval

logger = logging.getLogger(__name__)
logging.basicConfig()


def parse_arguments(args):
    """
    Parse all given arguments.
    :param args: list
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description=interval.__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--caluma-uri",
        metavar="STRING",
        type=str,
        help='defaults to "%(default)s"',
    )
    parser.set_defaults(caluma_uri=env("CALUMA_URI", default="http://caluma/graphql"))
    parser.add_argument(
        "-d", "--debug", action="store_true", help="print " "debug messages"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=interval.__version__
    )

    args = parser.parse_args(args)

    return args


def main():
    """
    Main CLI function for caluma_interval.
    """
    args = parse_arguments(sys.argv[1:])

    if args.debug:
        logger.level = logging.DEBUG
        interval.logger.level = logging.DEBUG
    else:
        logger.level = logging.INFO
        interval.logger.level = logging.INFO

    manager = interval.IntervalManager(caluma_uri=args.caluma_uri)
    manager.run()


if __name__ == "__main__":
    main()
