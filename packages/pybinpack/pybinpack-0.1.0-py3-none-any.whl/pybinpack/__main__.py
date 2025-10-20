from __future__ import annotations

import glob
import os
import shutil
import subprocess
import tempfile


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Clone, convert and build a Rust or Go project as a Python package."
    )
    parser.add_argument("target", help="Path or git URL of the target project.")
    parser.add_argument("--name", help="Name of the Python package.")
    parser.add_argument("--branch", help="Branch to clone.")
    parser.add_argument(
        "--tag-version", action="store_true", help="Use the latest git tag as version."
    )
    parser.add_argument("--output", help="Output file for metadata.", default="./dist/")
    args = parser.parse_args(argv)
    target: str = args.target
    name: str | None = args.name
    branch: str | None = args.branch
    tag_version: bool = args.tag_version
    output: str = os.path.abspath(args.output)

    os.makedirs(output, exist_ok=True)

    with tempfile.TemporaryDirectory() as tempdir:
        tmp_target = os.path.join(tempdir, "target")
        if os.path.isdir(target):
            # copy to temp dir
            shutil.copytree(target, tmp_target)
        else:
            subprocess.run(  # noqa: S603
                ("git", "clone", *(("--branch", branch) if branch else ()), target, tmp_target),
                check=True,
            )
        os.chdir(tmp_target)
        if os.path.exists("pyproject.toml"):
            print("pyproject.toml already exists, skipping conversion.")
            return 0
        if os.path.exists("Cargo.toml"):
            with open("Cargo.toml", encoding="utf-8") as f:
                cargo_toml = f.read()

            from pybinpack.cargo import cargo_to_pyproject

            version: str | None = None

            if tag_version:
                version = (
                    subprocess.run(
                        ("git", "describe", "--tags", "--abbrev=0"),
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    .stdout.strip()
                    .lstrip("v")
                )
                print(f"Using version from git tag: {version}")

            pyproject_data = cargo_to_pyproject(cargo_toml, name=name, version=version)
            import tomli_w

            with open("pyproject.toml", "wb") as f:
                tomli_w.dump(pyproject_data, f)
        elif os.path.exists("go.mod"):
            ...
        if not os.path.exists("pyproject.toml"):
            print("No pyproject.toml could be generated.")
            return 1
        result = subprocess.run(("uv", "build"), check=False)
        if result.returncode != 0:
            print("uv build failed.")
            return 1
        wheels = glob.glob("dist/*.whl")
        if not wheels:
            print("No wheels were built.")
            return 1
        wheel = wheels[0]
        subprocess.run(("python-metadata-parser", wheel, "--output", "raw"), check=True)  # noqa: S603
        shutil.copytree("dist", output, dirs_exist_ok=True)
    return 0


if __name__ == "__main__":
    # raise SystemExit(main(["https://github.com/BurntSushi/ripgrep.git"]))
    # raise SystemExit(main(["https://github.com/sharkdp/bat.git"]))
    # raise SystemExit(main(["https://github.com/GitoxideLabs/gitoxide.git"]))
    # raise SystemExit(main(["https://github.com/zellij-org/zellij.git"]))
    raise SystemExit(main())
