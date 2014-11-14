import pydigree


def read_gs_chromosome_template(templatef):
    """ Reads a genomeSIMLA format chromosome template file """
    with open(templatef) as f:
        label = f.readline().strip()  # The label and
        f.readline()  # the number of markers, both of which we dont need.
        c = pydigree.Chromosome(label=label)
        # genomeSIMLA chromosome files have marginal recombination probs
        # instead of map positions. We'll have to keep track of what the
        # last position was and add to it to get it into the shape we want
        # it to be in.
        last_cm = 0
        for line in f:
            if line == '\n':
                continue
            label, majf, minf, cm, bp = line.strip().split()
            cm = float(cm)
            last_cm += cm
            c.add_genotype(float(minf), last_cm, label=label, bp=bp)
    return c
