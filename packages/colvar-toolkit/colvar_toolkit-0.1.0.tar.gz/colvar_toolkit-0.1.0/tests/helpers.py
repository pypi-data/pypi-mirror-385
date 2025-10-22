from colvar import Colvar
import numpy as np
import os

DAT_LENGTH = 1001
DAT_COL = 428

BASE_COLVAR = "./tests/base.dat"
MISSING_MD_COLVAR = "./tests/missing_meta_data.dat"
TEST_COLVAR = "./tests/test.dat"

FIRST_THREE_KEYS = ["d5_1664", "d5_1665", "d5_1666"]
FIRST_KEY = "d5_1664"
NONEXISTENT_KEY = "pratyush"

def check_reproduce(colvar):
    colvar.write(TEST_COLVAR)
    new_colvar = Colvar.from_file(TEST_COLVAR)
    assert new_colvar.header == colvar.header
    assert new_colvar.shape == colvar.shape
    assert np.allclose(new_colvar._data, colvar._data)
    os.remove(TEST_COLVAR)