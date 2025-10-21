# Copyright: Multiple Authors
#
# This file is part of sigmf-python. https://github.com/sigmf/sigmf-python
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Hashing Functions"""

import hashlib
from pathlib import Path


def calculate_sha512(filename=None, fileobj=None, offset=None, size=None):
    """
    Return sha512 of file or fileobj.
    """
    the_hash = hashlib.sha512()
    bytes_to_hash = size
    bytes_read = 0

    if filename is not None:
        fileobj = open(filename, "rb")
    if size is None:
        bytes_to_hash = Path(filename).stat().st_size
    else:
        fileobj.seek(offset)

    while bytes_read < bytes_to_hash:
        buff = fileobj.read(min(4096, (bytes_to_hash - bytes_read)))
        the_hash.update(buff)
        bytes_read += len(buff)

    if filename is not None:
        fileobj.close()

    return the_hash.hexdigest()
