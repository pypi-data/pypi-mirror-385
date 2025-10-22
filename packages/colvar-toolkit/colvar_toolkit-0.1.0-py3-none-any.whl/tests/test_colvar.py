from colvar import Colvar
import pytest
import numpy as np

from helpers import *


def test_import():
    assert Colvar is not None

def test_load():
    cv = Colvar.from_file(BASE_COLVAR)
    assert cv is not None
    assert cv._data.shape == (DAT_COL, DAT_LENGTH)

def test_missing_metadata():
    with pytest.raises(ValueError):
        cv = Colvar.from_file(MISSING_MD_COLVAR)
        assert cv is None

def test_shape():
    cv = Colvar.from_file(BASE_COLVAR)
    assert cv.shape == (DAT_COL, DAT_LENGTH)
    assert cv.shape == (len(cv.header), len(cv._data[0]))
    assert cv.shape == cv._data.shape

def test_header():
    cv = Colvar.from_file(BASE_COLVAR)
    assert cv.header == cv._header
    assert cv.header[0:3] == FIRST_THREE_KEYS
    assert len(cv.header) == DAT_COL

def test_write():
    cv = Colvar.from_file(BASE_COLVAR)
    check_reproduce(cv)

def test_stride():
    cv = Colvar.from_file(BASE_COLVAR)
    cv.stride(2)
    assert cv.shape == (DAT_COL, np.ceil(DAT_LENGTH / 2).astype(int))
    check_reproduce(cv)

def test_stride_no_time():
    cv = Colvar.from_file(BASE_COLVAR)
    cv._time = None
    cv.stride(2)
    assert cv.shape == (DAT_COL, np.ceil(DAT_LENGTH / 2).astype(int))
    check_reproduce(cv)


def test_choose():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    assert cv2.header == FIRST_THREE_KEYS
    assert cv2.shape == (3, DAT_LENGTH)
    check_reproduce(cv2)


def test_choose_invariance():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    del cv[FIRST_KEY]
    assert cv2[FIRST_KEY] is not None


def test_choose_invariance2():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    cv[FIRST_KEY] = np.ones(DAT_LENGTH)
    assert not np.allclose(cv2[FIRST_KEY], np.ones(DAT_LENGTH))


