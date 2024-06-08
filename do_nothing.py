from os import devnull


def do_nothing(*args, **kwargs):
    with open(devnull, "w") as f:
        f.write(f"{args} {kwargs}")
