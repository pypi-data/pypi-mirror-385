import argparse as ap
import logging
import sys

from .. import __VERSION__
from ..errors import ERRORS
from ._parse_bulk import _parse_bulk


main_parser = ap.ArgumentParser(
    description=(
        "Parse `sacct` information for multiple Fractal jobs. "
        "[NOTE: Setting the environment variable `USE_LEGACY_FIELDS=1` "
        "provides compatibility with legacy SLURM (e.g. v15.08.7)]"
    ),
    allow_abbrev=False,
)

main_parser.add_argument(
    "--fractal-backend-url",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--emails",
    help=(
        "Comma-separated list of user emails, "
        "or path to a file with one email per line."
    ),
    type=str,
    required=True,
)
main_parser.add_argument(
    "--base-output-folder",
    type=str,
    help="Base folder for output files.",
    required=True,
)
main_parser.add_argument(
    "--first-month",
    help="First month to consider, in MM-YYYY format (e.g. 01-2025)",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--last-month",
    help="Last month to consider, in MM-YYYY format (e.g. 12-2025)",
    type=str,
    required=True,
)
main_parser.add_argument(
    "--verbose",
    help="If set, use DEBUG as a logging level.",
    action="store_true",
)


def _parse_arguments(sys_argv: list[str] | None = None) -> ap.Namespace:
    """
    Parse `sys.argv` or custom CLI arguments.

    Arguments:
        sys_argv: If set, overrides `sys.argv` (useful for testing).
    """
    if sys_argv is None:
        sys_argv = sys.argv[:]
    args = main_parser.parse_args(sys_argv[1:])
    return args


def main():
    args = _parse_arguments()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    fmt = "%(asctime)s; %(levelname)s; %(message)s"
    logging.basicConfig(level=logging_level, format=fmt)

    logging.debug(f"fractal-slurm-parse-bulk version: {__VERSION__}")
    logging.debug(f"{args=}")

    _parse_bulk(
        fractal_backend_url=args.fractal_backend_url,
        emails=args.emails,
        first_month=args.first_month,
        last_month=args.last_month,
        base_output_folder=args.base_output_folder,
    )

    if ERRORS.tot_errors > 0:
        logging.warning(ERRORS.get_report(verbose=args.verbose))
