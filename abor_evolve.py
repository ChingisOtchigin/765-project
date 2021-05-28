#upi file name to avoid any accidental import conflicts
import random

def combine_genome(genome1, genome2, mu1=0.01, mu2=0.01):
    """Combines two (equally sized) lists of [0,1) floats."""
    #largely reusing Matthew's code here 
    assert len(genome1) == len(genome2), 'Oops, genomes of different length'

    new_genome = [random.random() if random.random() < mu2 else pair[random.random() < 0.5] + random.gauss(0,1) * mu1 for pair in zip(genome1, genome2)] #kinda proud of this one

    for i, gene in enumerate(new_genome):
        if gene > 1.0:
            new_genome[i] = 2.0 - gene
        elif gene < 0.0:
            new_genome[i] = -gene
    
    return new_genome




#print(combine_genome([random.random() for _ in range(10)], [random.random() for _ in range(10)]))

