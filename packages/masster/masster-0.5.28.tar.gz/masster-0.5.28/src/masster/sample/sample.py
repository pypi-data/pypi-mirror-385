"""
sample.py - Mass Spectrometry Sample Analysis Module

This module provides comprehensive tools for processing and analyzing Data-Dependent Acquisition (DDA)
mass spectrometry data. It defines the `Sample` class, which offers methods to load, process, analyze,
and visualize mass spectrometry data from various file formats.

Supported File Formats:
    - mzML (standard XML format for mass spectrometry data)
    - Thermo RAW (native Thermo Fisher Scientific format)
    - Sciex WIFF (native Sciex format)
    - Sample5 (MASSter's native HDF5-based format for optimized storage)

Key Features:
    - **File Handling**: Load and save data in multiple formats with automatic format detection
    - **Feature Detection**: Detect and process mass spectrometry features using advanced algorithms
    - **Spectrum Analysis**: Retrieve and analyze MS1/MS2 spectra with comprehensive metadata
    - **Adduct Detection**: Find and annotate adducts and in-source fragments
    - **Isotope Analysis**: Detect and process isotopic patterns
    - **Chromatogram Extraction**: Extract and analyze chromatograms (EIC, BPC, TIC)
    - **Visualization**: Generate interactive and static plots for spectra, chromatograms, and 2D maps
    - **Statistics**: Compute and export detailed DDA run statistics and quality metrics
    - **Data Export**: Export processed data to various formats (XLSX, MGF, etc.)
    - **Memory Management**: Efficient handling of large datasets with on-disk storage options

Core Dependencies:
    - `pyopenms`: OpenMS library for file handling and feature detection algorithms
    - `polars`: High-performance data manipulation and analysis
    - `numpy`: Numerical computations and array operations
    - `bokeh`, `panel`, `holoviews`, `datashader`: Interactive visualizations and dashboards
    - `h5py`: HDF5 file format support for Sample5 files

Classes:
    Sample: Main class for handling DDA mass spectrometry data, providing methods for
            data import, processing, analysis, and visualization.

Typical Workflow:
    1. Load mass spectrometry data file
    2. Detect features using find_features()
    3. Optionally find MS2 spectra with find_ms2()
    4. Analyze and visualize results
    5. Export processed data

Example Usage:
    Basic analysis workflow:

    ```python
    from masster.sample import Sample

    # Load a mass spectrometry file
    sample = Sample(filename="experiment.mzML")

    # Detect features
    sample.find_features()

    # Find MS2 spectra for features
    sample.find_ms2()

    # Generate 2D visualization
    sample.plot_2d()

    # Export results
    sample.export_features("features.xlsx")
    ```

    Advanced usage with custom parameters:

    ```python
    from masster.sample import Sample
    from masster.sample.defaults import sample_defaults, find_features_defaults

    # Create custom parameters
    params = sample_defaults(log_level="DEBUG", label="My Experiment")
    ff_params = find_features_defaults(noise_threshold_int=1000)

    # Initialize with custom parameters
    sample = Sample(params=params)
    sample.load("data.raw")

    # Feature detection with custom parameters
    sample.find_features(params=ff_params)

    # Generate comprehensive statistics
    stats = sample.get_dda_stats()
    sample.plot_dda_stats()
    ```

Notes:
    - The Sample class maintains processing history and parameters for reproducibility
    - Large files can be processed with on-disk storage to manage memory usage
    - All visualizations are interactive by default and can be exported as static images
    - The module supports both individual sample analysis and batch processing workflows

Version: Part of the MASSter mass spectrometry analysis framework
Author: Zamboni Lab, ETH Zurich
"""

import importlib
import os
import sys

import polars as pl

from masster._version import get_version
from masster.logger import MassterLogger

from masster.sample.defaults.sample_def import sample_defaults
from masster.sample.defaults.find_features_def import find_features_defaults
from masster.sample.defaults.find_adducts_def import find_adducts_defaults
from masster.sample.defaults.find_ms2_def import find_ms2_defaults
from masster.sample.defaults.get_spectrum_def import get_spectrum_defaults

# Sample-specific imports - keeping these private, only for internal use
from masster.sample.h5 import _load_sample5
from masster.sample.h5 import _save_sample5
from masster.sample.helpers import _estimate_memory_usage
from masster.sample.helpers import _get_scan_uids
from masster.sample.helpers import _get_feature_uids
from masster.sample.adducts import find_adducts
from masster.sample.adducts import _get_adducts
from masster.sample.helpers import features_delete
from masster.sample.helpers import features_filter
from masster.sample.helpers import features_select
from masster.sample.helpers import select_closest_scan
from masster.sample.helpers import get_dda_stats
from masster.sample.helpers import get_feature
from masster.sample.helpers import get_scan
from masster.sample.helpers import get_eic
from masster.sample.helpers import set_source
from masster.sample.helpers import _recreate_feature_map
from masster.sample.helpers import _get_feature_map
from masster.sample.load import chrom_extract
from masster.sample.load import _index_file
from masster.sample.load import load
from masster.sample.load import load_noms1
from masster.sample.load import _load_ms1
from masster.sample.load import sanitize
from masster.sample.plot import plot_2d
from masster.sample.plot import plot_2d_oracle
from masster.sample.plot import plot_dda_stats
from masster.sample.plot import plot_chrom
from masster.sample.plot import plot_features_stats
from masster.sample.plot import plot_ms2_cycle
from masster.sample.plot import plot_ms2_eic
from masster.sample.plot import plot_ms2_q1
from masster.sample.plot import plot_bpc
from masster.sample.plot import plot_tic
from masster.sample.plot import _handle_sample_plot_output
from masster.sample.processing import _clean_features_df
from masster.sample.processing import _features_deisotope
from masster.sample.processing import _get_ztscan_stats
from masster.sample.processing import _spec_to_mat
from masster.sample.processing import analyze_dda
from masster.sample.processing import find_features
from masster.sample.processing import find_iso
from masster.sample.processing import find_ms2
from masster.sample.processing import get_spectrum
from masster.sample.parameters import store_history
from masster.sample.parameters import get_parameters
from masster.sample.parameters import update_parameters
from masster.sample.parameters import get_parameters_property
from masster.sample.parameters import set_parameters_property
from masster.sample.save import export_chrom
from masster.sample.save import export_dda_stats
from masster.sample.save import export_features
from masster.sample.save import export_mgf
from masster.sample.save import export_xlsx
from masster.sample.save import save


class Sample:
    """
    Main class for handling mass spectrometry sample data analysis.

    This class provides comprehensive functionality for loading, processing,
    and analyzing DDA (data-dependent acquisition) mass spectrometry data.
    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize a DDA (data-dependent acquisition) instance.

        This constructor initializes various attributes related to file handling,
        data storage, and processing parameters used for mass spectrometry data analysis.

        Parameters:
            **kwargs: Keyword arguments for setting sample parameters. Can include:
                     - A sample_defaults instance to set all parameters at once (pass as params=sample_defaults(...))
                     - Individual parameter names and values (see sample_defaults for available parameters)

                     Core initialization parameters:
                     - file (str, optional): The file path or file object to be loaded
                     - label (str, optional): An optional label to identify the file or dataset
                     - log_level (str): The logging level to be set for the logger. Defaults to 'INFO'
                     - log_label (str, optional): Optional label for the logger

                     Processing parameters:
                     - All parameters from sample_defaults class (see class documentation)

                     For backward compatibility, original signature is supported:
                     Sample(file=..., ondisk=..., label=..., log_level=..., log_label=...)
        """
        # Initialize default parameters

        # Check if a sample_defaults instance was passed
        if "params" in kwargs and isinstance(kwargs["params"], sample_defaults):
            params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            params = sample_defaults()

            # Update with any provided parameters
            for key, value in kwargs.items():
                if hasattr(params, key):
                    params.set(key, value, validate=True)

        # Store parameter instance for method access
        self.parameters = params

        # Set instance attributes for logger
        self.log_level = params.log_level.upper()
        self.log_label = params.log_label + " | " if params.log_label else ""
        self.log_sink = params.log_sink

        # Initialize independent logger
        self.logger = MassterLogger(
            instance_type="sample",
            level=params.log_level.upper(),
            label=params.log_label if params.log_label else "",
            sink=params.log_sink,
        )

        # Initialize history as dict to keep track of processing parameters
        self.history = {}
        self.store_history(["sample"], params.to_dict())

        # Initialize label from parameters
        self.label = params.label

        self.type = params.type  # dda, dia, ztscan
        self.polarity = params.polarity  # Initialize from parameters, may be overridden during raw file loading

        # this is the path to the original file. It's never sample5
        self.file_source = None
        # this is the path to the object that was loaded. It could be sample5
        self.file_path = None
        # Interface to handle the file operations (e.g., oms, alpharaw)
        self.file_interface = None
        # The file object once loaded, can be oms.MzMLFile or alpharaw.AlphaRawFile
        self.file_obj = None

        self._oms_features_map = None  # the feature map as obtained by openMS
        self.features_df = None  # the polars data frame with features
        # the polars data frame with metadata of all scans in the file
        self.scans_df = pl.DataFrame()
        # the polars data frame with MS1 level data
        self.ms1_df = pl.DataFrame()

        # lightweight lib data for matching, targeted analyses, etc. > superseded by study methods
        self.lib = None
        self.lib_match = None
        self.chrom_df = None

        if params.filename is not None:
            self.load(params.filename, ondisk=params.ondisk)

    # Attach module functions as class methods
    load = load
    load_noms1 = load_noms1
    _load_ms1 = _load_ms1  # Renamed from load_study for clarity
    load_study = _load_ms1  # Backward compatibility alias
    save = save
    find_features = find_features
    find_adducts = find_adducts
    _get_adducts = _get_adducts
    find_iso = find_iso
    find_ms2 = find_ms2
    get_spectrum = get_spectrum
    filter = features_filter
    select = features_select
    features_filter = filter  # New function that keeps only specified features
    filter_features = filter
    features_select = select
    select_features = select
    analyze_dda = analyze_dda
    store_history = store_history
    update_history = store_history  # Preferred name for consistency with Study class
    get_parameters = get_parameters
    update_parameters = update_parameters
    get_parameters_property = get_parameters_property
    set_parameters_property = set_parameters_property
    export_features = export_features
    export_xlsx = export_xlsx
    export_mgf = export_mgf
    export_chrom = export_chrom
    export_dda_stats = export_dda_stats
    plot_2d = plot_2d
    plot_2d_oracle = plot_2d_oracle
    plot_dda_stats = plot_dda_stats
    plot_chrom = plot_chrom
    plot_features_stats = plot_features_stats  # Renamed from plot_feature_stats
    plot_feature_stats = plot_features_stats  # Backward compatibility alias
    plot_ms2_cycle = plot_ms2_cycle
    plot_ms2_eic = plot_ms2_eic
    plot_ms2_q1 = plot_ms2_q1
    plot_bpc = plot_bpc
    plot_tic = plot_tic
    _handle_sample_plot_output = _handle_sample_plot_output
    get_eic = get_eic
    get_feature = get_feature
    get_scan = get_scan
    get_dda_stats = get_dda_stats
    select_closest_scan = select_closest_scan
    set_source = set_source
    _recreate_feature_map = _recreate_feature_map
    _get_feature_map = _get_feature_map

    # Additional method assignments for all imported functions
    # Removed internal-only methods: _load_sample5_study, _delete_ms2, _features_sync
    _estimate_memory_usage = _estimate_memory_usage
    _get_scan_uids = _get_scan_uids
    _get_feature_uids = _get_feature_uids
    features_delete = features_delete
    features_filter = features_filter
    _save_sample5 = _save_sample5
    _load_sample5 = _load_sample5

    # Removed internal-only load methods: _load_featureXML, _load_ms2data, _load_mzML, _load_raw, _load_wiff
    chrom_extract = chrom_extract
    _index_file = _index_file  # Renamed from index_file to be internal-only
    sanitize = sanitize
    _clean_features_df = _clean_features_df
    _features_deisotope = _features_deisotope
    _get_ztscan_stats = _get_ztscan_stats
    _spec_to_mat = _spec_to_mat
    # Removed internal-only methods: _save_featureXML, _get_adducts (used only in study modules)

    # defaults
    sample_defaults = sample_defaults
    find_features_defaults = find_features_defaults
    merge_defaults = find_features_defaults
    find_adducts_defaults = find_adducts_defaults
    find_ms2_defaults = find_ms2_defaults
    get_spectrum_defaults = get_spectrum_defaults

    def __dir__(self):
        """
        Custom __dir__ implementation to hide internal methods starting with '_'
        and backward compatibility aliases from tab completion and dir() calls,
        while keeping them accessible to class methods.

        Returns:
            list: List of public attribute and method names (excluding internal and deprecated methods)
        """
        # Define backward compatibility aliases to hide
        backward_compatibility_aliases = {
            "load_study",  # deprecated alias for _load_ms1
            "filter_features",  # alias for filter (deprecated naming)
            "select_features",  # alias for select (deprecated naming)
            "features_filter",  # confusing duplicate of filter
            "features_select",  # confusing duplicate of select
            "merge_defaults",  # alias for find_features_defaults (confusing)
            "plot_feature_stats",  # backward compatibility for plot_features_stats
            "store_history",  # deprecated alias for update_history
        }

        # Get all attributes from the class
        all_attrs = set()

        # Add attributes from the class and all its bases
        for cls in self.__class__.__mro__:
            all_attrs.update(cls.__dict__.keys())

        # Add instance attributes
        all_attrs.update(self.__dict__.keys())

        # Filter out attributes starting with '_' (but keep special methods like __init__, __str__, etc.)
        # Also filter out backward compatibility aliases
        public_attrs = [
            attr for attr in all_attrs if not attr.startswith("_") or attr.startswith("__") and attr.endswith("__")
        ]

        # Remove backward compatibility aliases from the public attributes
        public_attrs = [attr for attr in public_attrs if attr not in backward_compatibility_aliases]

        return sorted(public_attrs)

    def logger_update(
        self,
        level: str | None = None,
        label: str | None = None,
        sink: str | None = None,
    ):
        """Update the logging configuration for this Sample instance.

        Args:
            level: New logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            label: New label for log messages
            sink: New output sink (file path, file object, or "sys.stdout")
        """
        if level is not None:
            self.log_level = level.upper()
            self.logger.update_level(level)

        if label is not None:
            self.log_label = label + " | " if len(label) > 0 else ""
            self.logger.update_label(self.log_label)

        if sink is not None:
            if sink == "sys.stdout":
                self.log_sink = sys.stdout
            else:
                self.log_sink = sink
            self.logger.update_sink(self.log_sink)

    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        # Reset logger configuration flags to allow proper reconfiguration after reload
        try:
            import masster.logger as logger_module

            if hasattr(logger_module, "_SAMPLE_LOGGER_CONFIGURED"):
                logger_module._SAMPLE_LOGGER_CONFIGURED = False
        except Exception:
            pass

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all sample submodules
        sample_modules = []
        sample_module_prefix = f"{base_modname}.sample."

        # Get all currently loaded modules that are part of the sample package
        for module_name in sys.modules:
            if module_name.startswith(sample_module_prefix) and module_name != current_module:
                sample_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.logger",
            f"{base_modname}.lib",
        ]

        # Add study submodules
        study_modules = []
        study_module_prefix = f"{base_modname}.study."
        for module_name in sys.modules:
            if module_name.startswith(study_module_prefix) and module_name != current_module:
                study_modules.append(module_name)

        all_modules_to_reload = core_modules + sample_modules + study_modules

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    self.logger.debug(f"Reloaded module: {full_module_name}")
            except Exception as e:
                self.logger.warning(f"Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (sample.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            self.logger.debug("Module reload completed")
        except Exception as e:
            self.logger.error(f"Failed to reload current module {current_module}: {e}")

    def get_version(self):
        return get_version()

    def info(self):
        # show the key attributes of the object
        str = f"File: {os.path.basename(self.file_path)}\n"
        str += f"Path: {os.path.dirname(self.file_path)}\n"
        str += f"Source: {self.file_source}\n"
        str += f"Type: {self.type}\n"
        str += f"Polarity: {self.polarity}\n"
        str += f"MS1 scans: {len(self.scans_df.filter(pl.col('ms_level') == 1))}\n"
        str += f"MS2 scans: {len(self.scans_df.filter(pl.col('ms_level') == 2))}\n"
        if self.features_df is not None:
            str += f"Features: {len(self.features_df) if self.features_df is not None else 0}\n"
            str += f"Features with MS2 spectra: {len(self.features_df.filter(pl.col('ms2_scans').is_not_null()))}\n"
        else:
            str += "Features: 0\n"
            str += "Features with MS2 spectra: 0\n"
        mem_usage = self._estimate_memory_usage()
        str += f"Estimated memory usage: {mem_usage:.2f} MB\n"

        print(str)

    def __str__(self):
        if self.features_df is None:
            str = f"masster Sample, source: {os.path.basename(self.file_path)}, features: 0"
        else:
            str = f"masster Sample, source: {os.path.basename(self.file_path)}, features: {len(self.features_df)}"
        return str


if __name__ == "__main__":
    print(
        "This module is not meant to be run directly. Please import it in your script.",
    )
