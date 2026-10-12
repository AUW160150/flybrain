import numpy as np
from .graph_rnn import GraphRNN

class DiagonalLM(GraphRNN):
    """Independent scalar memories; deliberately not parameter matched."""
    def __init__(self,n:int,d:int,seed:int=1,execution:str='dense'):
        super().__init__(n,d,np.arange(n),np.arange(n),seed=seed,execution=execution)
