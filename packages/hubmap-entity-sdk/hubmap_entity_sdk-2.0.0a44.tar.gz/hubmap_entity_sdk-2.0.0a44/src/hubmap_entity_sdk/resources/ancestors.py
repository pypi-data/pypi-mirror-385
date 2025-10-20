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
from ..types.ancestor_retrieve_response import AncestorRetrieveResponse

__all__ = ["AncestorsResource", "AsyncAncestorsResource"]


class AncestorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AncestorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AncestorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AncestorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AncestorsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AncestorRetrieveResponse:
        """Get the ancestor list for an Entity.

        The ancestors are the nodes connected
        "upstream" from the current node. This list traverses all the levels in the
        graph.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/ancestors/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AncestorRetrieveResponse,
        )


class AsyncAncestorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAncestorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAncestorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAncestorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AsyncAncestorsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AncestorRetrieveResponse:
        """Get the ancestor list for an Entity.

        The ancestors are the nodes connected
        "upstream" from the current node. This list traverses all the levels in the
        graph.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/ancestors/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AncestorRetrieveResponse,
        )


class AncestorsResourceWithRawResponse:
    def __init__(self, ancestors: AncestorsResource) -> None:
        self._ancestors = ancestors

        self.retrieve = to_raw_response_wrapper(
            ancestors.retrieve,
        )


class AsyncAncestorsResourceWithRawResponse:
    def __init__(self, ancestors: AsyncAncestorsResource) -> None:
        self._ancestors = ancestors

        self.retrieve = async_to_raw_response_wrapper(
            ancestors.retrieve,
        )


class AncestorsResourceWithStreamingResponse:
    def __init__(self, ancestors: AncestorsResource) -> None:
        self._ancestors = ancestors

        self.retrieve = to_streamed_response_wrapper(
            ancestors.retrieve,
        )


class AsyncAncestorsResourceWithStreamingResponse:
    def __init__(self, ancestors: AsyncAncestorsResource) -> None:
        self._ancestors = ancestors

        self.retrieve = async_to_streamed_response_wrapper(
            ancestors.retrieve,
        )
