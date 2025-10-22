# build script for signal extensions

import os
import platform
import shutil
import subprocess
from pathlib import Path

from packaging.tags import sys_tags


def main():
    if not shutil.which("go"):
        raise RuntimeError(
            "Cannot find the go executable in $PATH. "
            "Make you sure install golang, via your package manager or https://go.dev/dl/"
        )
    os.environ["PATH"] = os.path.expanduser("~/go/bin") + ":" + os.environ["PATH"]
    subprocess.run(["go", "install", "github.com/go-python/gopy@master"], check=True)
    subprocess.run(
        ["go", "install", "golang.org/x/tools/cmd/goimports@latest"], check=True
    )
    src_path = Path(".") / "slidgnal"
    subprocess.run(
        [
            "gopy",
            "build",
            "-output=generated",
            "-no-make=true",
            ".",
        ],
        cwd=src_path,
        check=True,
    )


if __name__ == "__main__":
    main()
