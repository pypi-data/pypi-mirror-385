from colvar import Colvar
import pytest
import numpy as np

from helpers import *

def test_tappend():
    cv = Colvar.from_file(BASE_COLVAR)
    cv.tappend(cv)
    assert cv.shape == (DAT_COL, 2 * DAT_LENGTH)
    check_reproduce(cv)


def test_tappend_with_shorter():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    with pytest.raises(ValueError):
        cv.tappend(cv2)


def test_tappend_with_longer():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    cv2.tappend(cv)
    assert cv2.shape == (3, 2 * DAT_LENGTH)
    check_reproduce(cv2)

def test_tappend_from_nothing():
    cv = Colvar()
    cv2 = Colvar.from_file(BASE_COLVAR)
    cv.tappend(cv2)
    assert cv.shape == (DAT_COL, DAT_LENGTH)
    assert np.allclose(cv._data, cv2._data)
    assert cv.header == cv2.header
    check_reproduce(cv)

def test_tappend_no_time():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.choose(FIRST_THREE_KEYS)
    cv2._time = None
    cv2.tappend(cv2)
    assert cv2.shape == (3, 2 * DAT_LENGTH)
    check_reproduce(cv2)

def test_tappend_from_file():
    cv = Colvar.from_file(BASE_COLVAR)
    cv.tappend(BASE_COLVAR)
    assert cv.shape == (DAT_COL, 2 * DAT_LENGTH)


def test_self_tappend():
    cv = Colvar.from_file(BASE_COLVAR)
    cv.tappend(cv)
    assert cv.shape == (DAT_COL, 2 * DAT_LENGTH)
    check_reproduce(cv)


def test_tappend_return_val():
    cv = Colvar.from_file(BASE_COLVAR)
    cv2 = cv.tappend(cv)
    assert cv2 is not None
    assert cv2.shape == (DAT_COL, 2 * DAT_LENGTH)
    assert np.allclose(cv._data, cv2._data)
    check_reproduce(cv2)


def test_tappend_return_val_when_empty():
    cv = Colvar()
    cv2 = Colvar.from_file(BASE_COLVAR)
    cv3 = cv.tappend(cv2)
    assert cv3 is not None
    assert cv3.shape == (DAT_COL, DAT_LENGTH)
    assert np.allclose(cv3.data, cv2.data)
    assert np.allclose(cv.data, cv3.data)
    check_reproduce(cv2)


def test_daisy_chained_tappend():
    cv = Colvar()
    cv2 = Colvar.from_file(BASE_COLVAR)
    cv.tappend(cv2).tappend(cv2)
    assert cv.shape == (DAT_COL, 2 * DAT_LENGTH)
    assert cv.header == cv2.header
    check_reproduce(cv)


def test_kappend():
    pass
