from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Literal
    from typing import TypedDict
    from typing import Union

    from typing_extensions import NotRequired

    PyProjectBuildSystem = TypedDict(
        "PyProjectBuildSystem",
        {
            "requires": list[str],
            "build-backend": NotRequired[str],
            "backend-path": NotRequired[list[str]],
        },
    )

    class PyProjectTool(TypedDict): ...

    class PyProjectProjectAuthorOrMaintainer(TypedDict):
        name: NotRequired[str]
        email: NotRequired[str]

    # 2025/10/13
    # https://packaging.python.org/en/latest/specifications/pyproject-toml/
    PyProjectProject = TypedDict(
        "PyProjectProject",
        {
            "name": str,
            "version": NotRequired[str],
            "description": NotRequired[str],
            "readme": NotRequired[str],
            "requires-python": NotRequired[str],
            "license": NotRequired[str],
            "license-files": NotRequired[list[str]],
            "authors": NotRequired[list[PyProjectProjectAuthorOrMaintainer]],
            "maintainers": NotRequired[list[PyProjectProjectAuthorOrMaintainer]],
            "keywords": NotRequired[list[str]],
            "classifiers": NotRequired[list[str]],
            "urls": NotRequired[dict[str, str]],
            "scripts": NotRequired[dict[str, str]],
            "gui-scripts": NotRequired[dict[str, str]],
            "entry-points": NotRequired[dict[str, str]],
            "dependencies": NotRequired[list[str]],
            "optional-dependencies": NotRequired[dict[str, list[str]]],
            "dynamic": NotRequired[
                Sequence[
                    Literal[
                        "version",
                        "description",
                        "readme",
                        "requires-python",
                        "license",
                        "license-files",
                        "authors",
                        "maintainers",
                        "keywords",
                        "classifiers",
                        "urls",
                        "scripts",
                        "gui-scripts",
                        "entry-points",
                        "dependencies",
                        "optional-dependencies",
                    ]
                ]
            ],
        },
    )

    PyProject = TypedDict(
        "PyProject",
        {
            "build-system": NotRequired[PyProjectBuildSystem],
            "project": NotRequired[PyProjectProject],
            "tool": NotRequired[PyProjectTool],
            "dependency-groups": NotRequired[
                dict[str, list[Union[str, dict[Literal["include-group"], str]]]]
            ],
        },
    )


def loads(content: str) -> PyProject:
    """Load a pyproject.toml content"""
    import sys

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    return tomllib.loads(content)  # type: ignore[return-value, unused-ignore]


if __name__ == "__main__":
    with open("pyproject.toml", encoding="utf-8") as f:
        content = f.read()
    config = loads(content)
    import json

    print(json.dumps(config, indent=2))
