import unittest

from brevettiai.tooling.experiments import generate_model_name
from brevettiai.platform import Job


class TestExperimentName(unittest.TestCase):
    name = "test_model"
    message = "Testing 123 message"

    def test_no_job_type(self):
        job_type = None
        generate_model_name(self.name, job_type, self.message)

    def test_platform_job_type(self):
        job_type = Job
        generate_model_name(self.name, job_type, self.message)
