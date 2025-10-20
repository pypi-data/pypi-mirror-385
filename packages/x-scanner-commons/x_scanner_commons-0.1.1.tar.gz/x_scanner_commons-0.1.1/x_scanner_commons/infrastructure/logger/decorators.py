"""Logging decorators for request tracking and performance monitoring."""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional

from x_scanner_commons.infrastructure.logger.logger import (
    get_logger,
    get_request_context,
    set_request_context,
)


def log_request(
    logger_name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
    log_time: bool = True,
) -> Callable:
    """Decorator to log function/method calls.
    
    Args:
        logger_name: Logger name (defaults to function module)
        log_args: Log function arguments
        log_result: Log function result
        log_time: Log execution time
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get logger
            name = logger_name or func.__module__
            logger = await get_logger(name)
            
            # Build log context
            context = {
                "function": func.__name__,
                "module": func.__module__,
            }
            
            if log_args:
                context["args"] = str(args)
                context["kwargs"] = str(kwargs)
            
            # Log request start
            await logger.info(f"Calling {func.__name__}", **context)
            
            # Execute function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                
                # Log success
                end_time = time.time()
                context["status"] = "success"
                
                if log_time:
                    context["duration"] = f"{end_time - start_time:.3f}s"
                
                if log_result:
                    context["result"] = str(result)
                
                await logger.info(f"Completed {func.__name__}", **context)
                
                return result
                
            except Exception as e:
                # Log error
                end_time = time.time()
                context["status"] = "error"
                context["error"] = str(e)
                
                if log_time:
                    context["duration"] = f"{end_time - start_time:.3f}s"
                
                await logger.error(
                    f"Error in {func.__name__}: {e}",
                    exc_info=(type(e), e, e.__traceback__),
                    **context,
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # For sync functions, run in event loop
            loop = asyncio.new_event_loop()
            try:
                # Convert to async and run
                async def run() -> Any:
                    name = logger_name or func.__module__
                    logger = await get_logger(name)
                    
                    context = {
                        "function": func.__name__,
                        "module": func.__module__,
                    }
                    
                    if log_args:
                        context["args"] = str(args)
                        context["kwargs"] = str(kwargs)
                    
                    await logger.info(f"Calling {func.__name__}", **context)
                    
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        end_time = time.time()
                        context["status"] = "success"
                        
                        if log_time:
                            context["duration"] = f"{end_time - start_time:.3f}s"
                        
                        if log_result:
                            context["result"] = str(result)
                        
                        await logger.info(f"Completed {func.__name__}", **context)
                        
                        return result
                        
                    except Exception as e:
                        end_time = time.time()
                        context["status"] = "error"
                        context["error"] = str(e)
                        
                        if log_time:
                            context["duration"] = f"{end_time - start_time:.3f}s"
                        
                        await logger.error(
                            f"Error in {func.__name__}: {e}",
                            exc_info=(type(e), e, e.__traceback__),
                            **context,
                        )
                        raise
                
                return loop.run_until_complete(run())
            finally:
                loop.close()
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_request_context(**context_kwargs: Any) -> Callable:
    """Decorator to set request context for a function.
    
    Args:
        **context_kwargs: Context fields to set
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Save current context
            old_context = get_request_context()
            
            try:
                # Set new context
                set_request_context(**context_kwargs)
                
                # Execute function
                return await func(*args, **kwargs)
                
            finally:
                # Restore old context
                set_request_context(**old_context)
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Save current context
            old_context = get_request_context()
            
            try:
                # Set new context
                set_request_context(**context_kwargs)
                
                # Execute function
                return func(*args, **kwargs)
                
            finally:
                # Restore old context
                set_request_context(**old_context)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_performance(
    logger_name: Optional[str] = None,
    threshold: float = 1.0,
) -> Callable:
    """Decorator to log slow function execution.
    
    Args:
        logger_name: Logger name
        threshold: Time threshold in seconds for warning
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
                
            finally:
                duration = time.time() - start_time
                
                if duration > threshold:
                    name = logger_name or func.__module__
                    logger = await get_logger(name)
                    
                    await logger.warning(
                        f"Slow function execution: {func.__name__}",
                        function=func.__name__,
                        module=func.__module__,
                        duration=f"{duration:.3f}s",
                        threshold=f"{threshold:.3f}s",
                    )
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
                
            finally:
                duration = time.time() - start_time
                
                if duration > threshold:
                    # Log in background
                    loop = asyncio.new_event_loop()
                    try:
                        async def log() -> None:
                            name = logger_name or func.__module__
                            logger = await get_logger(name)
                            
                            await logger.warning(
                                f"Slow function execution: {func.__name__}",
                                function=func.__name__,
                                module=func.__module__,
                                duration=f"{duration:.3f}s",
                                threshold=f"{threshold:.3f}s",
                            )
                        
                        loop.run_until_complete(log())
                    finally:
                        loop.close()
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator