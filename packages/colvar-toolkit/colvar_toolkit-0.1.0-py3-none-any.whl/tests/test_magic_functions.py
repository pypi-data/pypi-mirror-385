from colvar import Colvar
import numpy as np
import pytest

from helpers import *

def test_magic_contains():
    cv = Colvar.from_file(BASE_COLVAR)
    assert FIRST_KEY in cv
    assert NONEXISTENT_KEY not in cv


def test_magic_getitem():
    cv = Colvar.from_file(BASE_COLVAR)
    assert np.allclose(cv[FIRST_KEY], cv._data[0])
    with pytest.raises(KeyError):
        cv[NONEXISTENT_KEY]


def test_magic_setitem():
    cv = Colvar.from_file(BASE_COLVAR)
    cv[NONEXISTENT_KEY] = np.ones(DAT_LENGTH)
    assert NONEXISTENT_KEY in cv
    assert np.allclose(cv[NONEXISTENT_KEY], np.ones(DAT_LENGTH))
    assert cv.shape == (DAT_COL + 1, DAT_LENGTH)
    check_reproduce(cv)


def test_magic_setitem_existing():
    cv = Colvar.from_file(BASE_COLVAR)
    cv[FIRST_KEY] = np.ones(DAT_LENGTH)
    assert np.allclose(cv[FIRST_KEY], np.ones(DAT_LENGTH))
    assert cv.shape == (DAT_COL, DAT_LENGTH)
    check_reproduce(cv)


def test_magic_setitem_wrong_length():
    cv = Colvar.from_file(BASE_COLVAR)
    with pytest.raises(ValueError):
        cv[NONEXISTENT_KEY] = np.ones(DAT_LENGTH - 1)


def test_magic_setitem_from_empty():
    cv = Colvar()
    cv[NONEXISTENT_KEY] = np.ones(DAT_LENGTH)
    assert NONEXISTENT_KEY in cv
    assert np.allclose(cv[NONEXISTENT_KEY], np.ones(DAT_LENGTH))
    assert cv.shape == (1, DAT_LENGTH)
    check_reproduce(cv)


def test_magic_delitem():
    cv = Colvar.from_file(BASE_COLVAR)
    del cv[FIRST_KEY]
    assert FIRST_KEY not in cv
    assert cv.shape == (DAT_COL - 1, DAT_LENGTH)
    check_reproduce(cv)