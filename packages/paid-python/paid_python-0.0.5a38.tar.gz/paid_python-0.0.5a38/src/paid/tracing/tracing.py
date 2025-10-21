# Initializing tracing for OTLP
import asyncio
import atexit
import contextvars
import functools
import logging
import os
import signal
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, Union

import dotenv
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace import NonRecordingSpan, SpanContext, Status, StatusCode, TraceFlags

# Configure logging
dotenv.load_dotenv()
log_level_name = os.environ.get("PAID_LOG_LEVEL")
if log_level_name is not None:
    log_level = getattr(logging, log_level_name.upper())
else:
    log_level = logging.ERROR  # Default to show errors
logger = logging.getLogger(__name__)
logger.setLevel(log_level)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Context variables for passing data to nested spans (e.g., in openAiWrapper)
paid_external_customer_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "paid_external_customer_id", default=None
)
paid_external_agent_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "paid_external_agent_id", default=None
)
# api_key storage
paid_token_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("paid_token", default=None)
# trace id storage (generated from token)
paid_trace_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar("paid_trace_id", default=None)
# flag to enable storing prompt contents
paid_store_prompt_var: contextvars.ContextVar[Optional[bool]] = contextvars.ContextVar(
    "paid_store_prompt", default=False
)
# user metadata
paid_user_metadata_var: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "paid_user_metadata", default=None
)

T = TypeVar("T")

_token: Optional[str] = None


def get_token() -> Optional[str]:
    """Get the stored API token."""
    global _token
    return _token


def set_token(token: str) -> None:
    """Set the API token."""
    global _token
    _token = token


otel_id_generator = RandomIdGenerator()

# Isolated tracer provider for Paid - separate from any user OTEL setup
paid_tracer_provider: Optional[TracerProvider] = None


class PaidSpanProcessor(SpanProcessor):
    """
    Span processor that:
    1. Prefixes all span names with 'paid.trace.'
    2. Automatically adds external_customer_id and external_agent_id attributes
       to all spans based on context variables set by the tracing decorator.
    """

    SPAN_NAME_PREFIX = "paid.trace."
    PROMPT_ATTRIBUTES_PREFIXES = {
        "gen_ai.prompt",
        "gen_ai.completion",
        "gen_ai.request.messages",
        "gen_ai.response.messages",
        "llm.output_message",
        "llm.input_message",
        "output.value",
        "input.value",
    }

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Called when a span is started. Prefix the span name and add attributes."""
        # Prefix the span name
        if span.name and not span.name.startswith(self.SPAN_NAME_PREFIX):
            span.update_name(f"{self.SPAN_NAME_PREFIX}{span.name}")

        # Add customer and agent IDs from context
        customer_id = paid_external_customer_id_var.get()
        if customer_id:
            span.set_attribute("external_customer_id", customer_id)

        agent_id = paid_external_agent_id_var.get()
        if agent_id:
            span.set_attribute("external_agent_id", agent_id)

        metadata = paid_user_metadata_var.get()
        if metadata:
            metadata_attributes: dict[str, Any] = {}

            def flatten_dict(d: dict[str, Any], parent_key: str = "") -> None:
                """Recursively flatten nested dictionaries into dot-notation keys."""
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        flatten_dict(v, new_key)
                    else:
                        metadata_attributes[new_key] = v

            flatten_dict(metadata)

            # Add all flattened metadata attributes to the span
            for key, value in metadata_attributes.items():
                span.set_attribute(f"metadata.{key}", value)

    def on_end(self, span: ReadableSpan) -> None:
        """Filter out prompt and response contents unless explicitly asked to store"""
        store_prompt = paid_store_prompt_var.get()
        if store_prompt:
            return

        original_attributes = span.attributes

        if original_attributes:
            # Filter out prompt-related attributes
            filtered_attrs = {
                k: v
                for k, v in original_attributes.items()
                if not any(k.startswith(prefix) for prefix in self.PROMPT_ATTRIBUTES_PREFIXES)
            }
            # Temporarily replace attributes for export
            # This works because the exporter reads attributes during serialization
            object.__setattr__(span, "_attributes", filtered_attrs)

    def shutdown(self) -> None:
        """Called when the processor is shut down. No action needed."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Called to force flush. Always returns True since there's nothing to flush."""
        return True


def _initialize_tracing(
    api_key: Optional[str] = None, collector_endpoint: Optional[str] = "https://collector.agentpaid.io:4318/v1/traces"
):
    """
    Initialize OpenTelemetry with OTLP exporter for Paid backend.

    Args:
        api_key: The API key for authentication. If not provided, will try to get from PAID_API_KEY environment variable.
        collector_endpoint: The OTLP collector endpoint URL.
    """
    global paid_tracer_provider

    try:
        if _token is not None:
            raise RuntimeError("Tracing is already initialized.")

        # Get API key from parameter or environment
        if api_key is None:
            import dotenv

            dotenv.load_dotenv()
            api_key = os.environ.get("PAID_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as parameter or via PAID_API_KEY environment variable"
                )

        set_token(api_key)

        resource = Resource(attributes={"api.key": api_key})
        # Create isolated tracer provider for Paid - don't use or modify global provider
        paid_tracer_provider = TracerProvider(resource=resource)

        # Add span processor to prefix span names and add customer/agent ID attributes
        paid_tracer_provider.add_span_processor(PaidSpanProcessor())

        # Set up OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=collector_endpoint,
            headers={},  # No additional headers needed for OTLP
        )

        # Use SimpleSpanProcessor for immediate span export.
        # There are problems with BatchSpanProcessor in some environments - ex. Airflow.
        # Airflow terminates processes before the batch is sent, losing traces.
        span_processor = SimpleSpanProcessor(otlp_exporter)
        paid_tracer_provider.add_span_processor(span_processor)

        # Terminate gracefully and don't lose traces
        def flush_traces():
            try:
                if paid_tracer_provider is not None and not paid_tracer_provider.force_flush(10000):
                    logger.error("OTEL force flush : timeout reached")
            except Exception as e:
                logger.error(f"Error flushing traces: {e}")

        def create_chained_signal_handler(signum: int):
            current_handler = signal.getsignal(signum)

            def chained_handler(_signum, frame):
                logger.warning(f"Received signal {_signum}, flushing traces")
                flush_traces()
                # Restore the original handler
                signal.signal(_signum, current_handler)
                # Re-raise the signal to let the original handler (or default) handle it
                os.kill(os.getpid(), _signum)

            return chained_handler

        # This is already done by default OTEL shutdown,
        # but user might turn that off - so register it explicitly
        atexit.register(flush_traces)

        # Handle signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, create_chained_signal_handler(sig))

        logger.info("Paid tracing initialized successfully - collector at %s", collector_endpoint)
    except Exception:
        logger.exception("Failed to initialize Paid tracing")
        raise


def get_paid_tracer() -> trace.Tracer:
    """
    Get the tracer from the isolated Paid tracer provider.

    Returns:
        The Paid tracer instance.

    Raises:
        RuntimeError: If the tracer provider is not initialized.
    """
    if paid_tracer_provider is None:
        raise RuntimeError("Paid tracer provider is not initialized. Call Paid.initialize_tracing() first.")
    return paid_tracer_provider.get_tracer("paid.python")


def _trace_sync(
    external_customer_id: str,
    fn: Callable[..., T],
    external_agent_id: Optional[str] = None,
    tracing_token: Optional[int] = None,
    store_prompt: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    args: Optional[Tuple] = None,
    kwargs: Optional[Dict] = None,
) -> T:
    args = args or ()
    kwargs = kwargs or {}
    token = get_token()
    if not token:
        raise RuntimeError(
            "No token found - tracing is not initialized and will not be captured. Call Paid.initialize_tracing() first."
        )

    # Set context variables for access by nested spans
    reset_id_ctx_token = paid_external_customer_id_var.set(external_customer_id)
    reset_agent_id_ctx_token = paid_external_agent_id_var.set(external_agent_id)
    reset_token_ctx_token = paid_token_var.set(token)
    reset_store_prompt_ctx_token = paid_store_prompt_var.set(store_prompt)
    reset_user_metadata_ctx_token = paid_user_metadata_var.set(metadata)

    # If user set trace context manually
    override_trace_id = tracing_token
    if not override_trace_id:
        override_trace_id = paid_trace_id.get()
    ctx: Optional[Context] = None
    if override_trace_id is not None:
        span_context = SpanContext(
            trace_id=override_trace_id,
            span_id=otel_id_generator.generate_span_id(),
            is_remote=True,
            trace_flags=TraceFlags(TraceFlags.SAMPLED),
        )
        ctx = trace.set_span_in_context(NonRecordingSpan(span_context))

    try:
        tracer = get_paid_tracer()
        logger.info(f"Creating span for external_customer_id: {external_customer_id}")
        with tracer.start_as_current_span("parent_span", context=ctx) as span:
            span.set_attribute("external_customer_id", external_customer_id)
            if external_agent_id:
                span.set_attribute("external_agent_id", external_agent_id)
            try:
                result = fn(*args, **kwargs)
                span.set_status(Status(StatusCode.OK))
                logger.info(f"Function {fn.__name__} executed successfully")
                return result
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise
    finally:
        paid_external_customer_id_var.reset(reset_id_ctx_token)
        paid_external_agent_id_var.reset(reset_agent_id_ctx_token)
        paid_token_var.reset(reset_token_ctx_token)
        paid_store_prompt_var.reset(reset_store_prompt_ctx_token)
        paid_user_metadata_var.reset(reset_user_metadata_ctx_token)


async def _trace_async(
    external_customer_id: str,
    fn: Callable[..., Union[T, Awaitable[T]]],
    external_agent_id: Optional[str] = None,
    tracing_token: Optional[int] = None,
    store_prompt: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    args: Optional[Tuple] = None,
    kwargs: Optional[Dict] = None,
) -> Union[T, Awaitable[T]]:
    args = args or ()
    kwargs = kwargs or {}
    token = get_token()
    if not token:
        raise RuntimeError(
            "No token found - tracing is not initialized and will not be captured. Call Paid.initialize_tracing() first."
        )

    # Set context variables for access by nested spans
    reset_id_ctx_token = paid_external_customer_id_var.set(external_customer_id)
    reset_agent_id_ctx_token = paid_external_agent_id_var.set(external_agent_id)
    reset_token_ctx_token = paid_token_var.set(token)
    reset_store_prompt_ctx_token = paid_store_prompt_var.set(store_prompt)
    reset_user_metadata_ctx_token = paid_user_metadata_var.set(metadata)

    # If user set trace context manually
    override_trace_id = tracing_token
    if not override_trace_id:
        override_trace_id = paid_trace_id.get()
    ctx: Optional[Context] = None
    if override_trace_id is not None:
        span_context = SpanContext(
            trace_id=override_trace_id,
            span_id=otel_id_generator.generate_span_id(),
            is_remote=True,
            trace_flags=TraceFlags(TraceFlags.SAMPLED),
        )
        ctx = trace.set_span_in_context(NonRecordingSpan(span_context))

    try:
        tracer = get_paid_tracer()
        logger.info(f"Creating span for external_customer_id: {external_customer_id}")
        with tracer.start_as_current_span("parent_span", context=ctx) as span:
            span.set_attribute("external_customer_id", external_customer_id)
            if external_agent_id:
                span.set_attribute("external_agent_id", external_agent_id)
            try:
                if asyncio.iscoroutinefunction(fn):
                    result = await fn(*args, **kwargs)
                else:
                    result = fn(*args, **kwargs)
                span.set_status(Status(StatusCode.OK))
                logger.info(f"Async function {fn.__name__} executed successfully")
                return result
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise
    finally:
        paid_external_customer_id_var.reset(reset_id_ctx_token)
        paid_external_agent_id_var.reset(reset_agent_id_ctx_token)
        paid_token_var.reset(reset_token_ctx_token)
        paid_store_prompt_var.reset(reset_store_prompt_ctx_token)
        paid_user_metadata_var.reset(reset_user_metadata_ctx_token)


def generate_tracing_token() -> int:
    """
    This will generate and return a tracing token but it will not set it
    for the tracing context. Needed when you only want to store or send a tracing token
    somewhere else.
    """
    return otel_id_generator.generate_trace_id()


def generate_and_set_tracing_token() -> int:
    """
    *Advanced feature*
    In cases when you can't share the same Paid.trace() or @paid_tracing() context with
    code that you want to track together (complex concurrency logic,
    or disjoint workflows, or work is separated between processes),
    then you can manually generate a tracing token with generate_and_set_tracing_token()
    and share it with the other parts of your application or service using set_tracing_token().

    This function returns tracing token and attaches it to all consequent
    Paid.trace() or @paid_tracing() tracing contexts. So all the costs and signals that share this
    tracing context are associated with each other.

    To stop associating the traces one can either call
    generate_and_set_tracing_token() once again or call unset_tracing_token().
    The former is suitable if you still want to trace but in a fresh
    context, and the latter will go back to unique traces per Paid.trace() or @paid_tracing().

    Returns:
        int: The tracing token (OpenTelemetry trace ID)

    Example:
        >>> from paid.tracing import generate_and_set_tracing_token, set_tracing_token, unset_tracing_token
        >>> # Process 1: Generate token
        >>> token = generate_and_set_tracing_token()
        >>> save_to_redis("workflow_123", token)
        >>>
        >>> # Process 2: Use token
        >>> token = load_from_redis("workflow_123")
        >>> set_tracing_token(token)
        >>> # ... do traced work ...
        >>> unset_tracing_token()
    """
    random_trace_id = otel_id_generator.generate_trace_id()
    _ = paid_trace_id.set(random_trace_id)
    return random_trace_id


def set_tracing_token(token: int):
    """
    *Advanced feature*
    In cases when you can't share the same Paid.trace() or @paid_tracing() context with
    code that you want to track together (complex concurrency logic,
    or disjoint workflows, or work is separated between processes),
    then you can manually generate a tracing token with generate_and_set_tracing_token()
    and share it with the other parts of your application or service using set_tracing_token().

    Sets tracing token. Provided token should come from generate_and_set_tracing_token().
    Once set, the consequent traces will be related to each other.

    Args:
        token (int): A tracing token from generate_and_set_tracing_token()

    Example:
        >>> from paid.tracing import set_tracing_token, unset_tracing_token, paid_tracing
        >>> # Retrieve token from storage
        >>> token = get_from_redis("workflow_123")
        >>> set_tracing_token(token)
        >>>
        >>> @paid_tracing("customer_123", "agent_123")
        >>> def process_workflow():
        ...     # This trace will be linked to the token
        ...     pass
        >>>
        >>> process_workflow()
        >>> unset_tracing_token()
    """
    _ = paid_trace_id.set(token)


def unset_tracing_token():
    """
    Unsets the token previously set by generate_and_set_tracing_token()
    or by set_tracing_token(token). Does nothing if the token was never set.
    When tracing token is unset, traces are unique for a single Paid.trace() or @paid_tracing() context.

    Example:
        >>> from paid.tracing import set_tracing_token, unset_tracing_token
        >>> set_tracing_token(stored_token)
        >>> try:
        ...     process_workflow()
        ... finally:
        ...     unset_tracing_token()  # Always clean up
    """
    _ = paid_trace_id.set(None)


def paid_tracing(
    external_customer_id: str,
    *,
    tracing_token: Optional[int] = None,
    external_agent_id: Optional[str] = None,
    store_prompt: bool = False,
    collector_endpoint: Optional[str] = "https://collector.agentpaid.io:4318/v1/traces",
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Decorator for tracing function execution with Paid.

    This decorator automatically handles both synchronous and asynchronous functions,
    providing the same functionality as client.trace() but in a more convenient form.

    Parameters
    ----------
    external_customer_id : str
        The external customer ID to associate with the trace.
    external_agent_id : Optional[str], optional
        The external agent ID to associate with the trace, by default None.
    store_prompt : bool, optional
        Whether to store prompt contents in span attributes, by default False.
    collector_endpoint: Optional[str] = "https://collector.agentpaid.io:4318/v1/traces",
        Most likely unneded to pass in, but can change OTEL collector HTTP endpoint if needed.

    Returns
    -------
    Callable
        The decorated function with tracing capabilities.

    Examples
    --------
    @paid_tracing(external_customer_id="customer123", external_agent_id="agent456")
    def my_function(arg1, arg2):
        return arg1 + arg2

    @paid_tracing(external_customer_id="customer123")
    async def my_async_function(arg1, arg2):
        return arg1 + arg2

    Notes
    -----
    If paid client and tracing are not already initialized, this decorator will automatically
    initialize it using the PAID_API_KEY environment variable. If even then initialization fails,
    the decorator will act as a noop.
    """

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Auto-initialize tracing if not done
                if get_token() is None:
                    try:
                        _initialize_tracing(None, collector_endpoint)
                    except Exception as e:
                        logger.error(f"Failed to auto-initialize tracing: {e}")
                        # Fall back to executing function without tracing
                        return await func(*args, **kwargs)

                try:
                    return await _trace_async(
                        external_customer_id=external_customer_id,
                        fn=func,
                        external_agent_id=external_agent_id,
                        tracing_token=tracing_token,
                        store_prompt=store_prompt,
                        metadata=metadata,
                        args=args,
                        kwargs=kwargs,
                    )
                except Exception as e:
                    logger.error(f"Failed to trace async function {func.__name__}: {e}")
                    raise e

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Auto-initialize tracing if not done
                if get_token() is None:
                    try:
                        _initialize_tracing(None, collector_endpoint)
                    except Exception as e:
                        logger.error(f"Failed to auto-initialize tracing: {e}")
                        # Fall back to executing function without tracing
                        return func(*args, **kwargs)

                try:
                    return _trace_sync(
                        external_customer_id=external_customer_id,
                        fn=func,
                        external_agent_id=external_agent_id,
                        tracing_token=tracing_token,
                        store_prompt=store_prompt,
                        metadata=metadata,
                        args=args,
                        kwargs=kwargs,
                    )
                except Exception as e:
                    logger.error(f"Failed to trace sync function {func.__name__}: {e}")
                    raise e

            return sync_wrapper

    return decorator
