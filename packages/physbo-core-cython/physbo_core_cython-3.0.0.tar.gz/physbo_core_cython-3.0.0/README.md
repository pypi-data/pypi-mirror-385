# Cythonized core modules for PHYSBO

This package contains the cythonized core modules for [PHYSBO](https://github.com/issp-center-dev/PHYSBO).
Originally, PHYSBO used Cython to speed up the performance of the core modules, but it requires a bit extra effort to build particularly on windows.
To simplify the build process, we moved the cythonized core modules to this package, and users can use PHYSBO without Cython (pure python).
If users want to improve the performance, they can install this package and use the cythonized core modules again.

## Dependencies

- Python >= 3.9
- Cython
- NumPy

## Install

- From PyPI (recommended)

```bash
python3 -m pip install physbo-core-cython
```

- From source (for developers)
    1. Download or clone the github repository

        ```bash
        git clone https://github.com/issp-center-dev/PHYSBO-Core-cython
        ```

    1. Install via pip

        ``` bash
        # ./PHYSBO is the root directory of PHYSBO
        # pip install options such as --user are avaiable

        python3 -m pip install ./PHYSBO-Core-cython
        ```

## Uninstall

```bash
python3 -m pip uninstall physbo-core-cython
```

## License

This is distributed under Mozilla Public License version 2.0 (MPL v2).

### Copyright

© *2020- The University of Tokyo. All rights reserved.*
This software was developed with the support of \"*Project for advancement of software usability in materials science*\" of The Institute for Solid State Physics, The University of Tokyo.
