# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import Body, Query, Headers, NotGiven, not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.index_list_response import IndexListResponse

__all__ = ["IndicesResource", "AsyncIndicesResource"]


class IndicesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IndicesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return IndicesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IndicesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return IndicesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IndexListResponse:
        """Reindex for a given UUID of dataset.

        Use this method to obtain a list of valid
        indices within the search-api endpoint. These index names are used in some of
        the subsequent calls made to the endpoint.
        """
        return self._get(
            "/indices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IndexListResponse,
        )


class AsyncIndicesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIndicesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncIndicesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIndicesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncIndicesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IndexListResponse:
        """Reindex for a given UUID of dataset.

        Use this method to obtain a list of valid
        indices within the search-api endpoint. These index names are used in some of
        the subsequent calls made to the endpoint.
        """
        return await self._get(
            "/indices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IndexListResponse,
        )


class IndicesResourceWithRawResponse:
    def __init__(self, indices: IndicesResource) -> None:
        self._indices = indices

        self.list = to_raw_response_wrapper(
            indices.list,
        )


class AsyncIndicesResourceWithRawResponse:
    def __init__(self, indices: AsyncIndicesResource) -> None:
        self._indices = indices

        self.list = async_to_raw_response_wrapper(
            indices.list,
        )


class IndicesResourceWithStreamingResponse:
    def __init__(self, indices: IndicesResource) -> None:
        self._indices = indices

        self.list = to_streamed_response_wrapper(
            indices.list,
        )


class AsyncIndicesResourceWithStreamingResponse:
    def __init__(self, indices: AsyncIndicesResource) -> None:
        self._indices = indices

        self.list = async_to_streamed_response_wrapper(
            indices.list,
        )
