from wisort.config import Config
from pathlib import Path
import questionary


def move_conflict_resolution(
    name: str, parent: Path, target: Path, dest: Path, cfg: Config
) -> (Path, bool):
    def dfile() -> Path:
        return parent / name

    match cfg.orders.move_conflict_strategy:
        case "manual":
            mode = questionary.select(
                f"{dfile().relative_to(dest)} already exists in {
                    dest
                }. What do you want to do?",
                choices=["remove", "skip", "rename"],
            ).ask()
            ncfg = cfg
            ncfg.orders.move_conflict_strategy = mode
            return move_conflict_resolution(name, parent, target, dest, cfg)
        case "remove":
            return (dfile(), True)
        case "skip":
            return (dfile(), False)
        case "rename":
            name = questionary.text(
                f"A file named {dfile().relative_to(dest)} already exists. Rename to:",
                validate=lambda n: not dfile().exists(),
            ).ask()
            return (dfile(), True)
        case _:
            raise Exception(
                f"`{cfg.orders.move_conflict_strategy}` is only a placeholder move conflict resolution strategy"
            )
