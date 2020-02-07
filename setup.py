from setuptools import setup, find_packages, Extension
import sys
import numpy
import os
import os.path as path
import multiprocessing

use_cython = True
force = False
profile = False
line_profile = False
install_rates = False

if "--skip-cython" in sys.argv:
    use_cython = False
    del sys.argv[sys.argv.index("--skip-cython")]

if "--force" in sys.argv:
    force = True
    del sys.argv[sys.argv.index("--force")]

if "--profile" in sys.argv:
    profile = True
    del sys.argv[sys.argv.index("--profile")]

if "--line-profile" in sys.argv:
    line_profile = True
    del sys.argv[sys.argv.index("--line-profile")]

if "--install-rates" in sys.argv:
    install_rates = True
    del sys.argv[sys.argv.index("--install-rates")]

source_paths = ['cherab', 'demos']
compilation_includes = [".", numpy.get_include()]
compilation_args = []
cython_directives = {
    'language_level': 3
}
setup_path = path.dirname(path.abspath(__file__))

if line_profile:
    compilation_args.append("-DCYTHON_TRACE=1")
    compilation_args.append("-DCYTHON_TRACE_NOGIL=1")
    cython_directives["linetrace"] = True

if use_cython:

    from Cython.Build import cythonize

    # build .pyx extension list
    extensions = []
    for package in source_paths:
        for root, dirs, files in os.walk(path.join(setup_path, package)):
            for file in files:
                if path.splitext(file)[1] == ".pyx":
                    pyx_file = path.relpath(path.join(root, file), setup_path)
                    module = path.splitext(pyx_file)[0].replace("/", ".")
                    extensions.append(Extension(module, [pyx_file], include_dirs=compilation_includes, extra_compile_args=compilation_args),)

    if profile:
        cython_directives["profile"] = True

    # generate .c files from .pyx
    extensions = cythonize(extensions, nthreads=multiprocessing.cpu_count(), force=force, compiler_directives=cython_directives)

else:

    # build .c extension list
    extensions = []
    for package in source_paths:
        for root, dirs, files in os.walk(path.join(setup_path, package)):
            for file in files:
                if path.splitext(file)[1] == ".c":
                    c_file = path.relpath(path.join(root, file), setup_path)
                    module = path.splitext(c_file)[0].replace("/", ".")
                    extensions.append(Extension(module, [c_file], include_dirs=compilation_includes, extra_compile_args=compilation_args),)

setup(
    name="cherab-compass",
    version="1.0.0",
    license="EUPL 1.1",
    namespace_packages=['cherab'],
    packages=find_packages(),
    include_package_data=True,
    ext_modules=extensions
)

