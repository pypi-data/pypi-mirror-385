import random
import threading
import time
from enum import Enum

from egse.log import logging
from egse.registry.client import RegistryClient
from egse.zmq_ser import connect_address

logger = logging.getLogger("egse.connect")

# random.seed(time.monotonic())  # uncomment for testing only, main application should set a seed.


def get_endpoint(
    service_type: str,
    protocol: str = None,
    hostname: str = None,
    port: int = 0,
):
    """
    Returns the endpoint for a service, either from the registry or by constructing
    it from protocol, hostname and port.

    If port is 0 (the default), attempt to retrieve the endpoint from the service registry.

    Args:
        service_type: The service type to look up in the registry.
        protocol: Protocol to use if constructing the endpoint.
        hostname: Hostname to use if constructing the endpoint.
        port: Port to use if constructing the endpoint.

    Returns:
        The endpoint string.

    Raises:
        RuntimeError: If no endpoint can be determined.
    """
    endpoint = None

    if port == 0:
        with RegistryClient() as reg:
            endpoint = reg.get_endpoint(service_type)
        if endpoint:
            logger.info(f"Endpoint for {service_type} found in registry: {endpoint}")
        else:
            logger.warning(f"No endpoint for {service_type} found in registry.")

    if not endpoint:
        if port == 0:
            raise RuntimeError(f"No service registered as {service_type} and no port provided.")
        endpoint = connect_address(protocol, hostname, port)
        logger.info(f"Endpoint constructed from protocol/hostname/port: {endpoint}")

    return endpoint


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CIRCUIT_OPEN = "circuit_open"  # Temporarily stopped trying


class BackoffStrategy(Enum):
    """
    Specifies the strategy for increasing the delay between retry attempts
    in backoff algorithms to reduce load and avoid overwhelming services.

    Strategies:
        EXPONENTIAL:
            The delay doubles with each retry attempt (e.g., 1s, 2s, 4s, 8s).
            This is the most widely used approach because it quickly reduces load on struggling systems.
        LINEAR:
            The delay increases by a fixed amount each time (e.g., 1s, 2s, 3s, 4s).
            This provides a more gradual reduction in request rate.
        FIXED:
            Uses the same delay between all retry attempts.
            Simple but less adaptive to system conditions.

    References:
        - AWS Architecture Blog: Exponential Backoff And Jitter
    """

    EXPONENTIAL = "exponential"
    """The delay doubles with each retry attempt (e.g., 1s, 2s, 4s, 8s). 
    This is the most widely used approach because it quickly reduces load on struggling systems."""
    LINEAR = "linear"
    """The delay increases by a fixed amount each time (e.g., 1s, 2s, 3s, 4s). 
    This provides a more gradual reduction in request rate."""
    FIXED = "fixed"
    """Uses the same delay between all retry attempts. Simple but less adaptive to system conditions."""


class JitterStrategy(Enum):
    """
    Specifies the strategy for applying jitter (randomization) to retry intervals
    in backoff algorithms to avoid synchronized retries and reduce load spikes.

    Strategies:
        NONE:
            No jitter is applied. The retry interval is deterministic.
        FULL:
            Applies full jitter by selecting a random value uniformly between 0 and the calculated interval.
            This maximizes randomness but can result in very short delays.
        EQUAL:
            Applies "equal jitter" as described in the AWS Architecture Blog.
            The interval is randomized within [interval/2, interval], ensuring a minimum delay of half the interval.
            Note: This is not the same as "a jitter of 50% around interval" (which would be [0.5 * interval, 1.5 * interval]).
        PERCENT_10:
            Applies a jitter of ±10% around the base interval, resulting in a random interval within [0.9 * interval, 1.1 * interval].

    References:
        - AWS Architecture Blog: Exponential Backoff And Jitter
    """

    NONE = "none"
    """No jitter is applied to the backoff."""
    FULL = "full"
    """Maximum distribution but can be too random with very short intervals."""
    EQUAL = "equal"
    """Best balance, maintains backoff properties while preventing synchronization."""
    PERCENT_10 = "10%"
    """Add a jitter of 10% around the base interval."""


def calculate_retry_interval(
    attempt_number,
    base_interval,
    max_interval,
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    jitter_strategy: JitterStrategy = JitterStrategy.EQUAL,
):
    """
    Calculates the next retry interval based on the given backoff and jitter strategies.

    Args:
        attempt_number (int): The current retry attempt (starting from 0).
        base_interval (float): The initial interval in seconds.
        max_interval (float): The maximum allowed interval in seconds.
        backoff_strategy (BackoffStrategy): Strategy for increasing the delay (exponential, linear, or fixed).
        jitter_strategy (JitterStrategy): Strategy for randomizing the delay to avoid synchronization.

    Returns:
        float: The computed retry interval in seconds.

    Notes:
        - See the docstrings for BackoffStrategy and JitterStrategy for details on each strategy.
        - Based on best practices from the AWS Architecture Blog: Exponential Backoff And Jitter.
    """

    if backoff_strategy == BackoffStrategy.EXPONENTIAL:
        interval = min(base_interval * (2**attempt_number), max_interval)
    elif backoff_strategy == BackoffStrategy.LINEAR:
        interval = min(base_interval + attempt_number, max_interval)
    else:
        interval = base_interval

    if jitter_strategy == JitterStrategy.NONE:
        return interval
    elif jitter_strategy == JitterStrategy.FULL:
        return random.uniform(0, interval)
    elif jitter_strategy == JitterStrategy.EQUAL:
        return interval / 2 + random.uniform(0, interval / 2)
    elif jitter_strategy == JitterStrategy.PERCENT_10:
        jitter_amount = interval * 0.1
        return interval + random.uniform(-jitter_amount, jitter_amount)

    return interval


class AsyncServiceConnector:
    """
    Asynchronous base class for robust service connection management with retry, backoff, and circuit breaker logic.

    This class is intended to be subclassed for managing persistent connections to external services
    (such as devices, databases, or remote APIs) that may be unreliable or temporarily unavailable.

    Features:
        - Automatic retry with configurable backoff and jitter strategies.
        - Circuit breaker to prevent repeated connection attempts after multiple failures.
        - Connection state tracking (disconnected, connecting, connected, circuit open).

    Usage:
        1. Subclass `AsyncServiceConnector` and override the `connect_to_service()` coroutine with your
           actual connection logic. Optionally, override `health_check()` for custom health verification.
        2. Store the actual connection object (e.g., socket, transport) as an instance attribute in your subclass.
        3. Use `attempt_connection()` to initiate connection attempts; it will handle retries and backoff automatically.
        4. Use `is_connected()` to check connection status.

    Example:
        class MyConnector(AsyncServiceConnector):
            async def connect_to_service(self):
                self.connection = await create_socket()
                return self.connection is not None

            def get_connection(self):
                return self.connection

    Note:
        The base class does not manage or expose the underlying connection object.
        Your subclass should provide a method or property to access it as needed.
    """

    def __init__(self, service_name: str):
        self.state = ConnectionState.DISCONNECTED
        self.last_attempt = 0
        self.base_interval = 1
        self.retry_interval = 1  # Start with 1 second
        self.max_retry_interval = 300  # Max 5 minutes
        self.failure_count = 0
        self.max_failures_before_circuit_break = 5
        self.circuit_break_duration = 60  # 1 minute
        self.circuit_opened_at = None

        self.service_name = service_name

    async def connect_to_service(self) -> bool:
        logger.warning(
            f"The connect_to_service() method is not implemented for {self.service_name}, connection will always fail."
        )
        return False

    async def health_check(self) -> bool:
        logger.warning(
            f"The health_check() method is not implemented for {self.service_name}, check will always return false."
        )
        return False

    def should_attempt_connection(self) -> bool:
        """Return True if we should attempt a new connection."""
        now = time.monotonic()

        # If circuit is open, check if we should close it
        if self.state == ConnectionState.CIRCUIT_OPEN:
            if now - self.circuit_opened_at > self.circuit_break_duration:
                self.state = ConnectionState.DISCONNECTED
                self.failure_count = 0
                self.retry_interval = 1
                return True
            return False

        # Regular backoff logic
        return now - self.last_attempt >= self.retry_interval

    async def attempt_connection(self):
        """Try to connect to the service.

        This will execute the callable argument `connect_to_service` that was passed
        into the constructor. That function shall return True when the connection
        succeeded, False otherwise.
        """
        if not self.should_attempt_connection():
            return

        self.state = ConnectionState.CONNECTING
        self.last_attempt = time.monotonic()

        try:
            success = await self.connect_to_service()

            if success:
                self.state = ConnectionState.CONNECTED
                self.failure_count = 0
                self.retry_interval = 1  # Reset backoff
                logger.info(f"Successfully connected to service {self.service_name}")
            else:
                # warning should have been logged by the connect_to_service() callable.
                self.handle_connection_failure()

        except Exception as exc:
            logger.warning(f"Failed to connect to service {self.service_name}: {exc}")
            self.handle_connection_failure()

    def handle_connection_failure(self):
        self.failure_count += 1

        # Open circuit breaker if too many failures
        if self.failure_count >= self.max_failures_before_circuit_break:
            self.state = ConnectionState.CIRCUIT_OPEN
            self.circuit_opened_at = time.time()
            logger.warning(
                f"Circuit breaker opened for service {self.service_name} after {self.failure_count} failures"
            )
        else:
            self.state = ConnectionState.DISCONNECTED
            self.retry_interval = calculate_retry_interval(
                self.failure_count,
                self.base_interval,
                self.max_retry_interval,
                BackoffStrategy.EXPONENTIAL,
                JitterStrategy.EQUAL,
            )
            logger.debug(f"retry_interval={self.retry_interval}")

    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED


class ServiceConnector:
    """
    Synchronous base class for robust service connection management with retry, backoff, and circuit breaker logic.

    This class is intended to be subclassed for managing persistent connections to external services
    (such as devices, databases, or remote APIs) that may be unreliable or temporarily unavailable.

    Features:
        - Automatic retry with configurable backoff and jitter strategies.
        - Circuit breaker to prevent repeated connection attempts after multiple failures.
        - Connection state tracking (disconnected, connecting, connected, circuit open).
        - Thread-safe operation using a lock for all state changes.

    Usage:
        1. Subclass `ServiceConnector` and override the `connect_to_service()` method with your
           actual connection logic. Optionally, override `health_check()` for custom health verification.
        2. Store the actual connection object (e.g., socket, transport) as an instance attribute in your subclass.
        3. Use `attempt_connection()` to initiate connection attempts; it will handle retries and backoff automatically.
        4. Use `is_connected()` to check connection status.

    Example:
        class MyConnector(ServiceConnector):
            def connect_to_service(self):
                self.connection = create_socket()
                return self.connection is not None

            def get_connection(self):
                return self.connection

    Note:
        The base class does not manage or expose the underlying connection object.
        Your subclass should provide a method or property to access it as needed.
    """

    def __init__(self, service_name: str):
        self.state = ConnectionState.DISCONNECTED
        self.last_attempt = 0
        self.base_interval = 1
        self.retry_interval = 1
        self.max_retry_interval = 300
        self.failure_count = 0
        self.max_failures_before_circuit_break = 5
        self.circuit_break_duration = 60
        self.circuit_opened_at = None
        self.service_name = service_name
        self._lock = threading.RLock()

    def connect_to_service(self) -> bool:
        logger.warning(
            f"The connect_to_service() method is not implemented for {self.service_name}, connection will always fail."
        )
        return False

    def health_check(self) -> bool:
        logger.warning(
            f"The health_check() method is not implemented for {self.service_name}, check will always return false."
        )
        return False

    def should_attempt_connection(self) -> bool:
        now = time.monotonic()
        with self._lock:
            if self.state == ConnectionState.CIRCUIT_OPEN:
                if now - self.circuit_opened_at > self.circuit_break_duration:
                    self.state = ConnectionState.DISCONNECTED
                    self.failure_count = 0
                    self.retry_interval = 1
                    return True
                return False
            return now - self.last_attempt >= self.retry_interval

    def attempt_connection(self):
        with self._lock:
            if not self.should_attempt_connection():
                return
            self.state = ConnectionState.CONNECTING
            self.last_attempt = time.monotonic()

        try:
            success = self.connect_to_service()
            with self._lock:
                if success:
                    self.state = ConnectionState.CONNECTED
                    self.failure_count = 0
                    self.retry_interval = 1
                    logger.info(f"Successfully connected to service {self.service_name}")
                else:
                    self.handle_connection_failure()
        except Exception as exc:
            logger.error(f"Failed to connect to service {self.service_name}: {exc}")
            with self._lock:
                self.handle_connection_failure()

    def handle_connection_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.max_failures_before_circuit_break:
            self.state = ConnectionState.CIRCUIT_OPEN
            self.circuit_opened_at = time.monotonic()
            logger.warning(
                f"Circuit breaker opened for service {self.service_name} after {self.failure_count} failures"
            )
        else:
            self.state = ConnectionState.DISCONNECTED
            self.retry_interval = calculate_retry_interval(
                self.failure_count,
                self.base_interval,
                self.max_retry_interval,
                BackoffStrategy.EXPONENTIAL,
                JitterStrategy.EQUAL,
            )
            logger.debug(f"retry_interval={self.retry_interval}")

    def is_connected(self) -> bool:
        with self._lock:
            return self.state == ConnectionState.CONNECTED
