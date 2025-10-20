from yet_another_retry import retry
from yet_another_retry.retry_handlers import exponential_backoff


@retry(
    retry_handler=exponential_backoff,
    tries=5,
    extra_kwargs={
        "base_delay": 1,
        "exponential_factor": 3,
        "max_delay_seconds": 1800,
        "jitter_range": 10,
    },
)
def my_function(retry_config: dict):
    print(f"This is attempt number: {retry_config['attempt']}")
    print(f"Last sleep was {retry_config['previous_delay']}")
    raise Exception("This is an exception")


my_function()
