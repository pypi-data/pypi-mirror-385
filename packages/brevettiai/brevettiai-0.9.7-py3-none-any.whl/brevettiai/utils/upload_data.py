#!/usr/bin/env python
"""
Functionality and script to upload data to the [Brevetti AI Platform](https://platform.brevetti.ai)

"""
import argparse
import os.path
import time
import concurrent
from tqdm import tqdm
import os
from brevettiai.platform.models.dataset import Dataset
from brevettiai.platform import PlatformAPI
from brevettiai.io.files import upload_files
from brevettiai.io import AnyPath


def recursive_relative_paths(path, reverse=False):
    for root, dirs, files in os.walk(path):
        if reverse:
            dirs[:] = dirs[::-1]
        for file in files:
            file_path = AnyPath(root).joinpath(file)
            dataset_path = file_path.relative_to(path)
            yield (file_path, dataset_path)


def filtered_generator(path, filter_files, reverse=False):
    all_gen = recursive_relative_paths(path)
    if len(filter_files):
        remote_type = type(filter_files[0])
        for (disk_path, dataset_path) in all_gen:
            ds_path_remote = remote_type(dataset_path)
            ix = filter_files.searchsorted(ds_path_remote)
            if ix >= len(filter_files) or filter_files[ix] != ds_path_remote:
                yield disk_path, dataset_path
    else:
        yield from all_gen

"""
Example usage:

python -m brevettiai.utils.upload_data my_local_folder --dataset_name "My new dataset name" --username my_name@my_domain.com --password *****
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', help='Absolute path to the folder containing the Dataset')
    parser.add_argument('--dataset_name', help='Name of the dataset as it will appear on the platform')
    parser.add_argument('--reference', help='Reference Field for the dataset')
    parser.add_argument('--username', help='Brevetti-AI platform username (https://platform.brevetti.ai)')
    parser.add_argument('--password', help='Brevetti-AI platform password (https://platform.brevetti.ai)')
    parser.add_argument('--dataset_id', help="Id of existing dataset to upload to")
    parser.add_argument('--overwrite', help="Overwrite data in existing dataset (only used if uploading to an existing dataset)", type=bool, default=False)
    parser.add_argument('--reverse', help="Reverse order of upload", type=bool, default=False)

    args = parser.parse_args()

    credentials = {}
    if "username" in args:
        credentials["username"] = args.username
    if "password" in args:
        credentials["password"] = args.password

    platform = PlatformAPI(**credentials, cache_remote_files=False, remember_me=True)

    if args.dataset_id:
        dataset_new = platform.get_dataset(args.dataset_id, write_access=True)
        platform.io.resolve_access_rights(str(dataset_new.bucket), resource_id=dataset_new.id, resource_type="dataset",
                                          mode="w")
    else:
        ds_name = args.dataset_name if args.dataset_name else os.path.basename(args.input_folder)
        dataset = Dataset(name=ds_name, reference=args.reference)
        print(f'Creating dataset {ds_name} on platform')
        dataset_new = platform.create(dataset, write_access=True)

    if not args.overwrite and args.dataset_id:
        import numpy as np
        remote_files = np.array([AnyPath(root).joinpath(y).relative_to(dataset_new.bucket)
                                 for root, dirs, files in platform.io.walk(str(dataset_new.bucket)) for y in files])
        remote_files.sort()
        generator = filtered_generator(args.input_folder, remote_files, reverse=args.reverse)
        print(f'Copying files to s3...')
    else:
        generator = recursive_relative_paths(args.input_folder, reverse=args.reverse)
        print('Copy entire dataset to s3...')

    start_procedure = time.time()

    source = []
    destination = []
    for (disk_path, dataset_path) in generator:
        source.append(disk_path)
        destination.append(dataset_new.bucket.joinpath(dataset_path))
    responses = list(upload_files(source, destination, force_overwrite_to_cloud=args.overwrite))

    print('End copy...')
    print(f'Dataset Created-Posted in {time.time() - start_procedure}s...')
