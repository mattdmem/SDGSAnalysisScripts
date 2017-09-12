from scripts import calculate_uniformity
import os
import pysam

def test_calculate_uniformity():
    test = calculate_uniformity()
    assert test.toJsonDict() == {"status": 2, "message": "test"}