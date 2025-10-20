# Electron Microscopy Pix (EMPix)

[![Test library](https://github.com/mrfitzpa/empix/actions/workflows/test_library.yml/badge.svg)](https://github.com/mrfitzpa/empix/actions/workflows/test_library.yml)
[![Code Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mrfitzpa/b7ef7892a2b5cf21ba4b6163c324afbe/raw/empix_coverage_badge.json)](https://github.com/mrfitzpa/empix/actions/workflows/measure_code_coverage.yml)
[![Documentation](https://img.shields.io/badge/docs-read-brightgreen)](https://mrfitzpa.github.io/empix)
[![PyPi Version](https://img.shields.io/pypi/v/empix.svg)](https://pypi.org/project/empix)
[![Conda-Forge Version](https://img.shields.io/conda/vn/conda-forge/empix.svg)](https://anaconda.org/conda-forge/empix)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

`empix` is a Python library that contains tools for analyzing electron
microscopy data that are not available in
[`hyperspy`](https://hyperspy.org/hyperspy-doc/current/index.html).

Visit the [`empix` website](https://mrfitzpa.github.io/empix) for a web version
of the installation instructions, the reference guide, and the examples archive.

The source code can be found in the [`empix` GitHub
repository](https://github.com/mrfitzpa/empix).



## Table of contents

- [Instructions for installing and uninstalling
  `empix`](#instructions-for-installing-and-uninstalling-empix)
  - [Installing `empix`](#installing-empix)
    - [Installing `empix` using
      `pip`](#installing-empix-using-pip)
    - [Installing `empix` using
      `conda`](#installing-empix-using-conda)
  - [Uninstalling `empix`](#uninstalling-empix)
- [Learning how to use `empix`](#learning-how-to-use-empix)



## Instructions for installing and uninstalling `empix`



### Installing `empix`

For all installation scenarios, first open up the appropriate command line
interface. On Unix-based systems, you could open e.g. a terminal. On Windows
systems you could open e.g. an Anaconda Prompt as an administrator.



#### Installing `empix` using `pip`

Before installing `empix`, make sure that you have activated the (virtual)
environment in which you intend to install said package. After which, simply
change into the root of the repository, and run the following command:

    pip install empix

The above command will install the latest stable version of `empix`.

To install the latest development version from the main branch of the [empix
GitHub repository](https://github.com/mrfitzpa/empix), one must first clone the
repository by running the following command:

    git clone https://github.com/mrfitzpa/empix.git

Next, change into the root of the cloned repository, and then run the following
command:

    pip install .

Note that you must include the period as well. The above command executes a
standard installation of `empix`.

Optionally, for additional features in `empix`, one can install additional
dependencies upon installing `empix`. To install a subset of additional
dependencies (along with the standard installation), run the following command
from the root of the repository:

    pip install .[<selector>]

where `<selector>` can be one of the following:

* `tests`: to install the dependencies necessary for running unit tests;
* `examples`: to install the dependencies necessary for executing files stored
  in `<root>/examples`, where `<root>` is the root of the repository;
* `docs`: to install the dependencies necessary for documentation generation;
* `all`: to install all of the above optional dependencies.

Alternatively, one can run:

    pip install empix[<selector>]

elsewhere in order to install the latest stable version of `empix`, along with
the subset of additional dependencies specified by `<selector>`.



#### Installing `empix` using `conda`

To install `empix` using the `conda` package manager, run the following command:

    conda install -c conda-forge empix

The above command will install the latest stable version of `empix`.



### Uninstalling `empix`

If `empix` was installed using `pip`, then to uninstall, run the following
command from the root of the repository:

    pip uninstall empix

If `empix` was installed using `conda`, then to uninstall, run the
following command from the root of the repository:

    conda remove empix



## Learning how to use `empix`

For those new to the `empix` library, it is recommended that they take a look at
the [Examples](https://mrfitzpa.github.io/empix/examples.html) page, which
contain code examples that show how one can use the `empix` library. While going
through the examples, readers can consult the [empix reference
guide](https://mrfitzpa.github.io/empix/_autosummary/empix.html) to understand
what each line of code is doing.