#!/usr/bin/env python3

'''
Network Validator 

Implementation of Validator, who's responsibility is to registry Nodes, 
track availability and authenticity of Nodes, issuing periodic challenges
and tracking responses, and their consecutivity

POC stage 
'''

import torch 
import hashlib 
import secrets
from modular_rnn import ModularRNN, FiniteFieldLinear
from collections import OrderedDict

Q= 36028797018963913 # prime within signed64
SEED = 1666
DIM = 30 


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)



class Validator:
    cache = OrderedDict()

    def __init__(self, seed=SEED, q=Q):
        self.seed = seed 
        self.q = q

    def register(self,node_id, N_pk):
        A, b = N_pk
        Validator.cache[node_id] = {
            'A':A,
            'b':b,
            'seed':SEED,
            'dim':DIM,
            'step_count':[],
            'consequtivity':0,
        }


    def challenge(self, node_id):
        steps = 10
        Validator.cache[node_id]['step_count']= steps
        node = Validator.cache[node_id]
        # a_t
        h = hashlib.hashlib(node['A'].cpu().numpy().tobytes()).digest()
        for _ in range(steps):
            h = hashlib.sha256(h).digest()
        a_t = torch.tensor([int.frombytes(h[i*4:(i+1)*4], 'big') % self.q for i in range(node['dim']) ]) 
        return a_t, steps 


    def verify(self):
        pass 


    def node_statistics(self, node_id):
        return {}

    @property
    def registry():
        return Validator.cache 

fc = FiniteFieldLinear(20, 30).to(device)

x = torch.randint(0, 128, (1,30), dtype=torch.int64).to(device).float()


print(fc(x))
