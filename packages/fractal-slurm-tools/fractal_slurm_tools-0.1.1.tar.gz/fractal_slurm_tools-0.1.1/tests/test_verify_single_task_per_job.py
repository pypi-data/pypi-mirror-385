import pytest
from fractal_slurm_tools.parse_bulk._parse_bulk import (
    _verify_single_task_per_job,
)


def test_verify_single_task_per_job():
    _verify_single_task_per_job([dict(NTasks=1)])
    with pytest.raises(NotImplementedError):
        _verify_single_task_per_job([dict(NTasks=2)])
