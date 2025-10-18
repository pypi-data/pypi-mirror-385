from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Literal
import json
from os import environ


class Library(BaseModel):
    destination: str
    filetypes: list[str] | str
    flatten: Optional[bool] | str = Field(default=None)


class Orders(BaseModel):
    unzip: bool = Field(default=True)
    dedupe: bool = Field(default=False)

    # portal: symlinks
    # remove: removes
    # auto: symlinks if duplicate looks intentional: completely other name, etc.
    dedupe_strategy: Literal["portal", "remove", "auto"] = Field(default="portal")

    recurse: bool = Field(default=True)
    move_strategy: Literal["preserveFolders", "flatten"] = Field(default="flatten")
    move_conflict_strategy: Literal["manual", "remove", "skip", "rename", "mode"] = (
        Field(default="mode")
    )
    honor_gitignore: bool = Field(default=True)
    ignore_dotfiles: bool = Field(default=True)
    delete_empty_files: bool = Field(default=True)


class Arguments(BaseModel):
    quiet: bool = Field(default=False)
    verbose: bool = Field(default=False)
    force: bool = Field(default=False)


class Config(BaseModel):
    # spell = spell (dict[str])
    # spell = list of str -> e.g. list of filetypes
    # ...
    runes: dict[str, str | list[str] | bool | int]
    libraries: dict[str, Library] | list[Library]
    orders: Orders
    args: Arguments


def load(
    path: str = "./config.json",
) -> Config:
    with open(path, "r") as f:
        data = json.load(f)
    return Config(**data)


# TODO: make this into decorator that wraps name?
def overwrite_with_cli_arguments(
    quiet: Optional[bool], verbose: Optional[bool], force: Optional[bool]
):
    if quiet is not None:
        loaded.args.quiet = quiet
    if verbose is not None:
        loaded.args.verbose = verbose
    if force is not None:
        loaded.orders.move_conflict_strategy = "remove"
        loaded.args.force = force


config_home = (
    Path(environ["XDG_CONFIG_HOME"])
    if "XDG_CONFIG_HOME" in environ
    else Path(environ["HOME"] / ".config")
)
loaded = load(Path(environ["XDG_CONFIG_HOME"]) / "wisort/config.json")
