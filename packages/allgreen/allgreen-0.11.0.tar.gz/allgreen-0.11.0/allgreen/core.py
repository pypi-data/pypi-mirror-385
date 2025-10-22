import signal
import threading
import time
import traceback
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any


class CheckStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CheckResult:
    status: CheckStatus
    message: str | None = None
    error: str | None = None
    duration_ms: float | None = None
    skip_reason: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == CheckStatus.PASSED

    @property
    def failed(self) -> bool:
        return self.status in (CheckStatus.FAILED, CheckStatus.ERROR)

    @property
    def skipped(self) -> bool:
        return self.status == CheckStatus.SKIPPED


class AllgreenError(Exception):
    pass


class CheckAssertionError(AllgreenError):
    pass


class CheckTimeoutError(AllgreenError):
    pass


def execute_with_robust_timeout(func: Callable, timeout_seconds: float) -> Any:
    """
    Execute function with robust timeout enforcement.

    Uses worker thread execution with hard timeout that can interrupt
    most blocking operations including network calls, file I/O, etc.

    This is more reliable than signal-based or timer-flag approaches
    for truly blocking operations.

    Args:
        func: Function to execute
        timeout_seconds: Maximum time to allow execution

    Returns:
        Result of func()

    Raises:
        CheckTimeoutError: If execution exceeds timeout
        Any exception raised by func()
    """
    if timeout_seconds <= 0:
        return func()

    # For very short timeouts or main thread + Unix, use signals (fastest)
    is_main_thread = threading.current_thread() is threading.main_thread()
    if hasattr(signal, 'SIGALRM') and is_main_thread and timeout_seconds >= 0.1:
        # Signal-based timeout for quick execution in main thread
        with timeout_context(int(timeout_seconds) or 1):
            return func()
    else:
        # Worker thread with hard timeout for robust interruption
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="allgreen_timeout") as executor:
            future = executor.submit(func)
            try:
                return future.result(timeout=timeout_seconds)
            except FutureTimeoutError:
                # The worker thread will be abandoned and eventually cleaned up
                raise CheckTimeoutError(f"Check timed out after {timeout_seconds:.1f} seconds") from None


async def execute_with_async_timeout(func: Callable, timeout_seconds: float) -> Any:
    """
    Execute function with timeout in async context (for ASGI apps like FastAPI).

    Runs the sync function in a thread pool to avoid blocking the event loop,
    with hard timeout enforcement.
    """
    import asyncio

    if timeout_seconds <= 0:
        # Even without timeout, run in executor to avoid blocking event loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func)

    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="allgreen_async") as executor:
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(executor, func),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            raise CheckTimeoutError(f"Check timed out after {timeout_seconds:.1f} seconds") from None


@contextmanager
def timeout_context(seconds: int):
    """Context manager for timing out function execution."""
    # Check if we're in the main thread and signals are available
    is_main_thread = threading.current_thread() is threading.main_thread()

    if hasattr(signal, 'SIGALRM') and is_main_thread:
        # Unix systems in main thread - use signals (more reliable)
        def timeout_handler(signum, frame):
            raise CheckTimeoutError(f"Check timed out after {seconds} seconds")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Threading-based timeout (works in all threads and systems)
        timer_expired = threading.Event()

        def timeout_func():
            timer_expired.set()

        timer = threading.Timer(seconds, timeout_func)
        timer.start()

        try:
            start_time = time.time()
            yield
            # Check if we timed out during execution
            if timer_expired.is_set() or (time.time() - start_time) >= seconds:
                raise CheckTimeoutError(f"Check timed out after {seconds} seconds")
        finally:
            timer.cancel()


class Expectation:
    def __init__(self, actual: Any):
        self.actual = actual

    def to_eq(self, expected: Any) -> None:
        if self.actual != expected:
            raise CheckAssertionError(
                f"Expected {self.actual!r} to equal {expected!r}"
            )

    def to_be_greater_than(self, expected: int | float) -> None:
        if not (isinstance(self.actual, (int, float)) and self.actual > expected):
            raise CheckAssertionError(
                f"Expected {self.actual!r} to be greater than {expected!r}"
            )

    def to_be_less_than(self, expected: int | float) -> None:
        if not (isinstance(self.actual, (int, float)) and self.actual < expected):
            raise CheckAssertionError(
                f"Expected {self.actual!r} to be less than {expected!r}"
            )


def expect(actual: Any) -> Expectation:
    return Expectation(actual)


def make_sure(condition: Any, message: str | None = None) -> None:
    if not condition:
        raise CheckAssertionError(message or f"Expected {condition!r} to be truthy")


class Check:
    def __init__(
        self,
        description: str,
        func: Callable[[], None],
        timeout: int | None = None,
        only_in: str | list[str] | None = None,
        except_in: str | list[str] | None = None,
        if_condition: bool | Callable[[], bool] | None = None,
        run: str | None = None,
    ):
        self.description = description
        self.func = func
        self.timeout = timeout or 10  # Default 10 second timeout
        self.only_in = self._normalize_env_list(only_in)
        self.except_in = self._normalize_env_list(except_in)
        self.if_condition = if_condition
        self.run = run

    def _normalize_env_list(self, env: str | list[str] | None) -> list[str] | None:
        if env is None:
            return None
        if isinstance(env, str):
            return [env]
        return env

    def should_run(self, environment: str = "development") -> tuple[bool, str | None]:
        # Check environment conditions
        if self.only_in and environment not in self.only_in:
            return False, f"Only runs in {', '.join(self.only_in)}, current: {environment}"

        if self.except_in and environment in self.except_in:
            return False, f"Skipped in {environment} environment"

        # Check if condition
        if self.if_condition is not None:
            if callable(self.if_condition):
                try:
                    if not self.if_condition():
                        return False, "Custom condition not met"
                except Exception as e:
                    return False, f"Custom condition failed: {e}"
            elif not self.if_condition:
                return False, "Custom condition is False"

        return True, None

    def execute(self, environment: str = "development") -> CheckResult:
        # Check basic conditions (environment, if_condition)
        should_run, skip_reason = self.should_run(environment)
        if not should_run:
            return CheckResult(
                status=CheckStatus.SKIPPED,
                skip_reason=skip_reason
            )

        # Check rate limiting if specified
        if self.run:
            should_run_rate, skip_reason_rate, cached_result = self._check_rate_limit(environment)
            if not should_run_rate:
                # Return cached result if we have one, otherwise create skipped result
                if cached_result:
                    # Use the cached result's actual status (PASSED/FAILED/ERROR)
                    # but indicate it's cached in the message
                    original_message = cached_result.get('message', '')
                    cache_indicator = " (cached result)"
                    cached_message = f"{original_message}{cache_indicator}" if original_message else "Cached result"

                    return CheckResult(
                        status=CheckStatus(cached_result['status']),  # Use original status
                        message=cached_message,
                        error=cached_result.get('error'),
                        duration_ms=cached_result.get('duration_ms', 0),
                        skip_reason=None  # Not actually skipped, just cached
                    )
                else:
                    return CheckResult(
                        status=CheckStatus.SKIPPED,
                        skip_reason=skip_reason_rate
                    )

        start_time = time.time()
        try:
            # Execute with robust timeout enforcement
            execute_with_robust_timeout(self.func, self.timeout)

            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.PASSED,
                message="Check passed",
                duration_ms=duration_ms
            )

            # Cache result for rate-limited checks
            if self.run:
                self._cache_result(result, environment)

            return result

        except CheckTimeoutError as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.ERROR,
                error=str(e),
                message="Check timed out",
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

        except CheckAssertionError as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.FAILED,
                message=str(e),
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.ERROR,
                error=f"{type(e).__name__}: {e}",
                message=traceback.format_exc(),
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

    async def execute_async(self, environment: str = "development") -> CheckResult:
        """
        Execute check asynchronously without blocking the event loop.

        This is essential for ASGI applications like FastAPI.
        """
        # Check basic conditions (environment, if_condition)
        should_run, skip_reason = self.should_run(environment)
        if not should_run:
            return CheckResult(
                status=CheckStatus.SKIPPED,
                skip_reason=skip_reason
            )

        # Check rate limiting if specified
        if self.run:
            should_run_rate, skip_reason_rate, cached_result = self._check_rate_limit(environment)
            if not should_run_rate:
                # Return cached result if we have one, otherwise create skipped result
                if cached_result:
                    # Use the cached result's actual status (PASSED/FAILED/ERROR)
                    # but indicate it's cached in the message
                    original_message = cached_result.get('message', '')
                    cache_indicator = " (cached result)"
                    cached_message = f"{original_message}{cache_indicator}" if original_message else "Cached result"

                    return CheckResult(
                        status=CheckStatus(cached_result['status']),  # Use original status
                        message=cached_message,
                        error=cached_result.get('error'),
                        duration_ms=cached_result.get('duration_ms', 0),
                        skip_reason=None  # Not actually skipped, just cached
                    )
                else:
                    return CheckResult(
                        status=CheckStatus.SKIPPED,
                        skip_reason=skip_reason_rate
                    )

        start_time = time.time()
        try:
            # Execute with async timeout enforcement
            await execute_with_async_timeout(self.func, self.timeout)

            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.PASSED,
                message="Check passed",
                duration_ms=duration_ms
            )

            # Cache result for rate-limited checks
            if self.run:
                self._cache_result(result, environment)

            return result

        except CheckTimeoutError as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.ERROR,
                error=str(e),
                message="Check timed out",
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

        except CheckAssertionError as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.FAILED,
                message=str(e),
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = CheckResult(
                status=CheckStatus.ERROR,
                error=f"{type(e).__name__}: {e}",
                message=traceback.format_exc(),
                duration_ms=duration_ms
            )
            if self.run:
                self._cache_result(result, environment)
            return result

    def _check_rate_limit(self, environment: str | None = None) -> tuple[bool, str | None, dict | None]:
        """Check if this rate-limited check should run."""
        if not self.run:
            return True, None, None

        # Import locally to avoid circular imports
        from .rate_limiting import RateLimitConfig, get_rate_tracker

        try:
            config = RateLimitConfig(self.run)
            tracker = get_rate_tracker()

            # Create a namespaced key to avoid collisions between environments
            check_key = f"{environment}::{self.description}" if environment else self.description

            return tracker.should_run_check(check_key, config)
        except ValueError:
            # Invalid rate limit pattern - run the check but log error
            return True, None, None

    def _cache_result(self, result: CheckResult, environment: str | None = None) -> None:
        """Cache the result of a rate-limited check."""
        if not self.run:
            return

        from .rate_limiting import get_rate_tracker

        # Convert CheckResult to dict for caching
        result_dict = {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "duration_ms": result.duration_ms,
        }

        tracker = get_rate_tracker()

        # Use the same namespaced key as _check_rate_limit
        check_key = f"{environment}::{self.description}" if environment else self.description

        tracker.record_result(check_key, result_dict)


class CheckRegistry:
    def __init__(self):
        self._checks: list[Check] = []

    def register(self, check: Check) -> None:
        self._checks.append(check)

    def get_checks(self) -> list[Check]:
        return self._checks.copy()

    def clear(self) -> None:
        self._checks.clear()

    def run_all(self, environment: str = "development") -> list[tuple[Check, CheckResult]]:
        results = []
        for check in self._checks:
            result = check.execute(environment)
            results.append((check, result))
        return results

    async def run_all_async(self, environment: str = "development") -> list[tuple[Check, CheckResult]]:
        """
        Run all checks asynchronously without blocking the event loop.

        Essential for ASGI applications like FastAPI. Each check runs in
        a worker thread with robust timeout enforcement.
        """
        results = []
        for check in self._checks:
            result = await check.execute_async(environment)
            results.append((check, result))
        return results


# Global registry
_registry = CheckRegistry()


def check(
    description: str,
    timeout: int | None = None,
    only_in: str | list[str] | None = None,
    except_in: str | list[str] | None = None,
    if_condition: bool | Callable[[], bool] | None = None,
    run: str | None = None,
):
    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        check_obj = Check(
            description=description,
            func=func,
            timeout=timeout,
            only_in=only_in,
            except_in=except_in,
            if_condition=if_condition,
            run=run,
        )
        _registry.register(check_obj)
        return func

    return decorator


def get_registry() -> CheckRegistry:
    return _registry
