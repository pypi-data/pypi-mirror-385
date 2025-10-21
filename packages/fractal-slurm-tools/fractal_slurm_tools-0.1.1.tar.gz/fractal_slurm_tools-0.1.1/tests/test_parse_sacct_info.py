import pytest
from devtools import debug
from fractal_slurm_tools.errors import ERRORS
from fractal_slurm_tools.errors import ErrorType
from fractal_slurm_tools.parse_sacct_info import parse_sacct_info
from humanfriendly import InvalidSize


LINES_OK = (
    "22496092|__TEST_ECHO_TASK__|u20-cva0000-009||2025-07-22T08:44:09|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.140|1||||||||||||||||billing=1,cpu=1,mem=2000M,node=1|billing=1,cpu=1,mem=2000M,node=1|standard|normal|sbatch --parsable /fake/fractal//proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par-slurm-submit.sh|/fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__|4\n"  # noqa: E501
    "22496092.batch|batch|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.026|1|0|0|0|0.00M|0.00M|0|1064K|0|1064K|1820K|1820K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||||4\n"  # noqa: E501
    "22496092.extern|extern|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.001|1|0|0|0|0|0|0|0|0|0|0|0|0|00:00:00|00:00:00|0||billing=1,cpu=1,mem=2000M,node=1|||||4\n"  # noqa: E501
    "22496092.0|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1|0|0|0|0|0|0|0|0|0|266248K|266248K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /fake/fractal/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"  # noqa: E501
    "22496092.1|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1|0|0|0|0|0|0|0|0|0|266248K|266248K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /fake/fractal/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"  # noqa: E501
)
LINES_ONGOING = (
    "23314079|wrap|u20-cva0000-006||2025-09-16T10:01:07|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1||||||||||||||||billing=1,cpu=1,mem=1M,node=1|billing=1,cpu=1,mem=1M,node=1|standard|normal|sbatch --wrap=sleep 100000|/home/tcompa|41"  # noqa: E501
    "23314079.batch|batch|u20-cva0000-006|1|2025-09-16T10:01:08|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1|||||||||||||||||cpu=1,mem=1M,node=1|||||41"  # noqa: E501
    "23314079.extern|extern|u20-cva0000-006|1|2025-09-16T10:01:08|2025-09-16T10:01:08|Unknown|RUNNING|00:00:41|00:00:41|41|00:00:00|1|||||||||||||||||billing=1,cpu=1,mem=1M,node=1|||||41"  # noqa: E501
)
LINES_NEVER_STARTED = "22305195|Harmony_to_OME-Zarr|None assigned||2025-07-14T13:07:55|None|2025-07-14T13:07:57|CANCELLED by 646321139|00:00:00|00:00:00|0|00:00:00|0||||||||||||||||billing=1,cpu=1,mem=4000M,node=1||standard|normal|sbatch --parsable /xxx/proj_v2_0000115_wf_0000236_job_0000996_20250714_110751/0_harmony_to_ome_zarr|0"  # noqa: E501
LINES_NON_PARSABLE = (
    "22496092|__TEST_ECHO_TASK__|u20-cva0000-009||2025-07-22T08:44:09|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.140|1||||||||||||||||billing=1,cpu=1,mem=2000M,node=1|billing=1,cpu=1,mem=2000M,node=1|standard|normal|sbatch --parsable /fake/fractal//proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par-slurm-submit.sh|/fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__|4\n"  # noqa: E501
    "22496092.0|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1|0|0|0|0|0|0|0|0|0|266248AAAAAAAa|266248AAAA|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /fake/fractal/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"  # noqa: E501
)

LINES_MISSING_VALUES = (
    "22496092|__TEST_ECHO_TASK__|u20-cva0000-009||2025-07-22T08:44:09|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.140|1||||||||||||||||billing=1,cpu=1,mem=2000M,node=1|billing=1,cpu=1,mem=2000M,node=1|standard|normal|sbatch --parsable /fake/fractal//proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par-slurm-submit.sh|/fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__|4\n"  # noqa: E501
    "22496092.0|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1||||||||||266248K|266248K|0|||0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /fake/fractal/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /fake/fractal/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"  # noqa: E501
)


def test_parse_sacct_info():
    ERRORS.set_user(email="user@example.org")

    assert parse_sacct_info(job_id="9999", sacct_stdout=LINES_OK) == []
    assert ERRORS.tot_errors == 1

    assert (
        parse_sacct_info(job_id="23314079", sacct_stdout=LINES_ONGOING) == []
    )
    assert ERRORS.tot_errors == 2

    assert (
        parse_sacct_info(job_id="22305195", sacct_stdout=LINES_NEVER_STARTED)
        == []
    )
    assert ERRORS.tot_errors == 3

    list_task_info = parse_sacct_info(job_id="22496092", sacct_stdout=LINES_OK)
    assert len(list_task_info) == 2

    assert ERRORS.tot_errors_per_type(ErrorType.MISSING_VALUE) == 0
    list_task_info = parse_sacct_info(
        job_id="22496092", sacct_stdout=LINES_MISSING_VALUES
    )
    debug(ERRORS.tot_errors_per_type(ErrorType.MISSING_VALUE))
    assert ERRORS.tot_errors_per_type(ErrorType.MISSING_VALUE) > 0

    with pytest.raises(InvalidSize, match="Failed to parse size"):
        parse_sacct_info(job_id="22496092", sacct_stdout=LINES_NON_PARSABLE)
