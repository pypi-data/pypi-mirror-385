from __future__ import annotations

import os

from datetime import datetime

import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.sample.sample import Sample


def save(self, filename=None, add_timestamp=True, compress=False):
    """
    Save the study to an HDF5 file with proper serialization of complex objects.

    Args:
        study: The study object to save
        filename (str, optional): Target file name. If None, uses default.
        add_timestamp (bool, optional): If True, appends timestamp to avoid overwriting.
                                      Default True for safety (original behavior).
        compress (bool, optional): If True, uses compressed mode and skips
                                   some heavy columns for maximum speed. Default False.
    """

    if filename is None:
        # save to default file name in folder
        if self.folder is not None:
            filename = os.path.join(self.folder, "data.study5")
        else:
            self.logger.error("either filename or folder must be provided")
            return
    else:
        # check if filename includes any path
        if not os.path.isabs(filename):
            if self.folder is not None:
                filename = os.path.join(self.folder, filename)
            else:
                filename = os.path.join(os.getcwd(), filename)

    # Add timestamp by default to avoid overwriting (original behavior restored)
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{filename.replace('.study5', '')}_{timestamp}.study5"

    # Log file size information for performance monitoring
    if hasattr(self, "features_df") and not self.features_df.is_empty():
        feature_count = len(self.features_df)
        sample_count = len(self.samples_df) if hasattr(self, "samples_df") and not self.samples_df.is_empty() else 0
        self.logger.debug(
            f"Saving study with {sample_count} samples and {feature_count} features to {filename}",
        )

    # Use compressed mode for large datasets
    if compress:
        from masster.study.h5 import _save_study5_compressed

        _save_study5_compressed(self, filename)
    else:
        from masster.study.h5 import _save_study5

        _save_study5(self, filename)

    if self.consensus_map is not None:
        # save the features as a separate file
        from masster.study.save import _save_consensusXML

        _save_consensusXML(self, filename=filename.replace(".study5", ".consensusXML"))
    self.filename = filename


def save_samples(self, samples=None):
    if samples is None:
        # get all sample_uids from samples_df
        samples = self.samples_df["sample_uid"].to_list()

    self.logger.info(f"Saving features for {len(samples)} samples...")

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_uid in tqdm(
        samples,
        total=len(samples),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Save samples",
        disable=tdqm_disable,
    ):
        # check if sample_uid is in samples_df
        if sample_uid not in self.samples_df.get_column("sample_uid").to_list():
            self.logger.warning(
                f"Sample with uid {sample_uid} not found in samples_df.",
            )
            continue
        # load the mzpkl file
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            continue
        ddaobj = Sample(filename=sample_row.row(0, named=True)["sample_path"])
        if "rt_original" not in ddaobj.features_df.columns:
            # add column 'rt_original' with rt values
            ddaobj.features_df = ddaobj.features_df.with_columns(
                pl.col("rt").alias("rt_original"),
            )
        # find the rows in features_df that match the sample_uid
        matching_rows = self.features_df.filter(pl.col("sample_uid") == sample_uid)
        if not matching_rows.is_empty():
            # Update rt values in ddaobj.features_df based on matching_rows
            rt_values = matching_rows["rt"].to_list()
            if len(rt_values) == len(ddaobj.features_df):
                ddaobj.features_df = ddaobj.features_df.with_columns(
                    pl.lit(rt_values).alias("rt"),
                )
        # save ddaobj
        ddaobj.save()
        sample_name = sample_row.row(0, named=True)["sample_name"]
        sample_path = sample_row.row(0, named=True)["sample_path"]

        # Find the index of this sample in the original order for features_maps
        sample_index = next(
            (
                i
                for i, row_dict in enumerate(self.samples_df.iter_rows(named=True))
                if row_dict["sample_uid"] == sample_uid
            ),
            None,
        )

        # Determine where to save the featureXML file based on sample_path location
        if sample_path.endswith(".sample5"):
            # If sample_path is a .sample5 file, save featureXML in the same directory
            featurexml_filename = sample_path.replace(".sample5", ".featureXML")
            self.logger.debug(
                f"Saving featureXML alongside .sample5 file: {featurexml_filename}",
            )
        else:
            # Fallback to study folder or current directory (original behavior)
            if self.folder is not None:
                featurexml_filename = os.path.join(
                    self.folder,
                    sample_name + ".featureXML",
                )
            else:
                featurexml_filename = os.path.join(
                    os.getcwd(),
                    sample_name + ".featureXML",
                )
            self.logger.debug(
                f"Saving featureXML to default location: {featurexml_filename}",
            )

        fh = oms.FeatureXMLFile()
        if sample_index is not None and sample_index < len(self.features_maps):
            fh.store(featurexml_filename, self.features_maps[sample_index])

    self.logger.debug("All samples saved successfully.")


def _save_consensusXML(self, filename: str):
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus features found.")
        return

    # Build consensus map from consensus_df with proper consensus_id values
    import pyopenms as oms

    consensus_map = oms.ConsensusMap()

    # Set up file descriptions for all samples
    file_descriptions = consensus_map.getColumnHeaders()
    if hasattr(self, "samples_df") and not self.samples_df.is_empty():
        for i, sample_row in enumerate(self.samples_df.iter_rows(named=True)):
            file_description = file_descriptions.get(i, oms.ColumnHeader())
            file_description.filename = sample_row.get("sample_name", f"sample_{i}")
            file_description.size = 0  # Will be updated if needed
            file_description.unique_id = i + 1
            file_descriptions[i] = file_description
        consensus_map.setColumnHeaders(file_descriptions)

    # Add consensus features to the map (simplified version without individual features)
    for consensus_row in self.consensus_df.iter_rows(named=True):
        consensus_feature = oms.ConsensusFeature()

        # Set basic properties
        consensus_feature.setRT(float(consensus_row.get("rt", 0.0)))
        consensus_feature.setMZ(float(consensus_row.get("mz", 0.0)))
        consensus_feature.setIntensity(float(consensus_row.get("inty_mean", 0.0)))
        consensus_feature.setQuality(float(consensus_row.get("quality", 1.0)))

        # Set the unique consensus_id as the unique ID
        consensus_id_str = consensus_row.get("consensus_id", "")
        if consensus_id_str and len(consensus_id_str) == 16:
            try:
                # Convert 16-character hex string to integer for OpenMS
                consensus_uid = int(consensus_id_str, 16)
                consensus_feature.setUniqueId(consensus_uid)
            except ValueError:
                # Fallback to hash if not hex
                consensus_feature.setUniqueId(hash(consensus_id_str) & 0x7FFFFFFFFFFFFFFF)
        else:
            # Fallback to consensus_uid
            consensus_feature.setUniqueId(consensus_row.get("consensus_uid", 0))

        consensus_map.push_back(consensus_feature)

    # Save the consensus map
    fh = oms.ConsensusXMLFile()
    fh.store(filename, consensus_map)
    self.logger.debug(f"Saved consensus map with {len(self.consensus_df)} features to {filename}")
    self.logger.debug("Features use unique 16-character consensus_id strings")


def save_consensus(self, **kwargs):
    """Save the consensus map to a file."""
    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return
    from masster.study.save import _save_consensusXML

    _save_consensusXML(self, **kwargs)
