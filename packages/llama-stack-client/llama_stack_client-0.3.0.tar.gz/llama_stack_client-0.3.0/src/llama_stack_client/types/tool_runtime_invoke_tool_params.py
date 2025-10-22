# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["ToolRuntimeInvokeToolParams"]


class ToolRuntimeInvokeToolParams(TypedDict, total=False):
    kwargs: Required[Dict[str, Union[bool, float, str, Iterable[object], object, None]]]
    """A dictionary of arguments to pass to the tool."""

    tool_name: Required[str]
    """The name of the tool to invoke."""
