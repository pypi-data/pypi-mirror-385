import argparse as ap
import logging
import sys
from pathlib import Path

from .. import __VERSION__
from ..errors import ERRORS
from ._aggregate import _aggregate


def _parse_arguments(sys_argv: list[str] | None = None) -> ap.Namespace:
    parser = ap.ArgumentParser(
        description="Aggregate per-user JSON stats files into a single CSV.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--base-input-folder",
        type=str,
        required=True,
        help=(
            "Folder that contains per-user subfolders with *_stats.json files."
        ),
    )
    parser.add_argument(
        "--base-output-folder",
        type=str,
        required=True,
        help="Folder where the aggregated CSV will be written.",
    )
    parser.add_argument(
        "--verbose",
        help="If set, use DEBUG logging.",
        action="store_true",
    )

    if sys_argv is None:
        sys_argv = sys.argv[:]
    args = parser.parse_args(sys_argv[1:])
    return args


def cli_entrypoint(
    base_input_folder: str,
    base_output_folder: str,
):
    base_input = Path(base_input_folder).resolve()
    base_output = Path(base_output_folder).resolve()

    if not base_input.is_dir():
        raise FileNotFoundError(f"Input folder does not exist: {base_input}")
    base_output.mkdir(parents=True, exist_ok=True)

    output_csv_path = base_output / f"{base_input.name}.csv"
    _aggregate(base_input, output_csv_path)


def main():
    args = _parse_arguments()

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    fmt = "%(asctime)s; %(levelname)s; %(message)s"
    logging.basicConfig(level=logging_level, format=fmt)

    logging.debug(f"fractal-slurm-aggregate version: {__VERSION__}")
    logging.debug(f"{args=}")

    cli_entrypoint(
        base_input_folder=args.base_input_folder,
        base_output_folder=args.base_output_folder,
    )

    if ERRORS.tot_errors > 0:
        logging.warning(ERRORS.get_report(verbose=args.verbose))
