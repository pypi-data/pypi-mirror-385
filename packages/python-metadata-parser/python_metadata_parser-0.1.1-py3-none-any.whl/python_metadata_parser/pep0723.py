from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator
    from typing import TypedDict

    from typing_extensions import NotRequired

    class ScriptMetadataTool(TypedDict): ...

    class ScriptMetadata(TypedDict):
        requires_python: str
        dependencies: list[str]
        tool: NotRequired[ScriptMetadataTool]


REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def stream(script: str) -> Iterator[tuple[str, str, re.Match[str]]]:
    """Read a stream of arbitrary metadata blocks."""
    import re

    for match in re.finditer(REGEX, script):
        yield (
            match.group("type"),
            "".join(
                line[2:] if line.startswith("# ") else line[1:]
                for line in match.group("content").splitlines(keepends=True)
            ),
            match,
        )


def read(script: str, name: str = "script") -> ScriptMetadata | None:
    """Read the metadata on Python 3.11 or higher"""
    matches = list(filter(lambda m: m[0] == name, stream(script)))
    if len(matches) > 1:
        msg = f"Multiple {name} blocks found"
        raise ValueError(msg)
    if len(matches) == 1:
        return tomllib.loads(matches[0][1])  # type: ignore[return-value, unused-ignore]
    return None


def add(script: str, dependency: str) -> str:
    """Modifying the content using the tomlkit library"""
    _type, content, match = next(filter(lambda x: x[0] == "script", stream(script)))
    try:
        import tomlkit
    except ImportError as e:
        msg = "tomlkit is required to add dependencies"
        raise ImportError(msg) from e

    config: ScriptMetadata = tomlkit.parse(content)  # type: ignore[assignment, unused-ignore]
    config["dependencies"].append(dependency)
    new_content = "".join(
        f"# {line}" if line.strip() else f"#{line}"
        for line in tomlkit.dumps(config).splitlines(keepends=True)
    )

    start, end = match.span("content")
    return script[:start] + new_content + script[end:]


if __name__ == "__main__":
    from textwrap import dedent

    sample_python_script = dedent("""\
        # /// script
        # requires-python = ">=3.11"
        # dependencies = [
        #   "requests<3",
        #   "rich",
        # ]
        # ///

        import requests
        from rich.pretty import pprint

        resp = requests.get("https://peps.python.org/api/peps.json")
        data = resp.json()
        pprint([(k, v["title"]) for k, v in data.items()][:10])
        """)
    # print(read(sample_python_script))

    for p in stream(sample_python_script):
        print(p)

    print(add(sample_python_script, "tomlkit"))
