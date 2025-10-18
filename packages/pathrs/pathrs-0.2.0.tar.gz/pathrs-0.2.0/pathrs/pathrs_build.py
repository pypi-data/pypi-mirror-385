#!/usr/bin/python3
# SPDX-License-Identifier: MPL-2.0
#
# libpathrs: safe path resolution on Linux
# Copyright (C) 2019-2025 Aleksa Sarai <cyphar@cyphar.com>
# Copyright (C) 2019-2025 SUSE LLC
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# This builds the _pathrs module (only needs to be done during the initial
# build of libpathrs, and can be redistributed alongside the pathrs.py wrapping
# library). It's much better than the ABI-mode of CFFI.

import re
import os
import sys

from typing import Any, Optional
from collections.abc import Iterable

import cffi


def load_hdr(ffi: cffi.FFI, hdr_path: str) -> None:
    with open(hdr_path) as f:
        hdr = f.read()

    # We need to first filter out all the bits of <pathrs.h> that are not
    # supported by cffi. Ideally this wouldn't be necessary, but the macro
    # support in cffi is very limited, and we make use of basic features that
    # are unsupported by cffi.

    # Drop all non-#define lines (directives are not supported).
    hdr = re.sub(r"^#\s*(?!define\b).*$", "", hdr, flags=re.MULTILINE)
    # Drop all:
    #  * "#define FOO(n) ..." lines (function-style macros are not supported).
    #  * Empty-value "#define FOO" lines (empty macros are not supported)
    # TODO: We probably should support multi-line macros.
    hdr = re.sub(r"^#\s*define\b\s*\w*(\(.*|)$", "", hdr, flags=re.MULTILINE)

    # Replace each struct-like body that has __CBINDGEN_ALIGNED before it,
    # remove the __CBINDGEN_ALIGNED and add "...;" as the last field in the
    # struct. This is how you tell cffi to get the proper alignment from the
    # compiler (__attribute__((aligned(n))) is not supported by cdef).
    hdr = re.sub(
        r"__CBINDGEN_ALIGNED\(\d+\)([^{;]*){([^}]+)}",
        r"\1 {\2 ...;}",
        hdr,
        flags=re.MULTILINE,
    )

    # Load the header.
    ffi.cdef(hdr)


def create_ffibuilder(**kwargs: Any) -> cffi.FFI:
    ffibuilder = cffi.FFI()
    ffibuilder.cdef("typedef uint32_t dev_t;")

    # We need to use cdef to tell cffi what functions we need to FFI to. But we
    # don't need the structs (I hope).
    for include_dir in kwargs.get("include_dirs", []):
        pathrs_hdr = os.path.join(include_dir, "pathrs.h")
        if os.path.exists(pathrs_hdr):
            load_hdr(ffibuilder, pathrs_hdr)

    # Add a source and link to libpathrs.
    ffibuilder.set_source(
        "_libpathrs_cffi", "#include <pathrs.h>", libraries=["pathrs"], **kwargs
    )

    return ffibuilder


def find_rootdir() -> str:
    # Figure out where the libpathrs source dir is.
    root_dir = None
    candidate = os.path.dirname(sys.path[0] or os.getcwd())
    while candidate != "/":
        try:
            # Look for a Cargo.toml which says it's pathrs.
            candidate_toml = os.path.join(candidate, "Cargo.toml")
            with open(candidate_toml, "r") as f:
                content = f.read()
            if re.findall(r'^name = "pathrs"$', content, re.MULTILINE):
                root_dir = candidate
                break
        except FileNotFoundError:
            pass
        candidate = os.path.dirname(candidate)

    if not root_dir:
        raise FileNotFoundError("Could not find pathrs source-dir root.")

    return root_dir


def srcdir_ffibuilder(root_dir: Optional[str] = None) -> cffi.FFI:
    """
    Build the CFFI bindings using the provided root_dir as the root of a
    pathrs source tree which has compiled cdylibs ready in target/*.
    """

    if root_dir is None:
        root_dir = find_rootdir()

    # Figure out which libs are usable.
    library_dirs: Iterable[str] = (
        os.path.join(root_dir, "target/%s/libpathrs.so" % (mode,))
        for mode in ("debug", "release")
    )
    library_dirs = (so_path for so_path in library_dirs if os.path.exists(so_path))
    library_dirs = sorted(library_dirs, key=lambda path: -os.path.getmtime(path))
    library_dirs = [os.path.dirname(path) for path in library_dirs]

    # Compile the libpathrs module.
    return create_ffibuilder(
        include_dirs=[os.path.join(root_dir, "include")],
        library_dirs=library_dirs,
    )


def system_ffibuilder() -> cffi.FFI:
    """
    Build the CFFI bindings using the installed libpathrs system libraries.
    """

    return create_ffibuilder(
        include_dirs=[
            "/usr/include",
            "/usr/local/include",
        ]
    )


if __name__ == "__main__":
    try:
        # Search for the compiled libraries to link to from our libpathrs
        # source if running outside of setuptools as a regular program.
        ffibuilder = srcdir_ffibuilder(root_dir=find_rootdir())
    except FileNotFoundError:
        # If we couldn't find a valid library in the source dir, just fallback
        # to using the system libraries.
        ffibuilder = system_ffibuilder()
    ffibuilder.compile(verbose=True)
elif os.environ.get("PATHRS_SRC_ROOT", "") != "":
    # If we're running in setup tools, we can't easily find the source dir.
    # However, distributions can set PATHRS_SRC_ROOT to the path of the
    # libpathrs source directory to make it easier to build the python modules
    # in the same %build script as the main library.
    ffibuilder = srcdir_ffibuilder(root_dir=os.environ.get("PATHRS_SRC_ROOT"))
else:
    # Use the system libraries if running inside standard setuptools.
    ffibuilder = system_ffibuilder()
