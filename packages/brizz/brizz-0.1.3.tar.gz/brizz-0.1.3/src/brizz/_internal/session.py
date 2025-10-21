"""Session context utilities for Brizz SDK."""

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from opentelemetry import context

from brizz._internal.semantic_conventions import PROPERTIES_CONTEXT_KEY, SESSION_ID

# Type variable for generic function support
F = TypeVar("F", bound=Callable[..., Any])


def new_context(properties: dict[str, str]) -> context.Context:
    """Create a new OpenTelemetry context with given properties.

    Args:
        properties: Dictionary of properties to add to context

    Returns:
        New OpenTelemetry context with the properties set
    """
    if not properties:
        return context.get_current()

    # Get existing properties and merge with new ones
    current_context = context.get_current()
    existing_properties = cast(dict[str, Any], current_context.get(PROPERTIES_CONTEXT_KEY, {})) or {}
    merged_properties = {**existing_properties, **properties}

    return context.set_value(PROPERTIES_CONTEXT_KEY, merged_properties)


def with_properties(properties: dict[str, str], fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a function with OpenTelemetry context properties.

    Args:
        properties: Dictionary of properties to add to context
        fn: Function to execute with the properties
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    if not properties:
        return fn(*args, **kwargs)

    # Get existing properties and merge with new ones
    token = context.attach(new_context(properties))
    try:
        return fn(*args, **kwargs)
    finally:
        context.detach(token)


def with_session_id(session_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a function with session context.

    All telemetry (traces, spans, events) generated within the function
    will include the session ID.

    Examples:
        Basic usage with function:
        ```python
        result = with_session_id('session-123', my_function, arg1, arg2)
        ```

        With async function:
        ```python
        result = await with_session_id('session-456', my_async_function)
        ```

        Wrapping AI operations:
        ```python
        async def ai_operation():
            response = await openai.chat.completions.create({
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
            emit_event('ai.response', {'tokens': response.usage.total_tokens})
            return response

        response = await with_session_id('chat-session', ai_operation)
        ```

    Args:
        session_id: Session identifier to include in all telemetry
        fn: Function to execute with session context
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    return with_properties({SESSION_ID: session_id}, fn, *args, **kwargs)


async def awith_properties(properties: dict[str, str], fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute an async function with OpenTelemetry context properties.

    Args:
        properties: Dictionary of properties to add to context
        fn: Async function to execute with the properties
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    if not properties:
        return await fn(*args, **kwargs)

    # Get existing properties and merge with new ones
    token = context.attach(new_context(properties))
    try:
        return await fn(*args, **kwargs)
    finally:
        context.detach(token)


async def awith_session_id(session_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute an async function with session context.

    All telemetry (traces, spans, events) generated within the function
    will include the session ID.

    Examples:
        Basic usage with async function:
        ```python
        result = await awith_session_id('session-123', my_async_function, arg1, arg2)
        ```

        Wrapping async AI operations:
        ```python
        async def ai_operation():
            response = await openai.chat.completions.create({
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
            emit_event('ai.response', {'tokens': response.usage.total_tokens})
            return response

        response = await awith_session_id('chat-session', ai_operation)
        ```

    Args:
        session_id: Session identifier to include in all telemetry
        fn: Async function to execute with session context
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    return await awith_properties({SESSION_ID: session_id}, fn, *args, **kwargs)


def session_context(session_id: str) -> Callable[[F], F]:
    """Decorator to add session context to a function.

    Args:
        session_id: Session identifier to include in all telemetry

    Returns:
        Decorator function

    Examples:
        ```python
        @session_context('my-session')
        def my_function():
            # All telemetry here will include session_id
            pass
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return with_session_id(session_id, func, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def asession_context(session_id: str) -> Callable[[F], F]:
    """Async decorator to add session context to an async function.

    Args:
        session_id: Session identifier to include in all telemetry

    Returns:
        Decorator function

    Examples:
        ```python
        @asession_context('my-async-session')
        async def my_async_function():
            # All telemetry here will include session_id
            pass
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await awith_session_id(session_id, func, *args, **kwargs)

        return async_wrapper  # type: ignore

    return decorator
