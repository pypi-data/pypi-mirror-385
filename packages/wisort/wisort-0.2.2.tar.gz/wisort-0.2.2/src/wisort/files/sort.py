from pathlib import Path, PurePath
from pathspec import PathSpec
from wisort.config import Config


def by_extension(
    directory: Path,
    cfg: Config,
    spec: PathSpec = None,
) -> dict[str, list[Path]]:
    if spec is None:
        spec = PathSpec.from_lines("gitwildmatch", [])
    paths: dict[str, list[Path]] = {}
    if not directory.is_dir():
        return []

    # copy specs -> otherwise child .gitignores mutate parent gitignores because of recursion
    local_spec = PathSpec.from_lines("gitwildmatch", list(spec.patterns))

    for entry in directory.iterdir():
        if (
            entry.name == ".gitignore"
            and cfg.orders.honor_gitignore
            and not entry.is_dir()
        ):
            if cfg.args.verbose:
                print(f"reading {entry.absolute()}")
            patterns = entry.read_text().splitlines()
            local_spec += PathSpec.from_lines("gitwildmatch", patterns)
            continue

        # Ignore dotfiles
        if entry.name[0] == "." and cfg.orders.ignore_dotfiles:
            continue

        # recursively go through subdirs
        if entry.is_dir() and cfg.orders.recurse:
            ps = by_extension(entry, cfg, local_spec)
            for key, p in ps.items():
                paths.setdefault(key, []).extend(p)
            continue

        in_gitignore = local_spec.match_file(str(entry.relative_to(directory)))
        if len(entry.suffix) != 0 and not (in_gitignore and cfg.orders.honor_gitignore):
            paths.setdefault(entry.suffix[1:], []).append(entry)

    return paths
