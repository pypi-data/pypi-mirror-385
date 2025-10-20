from __future__ import annotations

import argparse
import json
import os
import re
import zipfile
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from urllib.request import Request
from urllib.request import urlopen

from python_metadata_parser import core_metadata

if TYPE_CHECKING:
    from python_metadata_parser.core_metadata import RawCoreMetadata


def download(url: str, headers: dict[str, str] | None = None) -> bytes:
    req = Request(url, headers=headers or {})  # noqa: S310

    with urlopen(req) as f:  # noqa: S310
        return f.read()


def get_package_links(package_name: str) -> list[str]:
    ret: list[str] = []
    index_url = os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple/").rstrip("/")
    url = f"{index_url}/{package_name}/"
    html = download(url, headers={"Accept": "application/vnd.pypi.simple.v1+json"})
    try:
        data = json.loads(html)
        for file in data["files"]:
            ret.append(file["url"])
            if file.get("core-metadata", False) is not False:
                ret.append(file["url"] + ".metadata")
    except json.JSONDecodeError as e:
        msg = f"Could not fetch package metadata for {package_name}: {e!s}"
        raise ValueError(msg) from e
    return ret


def main(argv: list[str] | tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse Python package metadata from various sources",
        epilog=(
            "Examples:\n"
            "  %(prog)s requests                    # Latest version from PyPI\n"
            "  %(prog)s requests==2.31.0            # Specific version from PyPI\n"
            "  %(prog)s https://example.com/pkg.whl # Direct URL to wheel file\n"
            "  %(prog)s ./dist/mypackage.whl        # Local wheel file\n"
            "  %(prog)s METADATA                    # Local METADATA file\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        help="Package name, package==version, URL to wheel/metadata file, or local file path",
        metavar="TARGET",
    )
    parser.add_argument(
        "--output",
        choices=["raw", "pyproject"],
        default="pyproject",
        help=(
            "Output format: 'raw' for original metadata structure, "
            "'pyproject' for pyproject.toml compatible format (default: %(default)s)"
        ),
    )
    args = parser.parse_args(argv)

    target: str = args.target
    meta: RawCoreMetadata
    with TemporaryDirectory() as temp_dir:
        if not os.path.isfile(target):
            if not target.startswith(("http://", "https://")):
                dep_name, *_version = re.split(r"[=<>]+", target, maxsplit=1)
                version = _version[0] if _version else ""
                links = get_package_links(dep_name)
                target = links[-1]
                for link in links:
                    base_name = os.path.basename(link)
                    if version in base_name and base_name.endswith((".whl", ".whl.metadata")):
                        target = link

            target_path = os.path.join(temp_dir, "downloaded.whl")
            with open(target_path, "wb") as f:
                response = download(target)
                f.write(response)
            target = target_path

        if zipfile.is_zipfile(target):
            meta = core_metadata.load_whl_file(target)
        else:
            with open(target, "rb") as f:
                meta = core_metadata.loads(f.read())

    output_obj = meta if args.output == "raw" else core_metadata.to_pyproject_toml(meta)

    print(json.dumps(output_obj, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
