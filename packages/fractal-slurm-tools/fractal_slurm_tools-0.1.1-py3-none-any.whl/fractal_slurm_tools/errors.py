from enum import Enum


class ErrorType(str, Enum):
    JOB_NOT_FOUND = "Job not found"
    JOB_ONGOING = "Job never ended"
    JOB_NEVER_STARTED = "Job never started"
    MISSING_VALUE = "Missing value"


class Errors:
    def __init__(self):
        self._current_user: str | None = None
        self._errors: dict[tuple[str, ErrorType], int] = {}

    def _reset_state(self):
        """
        This is needed for tests, to avoid propagating ERRORS state.
        """
        self._current_user = None
        self._errors = {}

    @property
    def _existing_users(self) -> set[str]:
        return set(key[0] for key in self._errors)

    def set_user(self, *, email: str):
        self._current_user = email

    def add_error(self, error_type: ErrorType):
        if self._current_user is None:
            raise ValueError(
                "Cannot call `ERRORS.add_error` without `_current_user`."
            )
        if error_type not in list(ErrorType):
            raise ValueError(f"Unknown error type: {error_type}")
        self._errors.setdefault((self._current_user, error_type), 0)
        self._errors[(self._current_user, error_type)] += 1

    @property
    def tot_errors(self) -> int:
        return sum(self._errors.values())

    def tot_errors_per_type(self, error_type: ErrorType) -> int:
        return sum(
            [
                value
                for key, value in self._errors.items()
                if key[1] == error_type
            ]
        )

    def get_report(self, verbose: bool = False) -> str:
        """
        Produce a report of errors.
        """
        if not self._errors:
            return "No errors took place."

        msg = "Some errors took place:\n"
        for err_type in ErrorType:
            total = self.tot_errors_per_type(error_type=err_type)
            if total > 0:
                msg += f"- {err_type.value}: {total} times\n"
                if verbose:
                    for user in self._existing_users:
                        count = self._errors.get((user, err_type), 0)
                        if count > 0:
                            msg += f"      * {count} for {user}\n"
        return msg


ERRORS = Errors()
