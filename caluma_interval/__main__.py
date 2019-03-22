#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is the CLI for caluma_interval.
"""

import argparse
import logging
import sys

from envparse import env

from caluma_interval import client, interval

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
        "--caluma-endpoint",
        metavar="STRING",
        type=str,
        help='defaults to "%(default)s"',
    )
    parser.set_defaults(
        caluma_endpoint=env("CALUMA_ENDPOINT", default="http://caluma:8000/graphql")
    )
    parser.add_argument("-i", "--oidc-client-id", metavar="STRING", type=str)
    parser.set_defaults(oidc_client_id=env("OIDC_CLIENT_ID", default=None))
    parser.add_argument("-s", "--oidc-client-secret", metavar="STRING", type=str)
    parser.set_defaults(oidc_client_secret=env("OIDC_CLIENT_SECRET", default=None))
    parser.add_argument("-u", "--oidc-token-uri", metavar="STRING", type=str)
    parser.set_defaults(oidc_token_uri=env("OIDC_TOKEN_URI", default=None))
    parser.add_argument(
        "-d", "--debug", action="store_true", help="print debug messages"
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

    loggers = [logger, interval.logger, client.logger]

    for l in loggers:
        if args.debug:
            l.level = logging.DEBUG
        else:
            l.level = logging.INFO

    manager = interval.IntervalManager(
        caluma_endpoint=args.caluma_endpoint,
        oidc_client_id=args.oidc_client_id,
        oidc_client_secret=args.oidc_client_secret,
        oidc_token_uri=args.oidc_token_uri,
    )
    try:
        manager.run()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
