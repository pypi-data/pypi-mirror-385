# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr

__all__ = [
    "SamplingParams",
    "Strategy",
    "StrategyGreedySamplingStrategy",
    "StrategyTopPSamplingStrategy",
    "StrategyTopKSamplingStrategy",
]


class StrategyGreedySamplingStrategy(TypedDict, total=False):
    type: Required[Literal["greedy"]]
    """Must be "greedy" to identify this sampling strategy"""


class StrategyTopPSamplingStrategy(TypedDict, total=False):
    type: Required[Literal["top_p"]]
    """Must be "top_p" to identify this sampling strategy"""

    temperature: float
    """Controls randomness in sampling. Higher values increase randomness"""

    top_p: float
    """Cumulative probability threshold for nucleus sampling. Defaults to 0.95"""


class StrategyTopKSamplingStrategy(TypedDict, total=False):
    top_k: Required[int]
    """Number of top tokens to consider for sampling. Must be at least 1"""

    type: Required[Literal["top_k"]]
    """Must be "top_k" to identify this sampling strategy"""


Strategy: TypeAlias = Union[StrategyGreedySamplingStrategy, StrategyTopPSamplingStrategy, StrategyTopKSamplingStrategy]


class SamplingParams(TypedDict, total=False):
    strategy: Required[Strategy]
    """The sampling strategy."""

    max_tokens: int
    """The maximum number of tokens that can be generated in the completion.

    The token count of your prompt plus max_tokens cannot exceed the model's context
    length.
    """

    repetition_penalty: float
    """Number between -2.0 and 2.0.

    Positive values penalize new tokens based on whether they appear in the text so
    far, increasing the model's likelihood to talk about new topics.
    """

    stop: SequenceNotStr[str]
    """Up to 4 sequences where the API will stop generating further tokens.

    The returned text will not contain the stop sequence.
    """
