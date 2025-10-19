#!/usr/bin/env python
# coding: UTF-8

import gzip
import json
from pathlib import Path
from typing import Union, TypeAlias

import pydicom


def list_dicom_files(dir_path: str | Path) -> list[Path]:
    dir_path = Path(dir_path)
    return [p for p in dir_path.glob("**/*") if p.is_file() and pydicom.misc.is_dicom(p)]


def read_json(path: Path, is_gzip=False) -> dict | list[dict]:
    path = Path(path)

    if is_gzip:
        with gzip.open(str(path) + ".gz", "rt", encoding="utf-8") as f:
            return json.load(f)
    else:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    raise FileNotFoundError(f"File not found: {path} or {path}.gz")


def write_json(path: Path,
               obj: dict | list[dict],
               write_json_fmt=True,
               write_gzip_fmt=False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if write_json_fmt:
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    if write_gzip_fmt:
        with gzip.open(str(path) + ".gz", "wt", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)


def write_binary(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(data)
