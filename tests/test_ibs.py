from pydigree.ibs import ibs, chromwide_ibs
from pydigree.genotypes import GenotypedChromosome, SparseGenotypedChromosome

import numpy as np

def test_ibs():
    assert ibs( (2,2), (2,2) ) == 2
    assert ibs( (1,2), (1,2) ) == 2
    assert ibs( (2,1), (2,2) ) == 1
    assert ibs( (2,2), (2,1) ) == 1
    assert ibs( (1,1), (2,2) ) == 0
    assert ibs( (1,1), (0,0), missingval=64) == 64
    assert ibs( (1,1), (0,0) ) == None
    assert ibs( (0,0), (1,1) ) == None

def test_chromwide_ibs():
    g1 = [(2,2), (1,2), (1,2), (1,1), (0, 0)]
    g2 = [(2,2), (1,2), (2,2), (2,2), (1, 1)]

    a, b = [GenotypedChromosome(x) for x in zip(*g1)]
    c, d = [GenotypedChromosome(x) for x in zip(*g2)]

    expected = np.array([2,2,1,0,64])
    assert (chromwide_ibs(a,b,c,d) == expected).all()

    spa, spb = [SparseGenotypedChromosome(x) for x in zip(*g1)]
    spc, spd = [SparseGenotypedChromosome(x) for x in zip(*g2)]
    assert (chromwide_ibs(spa, spb, spc, spd) == expected).all()