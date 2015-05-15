from itertools import izip, chain, imap

import numpy as np

from pydigree.common import *
from pydigree.population import Population
from pydigree.individual import Individual
from pydigree.pedigree import Pedigree
from pydigree.pedigreecollection import PedigreeCollection
from pydigree.genotypes import GenotypedChromosome, SparseGenotypedChromosome


def read_ped(filename, population=None, delimiter=None, affected_labels=None,
             population_handler=None, data_handler=None, connect_inds=True, onlyinds=None):
    """
    Reads a plink format pedigree file, ie:
        familyid indid father mother sex whatever whatever whatever
    into a pydigree pedigree object, with optional population to
    assign to pedigree members. If you don't provide a population
    you can't simulate genotypes!

    Arguments
    -----
    filename: The file to be read
    population: The population to assign individuals to
    delimiter: a string defining the field separator, default: any whitespace
    affected_labels: The labels that determine affection status.
    population_handler: a function to set up the population 
    data_handler: a function to turn the data into useful individual information
    connect_inds: build references between individuals. Requires all
        individuals be present in the file
    onlyinds: a list of individuals to be processed, allows skipping parts
        of a file

    Returns: An object of class PedigreeCollection
    """
    sex_codes = {'1': 0, '2': 1, 'M': 0, 'F': 1, '0': None}
    if not affected_labels:
        affected_labels = {'1': 0, '2': 1,
                           'A': 1, 'U': 0,
                           'X': None,
                           '-9': None}

    # Tries to get a phenotype and returns unknown on failure
    def getph(ph):
        try:
            return affected_labels[ph]
        except KeyError:
            return None

    population = Population()

    p = Pedigree()
    if callable(population_handler):
        population_handler(p)

    pc = PedigreeCollection()

    with open(filename) as f:
        # Parse the lines in the file
        for line in f:
            split = line.strip().split(delimiter)
            fam, id, fa, mo, sex, aff = split[0:6]
            # Give a special id for now, to prevent overwriting duplicated
            # ids between families
            id = (fam, id)

            if onlyinds and (id not in onlyinds):
                continue

            p[id] = Individual(population, id, fa, mo, sex)
            p[id].phenotypes['affected'] = getph(aff)
            p[id].pedigree = p
            if callable(data_handler) and len(split) > 6:
                data = split[6:]
                data_handler(p[id],  data)

    # Fix the individual-level data
    for ind in p:
        if not connect_inds:
            continue
        fam, id = ind.id
        # Actually make the references instead of just pointing at strings
        ind.father = p[(fam, ind.father)] if ind.father != '0' else None
        ind.mother = p[(fam, ind.mother)] if ind.mother != '0' else None
        ind.sex = sex_codes[ind.sex]
        ind.register_with_parents()

    # Place individuals into pedigrees
    for pedigree_label in set(ind.id[0] for ind in p):
        ped = Pedigree(label=pedigree_label)
        if callable(population_handler):
            population_handler(ped)

        thisped = [x for x in p if x.id[0] == pedigree_label]
        for ind in thisped:
            ind.id = ind.id[1]
            ped[ind.id] = ind
            ind.population = ped
            ind.pedigree = ped
        pc[pedigree_label] = ped

    return pc


def read_phenotypes(pedigrees, csvfile, delimiter=',', missingcode='X'):
    """
    Reads a csv with header
    famid,ind,phen,phen,phen,phen etc etc

    Arguments
    ------
    Pedigrees:   An object of class PedigreeCollection
    csvfile:     the filename of the file containing phenotypes.
    delimiter:   the field delimiter for the file
    missingcode: the code for missing values

    Returns: Nothing
    """
    with open(csvfile) as f:
        header = f.readline().strip().split(delimiter)
        for line in f:
            # Match columns to their column name
            d = dict(zip(header, line.strip().split(delimiter)))
            for k, v in d.items():
                # Convert all phenotypes into floats
                try:
                    v = float(v)
                except ValueError:
                    if not v:
                        v = None
                if k in set(['famid', 'ind']):
                    continue
                fam, ind = d['famid'], d['ind']
                pedigrees[fam][ind].phenotypes[k] = v


def genotypes_from_sequential_alleles(chromosomes, data, missing_code='0', sparse=False):
    '''
    Takes a series of alleles and turns them into genotypes.

    For example: 
    The series '1 2 1 2 1 2' becomes 
    chrom1 = [1,1,1]
    chrom2 = [2,2,2]

    These are returned in the a list in the form [(chroma, chromb), (chroma, chromb)...]
    
    Arguments
    ------
    chromosomes: A list of ChromosomeTemplate objects corresponding to the genotypes
    data: The alleles to be turned into genotypes
    sparse: Return SparseGenotypedChromosomes instead of non-sparse

    Returns: A list of 2-tuples of GenotypedChromosome objects
    '''
    Chromobj = SparseGenotypedChromosome if sparse else GenotypedChromosome

    genotypes = []

    data = np.array(data)
    
    if not np.issubdtype(type(missing_code), data.dtype):
        raise ValueError('Invalid type for missing code: {}. Expected: {}'.format([type(missing_code), data.dtype]))

    if np.issubdtype(data.dtype, str):
        data[data == missing_code] = ''
    else:
        data[data == missing_code] = 0

    strand_a = data[0::2]
    strand_b = data[1::2]

    sizes = [x.nmark() for x in chromosomes]

    start = 0
    for i, size in enumerate(sizes):
        stop = start + size
        chroma = Chromobj(strand_a[start:stop])
        chromb = Chromobj(strand_b[start:stop])

        genotypes.append((chroma, chromb))
        start += size

    return genotypes
