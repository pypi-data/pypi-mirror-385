import argparse as ap
import logging
import sys
from pathlib import Path

from .. import __VERSION__
from ..errors import ERRORS
from ._parse_single_job import _parse_single_job


main_parser = ap.ArgumentParser(
    description=(
        "Parse `sacct` information for a single Fractal job."
        "[NOTE: Setting the environment variable `USE_LEGACY_FIELDS=1` "
        "provides compatibility with legacy SLURM (e.g. v15.08.7)]"
    ),
    allow_abbrev=False,
)

main_parser.add_argument(
    "--fractal-job-id",
    type=int,
    help="Example: '1234'.",
    required=True,
)
main_parser.add_argument(
    "--jobs-folder",
    type=str,
    help="Base folder for job-log subfolders.",
    required=True,
)
main_parser.add_argument(
    "--output-folder",
    type=str,
    help="Folder for CSV/JSON output files.",
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

    logging.debug(f"fractal-slurm-parse-single-job version: {__VERSION__}")
    logging.debug(f"{args=}")

    _parse_single_job(
        fractal_job_id=args.fractal_job_id,
        output_folder=Path(args.output_folder),
        jobs_base_folder=args.jobs_folder,
    )

    if ERRORS.tot_errors > 0:
        logging.warning(ERRORS.get_report(verbose=args.verbose))
