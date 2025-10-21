# Some advance methods to extract tar files locally and remotely

import tarfile
from pathlib import Path

import fsspec
import json
from indexed_gzip import IndexedGzipFile
from typing import TypedDict
import pathlib
class TarMember(TypedDict):
    name: str
    offset: int
    offset_data: int
    size: int

class TarGzStreamer:

    def __init__(
            self, url: str, 
            directory_json: pathlib.Path,
            output_directory: pathlib.Path):
        