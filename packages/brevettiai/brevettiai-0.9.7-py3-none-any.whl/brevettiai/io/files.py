import concurrent.futures
from tqdm import tqdm
from brevettiai.io import AnyPath


def _download_file(source, callback):
    if type(source) == str:
        source = AnyPath(source)
    content = source.read_bytes()
    if callback is not None:
        return callback(source, content)
    else:
        return content


def _upload(source, destination, callback, force_overwrite_to_cloud=False):
    if isinstance(source, AnyPath):
        response = source.copy(destination, force_overwrite_to_cloud=force_overwrite_to_cloud)
    else:
        if type(destination) == str:
            destination = AnyPath(destination)
        if type(source) == str:
            source = _download_file(source, callback=None)
        if force_overwrite_to_cloud or not destination.exists():
            response = destination.write_bytes(source)
        else:
            response = None

    if callback is not None:
        return callback(source, destination, response)
    else:
        return response


def load_files(paths, callback=None, monitor=True, tqdm_args=None, max_workers=16):
    """Download multiple files at once"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_download_file, src, callback=callback) for src in paths]

        if monitor:
            futures = tqdm(futures, **(tqdm_args or {}))

        for f in futures:
            yield f.result()


def upload_files(source_list, destination_paths, callback=None, monitor=True, tqdm_args=None, max_workers=16,
                 force_overwrite_to_cloud=True):
    """Download multiple files at once"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_upload, src, dst, callback=callback,
                                   force_overwrite_to_cloud=force_overwrite_to_cloud)
                   for src, dst in zip(source_list, destination_paths)]

    if monitor:
        futures = tqdm(futures, **(tqdm_args or {}))

    for f in futures:
        yield f.result()