from pathlib import Path
from wisort.config import Config, Library
from wisort.files.conflicts import move_conflict_resolution
import questionary


def move(map: dict[Path, Library], target: Path, cfg: Config):
    for src, lib in map.items():
        dest = Path(lib.destination).expanduser().absolute()

        if not dest.is_dir():
            raise Exception(
                f"Destination path {
                    dest.absolute()
                } is not a directory or does not exist"
            )

        # do some smart automations
        # dont move if in ignored
        # handle symlinks
        # unzip on move? -> smartly if zip has multiple elements zip to folder, otherwise zip to element directly

        # this doesnt support preserve file structure as of now

        parent: Path = dest
        name = src.name

        if (
            lib.flatten is not None and not lib.flatten
        ) or cfg.orders.move_strategy == "preserveFolders":
            parent = dest / src.relative_to(target).parent
            parent.mkdir(exist_ok=True, parents=True)

        df = parent / name

        if df.exists():
            # conflict resolution
            (df, m) = move_conflict_resolution(name, parent, target, dest, cfg)
            if not m:
                if cfg.args.verbose:
                    print(f"skipped {df.relative_to(dest)}")
                continue
        src.move(df)
