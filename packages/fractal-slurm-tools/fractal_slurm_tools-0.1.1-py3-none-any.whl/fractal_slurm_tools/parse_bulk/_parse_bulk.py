import calendar
import json
import logging
import os
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path

import requests

from ..errors import ERRORS
from ..parse_sacct_info import parse_sacct_info
from ..parse_sacct_info import SLURMTaskInfo
from ..run_sacct_command import run_sacct_command
from ..sacct_parser_functions import _str_to_bytes

logger = logging.getLogger(__name__)

SACCT_BATCH_SIZE = 20

# Override default parsers with non-human-readable ones.
PARSERS = {
    field: _str_to_bytes
    for field in (
        "MaxDiskWrite",
        "MaxDiskRead",
        "AveDiskWrite",
        "AveDiskRead",
        "AveRSS",
        "MaxRSS",
        "AveVMSize",
        "MaxVMSize",
    )
}


def _get_months_range(
    first_month: str, last_month: str
) -> list[tuple[int, int]]:
    """
    Generate a range of months between two "MM-YYYY" strings.

    E.g.:
        >>> _get_months_range("11-2023", "02-2024")
        [(11, 2023), (12, 2023), (1, 2024), (2, 2024)]
    """
    start = datetime.strptime(first_month, "%m-%Y")
    stop = datetime.strptime(last_month, "%m-%Y")
    if start > stop:
        raise ValueError(f"{last_month=} is before {first_month=}.")
    months_diff = (
        (stop.year - start.year) * 12 + (stop.month - start.month) + 1
    )
    dates_range = [
        datetime(
            year=start.year + (start.month - 1 + i) // 12,
            month=(start.month - 1 + i) % 12 + 1,
            day=1,
        )
        for i in range(months_diff)
    ]
    return [(dt.month, dt.year) for dt in dates_range]


def _verify_single_task_per_job(outputs: list[SLURMTaskInfo]) -> None:
    """
    Verify the single-task-per-step assumption, fail otherwise.
    """
    for out in outputs:
        if out["NTasks"] > 1:
            logger.error(json.dumps(out, indent=2))
            raise NotImplementedError(
                "Single-task-per-step assumption violation "
                f"(NTasks={out['NTasks']})"
            )


def get_slurm_job_ids_user_month(
    *,
    fractal_backend_url: str,
    user_email: str,
    token: str,
    year: int,
    month: int,
) -> list[int]:
    headers = dict(Authorization=f"Bearer {token}")
    fractal_backend_url = fractal_backend_url.rstrip("/")

    # Get list of users
    resp = requests.get(
        f"{fractal_backend_url}/auth/users/",
        headers=headers,
        timeout=10,
    )
    if not resp.ok:
        logger.error("Could not get the list of users.")
        logger.error(f"Response status: {resp.status_code}.")
        logger.error(f"Response body: {resp.json()}.")
        sys.exit(1)

    # Find matching user
    try:
        user_id = next(
            user["id"] for user in resp.json() if user["email"] == user_email
        )
    except StopIteration:
        logger.error(f"Could not find user with {user_email=}.")
        sys.exit(1)

    # Get IDs for SLURM jobs
    _, num_days = calendar.monthrange(year=year, month=month)
    timestamp_min = datetime(year, month, 1, tzinfo=timezone.utc).isoformat()
    timestamp_max = datetime(
        year, month, num_days, 23, 59, 59, tzinfo=timezone.utc
    ).isoformat()
    request_body = dict(
        user_id=user_id,
        timestamp_min=timestamp_min,
        timestamp_max=timestamp_max,
    )
    logger.debug(f"{request_body=}")
    resp = requests.post(
        f"{fractal_backend_url}/admin/v2/accounting/slurm/",
        headers=headers,
        json=request_body,
        timeout=10,
    )
    if not resp.ok:
        logger.error("Could not get the IDs of SLURM jobs.")
        logger.error(f"Response status: {resp.status_code}.")
        logger.error(f"Request body: {request_body}")
        logger.error(f"Response body: {resp.json()}.")
        sys.exit(1)
    slurm_job_ids = resp.json()
    return slurm_job_ids


def _run_single_user_single_month(
    user_email: str,
    year: int,
    month: int,
    fractal_backend_url: str,
    base_output_folder: str,
    token: str,
) -> None:
    # Get IDs of SLURM jobs
    logger.info(
        f"Find SLURM jobs for {user_email=} (month {year:4d}/{month:02d})."
    )
    slurm_job_ids = get_slurm_job_ids_user_month(
        fractal_backend_url=fractal_backend_url,
        user_email=user_email,
        year=year,
        month=month,
        token=token,
    )
    logger.info(
        f"Found {len(slurm_job_ids)} SLURM jobs "
        f"for {user_email=} (month {year:4d}/{month:02d})."
    )
    outdir = Path(base_output_folder, user_email)
    outdir.mkdir(exist_ok=True, parents=True)
    with (outdir / f"{year:4d}_{month:02d}_slurm_jobs.json").open("w") as f:
        json.dump(slurm_job_ids, f, indent=2)
    # Parse sacct
    tot_num_jobs = len(slurm_job_ids)
    logger.info(
        f"Start processing {tot_num_jobs} SLURM jobs "
        f"(in batches of {SACCT_BATCH_SIZE} jobs at a time)."
    )
    tot_cputime_hours = 0.0
    tot_diskread_GB = 0.0
    tot_diskwrite_GB = 0.0
    tot_num_tasks = 0
    list_task_info = []
    for starting_ind in range(0, tot_num_jobs, SACCT_BATCH_SIZE):
        # Prepare comma-separated
        batch_job_ids = slurm_job_ids[
            starting_ind : starting_ind + SACCT_BATCH_SIZE
        ]
        batch_job_ids = list(map(str, batch_job_ids))

        # batch string
        slurm_job_ids_batch = ",".join(batch_job_ids)
        logger.debug(f">> {slurm_job_ids_batch=}")
        # Run `sacct` and parse its output
        sacct_stdout = run_sacct_command(job_string=slurm_job_ids_batch)
        for job_id in batch_job_ids:
            current_list_task_info = parse_sacct_info(
                job_id=job_id,
                sacct_stdout=sacct_stdout,
                task_subfolder_name=None,
                parser_overrides=PARSERS,
            )
            _verify_single_task_per_job(current_list_task_info)
            list_task_info.extend(current_list_task_info)

        # Aggregate statistics
        num_tasks = len(list_task_info)
        tot_num_tasks += num_tasks
        logger.debug(f">> {slurm_job_ids_batch=} has {num_tasks=}.")
        for task_info in list_task_info:
            cputime_hours = task_info["CPUTimeRaw"] / 3600
            diskread_GB = task_info["AveDiskRead"] / 1e9
            diskwrite_GB = task_info["AveDiskWrite"] / 1e9
            tot_cputime_hours += cputime_hours
            tot_diskread_GB += diskread_GB
            tot_diskwrite_GB += diskwrite_GB
    logger.info(
        f"{tot_cputime_hours=:.1f}, "
        f"{tot_diskread_GB=:.3f} "
        f"{tot_diskwrite_GB=:.3f}\n\n"
    )
    stats = dict(
        user_email=user_email,
        year=year,
        month=month,
        tot_number_jobs=len(slurm_job_ids),
        tot_number_tasks=tot_num_tasks,
        tot_cpu_hours=tot_cputime_hours,
        tot_diskread_GB=tot_diskread_GB,
        tot_diskwrite_GB=tot_diskwrite_GB,
    )
    with (outdir / f"{year:4d}_{month:02d}_stats.json").open("w") as f:
        json.dump(stats, f, indent=2)

    return


def _parse_bulk(
    fractal_backend_url: str,
    emails: str,
    first_month: str,
    last_month: str,
    base_output_folder: str,
) -> None:
    token = os.getenv("FRACTAL_TOKEN", None)
    if token is None:
        sys.exit("Missing env variable FRACTAL_TOKEN")

    if Path(emails).is_file():
        with Path(emails).open("r") as f:
            user_emails = f.read().splitlines()
    else:
        user_emails = emails.split(",")
    user_emails = [e.strip() for e in user_emails if e.strip() != ""]

    months_range = _get_months_range(
        first_month=first_month, last_month=last_month
    )

    for user_email in user_emails:
        ERRORS.set_user(email=user_email)
        for month, year in months_range:
            _run_single_user_single_month(
                user_email=user_email,
                year=year,
                month=month,
                fractal_backend_url=fractal_backend_url,
                base_output_folder=base_output_folder,
                token=token,
            )
