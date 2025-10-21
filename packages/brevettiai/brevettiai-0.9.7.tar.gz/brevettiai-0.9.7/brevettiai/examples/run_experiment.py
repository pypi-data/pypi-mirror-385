# Example running a custom job on the brevettiai platform
from brevettiai.platform import PlatformAPI, Job, JobSettings


class CustomSettings(JobSettings):
    """Class containing all the custom parameters for the job"""

    parameter: int = 1


class CustomJob(Job):
    """Class for running the actual job, specifying which parameter set to use"""

    settings: CustomSettings

    def run(self):
        print(f"My parameter: {self.settings.parameter}")


def main():
    client = PlatformAPI()

    # Run with context generator in notebooks
    experiment = client.experiment(
        name="experiment",
        datasets=["ExampleDataset"],
        # application="8fa55abc-5bc6-4432-a53e-f31c2e524de2",
    )

    with experiment as job:
        print(job.datasets)
        artifact = job.artifacts_path / "test.txt"
        artifact.write_text("Hello, world!")
        job.complete(artifact)

    # Run jobs in scripts to enforce some control over the code
    experiment = client.experiment(
        name="experiment",
        job_type=CustomJob,
        settings=CustomSettings(parameter=42),
        datasets=["ExampleDataset"],
        # application="8fa55abc-5bc6-4432-a53e-f31c2e524de2",
    ).run(errors="raise")

    # Run test reports to test the model
    report = client.run_test(
        name="experiment test",
        job_type=CustomJob,
        settings=CustomSettings(parameter=17),
        on=experiment.model,
        datasets=["ExampleDataset"],
    )

    # Cleaning up
    experiment.delete()


if __name__ == "__main__":
    main()
