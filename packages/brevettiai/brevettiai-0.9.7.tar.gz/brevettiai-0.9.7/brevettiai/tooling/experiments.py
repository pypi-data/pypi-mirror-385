import logging
from typing import Optional, List

from brevettiai.datamodel import web_api_types as api
from brevettiai.platform import PlatformAPI, Job

log = logging.getLogger(__name__)


def generate_model_name(name, job_type, message):
    try:
        from brevettiai.interfaces.git_state import GitRepositoryState, git

        git_state = GitRepositoryState.from_type(job_type)
        branch = git_state.active_branch
    except Exception:
        log.warning("Could not get git state")
        branch = ""

    model_name = " - ".join(
        filter(None, (name, job_type.__name__ if job_type else None, branch, message))
    )
    return model_name


def get_datasets(dataset_names, allowed=None, web=None):
    if dataset_names is not None and all(hasattr(ds, "id") for ds in dataset_names):
        return dataset_names

    web = web or PlatformAPI()

    datasets = web.get_dataset()
    if allowed:
        datasets = list(filter(lambda ds: ds.id in allowed, datasets))

    if dataset_names:
        datasets = list(filter(lambda ds: ds.name in dataset_names, datasets))

    return datasets


def experiment(
    name,
    settings,
    job_type=None,
    datasets: Optional[List] = None,
    application=None,
    delete_incomplete=True,
    web: PlatformAPI = None,
    **kwargs,
):
    """
    Create development model on the platform and run the job

    Args:
        name: Name to append on the model name
        settings: Settings object of the model
        job_type: Type of job to run
        datasets: Names of datasets to include among training datasets on the application, None or [] for all datasets
        application: str id, 'api.Application' or to run experiment on
        delete_incomplete: delete models with the same name
        web: PlatformAPI if default not to be used

    Returns:
        Model
    """
    if application is None and not datasets:
        raise ValueError("Datasets should be given if application is not")

    # Log in to the platform
    web = web or PlatformAPI(remember_me=True)

    if application:
        if isinstance(application, str):
            application = web.get_application(application)
        if not isinstance(application, api.Application):
            raise Exception("Application not found")
        if (
            application
            and application.labels
            and hasattr(settings, "segmentation_colors")
        ):
            settings.segmentation_colors = dict(colors=application.labels)

        datasets = get_datasets(datasets, application.training_dataset_ids, web)
        model_name = generate_model_name(application.name, job_type, name)
    else:
        datasets = get_datasets(datasets, web=web)
        model_name = generate_model_name(None, job_type, name)

    if not model_name:
        raise ValueError("Model name must no be empty")
    if not datasets:
        raise ValueError("No matching datasets found")

    if delete_incomplete:
        # Remove existing models
        existing_models = web.get_model(name=model_name)

        for model in existing_models:
            in_app = model.id in application.model_ids if application else True
            if model.completed is None and in_app:
                print("Removing existing Model", model.name, model.id)
                web.delete(model)

    # Create model
    model = web.create_model(
        name=model_name,
        datasets=datasets,
        application=application,
        settings=settings,
        **kwargs,
    )

    return ExperimentContext(model, job_type, platform=web)


class ExperimentContext:
    job: Job

    def __init__(self, model, job_type, platform: PlatformAPI, verbose=True):
        self.model = model
        self.job_type = job_type
        self.platform = platform
        self.verbose = verbose

    def print_info(self):
        if self.verbose:
            print(f"{self.job.name} - {self.job.host_name}/models/{self.job.id}")
            print("Datasets:")
            for dataset in self.job.datasets:
                print(f"{dataset.name} - {dataset.get_uri()}")

    def __enter__(self):
        self.job = self.platform.initialize_training(
            self.model, job_type=self.job_type or Job
        )
        self.print_info()
        self.job.prepare_start()
        return self.job

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.job.check_started(raise_error=False):
            self.job.complete(package_path=None)

    def run(self, errors="raise"):
        try:
            self.job = self.platform.initialize_training(
                self.model, job_type=self.job_type or Job
            )
            self.print_info()
            self.job.start()
        except Exception as ex:
            log.error("Exception during training", exc_info=ex)
            if errors == "raise":
                raise ex
        return self

    def delete(self):
        self.platform.delete(self.model)


def run_test_report(
    name,
    settings,
    job_type,
    parent,
    datasets=None,
    application=None,
    web: PlatformAPI = None,
    delete_incomplete=True,
):
    """
    Create development test report on a model

    Args:
        name: Message to append on the model name
        parent: str id, 'api.Model' to run test report on
        application: str id or 'api.Application' to search for datasets
        job_type: Type of job to run
        settings: Settings object of the model
        datasets: Names of datasets to include among test datasets on the model application, None for all datasets
        web: PlatformAPI if default not to be used
        delete_incomplete: delete reports with the same name in the same model

    Returns:
        Test report
    """
    if application is None and not datasets:
        raise ValueError("Datasets should be given if application is not")

    # Log in to the platform
    web = web or PlatformAPI(remember_me=True)

    if isinstance(parent, str):
        parent = web.get_model(parent)
    if not isinstance(parent, api.Model):
        raise Exception("Parent not found")

    if isinstance(application, str):
        application = web.get_application(application)
    if application is None:
        application = web.get_application(parent.application_id)
    if application:
        settings.segmentation_colors = dict(colors=application.labels)

    # Get datasets
    if application:
        datasets = get_datasets(datasets, application.test_dataset_ids, web)
        model_name = generate_model_name(application.name, job_type, name)
    else:
        datasets = get_datasets(datasets, None, web)
        model_name = generate_model_name(None, job_type, name)

    if not model_name:
        raise ValueError("Model name must no be empty")
    if not datasets:
        raise ValueError("No matching datasets found")

    if delete_incomplete:
        existing_reports = web.get_report(name=model_name, parent_id=parent.id)

        for report in existing_reports:
            if not report.completed:
                print(
                    f"Removing existing incomplete report {report.name} from {report.parent_name}"
                )
                web.delete(report)

    # Create test report
    test_report = web.create_testreport(
        name=model_name, model=parent, datasets=datasets, settings=settings
    )
    job = web.initialize_report(test_report, job_type=job_type)

    print(f"{job.name} - {web.host}/reports/{test_report.id}")
    print("Datasets:")
    for dataset in job.datasets:
        print(f"{dataset.name} - {dataset.get_uri()}")

    job.start()
    return test_report
