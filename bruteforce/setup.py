from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import numpy
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

ext_modules = [Extension("mcsampler", ['mcsampler.pyx', 'randomkit.c'],
            include_dirs=[numpy_include],
            extra_compile_args=["-O3","-ffast-math"]),]

setup(
    name = "MC Sampling",
    ext_modules = cythonize(ext_modules),
)
