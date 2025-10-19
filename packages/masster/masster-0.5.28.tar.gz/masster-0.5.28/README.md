# masster
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/masster)](https://badge.fury.io/py/masster)
[![PyPI version](https://badge.fury.io/py/masster.svg)](https://badge.fury.io/py/masster)

**MASSter** is a Python package for the analysis of metabolomics experiments by LC-MS/MS data, with a main focus on the challenging tasks of untargeted and large-scale studies.  

## Background and motivation

MASSter is actively used, maintainted, and developed by the Zamboni Lab at ETH Zurich. The project started because many needs of were unmatched by the "usual" software packages (mzmine, msdial, W4M, ...), e.g. performance, scalability, sensitivity, robustness, speed, rapid implementation of new features, embedding in ETL systems, and so on. 

All methods include a long list of parameters, and might wrap alternative algorithms. These are only relevant for advanced users. We recommend running the processing methods with defaults, or using the Wizard.  

## Content

MASSter is designed to deal with DDA data, and hides functionalities for DIA and ZTScan DIA data. The sample-centric feature detection uses OpenMS, which is both accurate and fast, and it was wrapped with additional code to improve isotope and adduct detection. All other functionalities are own implementations: centroiding, RT alignment, adduct and isotopomer detection, merging of multiple samples, gap-filling, quantification, etc. 

MASSter was engineered to maximize quality of results, sensitivity, scalability, and also speed. Yes, it's Python which is notoriously slower than other languages, but considerable time was spent in speeding up everything, including the systematic use of [polars](https://pola.rs/), numpy vectorization, multiprocessing, chunking, etc. MASSter was tested with studies with 3000+ LC-MS/MS samples (1 Mio MS2 spectra), and it autonomously completed analysis within a few hours. 

## Architecture

MASSter defines own classes for Spectra, Chromatograms, Libraries, Samples, and Studies (= bunch of samples, i.e. a LC-MS sequence). Users will deal mostly with one Study() object at the time. Sample() objects are created when analyzing a batch - and saved for caching -, or will be used only for development, troubleshooting, or to generate illustrations. 

The analysis can be done in scripts (without user intervention, e.g. by the integrated Wizard), or interactively in notebooks, i.e. [marimo](https://marimo.io/) or [jupyter](https://jupyter.org/).

## Prerequisites

You'll need to install Python (3.10-3.13, 3.14 has not been tested yet).

MASSter reads raw (Thermo), wiff (SCIEX), or mzML data. Reading vendor formats relies on .NET libraries, and is only possible in Windows. On Linux or MacOS, you'll be forced to use mzML data.

**It's recommended to use data in either vendor's raw format (wiff and raw) or mzML in profile data.** MASSter includes a sophisticated and sufficiently fast centroiding algorithm that works well across the full dynamic range and will only act on the spectra that are relevant. In our tests with data from different vendors, the centroiding performed much better than most Vendor's implementations (that are primarily proteomics-centric). 

If still want to convert raw data to centroided mzML, please use (CentroidR)[https://github.com/Adafede/CentroidR/tree/0.0.0.9001]. 

## Installation

```bash
pip install masster
```

## Getting started
**The quickest way to use, or learn how to use MASSter, is to use the Wizard** which we integrated and, ideally, takes care of everything automatically. 

The Wizard only needs to know where to find the MS files and were the store the results.
```python
from masster import Wizard
wiz = Wizard(
    source=r'..\..\folder_with_raw_data',    # where to find the data
    folder=r'..\..folder_to_store_results',  # where to save the results
    ncores=10                                # this is optional
    )
wiz.test_and_run()
```

This will trigger the analysis of raw data, and the creation of a script to process all samples and then assemble the study. The whole processing will be stored as `1_masster_workflow.py` in the output folder. The wizard will test once and, if successull, run the full workflow using parallel processes. Once the processing is over you, navigate to `folder` to see what happened...

If you want to interact with your data, we recommend using [marimo](https://marimo.io/) or [jupyter](https://jupyter.org/) and open the `*.study5` file, for example:

```bash
# use marimo to open the script created by marino
marimo edit '..\..folder_to_store_results\2_interactive_analysis.py'
# or, if you use uv to manage an environment with masster 
uv run marimo edit '..\..folder_to_store_results\2_interactive_analysis.py'
```

### Basic Workflow for analyzing LC-MS study with 1-1000+ samples
In MASSter, the main object for data analysis is a `Study`, which consists of a bunch of `Samples`. 
```python
import masster
# Initialize the Study object with the default folder
study = masster.Study(folder=r'D:\...\mylcms')

# Load data from folder with raw data, here: WIFF
study.add(r'D:\...\...\...\*.wiff')

# Perform retention time correction
study.align(rt_tol=2.0)
study.plot_alignment()
study.plot_rt_correction()
study.plot_bpc()

# Find consensus features
study.merge(min_samples=3)   # this will keep only the features that were found in 3 or more samples
study.plot_consensus_2d()

# retrieve information
study.info()

# Retrieve EICs for quantification
study.fill()

# Integrate EICs according to consensus metadata
study.integrate()

# export results
study.export_mgf()
study.export_mztab()
study.export_xlsx()
study.export_parquet()

# Save the study to .study5
study.save()

# Some of the plots...
study.plot_samples_pca()
study.plot_samples_umap()
study.plot_samples_2d()

# To know more about the available methods...
dir(study)
```
The information is stored in Polars data frame, in particular:
```python
# information on samples
study.samples_df
# information on consensus features
study.consensus_df
# information on original features from ALL samples, including MS2 and EICs
study.features_df
```

### Analysis of a single sample
For troubleshooting, exploration, or just to create a figure on a single file, you might want to open and process a single file:  
```python
from masster import Sample
sample = Sample(filename='...') # full path to a *.raw, *.wiff, *.mzML, or *.sample5 file
# peek into sample
sample.info()

# process
sample.find_features(chrom_fwhm=0.5, noise=50) # for orbitrap data, set noise to 1e5
sample.find_adducts()
sample.find_ms2()

# access data
sample.features_df

# save results
sample.save() # stores to *.sample5, our custom hdf5 format
sample.export_mgf()

# some plots
sample.plot_bpc()
sample.plot_tic()
sample.plot_2d()
sample.plot_features_stats()

# explore methods
dir(study)
```

## Disclaimer

**MASSter is research software under active development.** While we use it extensively in our lab and strive for quality and reliability, please be aware:

- **No warranties**: The software is provided "as is" without any warranty of any kind, express or implied
- **Backward compatibility**: We do not guarantee backward compatibility between versions. Breaking changes may occur as we improve the software
- **Performance**: While optimized for our workflows, performance may vary depending on your data and system configuration
- **Results**: We do our best to ensure accuracy, but you should validate results independently for your research
- **Support**: This is an academic project with limited resources. Community support is available through GitHub issues, but we cannot guarantee response times
- **Production use**: If you plan to use MASSter in production or critical workflows, thorough testing with your data is recommended

We welcome feedback, bug reports, and contributions via GitHub!

## License
GNU Affero General Public License v3

See the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
This project uses several third-party libraries, including pyOpenMS which is licensed under the BSD 3-Clause License. For complete information about third-party dependencies and their licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Citation
If you use MASSter in your research, please cite this repository.
