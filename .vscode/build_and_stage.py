"""Build one OpenJoan preset and prepare its isolated runtime directory."""

import argparse
import filecmp
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


WORKSPACE = Path(__file__).resolve().parents[1]
ASSET_DIRECTORIES = (
    "Resource", "anim", "des", "font", "images", "int8x6", "item",
    "item_des", "map", "model", "movie", "music", "scenario", "script", "shader",
    "texture", "unit",
)


def stage_asset_tree(source, destination):
    """Share asset bytes without changing the paths seen by the game."""
    for directory, _, names in os.walk(source):
        original = Path(directory)
        local = destination / original.relative_to(source)
        local.mkdir(parents=True, exist_ok=True)
        for name in names:
            asset, target = original / name, local / name
            if target.exists() or target.is_symlink():
                continue
            if name.lower().endswith(".pln"):
                shutil.copy2(asset, target)
            else:
                target.hardlink_to(asset)


def stage(build_output, assets, runtime):
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "SAVE").mkdir(exist_ok=True)
    for name in ASSET_DIRECTORIES:
        stage_asset_tree(assets / name, runtime / name)

    ini = runtime / "openjoan.ini"
    if not ini.exists() and not ini.is_symlink():
        shutil.copy2(build_output / ini.name, ini)

    binary = build_output / "openjoan"
    staged_binary = runtime / binary.name
    # An actual copy keeps SDL_GetBasePath in this directory. Replace atomically
    # so staging never truncates an executable still running under GDB.
    if not staged_binary.is_file() or not filecmp.cmp(binary, staged_binary, shallow=False):
        with tempfile.TemporaryDirectory(dir=runtime, prefix=".stage-") as temporary:
            pending = Path(temporary) / binary.name
            shutil.copy2(binary, pending)
            pending.replace(staged_binary)
    print(f"Staged {staged_binary}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configuration", choices=("debug", "release", "tools"))
    args = parser.parse_args()
    assets = WORKSPACE / "play"
    config = "debug" if args.configuration == "tools" else args.configuration
    preset = f"vscode-linux-{config}"
    if args.configuration != "tools":
        if assets.is_symlink():
            parser.error("play must be a separate, local copy of the game assets")
        for name in ASSET_DIRECTORIES:
            directory = assets / name
            if not directory.is_dir() or directory.is_symlink():
                parser.error(f"expected a local asset directory at {directory}")

    subprocess.run(["cmake", "--preset", preset], cwd=WORKSPACE, check=True)
    build_preset = "vscode-linux-tools" if args.configuration == "tools" else preset
    subprocess.run(["cmake", "--build", "--preset", build_preset], cwd=WORKSPACE, check=True)
    if args.configuration != "tools":
        stage(WORKSPACE / "build" / preset / "src", assets, WORKSPACE / "run" / config)


if __name__ == "__main__":
    main()
