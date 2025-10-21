import base64
import json
import zlib
from typing import Literal, TypeVar
import pathlib

T = TypeVar("T")

ZIPJSON_KEY = "base64(zip(o))"
ZIPJSON_TYPE = dict[Literal["base64(zip(o))"], str]


def json_zip(j: T) -> ZIPJSON_TYPE:
    """Compress a JSON-serializable dictionary into a smaller dictionary."""
    j = {ZIPJSON_KEY: base64.b64encode(zlib.compress(json.dumps(j).encode("utf-8"))).decode("ascii")}

    return j


def json_unzip(j: ZIPJSON_TYPE) -> list[dict]:
    """Decompress a dictionary created by json_zip back into the original dictionary."""
    j = zlib.decompress(base64.b64decode(j[ZIPJSON_KEY]))
    return json.loads(j)


def get_package_download_cache_dir() -> pathlib.Path:
    import astropy.config.paths

    return astropy.config.paths.get_cache_dir_path("phoenix4all") 

