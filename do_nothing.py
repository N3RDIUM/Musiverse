from os import devnull


def do_nothing(*args, **kwargs):
    """
    ## The Black Hole

    Send all args and kwargs to devnull
    """
    with open(devnull, "w") as f:
        f.write(f"{args} {kwargs}")
