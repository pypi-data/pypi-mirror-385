"""Test dataaset functionality."""

##

import pytest

from dataclasses import dataclass

import numpy as np

from numpy.typing import NDArray
from typing import (
    Type,
    Any,
)

import atdata.dataset as ekd


## Sample test cases

@dataclass
class BasicTestSample( ekd.PackableSample ):
    name: str
    position: int
    value: float

@dataclass
class NumpyTestSample( ekd.PackableSample ):
    label: int
    image: NDArray

test_sample_classes = [
    (
        BasicTestSample, {
            'name': 'Hello, world!',
            'position': 42,
            'value': 1024.768,
        }
    ),
    (
        NumpyTestSample, {
            'label': 9_001,
            'image': np.random.randn( 1024, 1024 ),
        }
    )
]


## Tests

@pytest.mark.parametrize( ('SampleType', 'sample_data'), test_sample_classes )
def test_create_sample(
            SampleType: Type[ekd.PackableSample],
            sample_data: ekd.MsgpackRawSample,
        ):
    """
    Test our ability to create samples from semi-structured data
    """
    sample = SampleType.from_data( sample_data )
    assert isinstance( sample, SampleType ), f'Did not properly form sample for test type {SampleType}'

    for k, v in sample_data.items():
        cur_assertion: bool
        if isinstance( v, np.ndarray ):
            cur_assertion = np.all( getattr( sample, k ) == v ) == True
        else:
            cur_assertion = getattr( sample, k ) == v
        assert cur_assertion, f'Did not properly incorporate property {k} of test type {SampleType}'