# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from ..types import DocumentStatus, document_list_params, document_create_params, document_list_chunks_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncOffsetPagination, AsyncOffsetPagination
from .._base_client import AsyncPaginator, make_request_options
from ..types.document import Document
from ..types.document_chunk import DocumentChunk
from ..types.document_status import DocumentStatus
from ..types.document_response import DocumentResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        assignee: str,
        content: str,
        language: str,
        status: DocumentStatus,
        title: str,
        metadata: Dict[str, object] | Omit = omit,
        original_sentences: SequenceNotStr[str] | Omit = omit,
        scrape_job_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentResponse:
        """
        Creates a new document with the provided information.

        Args:
          assignee: User ID of the person assigned to this document

          content: Content of the initial document version

          language: Language of the initial document version

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the initial document version

          metadata: Optional metadata for the initial document version

          original_sentences: Array of original sentences from the source

          scrape_job_id: Optional ID of the scrape job that generated this document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v0/documents",
            body=maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "language": language,
                    "status": status,
                    "title": title,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "scrape_job_id": scrape_job_id,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentResponse,
        )

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
    ) -> DocumentResponse:
        """
        Retrieves detailed information about a specific document, including its
        parent-child relationships and active version details.

        Args:
          id: The unique identifier of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v0/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentResponse,
        )

    def list(
        self,
        *,
        assignee: str | Omit = omit,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        scrape_job_id: str | Omit = omit,
        skip: int | Omit = omit,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncOffsetPagination[Document]:
        """
        Retrieves a paginated list of documents with optional filtering by status,
        assignee, parent, and other criteria. Only returns documents with active
        approved versions unless otherwise specified.

        Args:
          assignee: Filter by assignee user ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          scrape_job_id: Filter by scrape job ID

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents",
            page=SyncOffsetPagination[Document],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "assignee": assignee,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "scrape_job_id": scrape_job_id,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=Document,
        )

    def list_chunks(
        self,
        *,
        document_id: str,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        skip: int | Omit = omit,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncOffsetPagination[DocumentChunk]:
        """
        Retrieves a paginated list of document chunks with optional filtering by
        document ID.

        Args:
          document_id: Filter by document ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents/chunked",
            page=SyncOffsetPagination[DocumentChunk],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "document_id": document_id,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_chunks_params.DocumentListChunksParams,
                ),
            ),
            model=DocumentChunk,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        assignee: str,
        content: str,
        language: str,
        status: DocumentStatus,
        title: str,
        metadata: Dict[str, object] | Omit = omit,
        original_sentences: SequenceNotStr[str] | Omit = omit,
        scrape_job_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentResponse:
        """
        Creates a new document with the provided information.

        Args:
          assignee: User ID of the person assigned to this document

          content: Content of the initial document version

          language: Language of the initial document version

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the initial document version

          metadata: Optional metadata for the initial document version

          original_sentences: Array of original sentences from the source

          scrape_job_id: Optional ID of the scrape job that generated this document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v0/documents",
            body=await async_maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "language": language,
                    "status": status,
                    "title": title,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "scrape_job_id": scrape_job_id,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentResponse,
        )

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
    ) -> DocumentResponse:
        """
        Retrieves detailed information about a specific document, including its
        parent-child relationships and active version details.

        Args:
          id: The unique identifier of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v0/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentResponse,
        )

    def list(
        self,
        *,
        assignee: str | Omit = omit,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        scrape_job_id: str | Omit = omit,
        skip: int | Omit = omit,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Document, AsyncOffsetPagination[Document]]:
        """
        Retrieves a paginated list of documents with optional filtering by status,
        assignee, parent, and other criteria. Only returns documents with active
        approved versions unless otherwise specified.

        Args:
          assignee: Filter by assignee user ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          scrape_job_id: Filter by scrape job ID

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents",
            page=AsyncOffsetPagination[Document],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "assignee": assignee,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "scrape_job_id": scrape_job_id,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=Document,
        )

    def list_chunks(
        self,
        *,
        document_id: str,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        skip: int | Omit = omit,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[DocumentChunk, AsyncOffsetPagination[DocumentChunk]]:
        """
        Retrieves a paginated list of document chunks with optional filtering by
        document ID.

        Args:
          document_id: Filter by document ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents/chunked",
            page=AsyncOffsetPagination[DocumentChunk],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "document_id": document_id,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_chunks_params.DocumentListChunksParams,
                ),
            ),
            model=DocumentChunk,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = to_raw_response_wrapper(
            documents.retrieve,
        )
        self.list = to_raw_response_wrapper(
            documents.list,
        )
        self.list_chunks = to_raw_response_wrapper(
            documents.list_chunks,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            documents.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            documents.list,
        )
        self.list_chunks = async_to_raw_response_wrapper(
            documents.list_chunks,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            documents.list,
        )
        self.list_chunks = to_streamed_response_wrapper(
            documents.list_chunks,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            documents.list,
        )
        self.list_chunks = async_to_streamed_response_wrapper(
            documents.list_chunks,
        )
