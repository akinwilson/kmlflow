#!/usr/bin/env python3

"""
Client Node application skeleton.

Implementation of Node generates SK and PK, and completes computational challenges to
ensure availability and authenticity.

POC stage
"""

import secrets
import hashlib
import torch
from functools import partial
from modular_rnn import ModularRNN, ModularTanh
from key import Key

Q = 36028797018963913  # prime within signed64
SEED = 1666
DIM = 30


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Node:

    def __init__(self, dim=DIM, seed=SEED, q=Q):
        self.q = q
        self.seed = seed
        self.dim = dim
        self.mrnn = partial(
            ModularRNN, key=Key, d_out=dim, d_in=dim, activation=ModularTanh()
        )

    # a_t needs to be row vector
    def contest(self, a_t, steps):
        return self.mrnn(steps=steps).to(device)(a_t)

    @property
    def pk(self):
        return self.mrnn(steps=1).key.pk()

    def __repl__(self):
        pass


mrnn = ModularRNN(30, 30, key=Key).to(device)

x = torch.randint(0, 128, (1, 30), dtype=torch.int64).to(device).float()

print(mrnn(x).shape)
