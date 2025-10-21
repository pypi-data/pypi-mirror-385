""" Flow
* Show releases and families (Find and compare models)
* Select a release
* Create and run a new model
* Publish the model
* Show releases in the new organization
* Run a model in the new organization with the new model as base model
* Run a test report
 """

from brevettiai.datamodel.model_release import ModelFamily
from brevettiai.platform import PlatformAPI, Job, JobSettings, test_backend
import pandas as pd


class CustomSettings(JobSettings):
    """Class containing all the custom parameters for the job"""

    parameter: int = 1


class CustomJob(Job):
    """Class for running the actual job, specifying which parameter set to use"""

    settings: CustomSettings

    def run(self):
        base_model_info = self.get_base_model()
        base_model_path = base_model_info.artifact.download(
            self.temp_path / "base_model", job=self
        )
        print(f"base_model: {base_model_path.read_text()}")


def show_releases(client):
    releases = client.get_modelreleases()
    df = pd.DataFrame(
        [
            {"family": x.model_family.name, "version": x.version, "release": x}
            for x in releases
        ]
    )
    # Print DataFrame
    print(df)
    return df


def show_families(client: PlatformAPI):
    families = client.get_modelfamilies()
    df = pd.DataFrame(
        [{"name": x.name, "description": x.description, "family": x} for x in families]
    )
    # Print DataFrame
    print(df)
    return df


def main():
    client = PlatformAPI(host=test_backend)

    releases_df = show_releases(client)
    families_df = show_families(client)
    try:
        client.get_modelreleases(
            family=client.get_modelfamilies(name="ExampleModelFamily").id
        )
        # Select a release
        release = (
            releases_df[releases_df.family == "ExampleModelFamily"].iloc[0].release
        )
        # Test get model release from id
        client.get_modelrelease(release.id)
    except Exception as e:
        print(e)
        release = None

    # Create new model
    experiment = client.experiment(
        name="experiment",
        datasets=["ExampleDataset", "test"],
        release_metadata={
            "modelFamily": (
                release.model_family.id
                if release
                else ModelFamily(name="ExampleModelFamily")
            ),
            "modelMetadata": {"type": "ExampleModel"},
        },
        base_model=release.base_model_description() if release else None,
        # application="8fa55abc-5bc6-4432-a53e-f31c2e524de2",
    )

    with experiment as job:
        base_model_info = job.get_base_model()
        if base_model_info:
            base_model_path = base_model_info.artifact.download(
                job.temp_path / "base_model", job=job
            )
        print(job.datasets)
        artifact = job.artifacts_path / "test.txt"
        artifact.write_text("Hello, world!")

        job.complete(artifact)

    client2 = PlatformAPI(
        host=test_backend, organization=client.get_organization_id("Second org")
    )

    show_releases(client2)

    client.publish_model(job.id, ["Second org", "Brevetti AI"])
    show_releases(client2)

    new_release = client2.get_modelreleases()[0]
    family2 = client2.get_modelfamilies(new_release.model_family.id)

    # Run jobs in scripts to enforce some control over the code
    experiment = client2.experiment(
        name="experiment",
        job_type=CustomJob,
        settings=CustomSettings(parameter=42),
        datasets=["ExampleDataset", "Test dataset"],
        base_model=new_release.base_model_description(),
        # application="8fa55abc-5bc6-4432-a53e-f31c2e524de2",
    ).run(errors="raise")

    # Run test reports to test the model
    report = client2.run_test(
        name="experiment test",
        job_type=CustomJob,
        settings=CustomSettings(parameter=17),
        on=experiment.model,
        datasets=["ExampleDataset", "Test dataset"],
    )

    # Cleaning up
    experiment.delete()


if __name__ == "__main__":
    main()
