import pytest

from ops2deb.exceptions import Ops2debError
from ops2deb.utils import separate_results_from_errors


def test_separate_results_from_errors_should_separate_results_from_ops2deb_exceptions():
    error = Ops2debError("An error")
    success = "success"
    test = {0: error, 1: success, 2: error, 4: success}
    results, errors = separate_results_from_errors(test)
    assert errors == {0: error, 2: error}
    assert results == {1: success, 4: success}


def test_separate_results_from_errors_should_raise_when_exception_is_not_an_ops2deb_error():  # noqa: E501
    error = RuntimeError("An error")
    test = {0: error}
    with pytest.raises(RuntimeError):
        separate_results_from_errors(test)
