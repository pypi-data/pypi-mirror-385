import base64
import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Type, Optional, Literal
from typing import Union, List
from urllib.parse import urlparse, unquote
from uuid import UUID

from oauthlib.oauth2 import LegacyApplicationClient, OAuth2Token
from pydantic import parse_raw_as
from requests_oauthlib import OAuth2Session

from brevettiai.datamodel import Dataset
from brevettiai.datamodel import Tag
from brevettiai.datamodel import web_api_types as api_types, model_release
from brevettiai.io.utils import prompt_for_password
from brevettiai.platform import PlatformBackend
from brevettiai.platform import annotations
from brevettiai.platform import backend as default_backend
from brevettiai.platform.dataset_items import delete_item, get_items, put_item
from brevettiai.platform.models import Job, JobSettings
from brevettiai.platform.platform_credentials import PlatformDatasetCredentials
from brevettiai.utils import env_variables

log = logging.getLogger(__name__)

OAUTH_CLIENT_ID = "generic_client"
OAUTH_TOKEN_URL = "/connect/token"
OAUTH_SCOPE = "api offline_access"
OAUTH_TOKENS_PATH = os.path.join(os.path.expanduser("~"), ".brevetti")


class PlatformAPI:
    """
    API interface to brevetti platform

    use `BREVETTI_AI_USER` and `BREVETTI_AI_PW` environment variables to use
    system-wide default username and password
    """

    _session: OAuth2Session = None
    persist_tokens = False
    _token_path = None
    _context_organization = None

    def __init__(
        self,
        username=None,
        password=None,
        organization="default",
        host=None,
        remember_me: bool = True,
    ):
        self.host = host or default_backend

        self._s3_credentials = PlatformDatasetCredentials(self)

        self.persist_tokens = remember_me
        self.login(username, password, organization=organization)

    @property
    def host(self):
        return (
            self._host.host if isinstance(self._host, PlatformBackend) else self._host
        )

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def backend(self):
        if isinstance(self._host, PlatformBackend):
            return self._host
        else:
            raise AttributeError("Backend unknown")

    def api(self, v: Literal[0, 1] = 0, organization: Optional[str] = None):
        if v == 1:
            organization = (
                self.get_organization_id(organization) or self._context_organization
            )
            if organization:
                return "/api/organizations/" + organization
            else:
                return f"/api"
        else:
            return "/api"

    def use(self, organization: Optional[str] = None):
        if not organization:
            self._context_organization = None
        self._context_organization = self.get_organization_id(organization)

    def token_updater(self, token):
        if self.persist_tokens:
            # Persist token
            log.info(f"Persisting token to {self._token_path}")
            self._token_path.parent.mkdir(parents=True, exist_ok=True)
            self._token_path.write_text(json.dumps(token))

    @property
    def session(self):
        if self._session is None:
            self._session = OAuth2Session(
                client=LegacyApplicationClient(
                    client_id=OAUTH_CLIENT_ID, scope=OAUTH_SCOPE
                ),
                auto_refresh_kwargs={
                    "client_id": OAUTH_CLIENT_ID,
                },
                auto_refresh_url=self.host + OAUTH_TOKEN_URL,
                token_updater=self.token_updater,
            )
        return self._session

    def login(self, username=None, password=None, organization="default"):
        username = username or os.getenv(env_variables.BREVETTI_AI_USER)
        password = password or os.getenv(env_variables.BREVETTI_AI_PW)

        token_dir = Path(OAUTH_TOKENS_PATH).joinpath()
        token_id = "/".join(
            (
                ("webapi." + self.host.split("://", 1)[-1]),
                f"{username or '*'}",
                organization,
            )
        )
        if username and password:
            self._token_path = token_dir / token_id
            token = self.session.fetch_token(
                token_url=self.host + OAUTH_TOKEN_URL,
                client_id=OAUTH_CLIENT_ID,
                username=username,
                password=password,
                organization_id=organization,
            )
            self.token_updater(token)
            return
        else:
            token_paths = list(token_dir.glob(token_id))
            token_paths_map = {p.name: [p] for p in token_paths}
            token_paths = token_paths_map.get(
                token_id, token_paths_map.get("default", token_paths)
            )
            try:
                for token_path in token_paths:
                    token = OAuth2Token(json.loads(token_path.read_text()))
                    self._token_path = token_path
                    self.session.token = token
                    # If expired get new token

                    if token["expires_at"] < time.time():
                        token = self.session.refresh_token(
                            token_url=self.host + OAUTH_TOKEN_URL
                        )
                        self.session.token = token
                        self.token_updater(token)
                    return
            except Exception:
                pass

            # Fallback to request login details
            if username is None:
                username = input(f"{self.host} - username: ")
            if password is None:
                password = prompt_for_password()

            self.login(username, password, organization=organization)

    def get_user_organizations(self):
        url = f"{self.host}/api/account/organizations"
        r = self.session.get(url)
        if r.ok:
            return parse_raw_as(List[api_types.Organization], r.content)

        raise Exception("Error getting organizations: HTTP{r.status_code}")

    @lru_cache(maxsize=None)
    def get_organization_id(self, organization: str):
        if organization is None:
            return None
        try:
            # If valid uuid return it
            UUID(organization)
            return organization
        except ValueError:
            pass
        organizations = self.get_user_organizations()
        try:
            return next(o.id for o in organizations if o.name == organization)
        except StopIteration:
            org_names = [o.name for o in organizations]
            raise StopIteration(
                f"Organization does not match any available organizations {org_names}"
            )

    def get_dataset(
        self,
        id: str = None,
        write_access=False,
        extended_details=False,
        *,
        organization: str = None,
        **kwargs,
    ) -> Union[Dataset, List[Dataset]]:
        """
        Get dataset, or list of all datasets

        Args:
            id: dataset id
            write_access: resolve accessrights to the dataset
            extended_details: Include extended details
            organization: organization to list from
            **kwargs: Extended search criteria: use ('name', 'reference' 'locked', ...)

        Returns:
            dataset if id is given, otherwise list of datasets
        """
        url = f"{self.host}{self.api(1, organization=organization)}/data"
        url = url if id is None else url + "/" + id
        if extended_details:
            url += "?extendedDetails=true"
        r = self.session.get(url)
        credentials = self._s3_credentials if write_access else None
        if id is None:
            return [
                Dataset(**x, backend=self.backend, credentials=credentials)
                for x in r.json()
                if all(x.get(k) == v for k, v in kwargs.items())
            ]
        else:
            return Dataset(**r.json(), backend=self.backend, credentials=credentials)

    def get_tag(self, id=None) -> Union[Tag, List[Tag]]:
        """
        Get tag or list of all tags

        Args:
            id: Tag id

        Returns:
            tag if id is given, otherwise a list of tags
        """
        url = f"{self.host}{self.api(0)}/resources/tags"
        url = url if id is None else url + "/" + id
        r = self.session.get(url)
        return parse_raw_as(Union[Tag, List[Tag]], r.content)

    def get_model(
        self, id=None, **kwargs
    ) -> Union[api_types.Model, List[api_types.Model]]:
        """
        Get model or list of all models

        Args:
            id: model id
            **kwargs: Extended search criteria: use ('name', 'reference' 'locked', ...)

        Returns:
            model if id is given, otherwise a list of models
        """
        url = f"{self.host}{self.api(0)}/models"
        url = url if id is None else url + "/" + id
        r = self.session.get(url)
        if id is None:
            models = parse_raw_as(List[api_types.Model], r.content)
            return [
                x
                for x in models
                if all(getattr(x, k, None) == v for k, v in kwargs.items())
            ]
        else:
            return parse_raw_as(api_types.Model, r.content)

    def get_report(
        self, id=None, **kwargs
    ) -> Union[api_types.Report, List[api_types.Report]]:
        """
        Get test report, or list of all reports

        Args:
            id: report id
            **kwargs: Extended search criteria: use ('name', 'reference' 'locked', ...)

        Returns:
            report if id is given, otherwise a list of reports
        """
        url = f"{self.host}{self.api(0)}/reports"
        url = url if id is None else url + "/" + id
        r = self.session.get(url)
        if id is None:
            reports = parse_raw_as(List[api_types.Report], r.content)
            return [
                x
                for x in reports
                if all(getattr(x, k, None) == v for k, v in kwargs.items())
            ]
        else:
            return parse_raw_as(api_types.Report, r.content)

    def get_artifacts(
        self,
        obj: Union[api_types.Model, api_types.Report],
        prefix: str = "",
        recursive: bool = False,
        add_prefix=False,
    ) -> List[api_types.FileEntry]:
        """
        Get artifacts for model or test report

        Args:
            obj: model/test report object
            prefix: object prefix (folder)

        Returns:
            List of files
        """
        if isinstance(obj, api_types.Model):
            r = self.session.get(
                f"{self.host}{self.api(0)}/models/{obj.id}/artifacts?prefix={prefix}"
            )
        elif isinstance(obj, api_types.Report):
            r = self.session.get(
                f"{self.host}{self.api(0)}/reports/{obj.id}/artifacts?prefix={prefix}"
            )
        else:
            raise NotImplementedError("Artifacts not available for type")
        artifacts = parse_raw_as(List[api_types.FileEntry], r.content)

        if not recursive:
            if add_prefix:
                for a in artifacts:
                    a.name = prefix + a.name
            return artifacts

        all_artifacts = []
        for a in artifacts:
            if a.mime_type == "folder":
                all_artifacts.extend(
                    self.get_artifacts(
                        obj,
                        prefix=f"{prefix}{a.name}/",
                        recursive=True,
                        add_prefix=add_prefix,
                    )
                )
            else:
                if add_prefix:
                    a.name = prefix + a.name
                all_artifacts.append(a)

        return all_artifacts

    def get_application_classification(
        self,
        application: api_types.Application = None,
        project: api_types.Project = None,
    ) -> Union[api_types.Application, List[api_types.Application]]:
        url = f"{self.host}{self.api(0)}/resources/projects/{project.id}/applications/{application.id}/classification"
        if application.type == 1:  # Classification application type
            r = self.session.get(url)
            return parse_raw_as(api_types.Application, r.content)
        elif application.type == 0:  # Generic application type
            return application
        else:  # Unknow application type
            raise ValueError("Unknown application type")

    def get_application(
        self, id=None, *, organization: Optional[str] = None
    ) -> Union[api_types.Application, List[api_types.Application]]:
        """
        Get application by id

        Args:
            id:
            organization:

        Returns:
            application if id is given, otherwise a list of applications
        """
        projects = self.get_project(organization=organization)
        applications = [
            a for p in projects for a in p.applications if id in {a.id, a.name}
        ]
        if len(applications) == 1:
            return applications[0]
        else:
            return applications

    def get_device(self, id=None):
        url = f"{self.host}{self.api(0)}/devices"
        url = url if id is None else url + "/" + id
        r = self.session.get(url)
        return parse_raw_as(List[api_types.Device], r.content)

    def get_project(
        self, id=None, *, organization: str = None
    ) -> Union[api_types.Project, List[api_types.Project]]:
        url = f"{self.host}{self.api(1, organization=organization)}/resources/projects"
        url = url if id is None else url + "/" + id
        r = self.session.get(url)
        return parse_raw_as(
            Union[api_types.Project, List[api_types.Project]], r.content
        )

    def get_modeltype(
        self, id=None, master=False
    ) -> Union[api_types.ModelType, List[api_types.ModelType]]:
        """
        Get model type

        Args:
            id:
            master: use master mode

        Returns:

        """
        url = f"{self.host}{self.api(0)}/{'master/' if master else 'resources/'}modeltypes/{id if id else ''}"
        r = self.session.get(url)
        return parse_raw_as(
            Union[api_types.ModelType, List[api_types.ModelType]], r.content
        )

    def get_reporttype(
        self, id=None, master=False
    ) -> Union[api_types.ReportType, List[api_types.ReportType]]:
        """
        Get report type

        Args:
            id:
            master: use master mode

        Returns:

        """
        url = f"{self.host}{self.api(0)}/{'master/' if master else 'resources/'}reporttypes/{id if id else ''}"
        r = self.session.get(url)
        return parse_raw_as(
            Union[api_types.ReportType, List[api_types.ReportType]], r.content
        )

    def get_available_model_types(self):
        """
        List all available model types
        """
        r = self.session.get(f"{self.host}{self.api(0)}/models/availabletypes")
        return parse_raw_as(List[api_types.ModelType], r.content)

    def get_dataset_annotations(self, dataset, **kwargs):
        if hasattr(dataset, "id"):
            dataset_id = dataset.id
        else:
            dataset_id = dataset

        return annotations.get_dataset_annotations(
            self.host, dataset_id, get_fn=self.session.get, **kwargs
        )

    def update_annotation(self, dataset, image_path, annotation, **kwargs):
        if hasattr(dataset, "id"):
            dataset_id = dataset.id
        else:
            dataset_id = dataset

        return annotations.update_annotation(
            self.host,
            dataset_id,
            image_path=image_path,
            annotation=annotation,
            post_fn=self.session.post,
            **kwargs,
        )

    def create_annotation(self, dataset, image_path, annotation_name=None):
        return annotations.create_annotation(
            self.host,
            dataset=dataset,
            image_path=image_path,
            annotation_name=annotation_name,
            post_fn=self.session.post,
        )

    def delete_annotation(self, dataset, image_path, annotation_name):
        return annotations.delete_annotation(
            self.host,
            dataset=dataset,
            image_path=image_path,
            annotation_name=annotation_name,
            delete_fn=self.session.delete,
        )

    def rename_annotation(
        self, dataset, image_path, annotation_name, new_annotation_name
    ):
        entry = self.get_dataset_annotations(dataset, image_path=image_path)
        annotation = entry.annotation_files[annotation_name]
        self.create_annotation(dataset, image_path, annotation_name=new_annotation_name)
        self.update_annotation(
            dataset,
            image_path,
            annotation_name=new_annotation_name,
            annotation=annotation,
        )
        self.delete_annotation(dataset, image_path, annotation_name=annotation_name)

    def get_items(self, dataset=None, item_id=None, filter: dict = None, **kwargs):
        return get_items(
            host=self.host,
            get_fn=self.session.get,
            dataset=dataset,
            item_id=item_id,
            filter=filter,
            **kwargs,
        )

    def put_item(self, item, **kwargs):
        return put_item(host=self.host, put_fn=self.session.put, item=item, **kwargs)

    def delete_item(self, dataset_id, item_id, **kwargs):
        return delete_item(
            host=self.host,
            delete_fn=self.session.delete,
            dataset_id=dataset_id,
            item_id=item_id,
            **kwargs,
        )

    def create(
        self, obj: Union[Dataset, Tag, api_types.Model, api_types.Report], **kwargs
    ):
        if isinstance(obj, Dataset):
            payload = obj.dict(
                include={"name", "reference", "notes", "locked"}, by_alias=True
            )
            payload["tagIds"] = [tag.id for tag in obj.tags]
            r = self.session.post(f"{self.host}{self.api(0)}/data/", json=payload)
            return self.get_dataset(r.json()["datasetId"], **kwargs)
        elif isinstance(obj, Tag):
            payload = obj.dict(
                include={"name", "parent_id"}, by_alias=True, exclude_none=True
            )
            self.session.post(f"{self.host}{self.api(0)}/resources/tags/", json=payload)

            # TODO: return tag id on api
            parent = self.get_tag(obj.parent_id)
            tag = next(
                filter(
                    lambda x: x.name == obj.name,
                    (parent.children if isinstance(parent, Tag) else parent),
                )
            )
            return tag
        elif isinstance(obj, api_types.Model):
            payload = obj.dict(
                include={
                    "name",
                    "model_type_id",
                    "application_id",
                    "settings",
                    "dataset_ids",
                    "tag_ids",
                    "release_metadata",
                    "base_model",
                },
                exclude_unset=True,
                exclude_none=True,
                by_alias=True,
            )
            payload["datasetIds"] = payload.pop("datasets")
            r = self.post("/models", json=payload)
            return api_types.Model.parse_raw(r.content)
        elif isinstance(obj, api_types.Report):
            payload = obj.dict(
                include={
                    "name",
                    "parent_id",
                    "parent_type",
                    "report_type_id",
                    "model_ids",
                    "settings",
                    "dataset_ids",
                    "tag_ids",
                },
                by_alias=True,
            )
            payload["datasetIds"] = payload.pop("datasets")
            payload["modelIds"] = payload.pop("models")
            payload["submitToCloud"] = (
                "submitToCloud" in kwargs and kwargs["submitToCloud"]
            )

            r = self.session.post(f"{self.host}{self.api(0)}/reports", json=payload)
            report = self.get_report(r.json()["id"])
            return report
        else:
            raise NotImplementedError(f"create not implemented for type {type(obj)}")

    def update(self, obj, master=False):
        if isinstance(obj, Dataset):
            payload = obj.dict(include={"name", "reference", "notes", "locked"})
            payload["tagIds"] = [tag.id for tag in obj.tags]
            self.session.post(f"{self.host}{self.api(0)}/data/{obj.id}", json=payload)
        elif isinstance(obj, Tag):
            payload = obj.dict(
                include={"name", "parent_id"}, by_alias=True, exclude_none=True
            )
            self.session.post(
                f"{self.host}{self.api(0)}/resources/tags/{obj.id}", json=payload
            )
        elif isinstance(obj, api_types.ModelType):
            if not master:
                raise PermissionError("Not authorized")
            self.session.post(
                f"{self.host}{self.api(0)}/master/modeltypes/update",
                json=obj.dict(by_alias=True),
            )
        elif isinstance(obj, api_types.ReportType):
            if not master:
                raise PermissionError("Not authorized")
            self.session.post(
                f"{self.host}{self.api(0)}/master/reporttypes/update",
                json=obj.dict(by_alias=True),
            )
        else:
            raise NotImplementedError(f"create not implemented for type {type(obj)}")

    def update_application_datasets(self, app: api_types.Application):
        project_id = next(
            p for p in self.get_project() for a in p.applications if a.id == app.id
        ).id
        self.session.post(
            f"{self.host}{self.api(0)}/resources/projects/{project_id}/applications/{app.id}/datasets",
            json=app.dict(
                by_alias=True,
                include={"name", "training_dataset_ids", "test_dataset_ids"},
            ),
        )

    def delete(
        self,
        obj: Union[
            Dataset,
            Tag,
            api_types.Model,
            api_types.Report,
            api_types.SftpUser,
            api_types.ReportType,
            api_types.ModelType,
        ],
    ):
        if isinstance(obj, Dataset):
            self.session.delete(f"{self.host}{self.api(0)}/data/{obj.id}")
        elif isinstance(obj, Tag):
            self.session.delete(f"{self.host}{self.api(0)}/resources/tags/{obj.id}")
        elif isinstance(obj, api_types.Model):
            self.session.delete(f"{self.host}{self.api(0)}/models/{obj.id}")
        elif isinstance(obj, api_types.Report):
            self.session.delete(f"{self.host}{self.api(0)}/reports/{obj.id}")
        elif isinstance(obj, api_types.SftpUser):
            self.session.delete(
                f"{self.host}{self.api(0)}/data/{obj.folder}/sftp/{obj.user_name}"
            )
        elif isinstance(obj, api_types.ModelType):
            self.session.delete(
                f"{self.host}{self.api(0)}/resources/modeltypes/{obj.id}"
            )
        elif isinstance(obj, api_types.ReportType):
            self.session.delete(
                f"{self.host}{self.api(0)}/resources/reporttypes/{obj.id}"
            )
        else:
            raise NotImplementedError(f"delete not implemented for type {type(obj)}")

    def get_persmission_groups(self):
        r = self.get(f"/admin/groups")
        return parse_raw_as(List[api_types.PermissionGroup], r.content)

    def get_dataset_permissions(self, dataset_id: str | Dataset):
        if hasattr(dataset_id, "id"):
            dataset_id = dataset_id.id

        r = self.get(f"/data/{dataset_id}/permissions")
        return parse_raw_as(List[api_types.PermissionListItem], r.content)

    def update_dataset_permission(
        self, id, user_id, group_id=None, permission_type="Editor"
    ):
        """
        Update dataset permissions for user

        Args:
            id:
            user_id:
            group_id:
            permission_type:

        Returns:

        """
        payload = {
            "groupId": group_id,
            "userId": user_id,
            "resourceId": id,
            "objectType": 0,
            "permissionType": permission_type,
        }
        r = self.session.post(
            f"{self.host}{self.api(0)}/admin/datasets/{id}/permissions", json=payload
        )
        return r

    def get_dataset_sts_assume_role_response(self, guid):
        cred = self.session.get(f"{self.host}/api/data/{guid}/securitycredentials")
        return cred.text

    def get_schema(self, obj: Union[api_types.ModelType, api_types.ReportType]):
        """
        Get schema for a certain model type

        Args:
            obj: modeltype or report type

        Returns:

        """
        r = self.session.get(obj.settings_schema_path, headers={})
        return r.json()

    def get_userinfo(self):
        """
        Get info on user
        """
        r = self.get("/manage/index")
        return api_types.User.parse_raw(r.content)

    def get_sftp_users(self, dataset, **kwargs) -> List[api_types.SftpUser]:
        r = self.session.get(
            f"{self.host}{self.api(0)}/data/{dataset.id}/sftp", **kwargs
        )
        users = parse_raw_as(List[api_types.SftpUser], r.content)
        for user in users:
            user.folder = user.folder or dataset.id
        return users

    def create_sftp_user(self, dataset, **kwargs) -> api_types.SftpUser:
        r = self.session.post(
            f"{self.host}{self.api(0)}/data/{dataset.id}/sftp", **kwargs
        )
        return api_types.SftpUser.parse_raw(r.content)

    def create_model(
        self,
        name,
        datasets,
        settings: JobSettings = None,
        model_type=None,
        tags=None,
        application: api_types.Application = None,
        release_metadata: model_release.ReleaseMetadata = None,
        base_model: model_release.ModelRelease = None,
    ):
        """
        Create a model on the platform

        Args:
            name (str): The name of the model.
            datasets (List[Dataset]): List of datasets to be used.
            settings (JobSettings, optional): Settings for the job. Defaults to None.
            model_type (ModelType, optional): The type of the model. Defaults to None.
            tags (List[Tag], optional): List of tags for the model. Defaults to None.
            application (Application, optional): The application associated with the model. Defaults to None.
            release_metadata (ReleaseMetadata, optional): Metadata for the model release. Defaults to None.
            base_model (ModelReleaseDescription, optional): Description of the base model. Defaults to None.

        Returns:
            Model: The created model on the platform.
        """
        tags = tags or []
        settings = settings or {}
        try:
            settings = settings.json()
        except AttributeError:
            settings = json.dumps(settings)

        model_type = model_type or self.backend.custom_model_type
        settings = settings or {}

        application_id = None if application is None else application.id
        model = api_types.Model(
            name=name,
            dataset_ids=[x.id for x in datasets],
            model_type_id=model_type.id,
            model_type_status=model_type.status,
            settings=settings,
            application_id=application_id,
            tag_ids=[x.id for x in tags],
            id="<unknown>",
            api_key="<unknown>",
            created="<unknown>",
            release_metadata=release_metadata,
            base_model=base_model,
        )
        return self.create(model)

    def create_testreport(
        self,
        name,
        model,
        datasets,
        report_type=None,
        settings=None,
        tags=None,
        submitToCloud=False,
    ):
        """
        Create a test report on the platform

        Args:
            name:
            model:
            datasets:
            report_type:
            settings:
            tags:
            submitToCloud: start test report in the cloud

        Returns:
            Test report after its creation on the platform
        """
        tags = tags or []
        tag_ids = [tag if isinstance(tag, str) else tag.id for tag in tags]
        report_type = report_type or self.backend.custom_report_type
        report_type_id = report_type if isinstance(report_type, str) else report_type.id

        settings = settings or {}
        try:
            settings = settings.json()
        except AttributeError:
            settings = json.dumps(settings)

        report = api_types.Report(
            name=name,
            model_ids=[model.id],
            dataset_ids=[x.id for x in datasets],
            id="<unknown>",
            api_key="<unknown>",
            created="<unknown>",
            parent_id=model.id,
            parent_name=model.name,
            parent_type="model",
            settings=settings,
            tag_ids=tag_ids,
            report_type_id=report_type_id,
        )
        return self.create(report, submitToCloud=submitToCloud)

    def initialize_training(
        self,
        model: Union[str, api_types.Model],
        job_type: Type[Job] = None,
        submitToCloud=False,
    ) -> Union[Job, None]:
        """
        Start training flow of a model

        Args:
            model: model or model id
            job_type:
            submitToCloud: start model in the cloud

        Returns:
            Job if submitToCloud is false, otherwise None
        """
        payload = {"submitToCloud": "true" if submitToCloud else "false"}

        if isinstance(model, str):
            model = self.get_model(model)

        if model.completed:
            print("Model already completed")
            return None

        r = self.session.post(
            f"{self.host}{self.api(0)}/models/{model.id}/start", params=payload
        )
        if submitToCloud:
            return None
        job_config = json.loads(self.download_url(r.json(), cache=False))
        type_selector = job_type or Job

        job = Job.init(
            type_selector=type_selector, job_config=job_config, backend=self.backend
        )
        return job

    def initialize_report(
        self, report: Union[str, api_types.Report], job_type: Type[Job] = None
    ) -> Union[Job, None]:
        """
        Start training flow of a model

        Args:
            report: model or model id
            job_type:

        Returns:
            Job
        """

        if isinstance(report, str):
            report = self.get_report(report)

        if report.completed:
            print("Model already completed")
            return None

        type_selector = [job_type] if issubclass(job_type, Job) else job_type

        job = Job.init(
            job_id=report.id,
            api_key=report.api_key,
            type_selector=type_selector,
            backend=self.backend,
        )
        return job

    def stop_model_training(self, model):
        """
        Stop training of model

        Args:
            model:

        Returns:

        """
        r = self.session.post(f"{self.host}{self.api(0)}/models/{model.id}/stop")
        return api_types.Model.parse_raw(r.content)

    def download_url(self, url, dst=None, **kwargs):
        if kwargs.get("headers") is not None:
            log.warning("Headers not supported")

        # by default withhold bearer token for download requests
        withhold_token = True

        if url.startswith("/api/"):
            # Unless it is a request to the API
            url = self.host + url
            withhold_token = False

        r = self.session.get(url, withhold_token=withhold_token)
        if not r.ok:
            raise Exception("Error downloading file")

        content = r.content

        if dst is None:
            return content

        if os.path.isdir(dst):
            fname = os.path.basename(unquote(urlparse(url).path))
            dst = os.path.join(dst, fname)
        else:
            if os.path.dirname(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)

        with open(dst, "wb") as f:
            f.write(content)

        return dst

    def experiment(
        self,
        name,
        job_type=None,
        settings=None,
        datasets: Optional[List] = None,
        application=None,
        **kwargs,
    ):
        """
        :param name: Name of the experiment
        :param job_type: class of the Job
        :param settings: Settings object or dict for the job
        :param datasets: list of datasets or string names
        :param application: string id or Application object
        :param kwargs: Other args; see tooling.experiments
        :return:
        """
        from brevettiai.tooling.experiments import experiment

        experiment = experiment(
            name=name,
            job_type=job_type,
            settings=settings or {},
            datasets=datasets,
            application=application,
            **kwargs,
            web=self,
        )
        print(f"{self.host}{self.api(0)}/models/{experiment.model.id}")
        return experiment

    def run_test(
        self,
        name,
        job_type,
        settings,
        on,
        datasets: Optional[List] = None,
        application=None,
        **kwargs,
    ):
        """
        :param name: Name of the experiment
        :param job_type: class of the Job
        :param settings: Settings object or dict for the job
        :param on: Model to run testreport on
        :param datasets: list of datasets or string names
        :param application: string id or Application object
        :param kwargs: Other args; see tooling.experiments
        :return:
        """
        from brevettiai.tooling.experiments import run_test_report

        return run_test_report(
            name=name,
            job_type=job_type,
            settings=settings,
            parent=on,
            datasets=datasets,
            application=application,
            **kwargs,
            web=self,
        )

    @property
    def s3_credentials(self):
        """Return S3 sts credentials chain"""
        return self._s3_credentials

    def get_modelfamilies(
        self,
        _id: Optional[str] = None,
        name: str = None,
        organization: Optional[str] = None,
    ):
        api_args = dict(v=1, organization=organization)
        if _id is None:
            r = self.get("/modelfamilies", api_args=api_args)
            families = parse_raw_as(List[model_release.ModelFamily], r.content)
            if name:
                # Name is unique, therefore there should be only one
                return next(f for f in families if f.name == name)
            else:
                return families

        r = self.get(
            f"/modelfamilies/{_id}",
            api_args=api_args,
        )
        return model_release.ModelFamily.parse_raw(r.content)

    def publish_model(self, _id: str, organizations: List[str]):
        if not organizations:
            raise ValueError("No organizations specified")

        organizations = [self.get_organization_id(org) for org in organizations]

        r = self.post(
            f"/models/{_id}/publish",
            api_args=dict(v=1),
            json=dict(organizations=organizations),
        )
        r.raise_for_status()
        return r.json()

    def get_modelrelease(self, _id: str, organization: Optional[str] = None):
        r = self.get(
            f"/modelreleases/{_id}", api_args=dict(v=1, organization=organization)
        )
        return model_release.ModelRelease.parse_raw(r.content)

    def get_modelreleases(
        self, family: Optional[str] = None, organization: Optional[str] = None
    ):
        if family:
            r = self.get(
                f"/modelfamilies/{family}/releases",
                api_args=dict(v=1, organization=organization),
            )
        else:
            r = self.get(
                f"/modelreleases", api_args=dict(v=1, organization=organization)
            )

        return parse_raw_as(List[model_release.ModelRelease], r.content)

    def get(self, url: str, api_args: dict = None, **kwargs):
        r = self.session.get(
            f"{self.host}{self.api(**(api_args or dict()))}{url}", **kwargs
        )
        r.raise_for_status()
        return r

    def post(self, url: str, api_args: dict = None, **kwargs):
        r = self.session.post(
            f"{self.host}{self.api(**(api_args or dict()))}{url}", **kwargs
        )
        r.raise_for_status()
        return r


def decode_jwt_token(access_token):
    return json.loads(str(base64.b64decode(access_token.split(".")[1] + "=="), "utf-8"))
