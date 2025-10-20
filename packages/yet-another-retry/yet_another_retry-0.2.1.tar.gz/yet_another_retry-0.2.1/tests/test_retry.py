from yet_another_retry import retry


def test_retry():

    try:
        assert function_to_retry()
    except:
        assert False


@retry()
def function_to_retry(retry_config: dict):

    attempt = retry_config["attempt"]
    tries = retry_config["tries"]
    if attempt == tries:
        return True

    raise Exception("This is an exception")
