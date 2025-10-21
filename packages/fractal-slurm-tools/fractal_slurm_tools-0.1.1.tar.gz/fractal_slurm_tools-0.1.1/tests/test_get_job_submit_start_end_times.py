import pytest
from fractal_slurm_tools.errors import ERRORS
from fractal_slurm_tools.errors import ErrorType
from fractal_slurm_tools.parse_sacct_info import get_job_submit_start_end_times

LINES_1 = (
    "22496092|__TEST_ECHO_TASK__|u20-cva0000-009||2025-07-22T08:44:09|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.140|1||||||||||||||||billing=1,cpu=1,mem=2000M,node=1|billing=1,cpu=1,mem=2000M,node=1|standard|normal|sbatch --parsable /fake/fractal//proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par-slurm-submit.sh|/fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__|4\n"  # noqa: E501
    "22496092.batch|batch|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.026|1|0|0|0|0.00M|0.00M|0|1064K|0|1064K|1820K|1820K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||||4\n"  # noqa: E501
    "22496092.extern|extern|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.001|1|0|0|0|0|0|0|0|0|0|0|0|0|00:00:00|00:00:00|0||billing=1,cpu=1,mem=2000M,node=1|||||4\n"  # noqa: E501
    "22496092.0|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1|0|0|0|0|0|0|0|0|0|266248K|266248K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /fake/fractal/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"  # noqa: E501
).splitlines()

LINES_2_ONGOING = (
    "23314079|wrap|u20-cva0000-006||2025-09-16T10:01:07|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1||||||||||||||||billing=1,cpu=1,mem=1M,node=1|billing=1,cpu=1,mem=1M,node=1|standard|normal|sbatch --wrap=sleep 100000|/home/tcompa|41"  # noqa: E501
    "23314079.batch|batch|u20-cva0000-006|1|2025-09-16T10:01:08|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1|||||||||||||||||cpu=1,mem=1M,node=1|||||41"  # noqa: E501
    "23314079.extern|extern|u20-cva0000-006|1|2025-09-16T10:01:08|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1|||||||||||||||||billing=1,cpu=1,mem=1M,node=1|||||41"  # noqa: E501
).splitlines()

LINES_3_NEVER_STARTED = (
    "22305195|Harmony_to_OME-Zarr|None assigned||2025-07-14T13:07:55|None|2025-07-14T13:07:57|CANCELLED by 646321139|00:00:00|00:00:00|0|00:00:00|0||||||||||||||||billing=1,cpu=1,mem=4000M,node=1||standard|normal|sbatch --parsable /xxx/proj_v2_0000115_wf_0000236_job_0000996_20250714_110751/0_harmony_to_ome_zarr|0"  # noqa: E501
).splitlines()


def test_get_job_submit_start_end_times():
    user_email = "foo@bar.xy"
    ERRORS.set_user(email=user_email)
    assert ERRORS._errors == {}

    with pytest.raises(ValueError, match="is not a string"):
        get_job_submit_start_end_times(
            job_id=123,
            sacct_lines=LINES_1,
        )

    get_job_submit_start_end_times(
        job_id="9999999",
        sacct_lines=LINES_1,
    )
    assert ERRORS._errors == {(user_email, ErrorType.JOB_NOT_FOUND): 1}

    job_info = get_job_submit_start_end_times(
        job_id="22496092",
        sacct_lines=LINES_1,
    )
    assert abs(job_info["job_queue_time"] - 5.0) < 1e-10
    assert abs(job_info["job_runtime"] - 4.0) < 1e-10

    get_job_submit_start_end_times(
        job_id="9999999",
        sacct_lines=LINES_1,
    )
    assert ERRORS._errors == {(user_email, ErrorType.JOB_NOT_FOUND): 2}

    job_info = get_job_submit_start_end_times(
        job_id="23314079",
        sacct_lines=LINES_2_ONGOING,
    )
    assert job_info is None
    assert ERRORS._errors == {
        (user_email, ErrorType.JOB_NOT_FOUND): 2,
        (user_email, ErrorType.JOB_ONGOING): 1,
    }

    job_info = get_job_submit_start_end_times(
        job_id="22305195",
        sacct_lines=LINES_3_NEVER_STARTED,
    )
    assert job_info is None
    assert ERRORS._errors == {
        (user_email, ErrorType.JOB_NOT_FOUND): 2,
        (user_email, ErrorType.JOB_ONGOING): 1,
        (user_email, ErrorType.JOB_NEVER_STARTED): 1,
    }
