from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

functions: dict[str, Callable] = {}


def template_function(fn: Callable):
    functions[fn.__name__] = fn
    return fn


template_function(urlparse)


@template_function
def path_stem(path: str):
    return Path(path).stem
