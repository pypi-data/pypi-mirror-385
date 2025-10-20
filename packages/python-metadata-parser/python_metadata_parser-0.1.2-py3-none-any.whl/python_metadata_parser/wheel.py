from __future__ import annotations

import ast
import email
import glob
import logging
import os
from typing import TYPE_CHECKING

from python_metadata_parser import core_metadata

if TYPE_CHECKING:
    from typing import TypedDict

    from python_metadata_parser.core_metadata import RawCoreMetadata

    class Data(TypedDict):
        purelib: list[str]
        platlib: list[str]
        headers: list[str]
        scripts: list[str]
        data: list[str]

    class DistInfoRecord(TypedDict):
        sign: str
        size: str

    class PythonFileInfo(TypedDict):
        imports: list[str]

    DistInfo = TypedDict(
        "DistInfo",
        {
            "entry_points.txt": dict[str, dict[str, str]],
            "WHEEL": dict[str, str],
            "RECORD": dict[str, DistInfoRecord],
            "METADATA": RawCoreMetadata,
            "top_level.txt": list[str],
        },
    )

    class WheelPackage(TypedDict):
        data: Data
        dist_info: DistInfo
        python_files: dict[str, PythonFileInfo]


logger = logging.getLogger(__name__)


def parse_wheel(io: bytes) -> dict[str, str]:
    msg = email.message_from_bytes(io)
    items = msg.items()
    if len(items) != len(set(items)):
        logger.info("DUPLICATE KEYS DETECTED: %s", items)
    return dict(msg.items())


def parse_entry_points(io: bytes) -> dict[str, dict[str, str]]:
    import configparser

    config = configparser.ConfigParser()
    config.read_string(io.decode())
    ret: dict[str, dict[str, str]] = {}
    for section in config.sections():
        ret[section] = dict(config[section])
    return ret


def parse_record(io: bytes) -> dict[str, DistInfoRecord]:
    ret: dict[str, DistInfoRecord] = {}
    for line in io.decode().splitlines():
        file, sign, size = line.split(",", maxsplit=2)
        ret[file] = {
            "sign": sign,
            "size": size,
        }
    return ret


def parse_dist_info(files: dict[str, bytes]) -> DistInfo:
    ret: DistInfo = {
        "entry_points.txt": parse_entry_points(files.pop("entry_points.txt", b"")),
        "RECORD": parse_record(files.pop("RECORD", b"")),
        "WHEEL": parse_wheel(files.pop("WHEEL", b"")),
        "METADATA": core_metadata.loads(files.pop("METADATA", b"")),
        "top_level.txt": files.pop("top_level.txt", b"").decode().splitlines(),
    }
    file_list = ret["RECORD"]
    top_level = (
        x.split("/", maxsplit=1)[0].split(".", maxsplit=1)[0]
        for x in file_list
        if x.endswith((".py", ".so"))
    )
    ret["top_level.txt"] = sorted({*ret["top_level.txt"], *top_level})
    for file in files:
        logger.debug("File Not Parsed: %s", file)
    return ret


def extract_python_info(f: bytes) -> PythonFileInfo:
    ret: list[str] = []
    try:
        tree = ast.parse(f)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                ret.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                ret.append(node.module)
    except Exception as e:  # noqa: BLE001
        logger.debug("Something went wrong: %s", str(e))
    return {"imports": sorted({x.split(".")[0] for x in ret})}


def load_wheel_package(wheel: str) -> WheelPackage:
    import zipfile

    data_dir: Data = {
        "purelib": [],
        "platlib": [],
        "headers": [],
        "scripts": [],
        "data": [],
    }
    dist_info_files: dict[str, bytes] = {}
    other: list[str] = []

    python_files: dict[str, PythonFileInfo] = {}

    with zipfile.ZipFile(wheel) as zp:
        for file in zp.namelist():
            if file.endswith("/"):
                # Its a directory, SKIP
                continue
            first, *rest = file.split("/", maxsplit=1)
            if first.endswith(".dist-info"):
                with zp.open(file) as f:
                    dist_info_files[rest[0]] = f.read()
            elif first.endswith(".data"):
                second, _rest = file.split("/", maxsplit=1)
                lst: list[str] = data_dir[second]  # type:ignore[literal-required]
                lst.append(file)
            else:
                other.append(file)
                if file.endswith(".py"):
                    with zp.open(file) as f:
                        python_files[file] = extract_python_info(f.read())

    new_var = parse_dist_info(dist_info_files)
    file_list = other
    top_level = (
        x.split("/", maxsplit=1)[0].split(".", maxsplit=1)[0]
        for x in file_list
        if x.endswith((".py", ".so"))
    )
    new_var["top_level.txt"] = sorted({*new_var["top_level.txt"], *top_level})

    return {
        "data": data_dir,  ##
        "dist_info": new_var,  ##
        "python_files": python_files,
    }


def parse_venv(venv: str) -> dict[str, DistInfo]:
    dist_infos = glob.iglob(os.path.join(venv, "lib", "python*", "site-packages", "*.dist-info"))
    ret: dict[str, DistInfo] = {}
    for i in dist_infos:
        dct = {}
        for f in glob.iglob(os.path.join(i, "**", "*"), recursive=True):
            if os.path.isdir(f):
                continue
            with open(f, "rb") as fp:
                dct[os.path.basename(f)] = fp.read()
        ret[os.path.basename(i)] = parse_dist_info(dct)
    return ret
