from copy import deepcopy

from .data import test_job

from usdol_wage_determination_model import Job


def test_basic():
    job = Job(**test_job)
    assert job.classification == test_job['classification']
    assert job.subclassification == test_job['subclassification']


def test_default_subclassification():
    test_default_job = deepcopy(test_job)
    del test_default_job['subclassification']
    job = Job(**test_default_job)
    assert job.classification == test_job['classification']
    assert job.subclassification is None
