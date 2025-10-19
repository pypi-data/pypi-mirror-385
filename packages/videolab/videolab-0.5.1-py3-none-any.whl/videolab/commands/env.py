# Copyright (C) 2025 Kian-Meng, Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import platform
import sys

from videolab import __version__


def env_command(args: argparse.Namespace) -> None:
    """
    Shows environment information.
    """
    print(f"videolab: {__version__}")
    print(f"python: {sys.version.splitlines()[0]}")
    print(f"platform: {platform.platform()}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    Registers the 'env' subcommand.
    """
    env_parser = subparsers.add_parser("env", help="Show environment information")
    env_parser.set_defaults(func=env_command)
