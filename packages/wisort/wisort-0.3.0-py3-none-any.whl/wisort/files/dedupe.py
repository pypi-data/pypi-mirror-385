from wisort.config import Config
from wisort.files.utils import creation_time, is_empty
from pathlib import Path
from blake3 import blake3


def find_dupes(target: Path, cfg: Config) -> dict[str, list[Path]]:
    dupes: dict[str, list[Path]] = {}
    for file in target.iterdir():
        if file.is_symlink():
            continue
        if file.is_dir() and cfg.orders.recurse:
            ds = find_dupes(file, cfg)
            for key, d in ds.items():
                dupes.setdefault(key, [d]).extend(d)
            continue

        if is_empty(file) and cfg.orders.delete_empty_files:
            file.unlink()
            continue
        file_bytes = file.read_bytes()
        digest = blake3(file_bytes).hexdigest()

        dupes.setdefault(digest, [file]).append(file)

    return dupes


def dedupe(target: Path, cfg: Config):
    dupes = find_dupes(target, cfg)
    n = 0
    for digest, duplicates in dupes.items():
        if len(duplicates) == 1:
            continue
        n += len(duplicates) - 1
        sorted_dupes = sorted(duplicates, key=lambda p: creation_time(p))
        original = sorted_dupes[0].resolve()
        for dupe in sorted_dupes:
            if original == dupe:
                continue
            match cfg.orders.dedupe_strategy:
                case "portal":
                    dupe.unlink()
                    dupe.symlink_to(sorted_dupes[0])
                    if cfg.args.verbose:
                        print(
                            f"symlinked {dupe.relative_to(target)} to {sorted_dupes[0]}"
                        )

                case "remove":
                    if cfg.args.verbose:
                        print(f"deleted {dupe.relative_to(target)}")
                    dupe.unlink()
    if cfg.args.verbose:
        print(f"{n} duplicates where taken care of")
