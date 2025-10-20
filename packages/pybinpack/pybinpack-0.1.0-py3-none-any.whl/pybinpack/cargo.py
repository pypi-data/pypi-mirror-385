from __future__ import annotations

from typing import TYPE_CHECKING

from python_metadata_parser import core_metadata

from pybinpack._util import toml_loads

if TYPE_CHECKING:
    from python_metadata_parser.pyproject import PyProject
    from typing_extensions import TypedDict

    Package = TypedDict(
        "Package",
        {
            "name": str,
            "version": str,
            "authors": list[str],
            "description": str,
            "documentation": str,
            "homepage": str,
            "repository": str,
            "keywords": list[str],
            "categories": list[str],
            "license": str,
            "exclude": list[str],
            "build": str,
            "autotests": bool,
            "edition": str,
            "rust-version": str,
        },
    )

    class CargoToml(TypedDict):
        package: Package


def cargo_to_pyproject(
    cargo_toml: str, name: str | None = None, version: str | None = None
) -> PyProject:
    """Convert Cargo.toml content to a Python project metadata dictionary."""
    cargo_data: CargoToml = toml_loads(cargo_toml)
    if "workspace" in cargo_data and "package" in cargo_data["workspace"]:  # type: ignore[typeddict-item]
        cargo_data["package"].update(cargo_data["workspace"]["package"])  # type: ignore[typeddict-item]
    authors = core_metadata.email_parser(None, ", ".join(cargo_data["package"]["authors"]))

    ret: PyProject = {
        "build-system": {"build-backend": "maturin", "requires": ["maturin>=1.7,<2.0"]},
        "project": {
            "name": name or cargo_data["package"]["name"],
            "version": version or cargo_data["package"]["version"],
            "description": cargo_data["package"]["description"].replace("\n", " ").strip(),
            "requires-python": ">=3.8",
            "authors": authors,
            "keywords": sorted(
                {
                    *cargo_data["package"].get("keywords", []),
                    *cargo_data["package"].get("categories", []),
                }
            ),
            "classifiers": [
                "Programming Language :: Rust",
                "Programming Language :: Python :: Implementation :: CPython",
                "Programming Language :: Python :: Implementation :: PyPy",
            ],
            "urls": {
                k.title(): cargo_data["package"][k]  # type: ignore[literal-required]
                for k in ("documentation", "homepage", "repository")
                if k in cargo_data["package"]
            },
            "readme": "README.md",
            "license": cargo_data["package"]["license"],
        },
        "tool": {},
    }

    ret["tool"]["maturin"] = {"bindings": "bin"}  # type: ignore[typeddict-unknown-key, unused-ignore]

    return ret
