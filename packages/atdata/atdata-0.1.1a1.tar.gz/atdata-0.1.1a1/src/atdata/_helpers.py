"""Assorted helper methods for `ekumen`"""

##
# Imports

from io import BytesIO
import ormsgpack as omp

import numpy as np


##
# 

def pack_instance( x ) -> bytes:
    return omp.packb( x )

def unpack( bs: bytes ):
    return omp.unpackb( bs )

##

def array_to_bytes(x: np.ndarray) -> bytes:
    np_bytes = BytesIO()
    np.save(np_bytes, x, allow_pickle=True)
    return np_bytes.getvalue()

def bytes_to_array(b: bytes) -> np.ndarray:
    np_bytes = BytesIO(b)
    return np.load(np_bytes, allow_pickle=True)