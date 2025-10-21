# Example running a custom job on the brevettiai platform
import logging
from collections import Counter
from pydantic import Field

import numpy as np
import pandas as pd

from brevettiai.platform import PlatformAPI, Job, JobSettings
from brevettiai.data.image.bcimg_dataset import BcimgDatasetSamples
from brevettiai.interfaces.pivot import export_pivot_table
from brevettiai.datamodel import ImageAnnotation
from brevettiai.io.files import load_files
from brevettiai.interfaces.facets_atlas import export_facets


log = logging.getLogger(__name__)


class ApplicationExplorationSettings(JobSettings):
    """Class containing all the custom parameters for the job"""
    data: BcimgDatasetSamples = Field(default_factory=BcimgDatasetSamples)


class ApplicationExploration(Job):
    """Class for running the actual job, specifying which parameter set to use"""
    settings: ApplicationExplorationSettings

    def build_pivot(self, samples):
        fields = {
            "category": "Folder",
            "label": "Annotation",
            "dataset_id": {
                "label": "Dataset id",
                "sort": [x.id for x in sorted(self.datasets, key=lambda x: x.name)]
            }
        }

        tags = self.backend.get_root_tags(self.id, self.api_key)
        export_pivot_table(self.artifacts_path / "pivot", samples, fields,
                           datasets=self.datasets, tags=tags, rows=["dataset_id"], cols=["label"])

    def build_facets(self, df, annotations, max_count=4096):
        if len(df) > max_count:
            idx = np.sort(np.random.choice(np.arange(len(df)), max_count, replace=False))
            df = df.iloc[idx]

        paths = df.apply(lambda x: BcimgDatasetSamples.build_path(**x), axis=1)

        # Add and remove columns
        urls = pd.Series([self.backend.get_annotation_url(p) for p in paths], name="URL", index=df.index)
        label_count = df.annotation_path.apply(
            lambda p: pd.Series(Counter(a.label for a in annotations[p].annotations), dtype=np.float32)
        ).fillna(0).astype(int).add_prefix("label ")
        df = df.drop(["annotation_path", "bucket", "path_format", "sequence_range"], axis=1, errors="ignore")

        df = pd.concat([urls, df, label_count], axis=1)

        export_facets(self.artifacts_path / "facets", df, paths)

    def run(self):
        # Load data from dataset
        all_sequences = self.settings.data.get_sequences(self.datasets)
        assert all_sequences.empty is False, "Datasets must contain at least 1 sequence"

        is_annotated_mask = ~all_sequences.annotation_frames.isna()
        annotated_sequences = all_sequences[is_annotated_mask]

        annotated_samples = self.settings.data.expand_sequences_with_annotations(annotated_sequences)

        annotations = dict(load_files(
            paths=annotated_samples.annotation_path.unique(),
            callback=lambda pth, x: (pth, ImageAnnotation.parse_raw(x)),
            tqdm_args=dict(desc="Loading annotations"),
        ))

        samples = self.settings.data.expand_annotations_files(annotated_samples, annotations)

        # Build exports
        self.build_pivot(samples)
        self.build_facets(annotated_samples, annotations)


def main(application="e1d58890-81cf-413c-a693-e702e792cf29", delete_after=True):
    platform = PlatformAPI()
    experiment = platform.experiment(
        name="exploration",
        job_type=ApplicationExploration,
        settings=ApplicationExplorationSettings(),
        application=application,
    )
    try:
        experiment.run(errors="raise")
    except Exception as ex:
        log.exception("error running job", exc_info=ex)
    finally:
        if delete_after:
            experiment.delete()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
