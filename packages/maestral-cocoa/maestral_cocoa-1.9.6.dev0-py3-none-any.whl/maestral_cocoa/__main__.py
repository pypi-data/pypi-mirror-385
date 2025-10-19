# -*- coding: utf-8 -*-

import argparse

from maestral.daemon import freeze_support as freeze_support_daemon
from maestral.cli import freeze_support as freeze_support_cli


def main():
    """
    This is the main entry point. It starts the GUI with the given config.
    """

    from .app import run

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-name", default="maestral")
    parsed_args, _ = parser.parse_known_args()

    run(parsed_args.config_name)


if __name__ == "__main__":
    freeze_support_cli()
    freeze_support_daemon()
    main()
