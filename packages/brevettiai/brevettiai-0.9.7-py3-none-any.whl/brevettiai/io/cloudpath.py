import os
import locale
import logging
import pydantic.json
from pathlib import PurePosixPath, Path, PosixPath, WindowsPath
from typing import Iterable, Tuple, Union, Generator, Optional, IO, Any, Dict

from cloudpathlib import S3Client, S3Path, CloudPath, AnyPath
from cloudpathlib.client import register_client_class
from cloudpathlib.cloudpath import register_path_class
from smart_open.s3 import open as s3open
from smart_open.smart_open_lib import _get_binary_mode, _encoding_wrapper
import atexit

from brevettiai.io import smart_open_patch
from brevettiai.utils import env_variables


log = logging.getLogger(__name__)
__all__ = ["smart_open_patch", "AnyPath"]
DEFAULT_ENCODING = locale.getpreferredencoding(do_setlocale=False)


class ProhibitedDummy:
    def __init__(self, msg):
        self.msg = msg

    def __getattr__(self, attr):
        raise AttributeError(f"{self.msg} - attribute '{attr}' not allowed ")


@register_client_class("s3")
class S3Client(S3Client):
    def __init__(self, cache=None, no_access=False, *args, **kwargs):
        if no_access:
            self.disable()
        else:
            super().__init__(*args, **kwargs)
            self.cache = cache

    def disable(self):
        """Disable use of a client"""
        dummy = ProhibitedDummy("S3Client not valid anymore")
        self.client = dummy
        self.s3 = dummy
        self.sess = dummy

    @classmethod
    def from_credentials(cls, credentials, resource_id, credentials_kwargs=None, **kwargs):
        credentials_kwargs = credentials_kwargs or {}
        info = credentials.get_credentials(resource_id=resource_id, **credentials_kwargs)

        return S3Client(
            aws_access_key_id=info["access_key"],
            aws_secret_access_key=info["secret_key"],
            aws_session_token=info["session_token"],
            **kwargs,
        )

    def CloudPath(self, cloud_path: Union[str, CloudPath], **kwargs) -> CloudPath:
        return self._cloud_meta.path_class(cloud_path=cloud_path, client=self, **kwargs)  # type: ignore

    def _get_metadata(self, cloud_path: S3Path) -> Dict[str, Any]:
        # get accepts all download extra args
        data = self.s3.ObjectSummary(cloud_path.bucket, cloud_path.key).get(
            **self.boto3_dl_extra_args
        )

        return {
            "last_modified": data["LastModified"],
            "size": data["ContentLength"],
            "etag": data["ETag"][1:-1],  # Remove quotation
            "content_type": data["ContentType"],
            "extra": data["Metadata"],
        }

    def _list_dir(self, cloud_path: S3Path, recursive=False, start_after=None, include_dirs=True, page_size=None,
                  max_items=None) \
            -> Iterable[Tuple[S3Path, bool]]:
        # shortcut if listing all available buckets
        if include_dirs and not cloud_path.bucket:
            if recursive:
                raise NotImplementedError(
                    "Cannot recursively list all buckets and contents; you can get all the buckets then recursively list each separately."
                )

            yield from (
                (self.CloudPath(f"s3://{b['Name']}", is_dir=True), True)
                for b in self.client.list_buckets().get("Buckets", [])
            )
            return

        prefix = cloud_path.key
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        yielded_dirs = set()

        paginator = self.client.get_paginator("list_objects_v2")

        for result in paginator.paginate(
                Bucket=cloud_path.bucket,
                Prefix=prefix,
                Delimiter=("" if recursive else "/"),
                StartAfter="" if start_after is None else prefix + start_after,
                PaginationConfig=dict(
                    PageSize=page_size,
                    MaxItems=max_items,
                ),
                **self.boto3_list_extra_args,
        ):
            # yield everything in common prefixes as directories
            if include_dirs:
                for result_prefix in result.get("CommonPrefixes", []):
                    canonical = result_prefix.get("Prefix").rstrip("/")  # keep a canonical form
                    if canonical not in yielded_dirs:
                        yield (
                            self.CloudPath(f"s3://{cloud_path.bucket}/{canonical}", is_dir=True),
                            True,
                        )
                        yielded_dirs.add(canonical)

            # check all the keys
            for result_key in result.get("Contents", []):
                if include_dirs:
                    # yield all the parents of any key that have not been yielded already
                    o_relative_path = result_key.get("Key")[len(prefix):]
                    for parent in PurePosixPath(o_relative_path).parents:
                        parent_canonical = prefix + str(parent).rstrip("/")
                        if parent_canonical not in yielded_dirs and str(parent) != ".":
                            yield (
                                self.CloudPath(f"s3://{cloud_path.bucket}/{parent_canonical}", is_dir=True),
                                True,
                            )
                            yielded_dirs.add(parent_canonical)

                    # if we already yielded this dir, go to next item in contents
                    canonical = result_key.get("Key").rstrip("/")
                    if canonical in yielded_dirs:
                        continue

                # s3 fake directories have 0 size and end with "/"
                if result_key.get("Key").endswith("/") and result_key.get("Size") == 0:
                    if include_dirs:
                        yield (
                            self.CloudPath(f"s3://{cloud_path.bucket}/{canonical}", is_dir=True),
                            True,
                        )
                        yielded_dirs.add(canonical)
                # yield object as file
                else:
                    # Remove quotation from etag as per spec https://www.rfc-editor.org/rfc/rfc2616#section-14.19
                    etag = result_key.get("ETag")[1:-1]
                    yield (
                        self.CloudPath(f"s3://{cloud_path.bucket}/{result_key.get('Key')}", etag=etag, is_dir=False),
                        False,
                    )


class S3ClientManager:
    def __init__(self, cache=None):
        self.clients = dict()
        self.cache = cache

    def register_client(self, partial_path, client):
        keys = self._prepare_path(partial_path)
        clients = self.clients
        for key in keys[:-1]:
            clients = clients.setdefault(key, dict())
            if type(clients) != dict:
                raise ValueError("Client already set")
        clients[keys[-1]] = client
        partial_path.client = client

    def resolve_access_rights(self, partial_path, credentials_getter):
        info = credentials_getter()
        client = S3Client(
            aws_access_key_id=info["access_key"],
            aws_secret_access_key=info["secret_key"],
            aws_session_token=info["session_token"],
            cache=self.cache,
        )
        self.register_client(partial_path=partial_path, client=client)

    @staticmethod
    def _prepare_path(path):
        if type(path) == str:
            return path[5:].split("/")
        else:
            return path.parts[1:]

    def get_client(self, path) -> S3Client:
        # Remove protocol and split
        keys = self._prepare_path(path)

        clients = self.clients
        for key in keys:
            try:
                clients = clients[key]
                if type(clients) != dict:
                    return clients
            except KeyError as ex:
                raise KeyError("No matching s3 client") from ex
        raise KeyError("No matching s3 client")

    def close(self):
        try:
            if self.cache is not None:
                self.cache.close()
        except Exception:
            pass


@register_path_class("s3")
class S3Path(S3Path):
    def __init__(self, cloud_path, client=None, etag=None, is_dir=None):
        if client is None:
            try:
                client = self.clientmanager.get_client(cloud_path)
            except KeyError:
                pass
        super().__init__(cloud_path, client)
        self._etag = etag
        self._is_dir = is_dir

    def refresh_client(self):
        client = self.clientmanager.get_client(self)
        self.client = client

    @property
    def _local(self) -> Path:
        """Cached local version of the file."""
        cache = self.client.cache
        if cache is None:
            return None
        else:
            return cache.cache_path / self._no_prefix

    def __fspath__(self):
        return str(self._local)

    def iterdir(self: CloudPath, recursive=False, **kwargs) -> Generator[CloudPath, None, None]:
        for f, _ in self.client._list_dir(self, recursive=recursive, **kwargs):
            if f != self:  # iterdir does not include itself in pathlib
                yield f

    def is_dir(self) -> bool:
        if self._is_dir is None:
            self._is_dir = super().is_dir()
        return self._is_dir

    def is_file(self) -> bool:
        return not self.is_dir()

    def remove(self, missing_ok: bool = True) -> None:
        self.unlink(missing_ok=missing_ok)

    @property
    def cached_etag(self):
        return self._etag

    @property
    def etag(self):
        if not self._etag:
            self._etag = super().etag
        return self._etag

    def _smart_open(
            self,
            mode: str = "r",
            buffering: int = -1,
            encoding: Optional[str] = None,
            errors: Optional[str] = None,
            newline: Optional[str] = None,
            **kwargs
    ) -> IO:
        # Stolen from smart_open__lib
        explicit_encoding = encoding
        encoding = explicit_encoding if explicit_encoding else DEFAULT_ENCODING

        try:
            binary_mode = _get_binary_mode(mode)
        except ValueError as ve:
            raise NotImplementedError(ve.args[0])

        binary = s3open(
            bucket_id=self.bucket,
            key_id=self.key,
            mode=binary_mode,
            version_id=None,
            client=self.client.client,
            **kwargs
        )
        fp = binary

        if 'b' not in mode or explicit_encoding is not None:
            fp = _encoding_wrapper(
                binary,
                mode,
                encoding=encoding,
                errors=errors,
                newline=newline,
            )
            try:
                setattr(fp, 'to_boto3', getattr(binary, 'to_boto3'))
                setattr(fp, 'response', binary._raw_reader.response)
            except AttributeError:
                pass
        else:
            try:
                setattr(fp, 'response', fp._raw_reader.response)
            except AttributeError:
                pass

        return fp

    def open(
            self,
            mode: str = "r",
            buffering: int = -1,
            encoding: Optional[str] = None,
            errors: Optional[str] = None,
            newline: Optional[str] = None,
            cache=True,
            multipart_upload=False
    ) -> IO:
        client = self.client
        if cache and "w" not in mode and hasattr(client, "cache") and client.cache is not None:
            file_cache = client.cache
            if cache == "check":
                # force load of etag if not known
                etag = self.etag
            fp = file_cache.cache(
                self, self._smart_open,
                mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline,
                getkwargs=dict(multipart_upload=multipart_upload)
            )
        else:
            fp = self._smart_open(
                mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline,
                multipart_upload=multipart_upload
            )

        return fp

    def read_bytes(self, cache=True) -> bytes:
        with self.open(mode="rb", cache=cache) as fp:
            return fp.read()

    def read_text(self, encoding: Optional[str] = None, errors: Optional[str] = None, cache=True) -> str:
        with self.open("r", encoding=encoding, errors=errors, cache=cache) as fp:
            return fp.read()

    def write_bytes(self, data: bytes, multipart_upload=False) -> int:
        """Open the file in bytes mode, write to it, and close the file.

        NOTE: vendored from pathlib since we override open
        https://github.com/python/cpython/blob/3.8/Lib/pathlib.py#L1235-L1242
        """
        # type-check for the buffer interface before truncating the file
        view = memoryview(data)
        with self.open(mode="wb", multipart_upload=multipart_upload) as f:
            return f.write(view)

    def write_text(
            self,
            data: str,
            encoding: Optional[str] = None,
            errors: Optional[str] = None,
            multipart_upload=False
    ) -> int:
        """Open the file in text mode, write to it, and close the file.

        NOTE: vendored from pathlib since we override open
        https://github.com/python/cpython/blob/3.8/Lib/pathlib.py#L1244-L1252
        """
        if not isinstance(data, str):
            raise TypeError("data must be str, not %s" % data.__class__.__name__)
        with self.open(mode="w", encoding=encoding, errors=errors, multipart_upload=multipart_upload) as f:
            return f.write(data)

    def __del__(self) -> None:
        # make sure that file handle to local path is closed
        if self._handle is not None:
            self._handle.close()


def set_default_s3_client_manager(client_manager):
    S3Path.clientmanager = client_manager


def register_s3_client_on_default_manager(client, partial_path):
    S3Path.clientmanager.register_client(client, partial_path)


def get_default_s3_client_manager() -> S3ClientManager:
    return S3Path.clientmanager


# Patch add copy function on pathlib Paths
def copy(self, destination, force_overwrite_to_cloud=True):
    if not self.exists() or not self.is_file():
        raise ValueError(
            f"Path {self} should be a file. To copy a directory tree use the method copytree."
        )
    if not force_overwrite_to_cloud and destination.exists():
        return

    with self.open("rb") as src:
        with destination.open("wb") as dst:
            dst.write(src.read())


_setup_has_run = [False]


def setup():
    if _setup_has_run[0]:
        return

    # Patch copy
    Path.copy = copy

    # Patch Pydantic
    pydantic.json.ENCODERS_BY_TYPE[PosixPath] = str
    pydantic.json.ENCODERS_BY_TYPE[WindowsPath] = str
    pydantic.json.ENCODERS_BY_TYPE[S3Path] = str

    # Set default client with no access
    S3Client(no_access=True).set_as_default_client()

    # Setup client manager with cache
    cache_path = os.getenv(env_variables.BREVETTI_AI_CACHE, None)
    if cache_path:
        from brevettiai.io.file_cache import FileCache
        cache = FileCache(cache_path=AnyPath(cache_path) / "s3")
        client_manager = S3ClientManager(cache=cache)
    else:
        client_manager = S3ClientManager()
    set_default_s3_client_manager(client_manager)

    # Register close of default manager
    atexit.register(lambda: get_default_s3_client_manager().close())


setup()
