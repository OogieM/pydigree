from nose.tools import assert_raises

from pydigree.common import product, cumsum, flatten, invert_dict, merge_dicts
from pydigree.common import count, grouper, log_base_change, mode
from pydigree.common import runs, runs_gte, interleave, is_sorted
from pydigree.cydigree.cyfuncs import runs_gte_uint8

from math import log, log10, e
import numpy as np

def float_equality(a,b):
    return abs(a-b) < 1e-15

def test_mode():
    a = [0,1,1,1,0,0,0,0]
    assert mode(a) == 0
    b = [1,2,3,1,2,1]
    assert mode(b) == 1

    assert_raises(IndexError, mode, []) 
def test_issorted():
    assert is_sorted([]) 
    assert is_sorted([1])

    assert is_sorted([1,2])
    assert not is_sorted([2,1])
    assert is_sorted([1,1,1,1])

def test_count():
    assert count(1, [0,0,0,1,1,1,0,0,0]) == 3
    assert count(1, [0]*10) == 0
    assert count('a', 'abba') == 2
    assert count(1, []) == 0
    
def test_product():
    assert product([1,2,3,4,5]) == 120
    assert product([0,1,2,3,4]) ==  0
    assert product([]) == 1

def test_cumsums():
    assert cumsum([]) == []
    assert cumsum([1,2,3]) == [1,3,6]

def test_grouper():
    groups = list(grouper([1,2]*100, 2))
    assert all(len(x) == 2 for x in groups)
    assert all(x == (1,2) for x in groups)

    groups = list(grouper([1,2]*100 + [1], 2))
    assert groups[-1] == (1, None)

def test_runs():
    dregion = (10,20)
    i = [1 if dregion[0] <= x <= dregion[1] else 0 for x in range(100)] 
    assert runs(i, lambda x: x>0) == [dregion]
    assert runs_gte(i, 1) == [dregion]
    assert runs_gte(i, 1, 20) == []
    assert runs_gte([], 1) == []
    assert runs([], lambda x: True) == []
    

    i = [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1]
    ir = [(4,8), (14, 16)]
    assert runs(i, lambda x: x > 0) == ir
    assert runs_gte(i, 1) == ir
    assert runs_gte_uint8(np.array(i, dtype=np.uint8), 1) == ir

    i = [0] * 100
    assert runs(i, lambda x: x > 0) == []
    assert runs_gte(i, 1) == []
    assert runs_gte_uint8(np.uint8(i),1) == []

    i = [1] * 100
    ir = [(0,99)]
    assert runs(i, lambda x: x>0) == ir
    assert runs_gte(i, 1) == ir
    assert runs_gte_uint8(np.array(i, dtype=np.uint8), 1) == ir

def test_flatten():
    assert list(flatten([1,2,2,3,4,4,5])) == [1,2,2,3,4,4,5]
    assert list(flatten([(1,2),2,3,(4,4,5)])) == [1,2,2,3,4,4,5]
    assert list(flatten([(1,(2,(2,(3,4)))),4,5])) == [1,2,2,3,4,4,5]
    assert list(flatten([])) == []

def test_mergedicts():
    a, b, c = {'a':1}, {'b':2}, {'c': 3}
    assert merge_dicts(a,b,c) == {'a': 1, 'b': 2, 'c': 3}
    assert merge_dicts({},{}) == {}

def test_invertdict():
    assert invert_dict({}) == {}
    assert invert_dict({1: 'a', 2: 'b'}) == {'a': 1, 'b': 2}

def test_logbasechange():
    assert float_equality(log(6), log_base_change(log10(6), e, 10))
    assert float_equality(log(4.2), log_base_change(log10(4.2), e, 10))

def test_interleave():
    assert interleave([1,1,1], [2,2,2]) == [1,2,1,2,1,2]
    assert interleave([1],[2]) == [1,2]
    assert interleave([],[]) == []
    assert_raises(ValueError, interleave, [1], [])

