def print_backoff(details) -> None:
    """Print backoff details"""
    print(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details),
        "yellow",
    )


def client_error(e) -> bool:
    """Give up if status code 400 <= x < 500"""
    return 400 <= e.response.status_code < 500
