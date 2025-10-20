import random


def exponential_backoff(
    e: Exception,
    retry_config: dict = {},
    base_delay: float | int = 1,
    exponential_factor: float | int = 2,
    max_delay_seconds: float | int = None,
    jitter_range: float | int = None,
    *args,
    **kwargs,
) -> int:
    """Retry handler increases the sleep time exponentially.

    How long to sleep is calculcated as::

        (base_delay x exponential_factor^attempt) + jitter

    Default parameters will result in a standard base-2 exponential increase::

        2, 4, 8, 16, 32, 64, 128....

    Args:
        e(Exception): The exception that occured. Defaults to Exception.
        retry_config(dict): The retry config from the decorator.
        base_delay_seconds(float | int): Base of the sleep calculation. Defaults to 1.
        exponential_factor(float | int): Multiplyer for the sleep calculation. Defaults to 2
        max_delay_seconds(float | int, optional): The max seconds to sleep between tries. If None no upper limit. Defaults to None.
        jitter_range(float | int, optional): If supplied, a random delay will be added between jitter_range and negative jitter_range (-jitter_range) with a step of 0.1 If None no jitter is added. Defaults to None

    Returns:
        float: Number of seconds to sleep

    """

    attempt = retry_config["attempt"]

    sleep_delay = base_delay * (exponential_factor**attempt)

    if max_delay_seconds and sleep_delay > max_delay_seconds:
        sleep_delay = max_delay_seconds

    if jitter_range and jitter_range > 0:
        # float between -jitter_max_seconds and jitter_max_seconds as a float added to the delay'
        # there are other functions to do this but to produce floats they are either slower or very convoluted.
        jitter = random.randint(-jitter_range * 10, jitter_range * 10) / 10
        sleep_delay += jitter

    # if we for some reason went below 0 we have to return 0
    if sleep_delay < 0:
        return 0

    return round(sleep_delay, 2)
