from typing import Any, Dict, List, Optional, Union

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from paid.tracing.tracing import (
    get_paid_tracer,
    logger,
    paid_external_agent_id_var,
    paid_external_customer_id_var,
    paid_token_var,
)

try:
    from mistralai import Mistral, models
    from mistralai.types import UNSET, OptionalNullable
except ImportError:
    raise ImportError(
        "mistralai package is a peer-dependency. To use the Paid wrapper around mistralai "
        "you're assumed to already have mistralai package installed."
    )


class PaidMistral:
    def __init__(self, mistral_client: Mistral, optional_tracing: bool = False):
        self.mistral = mistral_client
        self.tracer = get_paid_tracer()
        self.optional_tracing = optional_tracing

    @property
    def ocr(self):
        return OCRWrapper(self.mistral, self.tracer, self.optional_tracing)


class OCRWrapper:
    def __init__(self, mistral_client: Mistral, tracer: trace.Tracer, optional_tracing: bool):
        self.mistral = mistral_client
        self.tracer = tracer
        self.optional_tracing = optional_tracing

    def process(
        self,
        *,
        model: str,
        document: Union[models.Document, models.DocumentTypedDict],
        id: Optional[str] = None,
        pages: Optional[List[int]] = None,
        include_image_base64: Optional[bool] = None,
        image_limit: Optional[int] = None,
        image_min_size: Optional[int] = None,
        bbox_annotation_format: OptionalNullable[Union[models.ResponseFormat, models.ResponseFormatTypedDict]] = UNSET,
        document_annotation_format: OptionalNullable[
            Union[models.ResponseFormat, models.ResponseFormatTypedDict]
        ] = UNSET,
        retries: Optional[Any] = None,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Process document with OCR synchronously

        Args:
            model: OCR model name (e.g., "mistral-ocr-latest")
            document: Document to run OCR on
            id: Optional ID for the request
            pages: Specific pages user wants to process. List of page numbers starting from 0
            include_image_base64: Include image URLs in response
            image_limit: Max images to extract
            image_min_size: Minimum height and width of image to extract
            bbox_annotation_format: Structured output for extracted bounding boxes/images
            document_annotation_format: Structured output for entire document
            retries: Override default retry configuration
            server_url: Override default server URL
            timeout_ms: Override default request timeout in milliseconds
            http_headers: Additional headers to set or replace on requests
        """
        # Check if there's an active span (from capture())
        current_span = trace.get_current_span()
        if current_span == trace.INVALID_SPAN:
            if self.optional_tracing:
                logger.info(f"{self.__class__.__name__} No tracing, calling Mistral directly.")
                return self.mistral.ocr.process(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )
            raise RuntimeError("No OTEL span found. Make sure to call this method from Paid.trace().")

        external_customer_id = paid_external_customer_id_var.get()
        external_agent_id = paid_external_agent_id_var.get()
        token = paid_token_var.get()

        if not (external_customer_id and token):
            if self.optional_tracing:
                logger.info(f"{self.__class__.__name__} No external_customer_id or token, calling Mistral directly")
                return self.mistral.ocr.process(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )
            raise RuntimeError(
                "Missing required tracing information: external_customer_id or token."
                " Make sure to call this method from Paid.trace()."
            )

        with self.tracer.start_as_current_span("mistral.ocr.process") as span:
            attributes = {
                "gen_ai.system": "mistral",
                "gen_ai.operation.name": "ocr",
            }
            if bbox_annotation_format or document_annotation_format:
                attributes["gen_ai.ocr.annotated"] = "true"

            attributes["external_customer_id"] = external_customer_id
            attributes["token"] = token
            if external_agent_id:
                attributes["external_agent_id"] = external_agent_id
            span.set_attributes(attributes)

            try:
                # Make the actual Mistral OCR API call
                response = self.mistral.ocr.process(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )

                if (
                    hasattr(response, "usage_info")
                    and response.usage_info
                    and hasattr(response.usage_info, "pages_processed")
                ):
                    span.set_attribute("gen_ai.ocr.pages_processed", response.usage_info.pages_processed)
                if hasattr(response, "model"):
                    span.set_attribute("gen_ai.response.model", response.model)

                # Mark span as successful
                span.set_status(Status(StatusCode.OK))
                return response

            except Exception as error:
                # Mark span as failed and record error
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.record_exception(error)
                raise error

    async def process_async(
        self,
        *,
        model: str,
        document: Union[models.Document, models.DocumentTypedDict],
        id: Optional[str] = None,
        pages: Optional[List[int]] = None,
        include_image_base64: Optional[bool] = None,
        image_limit: Optional[int] = None,
        image_min_size: Optional[int] = None,
        bbox_annotation_format: OptionalNullable[Union[models.ResponseFormat, models.ResponseFormatTypedDict]] = UNSET,
        document_annotation_format: OptionalNullable[
            Union[models.ResponseFormat, models.ResponseFormatTypedDict]
        ] = UNSET,
        retries: Optional[Any] = None,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Process document with OCR asynchronously

        Args:
            model: OCR model name (e.g., "mistral-ocr-latest")
            document: Document to run OCR on
            id: Optional ID for the request
            pages: Specific pages user wants to process. List of page numbers starting from 0
            include_image_base64: Include image URLs in response
            image_limit: Max images to extract
            image_min_size: Minimum height and width of image to extract
            bbox_annotation_format: Structured output for extracted bounding boxes/images
            document_annotation_format: Structured output for entire document
            retries: Override default retry configuration
            server_url: Override default server URL
            timeout_ms: Override default request timeout in milliseconds
            http_headers: Additional headers to set or replace on requests
        """
        # Check if there's an active span (from capture())
        current_span = trace.get_current_span()
        if current_span == trace.INVALID_SPAN:
            if self.optional_tracing:
                logger.info(f"{self.__class__.__name__} No tracing, calling Mistral directly.")
                return await self.mistral.ocr.process_async(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )
            raise RuntimeError("No OTEL span found. Make sure to call this method from Paid.trace().")

        external_customer_id = paid_external_customer_id_var.get()
        external_agent_id = paid_external_agent_id_var.get()
        token = paid_token_var.get()

        if not (external_customer_id and token):
            if self.optional_tracing:
                logger.info(f"{self.__class__.__name__} No external_customer_id or token, calling Mistral directly")
                return await self.mistral.ocr.process_async(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )
            raise RuntimeError(
                "Missing required tracing information: external_customer_id or token."
                " Make sure to call this method from Paid.trace()."
            )

        with self.tracer.start_as_current_span("mistral.ocr.process_async") as span:
            attributes = {
                "gen_ai.system": "mistral",
                "gen_ai.operation.name": "ocr",
            }
            if bbox_annotation_format or document_annotation_format:
                attributes["gen_ai.ocr.annotated"] = "true"

            attributes["external_customer_id"] = external_customer_id
            attributes["token"] = token
            if external_agent_id:
                attributes["external_agent_id"] = external_agent_id
            span.set_attributes(attributes)

            try:
                # Make the actual Mistral OCR API call asynchronously
                response = await self.mistral.ocr.process_async(
                    model=model,
                    document=document,
                    id=id,
                    pages=pages,
                    include_image_base64=include_image_base64,
                    image_limit=image_limit,
                    image_min_size=image_min_size,
                    bbox_annotation_format=bbox_annotation_format,
                    document_annotation_format=document_annotation_format,
                    retries=retries,
                    server_url=server_url,
                    timeout_ms=timeout_ms,
                    http_headers=http_headers,
                )

                if (
                    hasattr(response, "usage_info")
                    and response.usage_info
                    and hasattr(response.usage_info, "pages_processed")
                ):
                    span.set_attribute("gen_ai.ocr.pages_processed", response.usage_info.pages_processed)
                if hasattr(response, "model"):
                    span.set_attribute("gen_ai.response.model", response.model)

                # Mark span as successful
                span.set_status(Status(StatusCode.OK))
                return response

            except Exception as error:
                # Mark span as failed and record error
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.record_exception(error)
                raise error
