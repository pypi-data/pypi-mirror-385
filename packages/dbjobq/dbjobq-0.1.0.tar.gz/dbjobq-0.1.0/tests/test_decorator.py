"""Tests for @job decorator."""

from dbjobq import job
from dbjobq.queue import _job_config, _job_registry


def test_job_decorator_basic():
    """Test basic @job decorator."""

    @job()
    def test_task(data):
        return data

    key = f"{test_task.__module__}.{test_task.__name__}"
    assert key in _job_registry
    assert _job_registry[key] == test_task
    assert _job_config[key] == {"max_retries": 0, "priority": 0}


def test_job_decorator_with_max_retries():
    """Test @job decorator with max_retries."""

    @job(max_retries=5)
    def test_task(data):
        return data

    key = f"{test_task.__module__}.{test_task.__name__}"
    assert _job_config[key]["max_retries"] == 5
    assert _job_config[key]["priority"] == 0


def test_job_decorator_with_priority():
    """Test @job decorator with priority."""

    @job(priority=10)
    def test_task(data):
        return data

    key = f"{test_task.__module__}.{test_task.__name__}"
    assert _job_config[key]["max_retries"] == 0
    assert _job_config[key]["priority"] == 10


def test_job_decorator_with_both():
    """Test @job decorator with both max_retries and priority."""

    @job(max_retries=3, priority=5)
    def test_task(data):
        return data

    key = f"{test_task.__module__}.{test_task.__name__}"
    assert _job_config[key]["max_retries"] == 3
    assert _job_config[key]["priority"] == 5


def test_decorated_function_still_callable():
    """Test that decorated function remains callable."""

    @job(max_retries=2)
    def test_task(data):
        return data["value"] * 2

    result = test_task({"value": 21})
    assert result == 42


def test_multiple_decorated_functions():
    """Test multiple functions with @job decorator."""

    @job(max_retries=1)
    def task1(data):
        pass

    @job(max_retries=2)
    def task2(data):
        pass

    key1 = f"{task1.__module__}.{task1.__name__}"
    key2 = f"{task2.__module__}.{task2.__name__}"

    assert key1 in _job_registry
    assert key2 in _job_registry
    assert _job_config[key1]["max_retries"] == 1
    assert _job_config[key2]["max_retries"] == 2
