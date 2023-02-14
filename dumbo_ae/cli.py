import dataclasses
from pathlib import Path
from uuid import UUID

import requests
import typer
from dumbo_utils.console import console
from dumbo_utils.validation import validate


@dataclasses.dataclass(frozen=True)
class AppOptions:
    debug: bool = dataclasses.field(default=False)


app_options = AppOptions()
app = typer.Typer()


def is_debug_on():
    return app_options.debug


def run_app():
    try:
        app()
    except Exception as e:
        if is_debug_on():
            raise e
        else:
            console.print(f"[red bold]Error:[/red bold] {e}")


def version_callback(value: bool):
    if value:
        import importlib.metadata
        __version__ = importlib.metadata.version("dumbo-ae")
        console.print("dumbo-ae", __version__)
        raise typer.Exit()


@app.callback()
def main(
        debug: bool = typer.Option(False, "--debug", help="Don't minimize browser"),
        version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True,
                                     help="Print version and exit"),
):
    """
    CLI per il corso di Architettura degli Elaboratori.
    """


@app.command(name="checker")
def checker(
        of: str = typer.Option(..., help="UUID dell'esercizio"),
        code_file: Path = typer.Argument(..., help="Path al file con il codice ARM"),
) -> None:
    """
    Confronta i risultati ottenuti dal codice scritto con quelli attesi, su un insieme di test.
    """
    try:
        UUID(of)
    except ValueError:
        raise ValueError("Il formato UUID è sbagliato")

    validate("code_file", code_file.exists(), equals=True, help_msg="Il file non esiste")
    with open(code_file) as the_file:
        code = the_file.read()
    validate("code", code, max_len=99999, help_msg="Il file eccede il limite di 99.999 caratteri")

    with console.status("In attesa del risultato..."):
        response = requests.post('http://localhost:8000/quiz-api/v2/student/self-correct/', data={
            'exercise': of,
            'code': code,
        })
    validate("status_code", response.status_code, equals=200, help_msg="Interazione con il server fallita")
    console.print(response.json()['result'])
