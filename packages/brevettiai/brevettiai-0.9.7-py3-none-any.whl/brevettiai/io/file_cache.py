import io
import logging
import os
import shutil
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
from tqdm import tqdm

import semidbm

log = logging.getLogger(__name__)


class FileCache:
    def __init__(self, cache_path=None):
        if cache_path is None:
            self._cache_tmp_dir = TemporaryDirectory()
            cache_path = self._cache_tmp_dir.name

        self.cache_path = Path(cache_path)

        # Create or load cache database, creating it if it does not exist
        self.cache_map = semidbm.open(self.cache_path / "_file_cache.dbm", 'c')
        self.cache_lock = threading.Lock()

    def cachekey(self, s3path):
        return str(s3path).encode("utf8")

    def check(self, check_etag=False):
        """
        Check and clean the contents of the cache
        :param check_etag: check etag and remove out of date items (Very slow as it produces 1 call per item)
        :return:
        """
        from brevettiai.io import S3Path

        with self.cache_lock:
            root_len = len(self.cache_path.parts)
            cachekeys = set()
            # Remove files not in cache database

            files = [path for path in self.cache_path.glob("[!_]*/**/*") if path.is_file()]
            for path in tqdm(files, desc="Checking files in cache"):
                if path.is_file():
                    # Build path on S3
                    s3path = S3Path("s3://").joinpath(*path.parts[root_len:])

                    cachekey = self.cachekey(s3path)
                    if cachekey in self.cache_map:
                        if check_etag:
                            try:
                                s3path.refresh_client()
                                cached_etag = self.cache_map[cachekey].decode()
                                if s3path.etag != cached_etag:
                                    log.info(f"Removing '{path}', {s3path.etag} != {cached_etag}")
                                    path.unlink()
                            except AttributeError:
                                pass

                        cachekeys.add(cachekey)
                    else:
                        log.info(f"Removing '{path}'")
                        path.unlink()

            # Remove keys not in files
            for cachekey in set(self.cache_map.keys()) - cachekeys:
                del self.cache_map[cachekey]

            self.cache_map.compact()

            log.info(f"""
            Cache stats
            path: {self.cache_path}
            items: {len(self.cache_map.keys())}
            """)

    def close(self):
        log.info("trying to close and compact cache")
        try:
            self.cache_map.close(compact=True)
        except Exception:
            pass

    def cache(self, path, _get, getkwargs, **kwargs):
        # cache path of file
        target = path._local
        cachekey = self.cachekey(path)

        try:
            with self.cache_lock:
                cached_etag_bytes = self.cache_map[cachekey]
            cached_etag = cached_etag_bytes.decode()

            if (not path.cached_etag) or path.etag == cached_etag and os.path.isfile(path):
                log.debug(f"Cache hit! '{path.cached_etag}' {path}")
                return open(path, **kwargs)
            log.debug(f"Cache dirty! '{path.cached_etag}' {path}")
        except (KeyError, UnicodeDecodeError) as ex:
            log.debug(f"Cache miss! '{path.cached_etag}' {path}")
            pass

        # Update cache
        target.parent.mkdir(parents=True, exist_ok=True)

        fp = _get(**kwargs, **getkwargs)
        part_target = target.parent / f"{target.name}.{time.perf_counter_ns()}.part"
        with open(part_target, "w" if isinstance(fp, io.TextIOBase) else "wb") as target_fp:
            shutil.copyfileobj(fp, target_fp, length=8192)
        os.replace(part_target, target)

        try:
            etag = fp.response.get("ETag", "")[1:-1]
        except AttributeError:
            etag = ""

        with self.cache_lock:
            self.cache_map[cachekey] = etag

        fp = target.open(**kwargs)
        return fp
