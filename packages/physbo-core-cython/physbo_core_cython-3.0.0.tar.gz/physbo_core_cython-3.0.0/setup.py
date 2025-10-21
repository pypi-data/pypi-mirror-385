# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2020- The University of Tokyo
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


from Cython.Build import cythonize

import numpy

compile_flags = [
    "-O3",
]
ext_mods = cythonize(
    [
        Extension(
            name="physbo_core_cython.misc._src.cythonized",
            sources=["src/physbo_core_cython/misc/_src/cythonized.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=compile_flags,
        ),
        Extension(
            name="physbo_core_cython.gp.cov._src.enhance_gauss",
            sources=["src/physbo_core_cython/gp/cov/_src/enhance_gauss.pyx"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=compile_flags,
        ),
    ]
)


setup(
    package_dir={"physbo_core_cython": "src/physbo_core_cython"},
    packages=find_packages(where="src"),
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_mods,
    name="physbo_core_cython",
)
