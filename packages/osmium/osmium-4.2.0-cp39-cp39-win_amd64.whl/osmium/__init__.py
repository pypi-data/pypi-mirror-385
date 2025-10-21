# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'osmium.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-osmium-4.2.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-osmium-4.2.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from ._osmium import (InvalidLocationError as InvalidLocationError,
                      apply as apply,
                      BaseHandler as BaseHandler,
                      BaseFilter as BaseFilter,
                      BufferIterator as BufferIterator,
                      SimpleWriter as SimpleWriter,
                      NodeLocationsForWays as NodeLocationsForWays,
                      OsmFileIterator as OsmFileIterator,
                      IdTracker as IdTracker)
from .helper import (make_simple_handler as make_simple_handler,
                     WriteHandler as WriteHandler,
                     MergeInputReader as MergeInputReader)
from .simple_handler import (SimpleHandler as SimpleHandler)
from .file_processor import (FileProcessor as FileProcessor,
                             zip_processors as zip_processors)
from .back_reference_writer import BackReferenceWriter as BackReferenceWriter
from .forward_reference_writer import ForwardReferenceWriter as ForwardReferenceWriter
import osmium.io
import osmium.osm
import osmium.index
import osmium.geom
import osmium.area
import osmium.filter
