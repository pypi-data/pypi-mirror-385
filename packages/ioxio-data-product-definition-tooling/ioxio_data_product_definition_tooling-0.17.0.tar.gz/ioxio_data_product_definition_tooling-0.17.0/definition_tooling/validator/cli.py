import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

from rich import print
from typer import Argument, Option, Typer

from definition_tooling.log import print_error, print_success, print_table
from definition_tooling.validator.core import DefinitionValidator
from definition_tooling.validator.errors import ValidatorError

cli = Typer()


def print_dashes(char="-", length=79):
    print(char * length)


@contextmanager
def header():
    print_dashes(char="=")
    yield
    print_dashes(char="=")


@cli.command(help="Validate Data Product definitions")
def cli_validate_specs(
    path: str = Argument(..., help="Path to directory with definitions in JSON format"),
    authorization_headers: bool = Option(
        False,
        help="Add headers for authorization ('Authorization' and "
        "'X-Authorization-Provider')",
    ),
    consent_headers: bool = Option(
        False,
        help="Add headers for consent ('X-Consent-Token')",
    ),
):
    sys.exit(validate_specs(Path(path), authorization_headers, consent_headers))


def validate_specs(
    path: Path, authorization_headers: bool, consent_headers: bool
) -> int:
    with header():
        print(f"OpenAPI specs root path: {path}")

    passed, failed = 0, 0
    for spec_path in path.glob("**/*.json"):
        print(f"File: {spec_path}")
        try:
            DefinitionValidator(
                spec_path=spec_path,
                root_path=path,
                authorization_headers=authorization_headers,
                consent_headers=consent_headers,
            ).validate()
        except Exception as exc:
            if isinstance(exc, ValidatorError):
                detail = ": " + str(exc) if str(exc) else ""
                print(f"{exc.__class__.__name__}{detail}")
            else:
                print("\n", traceback.format_exc())
            print_error("[FAILED]")
            failed += 1
        else:
            print_success("[PASSED]")
            passed += 1
        print_dashes("-")

    print_table(
        ["Summary", "#"],
        [
            ["Passed", passed],
            ["Failed", failed],
            ["Total", passed + failed],
        ],
        "green" if not failed else "red",
    )

    return 1 if failed else 0
