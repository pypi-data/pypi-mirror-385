from pathlib import Path
from wisort.config import loaded, overwrite_with_cli_arguments
from wisort.files import move
from wisort.files.sort import by_extension
from wisort.files.move import lib_map
from wisort.files.dedupe import dedupe
from wisort.runes import use_runes
from typing import Optional
import typer
import questionary

app = typer.Typer(
    help="""
🪄 wisort — The Magical File Sorting Companion

Sort, cleanse, and enchant your files with a touch of magic.
"""
)


def target_arg():
    return typer.Argument(
        Path.cwd(),
        help="Directory to sort (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    )


def dry_run_opt():
    return typer.Option(None, "--dry-run", "-d", help="Simulate actions")


def verbose_opt():
    return typer.Option(None, "--verbose", "-v", help="Verbose output")


def force_opt():
    return typer.Option(None, "--force", "-f", help="Force moving")


def quiet_opt():
    return typer.Option(False, "--quiet", "-q", help="Suppress non-critical output")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command(
    help="🪶 The magical apprentice that sorts your library of spellbooks and as you tell him"
)
def apprentice(
    target: Path = target_arg(),
    verbose: Optional[bool] = verbose_opt(),
    quiet: Optional[bool] = quiet_opt(),
    force: Optional[bool] = force_opt(),
):
    use_runes()
    overwrite_with_cli_arguments(quiet, verbose, force)
    if loaded.args.verbose:
        print(loaded)
    if loaded.orders.move_conflict_strategy == "mode":
        loaded.orders.move_conflict_strategy = "manual"
    if not loaded.args.quiet:
        print("""
            The apprentice stubles into your condominium sleepily.
        """)
    if len(loaded.libraries) == 0:
        if not loaded.args.quiet:
            print("""
            After a considerable amount of time searching for a library in your humble abode the apprentice realises there isn't one.
            The apprentice sighs...
            'Where does master keep sending me?', he said to himself as he left your dwelling visibly frustrated.
            """)
        return

    sorted = by_extension(target, loaded)
    l_map = lib_map(loaded.libraries)

    # future refactor maybe: replace l_map[k] by format_dest(l_map[k], path) or something to make formatting of the filename and options like flatten easier to implement
    dest_map = {
        path.absolute(): l_map[k]
        for k, paths in sorted.items()
        if k in l_map
        for path in paths
    }

    if len(dest_map) == 0:
        if not loaded.args.quiet:
            print("""
            'Damn this place is very tidy', he thought.
                  """)
            return

    if not loaded.args.quiet:
        print(f"""
            Your {len(loaded.libraries.keys())} libraries excite the apprentice as he gazes at the rows of neatly stored books in all the bookshelves
        """)
        print("""
            After a brief moment of reviewing your books he snorts.
            'Oh man the people nowadays really don't have structure in their libraries. I can see why my master sent me'
            """)
        print(f"""
            Ensuing a quick inspection of your spellbooks he realised there where only {len(dest_map)} books that needed organizing.
        """)

    if loaded.args.verbose:
        for path, dest in dest_map.items():
            print(f"""          {path.relative_to(target)} → {dest}""")

    if not loaded.args.quiet:
        print("""
            He remembered a nice spell his master thaught him the previous day to levitate and move objects.
            After an astoundingly high number of attempts he finally managed to move all books to their destinations using the spell. 
            Unsatisfied he sighed: 'If only I had done this normally without spells I would long be home by now.'.
            """)

    if not loaded.args.quiet:
        print("""
            The apprentice comes up to you and asks:
            'Can I organize your libraries?'
            """)

    run = questionary.confirm("Start file organization?").ask()
    if not run:
        return

    move(dest_map, target, loaded)

    if loaded.orders.dedupe:
        pass

    return


@app.command(
    help="🔮 Keeps your spellbooks and library organized for you as he was thaught."
)
def magician(
    target: Path = target_arg(),
    verbose: bool = verbose_opt(),
    quiet: bool = quiet_opt(),
):
    overwrite_with_cli_arguments(quiet, verbose, None)
    if loaded.orders.move_conflict_strategy == "mode":
        loaded.orders.move_conflict_strategy = "rename"
    if not loaded.args.quiet:
        print("POOOOOOOOF! A magician appears out of thin air.")

    print("The magician is still an apprentice. He hasn't finished his studies yet")


@app.command(help="🧹 Full spellbook: sort, dedupe, and format code")
def witch(
    target: Path = target_arg(),
    verbose: bool = verbose_opt(),
    quiet: bool = quiet_opt(),
):
    overwrite_with_cli_arguments(quiet, verbose, None)
    use_runes()
    if loaded.args.verbose:
        print(loaded)
    dedupe(target, loaded)
