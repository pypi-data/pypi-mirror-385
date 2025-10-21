import logging
import os
from copy import deepcopy
from typing import Any
from typing import Callable
from typing import TypedDict

from .errors import ERRORS
from .errors import ErrorType
from .sacct_fields import DELIMITER
from .sacct_fields import SACCT_FIELDS
from .sacct_parser_functions import _isoformat_to_datetime
from .sacct_parsers import SACCT_FIELD_PARSERS

logger = logging.getLogger(__name__)

SLURMTaskInfo = dict[str, Any]

INDEX_JOB_NAME = SACCT_FIELDS.index("JobName")
INDEX_STATE = SACCT_FIELDS.index("State")
INDEX_JOB_ID = SACCT_FIELDS.index("JobID")

INDEX_JOB_SUBMIT = SACCT_FIELDS.index("Submit")
INDEX_JOB_START = SACCT_FIELDS.index("Start")
INDEX_JOB_END = SACCT_FIELDS.index("End")

INDEX_REQ_TRES = SACCT_FIELDS.index("ReqTRES")
INDEX_PARTITION = SACCT_FIELDS.index("Partition")
INDEX_QOS = SACCT_FIELDS.index("QOS")
INDEX_WORK_DIR = (
    SACCT_FIELDS.index("WorkDir") if os.getenv("USE_LEGACY_FIELDS") else None
)
SKIPPED_INDICES_FOR_MISSING_VALUES = {
    INDEX_REQ_TRES,
    INDEX_PARTITION,
    INDEX_QOS,
    INDEX_WORK_DIR,
}


class JobSubmitStartEnd(TypedDict):
    job_Submit: str
    job_Start: str
    job_End: str
    job_queue_time: int
    job_runtime: int


def get_job_submit_start_end_times(
    *,
    job_id: str,
    sacct_lines: list[str],
) -> JobSubmitStartEnd | None:
    if not isinstance(job_id, str):
        raise ValueError(
            "`get_job_submit_start_end_times` argument "
            f"`{job_id=}` is not a string."
        )

    main_job_line = next(
        (
            line
            for line in sacct_lines
            if line.split(DELIMITER)[INDEX_JOB_ID] == job_id
        ),
        None,
    )
    if main_job_line is None:
        ERRORS.add_error(ErrorType.JOB_NOT_FOUND)
        logger.debug(f"Could not find main sacct line for {job_id=}.")
        return None
    main_job_line_fields = main_job_line.split(DELIMITER)
    job_Submit = main_job_line_fields[INDEX_JOB_SUBMIT]
    job_Start = main_job_line_fields[INDEX_JOB_START]
    job_End = main_job_line_fields[INDEX_JOB_END]

    if job_Start == "None":
        logger.debug(f"{job_id=} has {job_Start=}.")
        ERRORS.add_error(ErrorType.JOB_NEVER_STARTED)
        return None

    if job_End == "Unknown":
        logger.debug(f"{job_id=} has {job_End=}.")
        ERRORS.add_error(ErrorType.JOB_ONGOING)
        return None

    job_queue_time = (
        _isoformat_to_datetime(job_Start) - _isoformat_to_datetime(job_Submit)
    ).total_seconds()
    job_runtime = (
        _isoformat_to_datetime(job_End) - _isoformat_to_datetime(job_Start)
    ).total_seconds()

    return dict(
        job_Submit=job_Submit,
        job_Start=job_Start,
        job_End=job_End,
        job_queue_time=job_queue_time,
        job_runtime=job_runtime,
    )


def parse_sacct_info(
    job_id: int,
    sacct_stdout: str,
    task_subfolder_name: str | None = None,
    parser_overrides: dict[str, Callable] | None = None,
) -> list[SLURMTaskInfo]:
    """
    Parse `sacct` output for a single SLURM job

    Args:
        job_id: A single SLURM-job ID.
        sacct_stdout:
            The output of `sacct -j {job_ids_string} [...]`, where
            `job_id_string` includes `job_id` and possibly other job IDs.
        task_subfolder_name:
            Name of task subfolder, which is included in the output.
        parser_overrides:
            Overrides of the parser defined in `SACCT_FIELD_PARSERS`

    Returns:
        List of `SLURMTaskInfo` dictionaries (one per `python` line in
        `sacct` output).
    """
    logger.debug(f"START, with {job_id=}.")

    # Update parsers, if needed
    actual_parsers = deepcopy(SACCT_FIELD_PARSERS)
    actual_parsers.update(parser_overrides or {})

    # Split `sacct` output into lines
    lines = sacct_stdout.splitlines()

    job_info = get_job_submit_start_end_times(job_id=job_id, sacct_lines=lines)
    if job_info is None:
        return []

    list_task_info = []
    for line in lines:
        line_items = line.split(DELIMITER)
        # Skip non-Python steps/tasks
        if "python" not in line_items[INDEX_JOB_NAME]:
            continue
        # Skip running steps
        if line_items[INDEX_STATE] == "RUNNING":
            continue
        # Skip lines which are not like `JobID=1234.0` (because they
        # correspond to a different job)
        if line_items[INDEX_JOB_ID].split(".")[0] != job_id:
            continue
        # Parse all fields
        try:
            task_info = {
                SACCT_FIELDS[ind]: actual_parsers[SACCT_FIELDS[ind]](item)
                for ind, item in enumerate(line_items)
            }
        except Exception as e:
            logger.error(f"Could not parse {line=}")
            for ind, item in enumerate(line_items):
                logger.debug(f"'{SACCT_FIELDS[ind]}' raw item: {item}")
                logger.debug(
                    f"'{SACCT_FIELDS[ind]}' parsed item: "
                    f"{actual_parsers[SACCT_FIELDS[ind]](item)}"
                )
            raise e

        # Enrich `sacct` output for single-step lines with job-level info
        task_info.update(job_info)

        # Add task subfolder name to `sacct` info
        if task_subfolder_name is not None:
            task_info.update(dict(task_subfolder=task_subfolder_name))

        list_task_info.append(task_info)

    return list_task_info
