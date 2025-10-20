# -*- coding: utf-8 -*-

import argparse

from maestral.daemon import freeze_support as freeze_support_daemon
from maestral.cli import freeze_support as freeze_support_cli
from maestral.daemon import start_maestral_daemon_process


def get_config_name_arg() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-name", default="maestral")
    parsed_args, _ = parser.parse_known_args()
    return parsed_args.config_name


def main():
    """
    This is the main entry point. It starts the GUI with the given config.
    """
    config_name = get_config_name_arg()
    res = start_maestral_daemon_process(config_name)

    from .app import run

    run(config_name, res)


if __name__ == "__main__":
    freeze_support_cli()
    freeze_support_daemon()
    main()
