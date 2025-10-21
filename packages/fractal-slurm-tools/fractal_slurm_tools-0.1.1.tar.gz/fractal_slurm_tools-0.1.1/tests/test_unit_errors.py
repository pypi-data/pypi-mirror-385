import pytest
from fractal_slurm_tools.errors import ERRORS
from fractal_slurm_tools.errors import ErrorType


def test_ERRORS_cleanup_1():
    assert ERRORS._current_user is None
    ERRORS.set_user(email="asd")
    assert ERRORS._current_user == "asd"


def test_ERRORS_cleanup_2():
    assert ERRORS._current_user is None


def test_ERRORS():
    assert ERRORS._errors == {}
    assert "No errors" in ERRORS.get_report()
    assert ERRORS.tot_errors == 0

    with pytest.raises(ValueError, match="without `_current_user`"):
        ERRORS.add_error(ErrorType.JOB_NEVER_STARTED)
    assert ERRORS._existing_users == set()
    EMAIL = "user@example.org"
    ERRORS.set_user(email=EMAIL)
    assert ERRORS._existing_users == set()

    ERRORS.add_error(ErrorType.JOB_NEVER_STARTED)
    ERRORS.add_error(ErrorType.JOB_ONGOING)
    ERRORS.add_error(ErrorType.JOB_NEVER_STARTED)
    assert ERRORS._existing_users == {EMAIL}
    assert ERRORS.tot_errors == 3

    with pytest.raises(ValueError, match="Unknown error type"):
        ERRORS.add_error("invalid")

    assert ERRORS._errors == {
        (EMAIL, ErrorType.JOB_NEVER_STARTED): 2,
        (EMAIL, ErrorType.JOB_ONGOING): 1,
    }

    assert (
        f"{ErrorType.JOB_NEVER_STARTED.value}: 2 times" in ERRORS.get_report()
    )
    assert f"{ErrorType.JOB_ONGOING.value}: 1 times" in ERRORS.get_report()
