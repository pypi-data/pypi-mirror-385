# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import click

from .list import list_providers
from .inspect import inspect_provider


@click.group()
@click.help_option("-h", "--help")
def providers():
    """Manage API providers."""


# Register subcommands
providers.add_command(list_providers)
providers.add_command(inspect_provider)
