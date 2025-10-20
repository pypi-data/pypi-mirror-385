from __future__ import annotations

import email
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Optional

    from typing_extensions import Literal
    from typing_extensions import NotRequired
    from typing_extensions import TypedDict

    from python_metadata_parser.pyproject import PyProjectProject
    from python_metadata_parser.pyproject import PyProjectProjectAuthorOrMaintainer

    # Updated on 2025/10/13
    # https://packaging.python.org/en/latest/specifications/core-metadata/
    RawCoreMetadata = TypedDict(
        "RawCoreMetadata",
        {
            "Metadata-Version": Literal["1.0", "1.1", "1.2", "2.1", "2.2", "2.3", "2.4"],
            "Name": str,
            "Version": str,
            "Dynamic": NotRequired[list[str]],
            "Platform": NotRequired[list[str]],
            "Supported-Platform": NotRequired[list[str]],
            "Summary": NotRequired[str],
            "Description": NotRequired[str],
            "Description-Content-Type": NotRequired[str],
            "Keywords": NotRequired[str],
            "Author": NotRequired[str],
            "Author-email": NotRequired[str],
            "Maintainer": NotRequired[str],
            "Maintainer-email": NotRequired[str],
            "License": NotRequired[str],
            "License-Expression": NotRequired[str],
            "License-File": NotRequired[list[str]],
            "Classifier": NotRequired[list[str]],
            "Requires-Dist": NotRequired[list[str]],
            "Requires-Python": NotRequired[str],
            "Requires-External": NotRequired[list[str]],
            "Project-URL": NotRequired[list[str]],
            "Provides-Extra": NotRequired[list[str]],
            # Rarely Used Fields
            "Provides-Dist": NotRequired[list[str]],
            "Obsoletes-Dist": NotRequired[list[str]],
            # Deprecated Fields
            "Home-page": NotRequired[str],
            "Download-URL": NotRequired[str],
            "Requires": NotRequired[list[str]],
            "Provides": NotRequired[str],
            "Obsoletes": NotRequired[str],
            # Extra Field
            "Body": Optional[str],
        },
    )
    # History

__list_fields__ = {
    "Dynamic",
    "Platform",
    "Supported-Platform",
    "License-File",
    "Classifier",
    "Requires-Dist",
    "Requires-External",
    "Project-URL",
    "Provides-Extra",
    "Provides-Dist",
    "Obsoletes-Dist",
    "Requires",
}


def normalize(name: str) -> str:
    import re

    return re.sub(r"[-_.]+", "-", name).lower()


def loads(data: bytes | bytearray | str) -> RawCoreMetadata:
    if isinstance(data, str):
        msg = email.message_from_string(data)
    else:
        msg = email.message_from_bytes(data)

    ret: RawCoreMetadata = {}  # type: ignore[typeddict-item]
    for k, v in msg.items():
        if not isinstance(v, str):
            logger.debug("Was not parsed as a string! %s", v)
            v = str(v)  # noqa: PLW2901
        if k not in ret:
            ret[k] = v  # type: ignore[literal-required]
        else:
            previous = ret[k]  # type: ignore[literal-required]
            if not isinstance(previous, list):
                ret[k] = [previous]  # type: ignore[literal-required]
            ret[k].append(v)  # type: ignore[literal-required]

    ret["Body"] = str(msg.get_payload())

    for k, v in ret.items():  # type: ignore[assignment]
        if k in __list_fields__:
            if not isinstance(v, list):
                ret[k] = [v]  # type: ignore[literal-required]
        elif not isinstance(v, str):
            logger.error("%s should not be a list!", k)

    return ret


def update_deprecated_metadata_fields(data: RawCoreMetadata) -> RawCoreMetadata:
    data = data.copy()
    home_page = data.pop("Home-page", None)
    if home_page:
        logger.info("The 'Home-page' field is deprecated, use 'Project-URL' instead.")
        data.setdefault("Project-URL", []).append(f"Homepage, {home_page}")

    download_url = data.pop("Download-URL", None)
    if download_url:
        logger.info("The 'Download-URL' field is deprecated, use 'Project-URL' instead.")
        data.setdefault("Project-URL", []).append(f"Download, {download_url}")

    requires = data.pop("Requires", None)
    if requires:
        logger.info("The 'Requires' field is deprecated, use 'Requires-Dist' instead.")
        data.setdefault("Requires-Dist", []).extend(requires)

    provides = data.pop("Provides", None)
    if provides:
        logger.info("The 'Provides' field is deprecated, use 'Provides-Dist' instead.")
        data.setdefault("Provides-Dist", []).append(provides)

    obsoletes = data.pop("Obsoletes", None)
    if obsoletes:
        logger.info("The 'Obsoletes' field is deprecated, use 'Obsoletes-Dist' instead.")
        data.setdefault("Obsoletes-Dist", []).append(obsoletes)

    return data


def dumps(data: RawCoreMetadata) -> str:
    lines: list[str] = []
    for k, v in data.items():
        if k == "Body":
            continue
        if v is None:
            continue
        if isinstance(v, list):
            lines.extend(f"{k}: {vv}" for vv in v)
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n" + (data.get("Body") or "")


def email_parser(
    name_value: str | None,
    email_value: str | None,
) -> list[PyProjectProjectAuthorOrMaintainer]:
    import re

    items: list[PyProjectProjectAuthorOrMaintainer] = []
    if email_value:
        if name_value:
            items.append({"name": name_value, "email": email_value})
        else:
            pattern = re.compile(r"(?P<name>.*?)\s*<(?P<email>[^>]+)>")
            for email in email_value.split(","):
                match = pattern.search(email.strip())
                if match:
                    items.append(
                        match.groupdict()  # type: ignore[arg-type]
                    )
    return items


def to_pyproject_toml(data: RawCoreMetadata) -> PyProjectProject:
    """Convert core-metadata to pyproject.toml compatible dictionary"""
    import re
    from collections import defaultdict

    data = update_deprecated_metadata_fields(data)

    deps = defaultdict(list)
    for dep in data.get("Requires-Dist", []):
        if ";" in dep:
            lib, _, _specifiers = dep.partition("; ")
            specifiers = _specifiers.split(" and ")
            lib = lib.strip()
            extra = ""
            for spec in specifiers:
                _spec = spec.strip()
                if _spec.startswith("extra == "):
                    extra = _spec[10:-1]
                    continue
                lib += f"; {_spec.strip('()')}"
            deps[extra.strip()].append(lib.strip())
        else:
            deps[""].append(dep.strip())
    authors = email_parser(data.get("Author"), data.get("Author-email"))
    maintainers = email_parser(data.get("Maintainer"), data.get("Maintainer-email"))

    for item in authors:
        if item in maintainers:
            maintainers.remove(item)

    pyproject: PyProjectProject = {
        "name": normalize(data["Name"]),
        "version": data["Version"],
        "dynamic": data.get("Dynamic") or [],  # type: ignore[typeddict-item]
        "description": data.get("Summary") or "",
        "readme": "README.md",
        "requires-python": data.get("Requires-Python") or ">=3.10",
        "license": data.get("License-Expression") or data.get("License") or "MIT",
        "license-files": data.get("License-File") or [],
        "keywords": [x for x in re.split(r"[\s,]+", data.get("Keywords") or "") if x],
        "authors": authors,
        "maintainers": maintainers,
        "classifiers": data.get("Classifier") or [],
        "dependencies": deps.pop("", []) or [],
        "optional-dependencies": {**deps},
        "urls": {
            k.strip(): v.strip() for k, v in (u.split(",", 1) for u in data.get("Project-URL", []))
        },
        "scripts": {},
        "gui-scripts": {},
        "entry-points": {},
    }
    for it in (
        "dynamic",
        "license",
        "license-files",
        "maintainers",
        "optional-dependencies",
        "scripts",
        "gui-scripts",
        "entry-points",
    ):
        if not pyproject.get(it):
            pyproject.pop(it, None)  # type: ignore[misc]

    return pyproject


def load_whl_file(filename: str) -> RawCoreMetadata:
    import zipfile

    with zipfile.ZipFile(filename, "r") as z:
        dist_info = next((f for f in z.namelist() if f.endswith(".dist-info/METADATA")), None)
        if not dist_info:
            msg = "No .dist-info/METADATA file found in the wheel"
            raise ValueError(msg)
        with z.open(dist_info) as f:
            content = f.read()
            return loads(content)


if __name__ == "__main__":

    def download(url: str, headers: dict[str, str] | None = None) -> str:
        from urllib.request import Request
        from urllib.request import urlopen

        req = Request(url, headers=headers or {})  # noqa: S310

        with urlopen(req) as f:  # noqa: S310
            return f.read().decode("utf-8")

    def get_metadata(package_name: str, version: str | None = None) -> str:
        import json

        url = f"https://pypi.org/simple/{package_name}/"
        html = download(url, headers={"Accept": "application/vnd.pypi.simple.v1+json"})
        data = json.loads(html)

        version = version or data["versions"][-1]

        if version and version not in data["versions"]:
            msg = f"Version {version} not found for package {package_name}"
            raise ValueError(msg)
        file = next(
            (
                f
                for f in data["files"]
                if version in f["filename"]
                and f["filename"].endswith(".whl")
                and f["core-metadata"] is not False
            ),
            None,
        )

        if not file:
            msg = f"No wheel file with core-metadata found for package {package_name} version {version}"  # noqa: E501
            raise ValueError(msg)
        url = file["url"] + ".metadata"
        return download(url)

    # metadata = get_metadata("ai4_metadata", "2.4.1")
    metadata = get_metadata("lambda-dev-server")
    # import pathlib
    # metadata = pathlib.Path("dist/python_metadata_parser-0.1.dev1+gbe9c41129.d20251014.dist-info/METADATA").read_text(encoding="utf-8")  # noqa: E501

    from pprint import pprint

    # data = loads(metadata)
    data = load_whl_file(
        "dist/python_metadata_parser-0.1.dev1+gbe9c41129.d20251014-py3-none-any.whl"
    )
    pyproject = to_pyproject_toml(data)
    pprint(pyproject, indent=2, width=300, sort_dicts=False)

    # print(dumps(data))  # check round trip
    # pprint(data, indent=2, width=300, sort_dicts=False)
