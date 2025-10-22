# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import chat_stream_params, chat_retrieve_feedback_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["ChatResource", "AsyncChatResource"]


class ChatResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ChatResourceWithStreamingResponse(self)

    def retrieve_feedback(
        self,
        *,
        component_id: str | Omit = omit,
        end_date: str | Omit = omit,
        feedback_type: Literal["thumbsUp", "thumbsDown"] | Omit = omit,
        limit: str | Omit = omit,
        skip: str | Omit = omit,
        start_date: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves feedback data for the organization with optional filtering

        Args:
          component_id: Filter by component ID

          end_date: Filter by end date (ISO string)

          feedback_type: Filter by feedback type

          limit: Number of records to return (default: 100)

          skip: Number of records to skip (default: 0)

          start_date: Filter by start date (ISO string)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/chat/feedback",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "feedback_type": feedback_type,
                        "limit": limit,
                        "skip": skip,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_retrieve_feedback_params.ChatRetrieveFeedbackParams,
                ),
            ),
            cast_to=NoneType,
        )

    def stream(
        self,
        *,
        id: str | Omit = omit,
        component_id: str | Omit = omit,
        context: object | Omit = omit,
        group_ids: SequenceNotStr[str] | Omit = omit,
        message: chat_stream_params.Message | Omit = omit,
        messages: SequenceNotStr[str] | Omit = omit,
        session_id: str | Omit = omit,
        trigger: str | Omit = omit,
        user_id: str | Omit = omit,
        x_component_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Streams a chat response in real-time using server-sent events (SSE).

        Supports
        both AI SDK format (with messages array) and custom format (with message
        object).

        Args:
          id: Session ID (AI SDK uses "id")

          component_id: Component ID

          context: Additional context

          group_ids: Group IDs for access control

          message: Single message for custom format - contains text and optional images

          messages: Messages array for AI SDK format - list of conversation messages with roles

          session_id: Session ID

          trigger: Trigger for AI SDK (what triggered the message)

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return self._post(
            "/api/v1/chat/stream",
            body=maybe_transform(
                {
                    "id": id,
                    "component_id": component_id,
                    "context": context,
                    "group_ids": group_ids,
                    "message": message,
                    "messages": messages,
                    "session_id": session_id,
                    "trigger": trigger,
                    "user_id": user_id,
                },
                chat_stream_params.ChatStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncChatResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncChatResourceWithStreamingResponse(self)

    async def retrieve_feedback(
        self,
        *,
        component_id: str | Omit = omit,
        end_date: str | Omit = omit,
        feedback_type: Literal["thumbsUp", "thumbsDown"] | Omit = omit,
        limit: str | Omit = omit,
        skip: str | Omit = omit,
        start_date: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves feedback data for the organization with optional filtering

        Args:
          component_id: Filter by component ID

          end_date: Filter by end date (ISO string)

          feedback_type: Filter by feedback type

          limit: Number of records to return (default: 100)

          skip: Number of records to skip (default: 0)

          start_date: Filter by start date (ISO string)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/chat/feedback",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "feedback_type": feedback_type,
                        "limit": limit,
                        "skip": skip,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_retrieve_feedback_params.ChatRetrieveFeedbackParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def stream(
        self,
        *,
        id: str | Omit = omit,
        component_id: str | Omit = omit,
        context: object | Omit = omit,
        group_ids: SequenceNotStr[str] | Omit = omit,
        message: chat_stream_params.Message | Omit = omit,
        messages: SequenceNotStr[str] | Omit = omit,
        session_id: str | Omit = omit,
        trigger: str | Omit = omit,
        user_id: str | Omit = omit,
        x_component_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Streams a chat response in real-time using server-sent events (SSE).

        Supports
        both AI SDK format (with messages array) and custom format (with message
        object).

        Args:
          id: Session ID (AI SDK uses "id")

          component_id: Component ID

          context: Additional context

          group_ids: Group IDs for access control

          message: Single message for custom format - contains text and optional images

          messages: Messages array for AI SDK format - list of conversation messages with roles

          session_id: Session ID

          trigger: Trigger for AI SDK (what triggered the message)

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return await self._post(
            "/api/v1/chat/stream",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "component_id": component_id,
                    "context": context,
                    "group_ids": group_ids,
                    "message": message,
                    "messages": messages,
                    "session_id": session_id,
                    "trigger": trigger,
                    "user_id": user_id,
                },
                chat_stream_params.ChatStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ChatResourceWithRawResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.retrieve_feedback = to_raw_response_wrapper(
            chat.retrieve_feedback,
        )
        self.stream = to_raw_response_wrapper(
            chat.stream,
        )


class AsyncChatResourceWithRawResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.retrieve_feedback = async_to_raw_response_wrapper(
            chat.retrieve_feedback,
        )
        self.stream = async_to_raw_response_wrapper(
            chat.stream,
        )


class ChatResourceWithStreamingResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.retrieve_feedback = to_streamed_response_wrapper(
            chat.retrieve_feedback,
        )
        self.stream = to_streamed_response_wrapper(
            chat.stream,
        )


class AsyncChatResourceWithStreamingResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.retrieve_feedback = async_to_streamed_response_wrapper(
            chat.retrieve_feedback,
        )
        self.stream = async_to_streamed_response_wrapper(
            chat.stream,
        )
