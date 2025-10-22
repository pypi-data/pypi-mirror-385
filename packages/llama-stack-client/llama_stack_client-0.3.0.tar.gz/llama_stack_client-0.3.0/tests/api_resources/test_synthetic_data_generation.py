# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from llama_stack_client import LlamaStackClient, AsyncLlamaStackClient
from llama_stack_client.types import SyntheticDataGenerationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSyntheticDataGeneration:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_generate(self, client: LlamaStackClient) -> None:
        synthetic_data_generation = client.synthetic_data_generation.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        )
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    def test_method_generate_with_all_params(self, client: LlamaStackClient) -> None:
        synthetic_data_generation = client.synthetic_data_generation.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                    "context": "string",
                }
            ],
            filtering_function="none",
            model="model",
        )
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    def test_raw_response_generate(self, client: LlamaStackClient) -> None:
        response = client.synthetic_data_generation.with_raw_response.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        synthetic_data_generation = response.parse()
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    def test_streaming_response_generate(self, client: LlamaStackClient) -> None:
        with client.synthetic_data_generation.with_streaming_response.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            synthetic_data_generation = response.parse()
            assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSyntheticDataGeneration:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_generate(self, async_client: AsyncLlamaStackClient) -> None:
        synthetic_data_generation = await async_client.synthetic_data_generation.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        )
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    async def test_method_generate_with_all_params(self, async_client: AsyncLlamaStackClient) -> None:
        synthetic_data_generation = await async_client.synthetic_data_generation.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                    "context": "string",
                }
            ],
            filtering_function="none",
            model="model",
        )
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    async def test_raw_response_generate(self, async_client: AsyncLlamaStackClient) -> None:
        response = await async_client.synthetic_data_generation.with_raw_response.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        synthetic_data_generation = await response.parse()
        assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

    @parametrize
    async def test_streaming_response_generate(self, async_client: AsyncLlamaStackClient) -> None:
        async with async_client.synthetic_data_generation.with_streaming_response.generate(
            dialogs=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
            filtering_function="none",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            synthetic_data_generation = await response.parse()
            assert_matches_type(SyntheticDataGenerationResponse, synthetic_data_generation, path=["response"])

        assert cast(Any, response.is_closed) is True
