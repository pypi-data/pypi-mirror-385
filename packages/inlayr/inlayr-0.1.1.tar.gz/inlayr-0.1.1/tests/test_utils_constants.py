import os

from inlayr.utils import ConstDict

def test_defaults_loaded_nonempty():
    assert isinstance(ConstDict, dict)
    assert len(ConstDict) > 0
